import logging
import time
from pathlib import Path
from typing import NamedTuple

import docker
import pytest
import requests
from docker.models.containers import Container


class TestParameters(NamedTuple):
    __test__ = False
    base_url: str
    flush_tmp_file_enabled: bool
    request_session: requests.Session
    container: Container


@pytest.fixture(scope="module")
def mermaid_container():
    """
    Setup function for building and starting the mermaid-service image.
    Runs once per module and is cleaned up after execution

    Yields:
        Container: Built docker container
    """
    client = docker.from_env()
    image, _ = client.images.build(path=".", tag="mermaid_service", buildargs={"APP_IMAGE_VERSION": "1.0.0"})
    container = client.containers.run(
        image=image,
        detach=True,
        name="mermaid_service",
        ports={"9084": 9084},
        init=True,  # Enable Docker's init process (equivalent to tini)
    )
    time.sleep(5)

    yield container

    container.stop()
    container.remove()


@pytest.fixture(scope="module")
def test_parameters(mermaid_container: Container):
    """
    Setup function for test parameters and request session.
    Runs once per module and is cleaned up after execution.

    Args:
        mermaid_container (Container): mermaid-service docker container

    Yields:
        TestParameters: The setup test parameters
    """
    base_url = "http://localhost:9084"
    flush_tmp_file_enabled = False
    request_session = requests.Session()
    yield TestParameters(base_url, flush_tmp_file_enabled, request_session, mermaid_container)
    request_session.close()


def test_container_no_error_logs(test_parameters: TestParameters) -> None:
    logs = test_parameters.container.logs()

    assert len(logs.splitlines()) == 7


def test_convert_flowchart(test_parameters: TestParameters) -> None:
    mmd = __load_test_data("tests/test-data/flowchart.mmd")

    response = __send_request(base_url=test_parameters.base_url, request_session=test_parameters.request_session,
                              data=mmd, print_error=True)
    assert response.status_code == 200
    flush_tmp_file("test_convert_flowchart.svg", response.content, test_parameters.flush_tmp_file_enabled)

    expected_svg = __load_test_data("tests/test-data/flowchart-expected.svg")
    assert response.content.decode("utf-8").strip() == expected_svg.strip()


def test_convert_sequence_diagram(test_parameters: TestParameters) -> None:
    mmd = __load_test_data("tests/test-data/sequence-diagram.mmd")

    response = __send_request(base_url=test_parameters.base_url, request_session=test_parameters.request_session,
                              data=mmd, print_error=True)
    assert response.status_code == 200
    flush_tmp_file("test_convert_sequence_diagram.svg", response.content, test_parameters.flush_tmp_file_enabled)

    expected_svg = __load_test_data("tests/test-data/sequence-diagram-expected.svg")
    assert response.content.decode("utf-8").strip() == expected_svg.strip()


def test_convert_no_input(test_parameters: TestParameters) -> None:
    wrong_data = " "
    response = __send_request(base_url=test_parameters.base_url, request_session=test_parameters.request_session,
                              data=wrong_data, print_error=False)
    assert response.status_code == 400


def __load_test_data(file_path: str) -> str:
    with Path(file_path).open(encoding="utf-8") as mmd_file:
        content = mmd_file.read()
        return content


def __send_request(base_url: str, request_session: requests.Session, data, print_error,
                   parameters=None) -> requests.Response:
    url = f"{base_url}/convert"
    headers = {"Accept": "*/*", "Content-Type": "text/plain; charset=utf-8"}
    try:
        response = request_session.request(method="POST", url=url, headers=headers, data=data, verify=True,
                                           params=parameters)
        if response.status_code // 100 != 2 and print_error:
            logging.error(f"Error: Unexpected response: '{response}'")
            logging.error(f"Error: Response content: '{response.content}'")
        return response
    except requests.exceptions.RequestException as e:
        logging.error(f"Error: {e}")
        raise


def flush_tmp_file(file_name: str, file_bytes: bytes, flush_tmp_file_enabled: bool) -> None:
    if flush_tmp_file_enabled:
        with Path(file_name).open("wb") as f:
            f.write(file_bytes)
