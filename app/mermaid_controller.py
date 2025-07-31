import asyncio
import logging
import os
import platform
import tempfile
from pathlib import Path

import anyio
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
async def convert(request: Request) -> Response:
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

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mmd") as mmd_input_file:
            mmd_input_filepath = mmd_input_file.name
        with tempfile.NamedTemporaryFile(delete=False, suffix=".svg") as svg_output_file:
            svg_output_filepath = svg_output_file.name

        # Create temporary files for Mermaid input and SVG output
        async with await anyio.open_file(mmd_input_filepath, mode="w", encoding="utf-8") as f:
            await f.write(mmd)

        await run_mermaid_cli(mmdc_bin, mmd_input_filepath, svg_output_filepath)

        # Read the generated SVG content
        async with await anyio.open_file(svg_output_filepath, mode="r", encoding="utf-8") as f:
            svg_content = await f.read()

        return Response(svg_content, media_type="image/svg+xml", status_code=200)

    except AssertionError as e:
        return process_error(e, "Assertion error, check the request body", 400)
    except (UnicodeDecodeError, LookupError) as e:
        return process_error(e, "Cannot decode request body", 400)
    except RuntimeError as e:
        # If mmdc returns a non-zero exit code (error)
        return process_error(e, "Mermaid CLI conversion failed", 500)
    except FileNotFoundError as e:
        # If mmdc executable is not found
        error_message = f"Mermaid CLI (mmdc) not found. Ensure it's installed and in the PATH. Path attempted: {mmdc_bin}"
        return process_error(e, error_message, 500)
    except Exception as e:
        return process_error(e, "Unexpected error due converting to SVG", 500)
    finally:
        await clean_up_tmp_files(mmd_input_filepath, svg_output_filepath)


async def clean_up_tmp_files(mmd_input_filepath: str | None, svg_output_filepath: str | None) -> None:
    for path in [mmd_input_filepath, svg_output_filepath]:
        try:
            if path:
                Path(path).unlink(missing_ok=True)
        except Exception as cleanup_error:
            logging.warning(f"Failed to delete temp file {path}: {cleanup_error}")


async def run_mermaid_cli(mmdc_bin: str, input_path: str, output_path: str) -> None:
    # Construct and execute the command to call mermaid-cli
    # -i: input file, -o: output file
    # -p /puppeteer-config.json: Include the Puppeteer config file from the base image
    process = await asyncio.create_subprocess_exec(
        mmdc_bin,
        "-i",
        input_path,
        "-o",
        output_path,
        "-p",
        "/puppeteer-config.json",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        raise RuntimeError(f"Mermaid CLI failed: {stderr.decode()}")


def process_error(e: Exception, err_msg: str, status: int) -> Response:
    logging.exception(msg=err_msg + ": " + str(e))
    return Response(err_msg + ": " + getattr(e, "message", repr(e)), media_type="plain/text", status_code=status)


def start_server(port: int) -> None:
    uvicorn.run(app=app, host="", port=port)
