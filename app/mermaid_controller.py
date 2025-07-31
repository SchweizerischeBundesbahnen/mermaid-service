import logging
import os
import platform
import subprocess
import tempfile
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Request, Response

from app.schemas import VersionSchema

app = FastAPI(openapi_url="/static/openapi.json", docs_url="/api/docs")


@app.get("/version", response_model=VersionSchema)
async def version() -> dict[str, str | None]:
    """
    Get version information
    """
    return {
        "python": platform.python_version(),
        "mermaidCli": os.environ.get("MERMAID_CLI_VERSION") or "",
        "mermaidService": os.environ.get("MERMAID_SERVICE_VERSION") or "",
        "timestamp": os.environ.get("MERMAID_SERVICE_BUILD_TIMESTAMP") or "",
    }


@app.post(
    "/convert",
    responses={400: {"content": {"text/plain": {}}, "description": "Invalid Input"}, 500: {"content": {"text/plain": {}}, "description": "Internal SVG Conversion Error"}},
)
async def convert(
    request: Request,
) -> Response:
    """
    Convert MMD to SVG
    """
    mmd_input_filepath = None
    svg_output_filepath = None
    mmdc_bin = os.getenv("MMDC")

    try:
        mmd = (await request.body()).decode("utf-8")

        if not mmdc_bin:
            raise FileNotFoundError("Environment variable MMDC is not set or empty")

        if not mmd.strip():
            raise AssertionError("Empty request body")

        mmd_input_filepath, svg_output_filepath, svg_content = convert_mmd_to_svg(mmdc_bin, mmd)

        return Response(svg_content, media_type="image/svg+xml", status_code=200)

    except AssertionError as e:
        return process_error(e, "Assertion error, check the request body", 400)
    except (UnicodeDecodeError, LookupError) as e:
        return process_error(e, "Cannot decode request body", 400)
    except subprocess.CalledProcessError as e:
        # If mmdc returns a non-zero exit code (error)
        error_message = f"Mermaid CLI conversion failed. STDERR: {e.stderr}, STDOUT: {e.stdout}"
        return process_error(e, error_message, 500)
    except FileNotFoundError as e:
        # If mmdc executable is not found
        error_message = f"Mermaid CLI (mmdc) not found. Ensure it's installed and in the PATH. Path attempted: {mmdc_bin}"
        return process_error(e, error_message, 500)
    except Exception as e:
        return process_error(e, "Unexpected error due converting to SVG", 500)
    finally:
        # Clean up temporary files
        if mmd_input_filepath and Path(mmd_input_filepath).exists():
            Path(mmd_input_filepath).unlink()
        if svg_output_filepath and Path(svg_output_filepath).exists():
            Path(svg_output_filepath).unlink()


def convert_mmd_to_svg(mmdc_bin: str, mmd: str) -> tuple[str, str, str]:
    # Create temporary files for Mermaid input and SVG output
    with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".mmd", encoding="utf-8") as mmd_input_file:
        mmd_input_file.write(mmd)
        mmd_input_filepath = mmd_input_file.name

    with tempfile.NamedTemporaryFile(delete=False, suffix=".svg") as svg_output_file:
        svg_output_filepath = svg_output_file.name

    # Construct the command to call mermaid-cli
    # -i: input file, -o: output file
    # -p /puppeteer-config.json: Include the Puppeteer config file from the base image
    command = [mmdc_bin, "-i", mmd_input_filepath, "-o", svg_output_filepath, "-p", "/puppeteer-config.json"]

    # Execute the command
    # capture_output=True captures stdout and stderr
    # text=True decodes stdout/stderr as text
    subprocess.run(command, capture_output=True, text=True, check=True)  # noqa: S603 we trust the command

    # Read the generated SVG content
    with Path(svg_output_filepath).open(encoding="utf-8") as f:
        svg_content = f.read()

    return mmd_input_filepath, svg_output_filepath, svg_content


def process_error(e: Exception, err_msg: str, status: int) -> Response:
    logging.exception(msg=err_msg + ": " + str(e))
    return Response(err_msg + ": " + getattr(e, "message", repr(e)), media_type="plain/text", status_code=status)


def start_server(port: int) -> None:
    uvicorn.run(app=app, host="", port=port)
