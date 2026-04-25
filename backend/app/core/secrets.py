from functools import lru_cache
import logging

from google.cloud import secretmanager

logger = logging.getLogger(__name__)


@lru_cache(maxsize=128)
def get_secret(secret_id: str, project_id: str, version_id: str = "latest") -> str:
   
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"

    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("utf-8")