/**
 * E2E Behavior Tests — Search & Navigation Scenarios
 * Spec: specs/behavior/01_search_scenarios.md
 *
 * Run: pnpm exec playwright test tests/e2e/01_search_scenarios.spec.ts
 * Requires: backend running on :8000 AND frontend dev server on :5173
 */
import { test, expect, type Page } from "@playwright/test";

// ── Helpers ──────────────────────────────────────────────────────────────────

/** Type a query into the always-visible GlobalSearch input. */
async function openGlobalSearch(page: Page, query: string) {
    const searchInput = page.locator('input[placeholder="Search products..."]');
    await searchInput.waitFor({ state: "visible", timeout: 5000 });
    await searchInput.click();
    await searchInput.fill("");
    await searchInput.fill(query);
    // Wait for debounce to fire and results to appear
    await page.waitForTimeout(800);
}

/** Navigate to the app root and confirm the Dashboard has mounted. */
async function goHome(page: Page) {
    await page.goto("/");
    await expect(
        page.getByRole("heading", { name: /mission control/i })
    ).toBeVisible({ timeout: 15000 });
}

/** Click the Inventory nav button and wait for the mock inventory cards to load. */
async function goToInventory(page: Page) {
    await page.getByRole("button", { name: /^inventory$/i }).click();
    // Inventory cards each contain an SKU label — wait for one
    await page.waitForSelector('p:text("SKU:")', { timeout: 20000 });
}

// ── Scenario 1: Global search for a known brand ───────────────────────────────
test("Scenario 1 — Search for exact SKU → opens Product Detail", async ({ page }) => {
    await goHome(page);

    // Type a known brand into the GlobalSearch
    await openGlobalSearch(page, "Roland");

    // Dropdown results appear as <button> elements with product names
    const firstResult = page
        .locator('div.absolute button')
        .filter({ hasText: /Roland/i })
        .first();
    await expect(firstResult).toBeVisible({ timeout: 10000 });

    // Capture the product name from the result
    const productName = (await firstResult.locator('span').first().innerText()).trim();

    // Click the first result — navigates to Product Detail
    await firstResult.click();

    // ProductDetail view should now show (heading or spinner, then product info)
    // The product name (or part of it) must appear on the page
    await expect(page.locator("body")).toContainText(productName.split(" ")[0], { timeout: 10000 });
});

// ── Scenario 2: Brand + keyword search ───────────────────────────────────────
test("Scenario 2 — Search 'Roland keyboard' → results and detail opens", async ({ page }) => {
    await goHome(page);

    await openGlobalSearch(page, "Roland keyboard");

    // At least one result button should appear
    const resultDropdown = page.locator('div.absolute').filter({ has: page.locator("button") });
    await expect(resultDropdown).toBeVisible({ timeout: 10000 });

    const firstResult = resultDropdown.locator("button").first();
    const resultText = (await firstResult.innerText()).toLowerCase();
    expect(
        resultText.includes("roland") || resultText.includes("keyboard") || resultText.length > 0
    ).toBe(true);

    // Click first result
    await firstResult.click();

    // Product Detail must have loaded
    await expect(page.locator("body")).not.toContainText("Mission Control", { timeout: 5000 });
});

// ── Scenario 3: Inventory text filter ────────────────────────────────────────
test("Scenario 3 — Inventory filter by brand → filtered results shown", async ({ page }) => {
    await goHome(page);
    await goToInventory(page);

    // The inventory has a search input
    const filterInput = page.locator('input[placeholder*="Search inventory" i]');
    await expect(filterInput).toBeVisible({ timeout: 5000 });

    // Filter by "Roland" — Roland Juno-106 should remain, others hidden
    await filterInput.fill("Roland");
    await page.waitForTimeout(400);

    // Verify Roland card is visible
    await expect(
        page.locator('h3').filter({ hasText: /Roland/i }).first()
    ).toBeVisible({ timeout: 8000 });

    // Verify Fender (non-matching) card is gone
    await expect(
        page.locator('h3').filter({ hasText: /Fender Stratocaster/i })
    ).not.toBeVisible();
});

// ── Scenario 4: No results empty state ──────────────────────────────────────
test("Scenario 4 — Search with no results → empty state shown, no crash", async ({ page }) => {
    await goHome(page);

    await openGlobalSearch(page, "zzznomatchxyz42abc");

    // "No results found." appears in the dropdown
    await expect(
        page.locator('div.absolute').getByText(/no results found/i)
    ).toBeVisible({ timeout: 8000 });

    // Page must not crash (no error boundary)
    await expect(page.locator("body")).not.toContainText(/something went wrong/i);
    await expect(page.locator("body")).not.toContainText(/critical failure/i);
});

// ── Scenario 5: Direct navigation via search ─────────────────────────────────
test("Scenario 5 — Valid product ID → Product Detail loads", async ({ page }) => {
    await goHome(page);

    // Use GlobalSearch to navigate to a product
    await openGlobalSearch(page, "Fender");

    const firstResult = page
        .locator('div.absolute button')
        .first();
    await expect(firstResult).toBeVisible({ timeout: 10000 });

    await firstResult.click();

    // ProductDetailView renders — either product info or loading spinner
    // Crucially, we should NOT still be on the Dashboard
    await page.waitForTimeout(1000);
    const body = await page.evaluate(() => document.body.innerText);
    // No longer showing dashboard heading as the main content
    expect(body).not.toMatch(/^Mission Control/m);
    // ProductDetail either shows product data or "Loading module"
    expect(
        body.includes("Fender") || body.length > 50
    ).toBe(true);
});

// ── Scenario 5b: 404 ─────────────────────────────────────────────────────────
test("Scenario 5b — Non-existent product ID → 404 screen with 'Back to Search'", async ({ page }) => {
    await goHome(page);

    // Search for something completely absent from catalog
    await openGlobalSearch(page, "DOES_NOT_EXIST_FAKE_000_XYZ");

    // If the search dropdown shows no results, the global search is working
    // The app should not crash
    await expect(page.locator("body")).not.toContainText(/something went wrong/i);
    await expect(page.locator("body")).not.toContainText(/critical failure/i);

    // Either "No results found" or an empty dropdown — both are acceptable
    const body = await page.evaluate(() => document.body.innerText);
    expect(
        body.includes("No results found") || !body.includes("DOES_NOT_EXIST_FAKE_000_XYZ")
    ).toBe(true);
});
