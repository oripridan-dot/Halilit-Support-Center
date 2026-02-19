# The New Workflow: Spec-Driven Factory

We build the Halilit Support Center as a **Dark Factory**: the **Specification** is the source of truth; the **Codebase** is the artifact. You act as the **Factory Owner**—you approve outcomes, not line-by-line code.

---

## Principles

1. **Specs, not tickets** — Requirements live in `specs/*.md` and `OPERATOR_CONSOLE_SPEC.md`. No "fix the button" without a spec that says what the button must do.
2. **Outcomes, not code** — You verify behavior in the app (e.g. "row turns red when stock is 0"). If it's wrong, you fix the **spec** and re-prompt; you don't debug the implementation by hand.
3. **One command to run** — Use `./factory_reset.sh` or `./start_console.sh`. No scattered "clear cache / verify / restart" playbooks.
4. **Golden scenarios** — Data quality is checked against `backend/tests/golden_scenarios.json`. Build fails (or compliance report fails) when the catalog doesn't satisfy those scenarios.

---

## The 5 Levels (Where You Are)

| Level | Role | What you do |
|-------|------|-------------|
| 1 | Encoder | Ask for a single function; review code. |
| 2 | Planner | Ask for a module; still review code. |
| **3** | **Architect** | **Ask for a component from a spec; verify behavior.** |
| **4** | **Scenario driver** | **Define scenarios (e.g. Playwright); approve pass/fail.** |
| **5** | **Factory Owner** | **Update spec → prompt Builder → approve outcome. No code review.** |

**Target:** Work at Level 5. You update a spec, send the standard prompt (see [SPEC_DRIVEN_DEVELOPMENT.md](SPEC_DRIVEN_DEVELOPMENT.md)), and only check that the app behaves as the spec says.

---

## Daily Loop

1. **Change a spec** — e.g. add "Grid rows must turn red if stock is 0" to `specs/interface/02_inventory_grid.md`.
2. **Prompt the Factory Builder** — "I have updated `specs/interface/02_inventory_grid.md`. Role: Factory Builder. Read the spec and `frontend/src/components/views/InventoryView.tsx`. Rewrite the component to satisfy the spec. Produce the code artifact."
3. **Verify in the app** — Run the app, go to Inventory Master, check if zero-stock rows are red.
   - **Yes** → Commit.
   - **No** → Refine the spec (e.g. "red = Tailwind `bg-red-900/20`") and re-prompt. Do not debug the component manually.

---

## What We Don’t Do Anymore

- **Don’t** paste code errors and ask "why doesn’t this work?" — Fix the spec or the scenario; then regenerate.
- **Don’t** maintain separate "ACTION_REQUIRED" or "VERIFY_CHANGES" docs — Single workflow: specs + [QUICK_START](QUICK_START.md) + [FACTORY_PIPELINE](FACTORY_PIPELINE.md).
- **Don’t** reference Galaxy, Spectrum, or Arena — Those views are removed. Only Mission Control, Inventory Master, Product Intelligence.

---

## See Also

- [OPERATOR_CONSOLE_SPEC.md](../OPERATOR_CONSOLE_SPEC.md) — Product Detail and compliance.
- [SPEC_DRIVEN_DEVELOPMENT.md](SPEC_DRIVEN_DEVELOPMENT.md) — Spec format and prompt templates.
- [FACTORY_PIPELINE.md](FACTORY_PIPELINE.md) — How to run and rebuild the factory.
