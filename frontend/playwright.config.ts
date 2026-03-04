import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright E2E Test Configuration — Halilit Support Center
 *
 * Cycle design:
 *   01_search_scenarios  — GlobalSearch UX (search, results, navigation)
 *   02_navigation        — Sidebar nav, view transitions, header labels
 *   03_product_detail    — ProductDetailView rendering and controls
 *   04_inventory         — Inventory list, filter, pagination
 *   05_resilience        — Error states, empty states, no-crash contracts
 *
 * Browser: Chromium only in Codespace/dev environments.
 * To add Firefox / WebKit run: npx playwright install firefox webkit
 */
export default defineConfig({
    testDir: './tests/e2e',

    // Per-test timeout — generous for slow Codespace cold-starts
    timeout: 45_000,

    expect: {
        // Assertion polling window — 10 s covers most lazy-load patterns
        timeout: 10_000,
    },

    fullyParallel: false,          // sequential keeps server logs readable locally
    forbidOnly: !!process.env.CI,
    retries: process.env.CI ? 2 : 1,  // 1 retry locally to absorb flakes
    workers: 1,                    // single worker keeps API load predictable

    reporter: [
        ['html', { open: 'never', outputFolder: 'playwright-report' }],
        ['list'],
    ],

    use: {
        baseURL: 'http://localhost:5173',
        trace: 'on-first-retry',
        screenshot: 'only-on-failure',
        video: 'retain-on-failure',
        // Keep navigation deterministic even on slow networks
        actionTimeout: 15_000,
        navigationTimeout: 30_000,
    },

    projects: [
        {
            name: 'chromium',
            use: { ...devices['Desktop Chrome'] },
        },
        // Uncomment after: npx playwright install firefox webkit
        // { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
        // { name: 'webkit',  use: { ...devices['Desktop Safari'] } },
    ],

    webServer: {
        command: 'pnpm run dev',
        url: 'http://localhost:5173',
        // Reuse the already-running Vite dev server in local/Codespace
        reuseExistingServer: true,
        timeout: 120_000,
    },
});
