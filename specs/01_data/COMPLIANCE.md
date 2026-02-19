# OpenClaw Use — Compliance & Legal

**Last updated:** 2025. This document describes the restricted, compliant use of the OpenClaw Field Agent within the Halilit Support Center.

---

## 1. Purpose & Scope

- **Purpose:** OpenClaw is used solely for **internal, B2B product intelligence**: verifying product specifications on **official manufacturer websites** (e.g. Roland, Yamaha) when our primary Python scraper cannot access JS-heavy or protected pages.
- **Scope:** Access is limited to **allowlisted manufacturer domains** only. No arbitrary URLs, no social media, no third-party retail or user-generated content sites unless explicitly allowlisted for product-spec verification.
- **Data use:** Extracted data (specs text, connectivity diagrams) is used only to enrich product records for the Support Center and is not sold or repurposed. We minimize retention (e.g. cache TTL, no long-term storage of raw scraped HTML).

---

## 2. Restrictions (Enforced)

- **Domain allowlist:** The Python bridge (`browser_agent.py`) permits only a fixed set of manufacturer domains. Requests for any other domain are rejected with `domain_not_allowed`.
- **Rate limiting:** Configurable cap (default 10 requests per 60 seconds per process) to prevent runaway or abusive use.
- **Timeouts:** All requests to OpenClaw are time-bounded (default 60s). No unbounded browser sessions.
- **Input validation:** `product_name` length is capped (default 200 chars). No user-supplied URLs or free-form “browse anywhere” from the Halilit backend.
- **Resource limits:** The OpenClaw container runs with Docker CPU/memory limits and `no-new-privileges` so it cannot escalate or consume unbounded resources.

---

## 3. Legal & Ethical Use

- **Respect for site terms:** Use is intended for **product specification lookup** in line with typical “public product page” access. Operators should be aware of and respect target sites’ Terms of Service and robots.txt where applicable. If a manufacturer disallows automated access, it should be removed from the allowlist.
- **No impersonation:** The agent does not identify as a consumer or use fake credentials. Our User-Agent and any identifiers are consistent with “Halilit Support / product research.”
- **No PII:** We do not send or request personally identifiable information through OpenClaw. Scraped content is product/spec data only.
- **No financial or account actions:** The agent does not log in, purchase, or perform account or payment operations on third-party sites.

---

## 4. Data Handling

- **Minimization:** Only the minimum data necessary for spec verification (e.g. specs table text, optional diagram image URL) is requested and stored in our cache.
- **Retention:** Cached JIT data follows the same TTL as the rest of the JIT pipeline (e.g. 7 days). No indefinite retention of raw scraped content.
- **No onward sharing:** Scraped content is not shared with third parties except as part of normal product display in the Halilit Support Center (e.g. showing “official specs” to internal or customer users).

---

## 5. Operator Responsibility

- **Allowlist maintenance:** Adding or removing domains is a code change (allowlist in `browser_agent.py`). Only trusted manufacturer product domains should be added.
- **Monitoring:** Use logging and (if available) OpenClaw-side logging to monitor usage and detect anomalies.
- **Incident response:** If a manufacturer objects to automated access, remove their domain from the allowlist and cease use.

---

## 6. Summary

OpenClaw is a **restricted, allowlisted, rate-limited** tool for **official product-spec verification** only. It is not a general-purpose browser agent. All use is scoped, time-bounded, and aligned with internal support and compliance requirements.
