FROM minlag/mermaid-cli:11.9.0@sha256:ed8df1d6ce4049724121f3e3f76c0d268b717d80483acca16fd37783de941879
LABEL maintainer="SBB Polarion Team <polarion-opensource@sbb.ch>"

ARG WORKING_DIR="/opt/mermaid"
# DO NOT CHANGE APP_IMAGE_VERSION --> It is controlled by the pipeline
ARG APP_IMAGE_VERSION=0.0.0

USER root

# hadolint ignore=DL3008
# hadolint ignore=DL3018
RUN apk update && apk add --no-cache \
    build-base \
    python3 \
    python3-dev \
    py3-pip \
    py3-setuptools \
    py3-wheel \
    py3-virtualenv

ENV MERMAID_SERVICE_VERSION=${APP_IMAGE_VERSION}

RUN mkdir -p ${WORKING_DIR}

WORKDIR ${WORKING_DIR}

COPY requirements.txt ${WORKING_DIR}/requirements.txt
COPY ./app/ ${WORKING_DIR}/app/
COPY ./poetry.lock ${WORKING_DIR}
COPY ./pyproject.toml ${WORKING_DIR}

COPY ./entrypoint.sh ${WORKING_DIR}

RUN BUILD_TIMESTAMP="$(date -u +'%Y-%m-%dT%H:%M:%SZ')" && \
    echo "${BUILD_TIMESTAMP}" > "${WORKING_DIR}/.build_timestamp"

RUN chown -R mermaidcli:mermaidcli ${WORKING_DIR}

USER mermaidcli

RUN chmod +x ${WORKING_DIR}/entrypoint.sh

# Create and configure logging directory
RUN mkdir -p ${WORKING_DIR}/logs && \
    chmod 777 ${WORKING_DIR}/logs

ENV VIRTUAL_ENV=${WORKING_DIR}/.venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN pip install --no-cache-dir -r "${WORKING_DIR}"/requirements.txt && poetry install --no-root --only main

EXPOSE 9084

ENTRYPOINT [ "./entrypoint.sh" ]
