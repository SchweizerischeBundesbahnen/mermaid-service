# Copy uv from official image
FROM ghcr.io/astral-sh/uv:0.9.26@sha256:9a23023be68b2ed09750ae636228e903a54a05ea56ed03a934d00fe9fbeded4b AS uv-source

FROM minlag/mermaid-cli:11.12.0@sha256:bad64c9d9ad917c8dfbe9d9e9c162b96f6615ff019b37058638d16eb27ce7783
LABEL maintainer="SBB Polarion Team <polarion-opensource@sbb.ch>"

# Copy uv binary from source stage
COPY --from=uv-source /uv /usr/local/bin/uv

ARG WORKING_DIR="/opt/mermaid"
# DO NOT CHANGE APP_IMAGE_VERSION --> It is controlled by the pipeline
ARG APP_IMAGE_VERSION=0.0.0

USER root

# hadolint ignore=DL3018
RUN apk update && apk add --no-cache \
    python3 \
    python3-dev \
    build-base

ENV MERMAID_SERVICE_VERSION=${APP_IMAGE_VERSION}

RUN mkdir -p ${WORKING_DIR}

WORKDIR ${WORKING_DIR}

COPY ./app/ ${WORKING_DIR}/app/
COPY ./uv.lock ${WORKING_DIR}
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

# Install dependencies (no-dev excludes dev/test groups, no-install-project for app-only)
RUN uv sync --frozen --no-dev --no-install-project

# Add venv to PATH
ENV PATH="${WORKING_DIR}/.venv/bin:$PATH"

EXPOSE 9084

ENTRYPOINT [ "./entrypoint.sh" ]
