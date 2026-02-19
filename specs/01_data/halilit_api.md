---
name: halilit_knowledge_base
description: Access the Halilit Support Center data to answer questions about products, stock, and compatibility. Internal use only. See COMPLIANCE.md.
---

# Halilit Support Center — Internal API Tools

**Use:** Internal product/stock/compatibility queries only. No PII or payment operations.

## Tool: lookup_product

Get specs, price, and product info by name or model.

**Request:** `GET http://backend:8000/api/products/search?q={{query}}`

**Parameters:**

- `query` — Product name or model (e.g. `FP-30X`, `Roland FP-30X`)

**Example:** `GET http://backend:8000/api/products/search?q=FP-30X`

---

## Tool: get_jit_intelligence

Get full JIT intelligence (specs, verdict, field notes) for a product by ID. Use after `lookup_product` when you have the product `id` (halilit_id).

**Request:** `POST http://backend:8000/api/jit/product/{{product_id}}`

**Parameters:**

- `product_id` — Halilit product ID (e.g. from lookup_product response).

**Note:** This endpoint returns Server-Sent Events (SSE). Consume the stream and use the `official_specs`, `verdict`, and `field_notes` events for the answer.

---

## Tool: get_visual_advice

Get visual signal-chain / connectivity advice for a product. Uses the same JIT stream; the `visual_intel` event contains signal chain and cheat sheet data.

**Request:** Same as `get_jit_intelligence` — the SSE stream includes a `visual_intel` event.
