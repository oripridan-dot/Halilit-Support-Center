# backend/pyroscope_integration.py
import os
import logging
from pyroscope import configure, start_profiler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_pyroscope():
    """Initializes and starts the Pyroscope agent."""
    server_address = os.getenv("PYROSCOPE_SERVER_ADDRESS")
    application_name = os.getenv("PYROSCOPE_APPLICATION_NAME")
    api_key = os.getenv("PYROSCOPE_API_KEY")

    if not all([server_address, application_name, api_key]):
        missing_vars = [
            var for var, value in zip(
                ["PYROSCOPE_SERVER_ADDRESS", "PYROSCOPE_APPLICATION_NAME", "PYROSCOPE_API_KEY"],
                [server_address, application_name, api_key]
            ) if value is None
        ]
        missing_vars_str = ", ".join(missing_vars)
        logger.warning(f"Pyroscope initialization skipped: Missing environment variable(s): {missing_vars_str}")
        return

    try:
        configure(
            application_name=application_name,
            server_address=server_address,
            api_key=api_key,
        )
        start_profiler()
        logger.info("Pyroscope agent started successfully.")
    except Exception as e:
        logger.error(f"Failed to start Pyroscope agent: {e}")

if __name__ == '__main__':
    # Example usage (for testing purposes) - will not be executed in production
    init_pyroscope()
    # Simulate some work to be profiled (optional)
    import time
    time.sleep(5)