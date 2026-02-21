"""
Pyroscope integration for Halilit Support Center.

Spec: specs/interface/evolution_pyroscope.md

opt-in: set PYROSCOPE_SERVER_ADDRESS, PYROSCOPE_APPLICATION_NAME, PYROSCOPE_API_KEY
        in .env.  When the vars are absent the module is a silent no-op so the
        server still starts correctly without Pyroscope.

Install (optional):
  pip install pyroscope-io
"""
import contextlib
import functools
import os
import logging
from typing import Any, Callable, Iterator

try:
    import pyroscope
except ImportError:
    pyroscope = None  # type: ignore[assignment]


logger = logging.getLogger(__name__)


def init_pyroscope() -> bool:
    """
    Initialise the Pyroscope agent.
    Returns True on success, False when vars are missing or import failed.
    """
    if pyroscope is None:
        logger.debug("Pyroscope SDK not installed — profiling disabled.")
        return False

    server_address = os.getenv("PYROSCOPE_SERVER_ADDRESS")
    application_name = os.getenv(
        "PYROSCOPE_APPLICATION_NAME", "halilit-support-center")
    api_key = os.getenv("PYROSCOPE_API_KEY")

    if not server_address:
        logger.debug("PYROSCOPE_SERVER_ADDRESS not set — profiling disabled.")
        return False

    try:
        cfg: dict[str, Any] = {
            "application_name": application_name,
            "server_address": server_address,
            "tags": {"host": os.uname().nodename, "env": os.getenv("ENV", "dev")},
        }
        if api_key:
            cfg["api_key"] = api_key
        pyroscope.configure(**cfg)
        logger.info("✅ Pyroscope initialised → %s (%s)",
                    server_address, application_name)
        return True
    except Exception as exc:
        logger.error("Pyroscope init error: %s", exc)
        return False


def startup_check() -> bool:
    """Return True if the required env-vars are present."""
    if not os.getenv("PYROSCOPE_SERVER_ADDRESS"):
        logger.warning(
            "Pyroscope startup check failed: PYROSCOPE_SERVER_ADDRESS missing.")
        return False
    logger.info("Pyroscope startup check passed.")
    return True


@contextlib.contextmanager
def profile(tags: dict[str, str] | None = None) -> Iterator[None]:
    """
    Context manager that wraps a code block with Pyroscope tags.
    Safe no-op when pyroscope is not installed or not configured.

    Usage::

        with profile({"function": "build_catalog", "brand": brand}):
            run_expensive_work()
    """
    if pyroscope is None or tags is None:
        yield
        return
    try:
        with pyroscope.tag_wrapper(tags):
            yield
    except Exception:
        yield  # never block the calling code


def instrument(name: str | None = None) -> Callable:
    """
    Decorator that automatically tags a function call with its qualified name.

    Usage::

        @instrument()
        def build_catalog(root):
            ...
    """
    def decorator(fn: Callable) -> Callable:
        tag_name = name or f"{fn.__module__}.{fn.__qualname__}"

        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            with profile({"function": tag_name}):
                return fn(*args, **kwargs)

        return wrapper
    return decorator


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    ok = init_pyroscope()
    if ok:
        with profile({"function": "self_test"}):
            print("Pyroscope self-test: profiling active.")
    else:
        print("Pyroscope not available / not configured — self-test skipped.")


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
                ["PYROSCOPE_SERVER_ADDRESS",
                    "PYROSCOPE_APPLICATION_NAME", "PYROSCOPE_API_KEY"],
                [server_address, application_name, api_key],
            )
            if not value
        ]
        logging.warning(
            f"Pyroscope not initialized: Missing environment variables: {', '.join(missing_vars)}")
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
        logging.warning(
            "Pyroscope startup check failed: Missing environment variables.")
        return False
    else:
        logging.info(
            "Pyroscope startup check passed. Environment variables are present.")
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
