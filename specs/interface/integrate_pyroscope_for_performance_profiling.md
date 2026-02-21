# Spec: Integrate Pyroscope for Performance Profiling
**Version:** 1.0
**Component:** `backend/pyroscope_integration.py`

## Purpose
To integrate Pyroscope for continuous performance profiling of the Halilit Support Center backend. This will enable efficient identification and resolution of performance bottlenecks, leading to improved responsiveness and scalability. Addresses the "Speed of Service" technical standard by providing tools to monitor and improve latency.

## Requirements
- [x] Create a new Python module `backend/pyroscope_integration.py` containing the logic for initializing and configuring the Pyroscope agent.
- [x] Install the Pyroscope Python agent (`pyroscopeio`) as a project dependency. Add `pyroscopeio` to `requirements.txt`.
- [x] The `backend/pyroscope_integration.py` module must define a function `init_pyroscope()` that initializes the Pyroscope agent.
- [x] The `init_pyroscope()` function must read Pyroscope configuration parameters (server address, application name, API key) from environment variables. The environment variables must be named: `PYROSCOPE_SERVER_ADDRESS`, `PYROSCOPE_APPLICATION_NAME`, and `PYROSCOPE_API_KEY`.
- [x] The `init_pyroscope()` function must start the Pyroscope agent.
- [x] The `init_pyroscope()` function must handle potential configuration errors gracefully (e.g., missing environment variables) and log appropriate error messages. If configuration is missing, it MUST NOT halt execution of the rest of the application — simply log the error.
- [x] Call `init_pyroscope()` early in the application startup sequence to ensure that profiling starts as soon as possible. Specifically, call it from `backend/main.py` during application initialization.
- [x] The integration must support CPU profiling, memory profiling, and block profiling.
- [x] Add a startup check to ensure that pyroscope can be started, given required environment variables.

## Data Contract
N/A — This feature does not involve data contracts in the traditional sense. It focuses on application instrumentation.

## Behavior Scenarios
- **Scenario:** Pyroscope is correctly configured and running.
  - Input: All required environment variables are set correctly.
  - Outcome: The Pyroscope agent starts successfully and begins profiling the application. Performance data is visible in the Pyroscope UI.
- **Scenario:** Required environment variables are missing.
  - Input: One or more of the required environment variables (`PYROSCOPE_SERVER_ADDRESS`, `PYROSCOPE_APPLICATION_NAME`, `PYROSCOPE_API_KEY`) are not set.
  - Outcome: The `init_pyroscope()` function logs an error message indicating the missing environment variable(s). The application continues to function normally (without profiling).
- **Scenario:** The Pyroscope server is unreachable.
    - Input: The `PYROSCOPE_SERVER_ADDRESS` environment variable is set to an invalid address.
    - Outcome: The `init_pyroscope()` function logs an error message indicating the connection failure. The application continues to function normally (without profiling).

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
- `pytest backend/tests/test_pyroscope_integration.py -v`
