# Spec: Integrate Pyroscope for Performance Profiling
**Version:** 1.0
**Component:** `backend/main.py`

## Purpose
To integrate Pyroscope for continuous performance profiling of the Halilit Support Center backend. This will enable efficient identification and resolution of performance bottlenecks, leading to improved responsiveness and scalability. Addresses the "Speed of Service" technical standard by providing tools to monitor and improve latency.

## Requirements
- [x] Install the Pyroscope Python agent (`pyroscopeio`) as a project dependency. Add `pyroscopeio` to `requirements.txt`.
- [x] Create a new Python module `backend/pyroscope_integration.py` containing the logic for initializing and configuring the Pyroscope agent.
- [x] The `backend/pyroscope_integration.py` module must define a function `init_pyroscope()` that initializes the Pyroscope agent.
- [x] The `init_pyroscope()` function must read Pyroscope configuration parameters (server address, application name, API key) from environment variables. The environment variables must be named: `PYROSCOPE_SERVER_ADDRESS`, `PYROSCOPE_APPLICATION_NAME`, and `PYROSCOPE_API_KEY`.
- [x] The `init_pyroscope()` function must start the Pyroscope agent.
- [x] The `init_pyroscope()` function must handle potential configuration errors gracefully (e.g., missing environment variables) and log appropriate error messages. If configuration is missing, it MUST NOT halt execution of the rest of the application — simply log the error.
- [x] Call `init_pyroscope()` early in the application startup sequence to ensure that profiling starts as soon as possible. Specifically, call it from `backend/main.py` during application initialization.
- [x] The integration must support CPU profiling, memory profiling, and block profiling.
- [x] Add a startup check to ensure that pyroscope can be started, given required environment variables.

## Behavior Scenarios
- **Scenario:** All required environment variables are set.
  - Input: `PYROSCOPE_SERVER_ADDRESS`, `PYROSCOPE_APPLICATION_NAME`, and `PYROSCOPE_API_KEY` are set to valid values.
  - Outcome: The Pyroscope agent starts successfully and begins profiling the application. The console displays a message indicating that Pyroscope has started.
- **Scenario:** One or more required environment variables are missing.
  - Input: `PYROSCOPE_SERVER_ADDRESS` is missing.
  - Outcome: The Pyroscope agent does not start. An error message is logged indicating the missing environment variable. The application continues to run without Pyroscope profiling.
- **Scenario:** Pyroscope server is unreachable.
  - Input: `PYROSCOPE_SERVER_ADDRESS` points to a non-existent server.
  - Outcome: The Pyroscope agent attempts to start but fails to connect to the server. An error message is logged. The application continues to run, but no profiling data is sent to Pyroscope.

## Stitch UI Prompt
(Not applicable for backend spec)

## Verification Commands
- `python -m py_compile backend/main.py`
- `python -m py_compile backend/pyroscope_integration.py`
- `pytest backend/tests/test_pyroscope_integration.py -v`
