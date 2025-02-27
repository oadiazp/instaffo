from dotenv import load_dotenv
import logging
import yaml
import json
import os
from pathlib import Path
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

_LOGGER = logging.getLogger("python_developer_test")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(funcName)s - %(message)s",
)

load_dotenv(override=True)


class IndexPopulationError(Exception):
    """
    Raised when index population fails.
    """


def read_yaml(file_path):
    with open(file=file_path, encoding="utf-8", mode="r") as file_pointer:
        return yaml.full_load(file_pointer)


ES_URL = os.getenv("ES_URL")

ES_CONFIG_PATH = Path(__file__).parent / "es_config"
DATA_PATH = Path(__file__).parent / "data"


def index_setup(*, es_client: Elasticsearch, index_name: str, index_settings: dict):
    if es_client.indices.exists(index=index_name):
        es_client.indices.delete(index=index_name)

    index_mapping = read_yaml(ES_CONFIG_PATH / ("mappings_" + index_name + ".yml"))

    es_client.indices.create(
        index=index_name, mappings=index_mapping, settings=index_settings
    )
    _LOGGER.info(f"Successfully created index {index_name}.")


def populate(*, es_client: Elasticsearch, index_name: str) -> None:
    """
    Populates indices defined in config by inserting all actions.

    Args:
        index_name (str): Name of index to populate, e.g. candidates or jobs.

    Raises:
        IndexPopulationError: If errors occur in bulk insertion.
    """

    with open(DATA_PATH / (index_name + ".json")) as file_pointer:
        actions = json.load(file_pointer)

    _, errors = bulk(
        client=es_client,
        actions=actions,
        index=index_name,
        chunk_size=50,
        raise_on_error=False,
        refresh=True,
    )
    if errors:
        raise IndexPopulationError(f"failed to index some documents: {errors}.")

    _LOGGER.info(f"Successfully populated index {index_name}.")


if __name__ == "__main__":
    es_client = Elasticsearch(ES_URL)
    es_client.cluster.put_settings(
        persistent=read_yaml(ES_CONFIG_PATH / "cluster_settings.yml")["persistent"]
    )

    index_settings = read_yaml(ES_CONFIG_PATH / "index_settings.yml")

    index_setup(es_client=es_client, index_name="jobs", index_settings=index_settings)
    populate(es_client=es_client, index_name="jobs")

    index_setup(
        es_client=es_client, index_name="candidates", index_settings=index_settings
    )
    populate(es_client=es_client, index_name="candidates")
