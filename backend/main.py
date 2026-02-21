import os
import logging
from backend import pyroscope_integration

def init_app():
    """
    Initializes the application.  Calls init_pyroscope early in the startup.
    """
    logging.basicConfig(level=logging.INFO)
    pyroscope_integration.init_pyroscope()
    logging.info("Application initialized.")

if __name__ == "__main__":
    init_app()
    print("Backend application running...")