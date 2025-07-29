[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=SchweizerischeBundesbahnen_open-source-polarion-docker-repo-template&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=SchweizerischeBundesbahnen_open-source-polarion-docker-repo-template)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=SchweizerischeBundesbahnen_open-source-polarion-docker-repo-template&metric=bugs)](https://sonarcloud.io/summary/new_code?id=SchweizerischeBundesbahnen_open-source-polarion-docker-repo-template)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=SchweizerischeBundesbahnen_open-source-polarion-docker-repo-template&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=SchweizerischeBundesbahnen_open-source-polarion-docker-repo-template)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=SchweizerischeBundesbahnen_open-source-polarion-docker-repo-template&metric=coverage)](https://sonarcloud.io/summary/new_code?id=SchweizerischeBundesbahnen_open-source-polarion-docker-repo-template)
[![Duplicated Lines (%)](https://sonarcloud.io/api/project_badges/measure?project=SchweizerischeBundesbahnen_open-source-polarion-docker-repo-template&metric=duplicated_lines_density)](https://sonarcloud.io/summary/new_code?id=SchweizerischeBundesbahnen_open-source-polarion-docker-repo-template)
[![Lines of Code](https://sonarcloud.io/api/project_badges/measure?project=SchweizerischeBundesbahnen_open-source-polarion-docker-repo-template&metric=ncloc)](https://sonarcloud.io/summary/new_code?id=SchweizerischeBundesbahnen_open-source-polarion-docker-repo-template)
[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=SchweizerischeBundesbahnen_open-source-polarion-docker-repo-template&metric=reliability_rating)](https://sonarcloud.io/summary/new_code?id=SchweizerischeBundesbahnen_open-source-polarion-docker-repo-template)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=SchweizerischeBundesbahnen_open-source-polarion-docker-repo-template&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=SchweizerischeBundesbahnen_open-source-polarion-docker-repo-template)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=SchweizerischeBundesbahnen_open-source-polarion-docker-repo-template&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=SchweizerischeBundesbahnen_open-source-polarion-docker-repo-template)
[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=SchweizerischeBundesbahnen_open-source-polarion-docker-repo-template&metric=vulnerabilities)](https://sonarcloud.io/summary/new_code?id=SchweizerischeBundesbahnen_open-source-polarion-docker-repo-template)

# <<docker-image-name>> Service

<< Short Description >>

## Features

<< List of features >>

## Getting Started

### Installation

To install the latest version of the <<docker-image-name>> Service, run the following command:

```bash
docker pull ghcr.io/schweizerischebundesbahnen/<<docker-image-name>>:latest
```

### Running the Service

To start the <<docker-image-name>> service container, execute:

```bash
  docker run --detach \
    --init \
    --publish <<port>>:<<port>> \
    --name <<docker-image-name>> \
    ghcr.io/schweizerischebundesbahnen/<<docker-image-name>>:latest
```

The service will be accessible on port <<port>>.

> **Important**: The `--init` flag enables Docker's built-in init process which handles signal forwarding and zombie process reaping. This is required for proper operation of the service.

### Logging Configuration

The service includes a robust logging system with the following features:

- Log files are stored in `/opt/<<docker-image-name>>/logs` directory
- Log level can be configured via `LOG_LEVEL` environment variable (default: INFO)
- Log format: `timestamp - logger name - log level - message`
- Each service start creates a new timestamped log file

To customize logging when running the container:

```bash
docker run --detach \
  --publish <<port>>:<<port>> \
  --name <<docker-image-name>> \
  --env LOG_LEVEL=DEBUG \
  --volume /path/to/local/logs:/opt/<<docker-image-name>>/logs \
  ghcr.io/schweizerischebundesbahnen/<<docker-image-name>>:latest
```

Available log levels:

- DEBUG: Detailed information for debugging
- INFO: General operational information (default)
- WARNING: Warning messages for potential issues
- ERROR: Error messages for failed operations
- CRITICAL: Critical issues that require immediate attention

### Using as a Base Image

To extend or customize the service, use it as a base image in the Dockerfile:

```Dockerfile
FROM ghcr.io/schweizerischebundesbahnen/<<docker-image-name>>:latest
```

### Using Docker Compose

To run the service using Docker Compose:

```bash
docker-compose up -d
```

The Docker Compose configuration includes the `init: true` parameter which enables proper process management for the container.

## Development

### Building the Docker Image

To build the Docker image from the source with a custom version, use:

```bash
  docker build \
    --build-arg APP_IMAGE_VERSION=0.0.0 \
    --file Dockerfile \
    --tag <<docker-image-name>>:0.0.0 .
```

Replace 0.0.0 with the desired version number.

### Running the Development Container

To start the Docker container with your custom-built image:

```bash
  docker run --detach \
    --publish 9080:9080 \
    --name <<docker-container-name>> \
    <<docker-image-name>>:0.0.0
```

### Stopping the Container

To stop the running container, execute:

```bash
  docker container stop <<docker-container-name>>
```

### Testing

#### container-structure-test

The container-structure-test tool is used to verify that the Docker image meets expected standards and specifications. It validates the container structure, ensuring proper file paths, permissions, and commands are available, which helps maintain consistency and reliability of the containerized application.

Before running the following command, ensure that the `container-structure-test` tool is installed. You can find installation instructions in the [official documentation](https://github.com/GoogleContainerTools/container-structure-test).

```bash
container-structure-test test --image <<docker-container-name>>:0.0.0 --config ./tests/container/container-structure-test.yaml
```

#### grype

Grype is used for vulnerability scanning of the Docker image. This tool helps identify known security vulnerabilities in the dependencies and packages included in the container, ensuring the deployed application meets security standards and doesn't contain known exploitable components.

To scan the Docker image for vulnerabilities, you can use Grype. First, ensure that Grype is installed by following the [installation instructions](https://github.com/anchore/grype#installation).

Then run the vulnerability scan on your image:

```bash
grype <<docker-container-name>>:0.0.0
```

#### tox

Tox automates testing in different Python environments, ensuring that the application works correctly across various Python versions and configurations. It helps maintain compatibility and provides a standardized way to run test suites, formatting checks, and other quality assurance processes.

```bash
poetry run tox
```

#### pytest (for debugging)

Pytest is used for unit and integration testing of the application code. These tests verify that individual components and the entire application function correctly according to specifications. Running pytest during development helps catch bugs early and ensures code quality.

```bash
# all tests
poetry run pytest
```

```bash
# a specific test
poetry run pytest tests/test_app.py -v
```

#### pre-commit

Pre-commit hooks run automated checks on code before it's committed to the repository. This ensures consistent code style, formatting, and quality across the project. It helps catch common issues early in the development process, maintaining high code standards and reducing the need for style-related revisions during code reviews.

```bash
poetry run pre-commit run --all
```

### REST API

This service provides REST API. OpenAPI Specification can be obtained [here](app/static/openapi.json).
