# backend/pyroscope_integration.py
import os
import logging
from pyroscope import Pyroscope

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_pyroscope():
    """Initializes and starts the Pyroscope agent."""
    server_address = os.getenv("PYROSCOPE_SERVER_ADDRESS")
    application_name = os.getenv("PYROSCOPE_APPLICATION_NAME")
    api_key = os.getenv("PYROSCOPE_API_KEY")

    if not all([server_address, application_name, api_key]):
        missing_vars = []
        if not server_address:
            missing_vars.append("PYROSCOPE_SERVER_ADDRESS")
        if not application_name:
            missing_vars.append("PYROSCOPE_APPLICATION_NAME")
        if not api_key:
            missing_vars.append("PYROSCOPE_API_KEY")

        error_message = f"Pyroscope initialization skipped due to missing environment variable(s): {', '.join(missing_vars)}"
        logger.warning(error_message)
        return

    try:
        Pyroscope.start(
            server_address=server_address,
            application_name=application_name,
            api_key=api_key,
            tags={"env": "dev"},
            cpu_profiling=True,
            memory_profiling=True,
            block_profiling=True,
        )
        logger.info("Pyroscope agent started successfully.")

    except Exception as e:
        error_message = f"Failed to start Pyroscope agent: {e}"
        logger.error(error_message)