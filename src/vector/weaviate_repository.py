import time
import traceback
from contextlib import contextmanager
from typing import Generic, Type, TypeVar, Union
from uuid import uuid4

import weaviate
import weaviate.classes as wvc
import weaviate.classes.config as wc
import weaviate.classes.query as wq
from pydantic import BaseModel
from weaviate.auth import Auth
from weaviate.classes.config import Property
from weaviate.classes.init import AdditionalConfig, Timeout
from weaviate.exceptions import WeaviateQueryError

from src.vector.base_repository import BaseRepository
from src.utils.logger.logger import logger
from src.utils.statuses import Statuses, Status
from config import settings

T = TypeVar("T", bound=BaseModel)


class WeaviateRepository(BaseRepository[T], Generic[T]):
    def __init__(self, model: Type[T], collection_name: str) -> None:
        super().__init__(model, collection_name)
        self.client = None

    @staticmethod
    def _connect_to_remote():
        return weaviate.connect_to_custom(
            http_host=settings.weaviate.host,
            http_port=settings.weaviate.port,
            http_secure=True,
            grpc_host=settings.weaviate.grpc_host,
            grpc_port=settings.weaviate.grpc_port,
            grpc_secure=True,
            headers={"X-OpenAI-Api-Key": settings.ai_providers.openai_key},
            auth_credentials=Auth.api_key(settings.authorisation.WEAVIATE_AUTHORISATION_KEY),
            additional_config=AdditionalConfig(timeout=Timeout(init=5, query=10, insert=90)),
            skip_init_checks=True,
        )

    def connect(self, max_attempts: int = 3) -> None:
        for attempt in range(max_attempts):
            try:
                self.client = self._connect_to_remote()
                return
            except Exception as e:
                logger.error(f"Error during connection to VectorDB: {e}. Attempt - {attempt}")
                time.sleep(attempt * 2)
                continue

    def _disconnect(self) -> None:
        if self.client:
            self.client.close()

    @contextmanager
    def remote_connection(self):
        try:
            self.connect()
            yield self.client
        except Exception as e:
            logger.error(f"Error in vector db: {e}\n{traceback.format_exc()}")
        finally:
            self._disconnect()

    def search(self, query: str, limit: int = 5, **kwargs) -> list[T]:
        return self.hybrid_search(query, limit=limit, **kwargs)

    def insert(self, obj: T) -> None:
        with self.remote_connection() as client:
            collection = client.collections.get(self.collection_name)
            with collection.batch.dynamic() as batch:
                batch.add_object(properties=self._to_dict(obj))
                if batch.number_errors > 0:
                    logger.error(f"Batch error during insert in {self.collection_name}")

    def insert_many(self, objects: list[T]) -> list[T] | Status:
        failed_objects = []
        failed_references = []
        inserted_uuids = []

        with self.remote_connection() as client:
            try:
                collection = client.collections.get(self.collection_name)
                with collection.batch.dynamic() as batch:
                    for obj in objects:
                        batch.add_object(
                            properties=self._to_dict(obj),
                            uuid=obj.uuid,
                        )
                        inserted_uuids.append(obj.uuid)

                if collection.batch.failed_objects:
                    failed_objects.extend(collection.batch.failed_objects)
                if collection.batch.failed_references:
                    failed_references.extend(collection.batch.failed_references)

            except Exception as e:
                error_str = str(e)
                if "memory pressure" in error_str or "not enough memory mappings" in error_str:
                    logger.warning(f"Memory pressure detected, falling back to smaller batches: {error_str}")
                    return self._insert_many_fallback(objects)

                return Statuses.error(f"Batch insert failed: {error_str}")

        if failed_objects or failed_references:
            return Statuses.error(f"Failed to insert {len(failed_objects)} objects. Check logs for details.")

        result = []
        for uuid in inserted_uuids:
            obj = self.get_by_uuid(str(uuid))
            if obj is not None:
                result.append(obj)

        return result

    def _insert_many_fallback(self, objects: list[T]) -> list[T] | Status:
        failed_count = 0
        failed_details = []
        inserted = []

        with self.remote_connection() as client:
            collection = client.collections.get(self.collection_name)
            for i, obj in enumerate(objects):
                try:
                    if getattr(obj, "uuid", None) is None:
                        obj.uuid = str(uuid4())

                    collection.data.insert(
                        properties=self._to_dict(obj),
                        uuid=obj.uuid,
                    )
                    inserted.append(obj.uuid)
                except Exception as e:
                    error_msg = f"Object {i + 1}/{len(objects)}: {str(e)}"
                    logger.error(f"Failed to insert single object: {error_msg}")
                    failed_details.append(error_msg)
                    failed_count += 1

        if failed_count > 0:
            return Statuses.error(
                f"Failed to insert {failed_count}/{len(objects)} objects. Errors: {'; '.join(failed_details[:3])}",
            )

        result = []
        for uuid in inserted:
            obj = self.get_by_uuid(str(uuid))
            if obj is not None:
                result.append(obj)

        return result

    def update(self, uuid: str, obj: T) -> T | Status | None:
        with self.remote_connection() as client:
            try:
                properties = self._to_dict(obj)
                if properties:
                    collection = client.collections.get(self.collection_name)
                    collection.data.update(uuid=uuid, properties=properties)
                    return self.get_by_uuid(uuid)
                return self.get_by_uuid(uuid)
            except AttributeError as e:
                if "success" in str(e):
                    return self.get_by_uuid(uuid)
            except Exception as e:
                return Statuses.error(str(e))

    def delete(self, uuid: str) -> Status:
        with self.remote_connection() as client:
            try:
                collection = client.collections.get(self.collection_name)
                collection.data.delete_by_id(uuid)
                return Statuses.success()
            except AttributeError as e:
                if "success" in str(e):
                    return Statuses.success()
                return Statuses.not_found(str(e))
            except Exception as e:
                return Statuses.error(str(e))

    def hybrid_search(
            self,
            query: str,
            query_properties: list[str] | None = None,
            limit: int = 5,
            alpha: float = 0.7,
            max_attempts: int = 5,
            minimal_score: float = 0.8,
    ) -> list[T] | Status | None:
        error_message = None
        for attempt in range(max_attempts):
            with self.remote_connection() as client:
                try:
                    collection = client.collections.get(self.collection_name)
                    response = collection.query.hybrid(
                        query=query,
                        return_metadata=wq.MetadataQuery(score=True, explain_score=True),
                        query_properties=query_properties,
                        fusion_type=wq.HybridFusion.RELATIVE_SCORE,
                        limit=limit,
                        alpha=alpha,
                    )
                    list_objects = []
                    for obj in response.objects:
                        if obj.metadata.score > minimal_score:
                            created_object = self._from_dict(obj.properties)
                            if hasattr(created_object, "score"):
                                created_object.score = obj.metadata.score
                            if hasattr(created_object, "uuid"):
                                created_object.uuid = obj.uuid
                            list_objects.append(created_object)
                    return list_objects
                except WeaviateQueryError as e:
                    error = str(e)
                    errors_patterns = {
                        "Deadline Exceeded", "EOF", "DEADLINE_EXCEEDED",
                        "OpenAI API failed with status: 500 error",
                    }
                    if any(p in error for p in errors_patterns):
                        logger.warning(f"Attempt {attempt + 1}/{max_attempts} failed: {error}")
                        error_message = error
                    else:
                        logger.error(f"Unhandled WeaviateQueryError in hybrid_search: {e}")
                except Exception as e:
                    logger.error(f"Error in hybrid_search: {type(e).__name__}: {e}")
        logger.error(f"hybrid_search exhausted attempts: {error_message}")
        return []

    def near_text_search(
            self,
            query: str,
            limit: int = 5,
            allowed_vector_distance: float = 0.18,
            max_attempts: int = 5,
    ) -> list[T] | Status | None:
        error_message = None
        for attempt in range(max_attempts):
            with self.remote_connection() as client:
                try:
                    collection = client.collections.get(self.collection_name)
                    response = collection.query.near_text(
                        query=query,
                        return_metadata=wq.MetadataQuery(distance=True),
                        distance=allowed_vector_distance,
                        limit=limit,
                    )
                    return [self._from_dict(o.properties) for o in response.objects]
                except WeaviateQueryError as e:
                    error = str(e)
                    if any(p in error for p in {"Deadline Exceeded", "EOF", "DEADLINE_EXCEEDED"}):
                        logger.warning(f"Attempt {attempt + 1}/{max_attempts} failed: {error}")
                        error_message = error
                        continue
                    logger.error(f"Unhandled WeaviateQueryError in near_text_search: {e}")
                except Exception as e:
                    logger.error(f"Error in near_text_search: {type(e).__name__}: {e}")
        logger.error(f"near_text_search exhausted attempts: {error_message}")
        return []

    def bm25_search(self, query: str, limit: int = 7) -> list[T]:
        with self.remote_connection() as client:
            collection = client.collections.get(self.collection_name)
            response = collection.query.bm25(query=query, limit=limit)
            return [self._from_dict(o.properties) for o in response.objects]

    def create_collection(self, list_properties: list[Property]) -> Status:
        with self.remote_connection() as client:
            try:
                client.collections.create(
                    name=self.collection_name,
                    properties=list_properties,
                    vectorizer_config=wvc.config.Configure.Vectorizer.text2vec_openai(),
                    generative_config=wc.Configure.Generative.openai(),
                )
                return Statuses.success()
            except Exception as e:
                return Statuses.error(str(e))

    def delete_collection(self) -> None:
        with self.remote_connection() as client:
            client.collections.delete(self.collection_name)

    def get_all_vectors(
            self,
            limit: int | None = None,
            with_vectors: bool = False,
            order_by: str | None = None,
    ) -> Union[list[T] | Status | None]:
        with self.remote_connection() as client:
            try:
                collection = client.collections.get(self.collection_name)

                if order_by and limit:
                    response = collection.query.fetch_objects(
                        limit=limit,
                        include_vector=with_vectors,
                        sort=wq.Sort.by_property(name=order_by, ascending=True),
                    )
                    return [self._from_dict_with_uuid(item) for item in response.objects]
                elif limit and not order_by:
                    response = collection.query.fetch_objects(
                        limit=limit,
                        include_vector=with_vectors,
                    )
                    return [self._from_dict_with_uuid(item) for item in response.objects]
                else:
                    return [
                        self._from_dict_with_uuid(item)
                        for item in collection.iterator(include_vector=with_vectors)
                    ]
            except weaviate.exceptions.WeaviateQueryError as e:
                if "could not find class" in e.message:
                    return Statuses.not_found(f"Collection '{self.collection_name}' not found.")
            except Exception as e:
                return Statuses.error(str(e))

    def _from_dict_with_uuid(self, item) -> T:
        data = dict(item.properties)
        data['uuid'] = str(item.uuid)
        return self._from_dict(data)

    def get_by_uuid(self, uuid: str) -> T | None:
        with self.remote_connection() as client:
            collection = client.collections.get(self.collection_name)
            data_object = collection.query.fetch_object_by_id(uuid)
            if data_object is None:
                return None
            return self._from_dict_with_uuid(data_object)
