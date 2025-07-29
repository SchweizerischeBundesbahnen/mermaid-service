#!/bin/sh

BUILD_TIMESTAMP="$(cat /opt/mermaid/.build_timestamp)"
export MERMAID_SERVICE_BUILD_TIMESTAMP="${BUILD_TIMESTAMP}"

MMDC="/home/mermaidcli/node_modules/.bin/mmdc"
export MMDC
MERMAID_CLI_VERSION="$(${MMDC} --version | awk '{print $1}')"
export MERMAID_CLI_VERSION

poetry run python -m app.mermaid_service_application &

wait

exit $?
