// Contract: Integrate Pyroscope for Performance Profiling

// This feature does not involve a traditional API data contract.
// Pyroscope initialization is handled internally within the backend.
// No external API endpoints or data structures are directly exposed.

// The following type definitions are provided for illustrative purposes only.
// They reflect the configuration parameters used by the Pyroscope agent.
// The values are read from environment variables, but are not used for explicit API requests or responses.

export type PyroscopeConfig = {
  serverAddress?: string;
  applicationName?: string;
  apiKey?: string;
};

export type PyroscopeError = {
    message: string;
}