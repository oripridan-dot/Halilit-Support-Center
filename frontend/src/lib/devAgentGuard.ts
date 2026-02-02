/**
 * DevAgent Pre-Save Guard
 * Prevents syntax and type errors before they happen
 */

interface ValidationResult {
    is_safe: boolean;
    can_save: boolean;
    errors_count: number;
    warnings_count: number;
    errors: Array<{
        line: number;
        type: string;
        message: string;
        severity: string;
    }>;
    warnings: Array<{
        type: string;
        message: string;
        severity: string;
    }>;
    suggestions: string[];
    message: string;
}

/**
 * Validate code before saving/running
 */
export async function validateBeforeSave(
    filePath: string,
    code: string,
): Promise<ValidationResult> {
    try {
        const response = await fetch("/api/dev/validate-before-save", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ file_path: filePath, code }),
        });

        if (response.ok) {
            return await response.json();
        }

        throw new Error("Validation service unavailable");
    } catch (error) {
        console.error("DevAgent validation failed:", error);
        // Fail open - allow save if validation service is down
        return {
            is_safe: true,
            can_save: true,
            errors_count: 0,
            warnings_count: 0,
            errors: [],
            warnings: [
                {
                    type: "Validation Service Unavailable",
                    message: "DevAgent validation skipped",
                    severity: "info",
                },
            ],
            suggestions: [],
            message: "⚠️ Validation service unavailable",
        };
    }
}

/**
 * Validate syntax only (faster, for real-time checking)
 */
export async function validateSyntax(
    filePath: string,
    code: string,
): Promise<boolean> {
    try {
        const response = await fetch("/api/dev/validate-syntax", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ file_path: filePath, code }),
        });

        if (response.ok) {
            const result = await response.json();
            return result.is_safe;
        }

        return true; // Fail open
    } catch (error) {
        console.error("Syntax validation failed:", error);
        return true; // Fail open
    }
}

/**
 * Install as window.onbeforeunload if enabled
 */
export function installSaveGuard() {
    if (import.meta.env.DEV) {
        console.log("🛡️ DevAgent Save Guard installed");

        // This would need VS Code extension integration for real file saves
        // For now, just expose the API
        (window as any).DevAgent = (window as any).DevAgent || {};
        (window as any).DevAgent.validateBeforeSave = validateBeforeSave;
        (window as any).DevAgent.validateSyntax = validateSyntax;

        console.log(
            "✅ Use DevAgent.validateBeforeSave(filePath, code) to check code",
        );
    }
}
