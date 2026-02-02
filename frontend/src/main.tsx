import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { CopilotKit } from "@copilotkit/react-core";
import { CopilotSidebar } from "@copilotkit/react-ui";
import "@copilotkit/react-ui/styles.css";
import App from "./App.tsx";
import "./index.css";

const rootElement = document.getElementById("root");

// Check if CopilotKit API key is available
const copilotApiKey = import.meta.env.VITE_COPILOT_API_KEY;
const useCopilot = !!copilotApiKey;

if (rootElement) {
  try {
    createRoot(rootElement).render(
      <StrictMode>
        {useCopilot ? (
          <CopilotKit publicApiKey={copilotApiKey}>
            <CopilotSidebar
              instructions="You are the Halilit AI Agent Commander. You control the Trinity Swarm (CommercialScout, OfficialVerifier, ExternalValidator) to audit and enrich product catalogs. Ask me to run audits or check product data."
              defaultOpen={false}
            >
              <App />
            </CopilotSidebar>
          </CopilotKit>
        ) : (
          <App />
        )}
      </StrictMode>,
    );
  } catch (error) {
    rootElement.innerHTML = `
      <div style="padding: 40px; font-family: system-ui; max-width: 600px; margin: 0 auto;">
        <h1 style="color: #ef4444;">Failed to Load Application</h1>
        <p style="color: #64748b;">Check browser console for details</p>
        <pre style="background: #1e293b; color: #e2e8f0; padding: 20px; border-radius: 8px; overflow: auto;">${error}</pre>
      </div>
    `;
  }
}
