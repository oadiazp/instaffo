FROM python:3.9.16-slim-buster

COPY populate_es_indices.py .
COPY es_config/ ./es_config/
COPY data/ ./data/

ARG ES_URL
ENV ES_URL=${ES_URL}

RUN pip install elasticsearch==8.17.0 pyyaml python-dotenv

ENTRYPOINT ["python", "populate_es_indices.py"]