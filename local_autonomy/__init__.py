"""
Local Autonomy Module — Halilit Support Center
===============================================
This module provides the product's self-maintenance layer as defined in
TOOLOO_MASTER_PLAN.md Chapter 2.

Components:
  product_mcp_server.py  — exposes live product state to TooLoo Core via MCP
  facade_agent.py        — classifies and routes mandates to TooLoo Core
  warden.py              — hybrid loop (cron + event-driven) for minor self-fixes
  db_janitor.py          — auto-indexes slow queries, monitors DB health
  escalation_webhook.py  — fires HTTP webhook to TooLoo Core for architectural issues
  dependency_drift.py    — detects package version drift and stale dependencies
"""

__version__ = "0.1.0-scaffold"
