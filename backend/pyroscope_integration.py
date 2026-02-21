import os
import logging

try:
    import pyroscope
except ImportError:
    pyroscope = None
    logging.warning("Pyroscope is not installed. Performance profiling will be disabled.")


def init_pyroscope():
    """
    Initializes and configures the Pyroscope agent.
    Reads configuration from environment variables.
    """
    server_address = os.getenv("PYROSCOPE_SERVER_ADDRESS")
    application_name = os.getenv("PYROSCOPE_APPLICATION_NAME")
    api_key = os.getenv("PYROSCOPE_API_KEY")

    if not all([server_address, application_name, api_key]):
        missing_vars = [
            var
            for var, value in zip(
                ["PYROSCOPE_SERVER_ADDRESS", "PYROSCOPE_APPLICATION_NAME", "PYROSCOPE_API_KEY"],
                [server_address, application_name, api_key],
            )
            if not value
        ]
        logging.warning(f"Pyroscope not initialized: Missing environment variables: {', '.join(missing_vars)}")
        return

    try:
        if pyroscope:
            pyroscope.configure(
                application_name=application_name,
                server_address=server_address,
                api_key=api_key,
                tags={"host": os.uname().nodename},
            )
            logging.info("Pyroscope initialized successfully.")
    except Exception as e:
        logging.error(f"Error initializing Pyroscope: {e}")


def startup_check():
    """
    Performs a simple check to ensure Pyroscope can start given the environment variables.
    Logs a message indicating success or failure.
    """
    server_address = os.getenv("PYROSCOPE_SERVER_ADDRESS")
    application_name = os.getenv("PYROSCOPE_APPLICATION_NAME")
    api_key = os.getenv("PYROSCOPE_API_KEY")

    if not all([server_address, application_name, api_key]):
        logging.warning("Pyroscope startup check failed: Missing environment variables.")
        return False
    else:
        logging.info("Pyroscope startup check passed. Environment variables are present.")
        return True


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    init_pyroscope()
    if pyroscope:
        with pyroscope.tag_wrapper({"function": "my_function"}):
            print("Running my_function under Pyroscope profiling...")
        print("Pyroscope test complete.")
    else:
        print("Pyroscope not available, skipping test.")