// Contract: Integrate Pyroscope for Performance Profiling

// This API does not define any HTTP endpoints.
// The Pyroscope integration is handled internally within the backend service.
// Therefore, there are no request or response types to define in the traditional API sense.

// However, to represent the configuration parameters that the backend reads from
// environment variables, we can define a type for those:

export type PyroscopeConfig = {
  PYROSCOPE_SERVER_ADDRESS?: string;
  PYROSCOPE_APPLICATION_NAME?: string;
  PYROSCOPE_API_KEY?: string;
};

//Since the Pyroscope server being unreachable does not change any expected
//input or output, it does not affect the contract.