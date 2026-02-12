"""MCP (Model Context Protocol) bridge for Halilit Support Center.

Provides standardized tool access for Trinity Swarm agents.

Architecture:
    MCPRouter → MCPRegistry → MCPClient → MCP Servers

All servers disabled by default. Zero impact until enabled in mcp_config.json.
"""
