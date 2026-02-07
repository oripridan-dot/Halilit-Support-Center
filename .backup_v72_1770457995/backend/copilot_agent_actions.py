"""
CopilotKit Agent Actions

Frontend-facing definitions for agent actions that use the Skills Framework.
These are exposed through the CopilotKit provider.
"""

export const INGESTION_SKILL_ACTIONS = {
    // Harvest Phase - Extract and normalize
    harvest: {
        description: "Extract and normalize raw product data from source",
        displayName: "🔄 Harvest Product",
        endpoint: "/api/copilot/execute-skill",
        parameters: {
            skill: "harvest",
            context: {
                raw_product: "object",
                brand: "string"
            }
        }
    },

    // Enrich Phase - Add taxonomy + official data
    enrich: {
        description: "Add taxonomy classification and official specifications",
        displayName: "📚 Enrich with Taxonomy",
        endpoint: "/api/copilot/execute-skill",
        parameters: {
            skill: "enrich",
            context: {
                draft: "IngestionProductDraft"
            }
        }
    },

    // Tier Phase - Pricing
    tier: {
        description: "Calculate pricing tier and discount",
        displayName: "💰 Calculate Tier",
        endpoint: "/api/copilot/execute-skill",
        parameters: {
            skill: "tier",
            context: {
                draft: "IngestionProductDraft"
            }
        }
    },

    // Prepare Phase - Display
    prepare: {
        description: "Prepare display properties for frontend",
        displayName: "🎨 Prepare Display",
        endpoint: "/api/copilot/execute-skill",
        parameters: {
            skill: "prepare",
            context: {
                draft: "IngestionProductDraft"
            }
        }
    },

    // Validate Phase - Audit
    validate: {
        description: "Audit product against compliance rules",
        displayName: "✅ Validate Product",
        endpoint: "/api/copilot/execute-skill",
        parameters: {
            skill: "validate",
            context: {
                draft: "IngestionProductDraft"
            }
        }
    },

    // Approve Phase - Final decision
    approve: {
        description: "Final approval and recording",
        displayName: "🏁 Approve",
        endpoint: "/api/copilot/execute-skill",
        parameters: {
            skill: "approve",
            context: {
                draft: "IngestionProductDraft",
                is_valid: "boolean",
                errors: "string[]"
            }
        }
    },

    // Pipeline Phase - Full execution
    pipeline: {
        description: "Execute complete 6-phase ingestion pipeline",
        displayName: "🚀 Full Pipeline",
        endpoint: "/api/copilot/pipeline",
        parameters: {
            raw_product: "object",
            brand: "string"
        }
    },

    // Batch Phase - Multiple products
    batch: {
        description: "Ingest multiple products with progress tracking",
        displayName: "📦 Batch Ingest",
        endpoint: "/api/copilot/batch-ingest",
        parameters: {
            products: "object[]",
            brand: "string"
        }
    }
}

// Export as JavaScript instead of Python
export const initializeAgentActions = () = > {
    return Object.entries(INGESTION_SKILL_ACTIONS).map(([key, action])=> ({
        name: key,
        ...action
    }))
}
