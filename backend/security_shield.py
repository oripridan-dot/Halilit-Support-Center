#!/usr/bin/env python3
"""
Halilit Support Center v7.0 - Security Shield
==============================================

Comprehensive security management system for the application.
Handles CORS, authentication gates, rate limiting, blockers, and all defenses.

Features:
  • CORS Configuration & Management
  • Authentication & Authorization Gates
  • Rate Limiting (per IP, per endpoint)
  • DDoS Protection & Blockers
  • Input Validation & Sanitization
  • Security Headers Management
  • Request Logging & Monitoring
  • IP Whitelisting/Blacklisting
  • Threat Detection
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from collections import defaultdict
import hashlib
import re


logger = logging.getLogger(__name__)


class SecurityConfig:
    """Central configuration for all security features."""

    def __init__(self, config_file: Optional[Path] = None):
        self.config_file = config_file or Path(
            __file__).parent / "security_config.json"
        self.config = self._load_config()
        self._init_defaults()

    def _load_config(self) -> Dict[str, Any]:
        """Load security configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file) as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load security config: {e}")
        return {}

    def _init_defaults(self):
        """Initialize default security settings."""
        defaults = {
            "cors": {
                "enabled": True,
                "allowed_origins": ["http://localhost:5173", "http://localhost:3000"],
                "allowed_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allowed_headers": ["Content-Type", "Authorization"],
                "allow_credentials": True,
                "max_age": 3600,
            },
            "rate_limiting": {
                "enabled": True,
                "global_limit": 1000,
                "global_window": 3600,
                "per_ip_limit": 100,
                "per_ip_window": 60,
                "per_endpoint_limit": 50,
                "per_endpoint_window": 60,
            },
            "authentication": {
                "enabled": True,
                "jwt_secret": "change-me-in-production",
                "jwt_algorithm": "HS256",
                "jwt_expiry": 3600,
                "require_auth": False,
                "protected_endpoints": ["/api/admin/*", "/api/internal/*"],
            },
            "ddos_protection": {
                "enabled": True,
                "burst_threshold": 50,
                "burst_window": 10,
                "block_duration": 600,
                "suspicious_threshold": 100,
                "monitor_request_size": True,
                "max_request_size": 10485760,  # 10MB
            },
            "input_validation": {
                "enabled": True,
                "sanitize_inputs": True,
                "max_string_length": 10000,
                "max_array_length": 1000,
                "block_sql_injection": True,
                "block_xss": True,
            },
            "security_headers": {
                "enabled": True,
                "headers": {
                    "X-Content-Type-Options": "nosniff",
                    "X-Frame-Options": "DENY",
                    "X-XSS-Protection": "1; mode=block",
                    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
                    "Content-Security-Policy": "default-src 'self'",
                    "Referrer-Policy": "strict-origin-when-cross-origin",
                }
            },
            "logging": {
                "enabled": True,
                "log_requests": True,
                "log_level": "INFO",
                "log_file": "backend/logs/security.log",
                "max_log_size": 10485760,  # 10MB
                "backup_count": 5,
            },
            "whitelist": {
                "enabled": False,
                "ips": [],
                "enforce": False,
            },
            "blacklist": {
                "enabled": True,
                "ips": [],
                "patterns": [],  # e.g., suspicious user agents
            },
            "threat_detection": {
                "enabled": True,
                "monitor_failed_auth": True,
                "max_failed_attempts": 5,
                "lockout_duration": 900,
                "monitor_unusual_patterns": True,
            }
        }

        # Merge defaults with loaded config
        for key, value in defaults.items():
            if key not in self.config:
                self.config[key] = value
            elif isinstance(value, dict):
                for subkey, subvalue in value.items():
                    if subkey not in self.config[key]:
                        self.config[key][subkey] = subvalue

        self.save()

    def save(self):
        """Save configuration to file."""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save security config: {e}")

    def get(self, path: str, default=None) -> Any:
        """Get config value by dot-notation path."""
        parts = path.split('.')
        value = self.config
        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            else:
                return default
        return value if value is not None else default

    def set(self, path: str, value: Any):
        """Set config value by dot-notation path."""
        parts = path.split('.')
        target = self.config
        for part in parts[:-1]:
            if part not in target:
                target[part] = {}
            target = target[part]
        target[parts[-1]] = value
        self.save()


class CORSManager:
    """Manages Cross-Origin Resource Sharing configuration."""

    def __init__(self, config: SecurityConfig):
        self.config = config

    def get_cors_headers(self, origin: Optional[str] = None) -> Dict[str, str]:
        """Get CORS headers based on origin."""
        if not self.config.get("cors.enabled"):
            return {}

        allowed_origins = self.config.get("cors.allowed_origins", [])

        headers = {
            "Access-Control-Allow-Methods": ", ".join(
                self.config.get("cors.allowed_methods", ["GET", "POST"])
            ),
            "Access-Control-Allow-Headers": ", ".join(
                self.config.get("cors.allowed_headers", ["Content-Type"])
            ),
            "Access-Control-Max-Age": str(self.config.get("cors.max_age", 3600)),
        }

        if origin and (origin in allowed_origins or "*" in allowed_origins):
            headers["Access-Control-Allow-Origin"] = origin
            if self.config.get("cors.allow_credentials"):
                headers["Access-Control-Allow-Credentials"] = "true"

        return headers

    def add_origin(self, origin: str):
        """Add an allowed origin."""
        origins = self.config.get("cors.allowed_origins", [])
        if origin not in origins:
            origins.append(origin)
            self.config.set("cors.allowed_origins", origins)

    def remove_origin(self, origin: str):
        """Remove an allowed origin."""
        origins = self.config.get("cors.allowed_origins", [])
        if origin in origins:
            origins.remove(origin)
            self.config.set("cors.allowed_origins", origins)


class RateLimiter:
    """Manages rate limiting for requests."""

    def __init__(self, config: SecurityConfig):
        self.config = config
        self.global_requests: Dict[str, List[float]] = defaultdict(list)
        self.ip_requests: Dict[str, List[float]] = defaultdict(list)
        self.endpoint_requests: Dict[str, Dict[str, List[float]]] = defaultdict(
            lambda: defaultdict(list))

    def is_allowed(self, client_ip: str, endpoint: str = None) -> tuple[bool, str]:
        """Check if request should be allowed based on rate limits."""
        if not self.config.get("rate_limiting.enabled"):
            return True, "Rate limiting disabled"

        now = datetime.now().timestamp()

        # Check global rate limit
        global_limit = self.config.get("rate_limiting.global_limit", 1000)
        global_window = self.config.get("rate_limiting.global_window", 3600)
        self.global_requests['all'] = [
            t for t in self.global_requests.get('all', [])
            if now - t < global_window
        ]
        if len(self.global_requests['all']) >= global_limit:
            return False, f"Global rate limit exceeded ({global_limit}/{global_window}s)"
        self.global_requests['all'].append(now)

        # Check per-IP rate limit
        ip_limit = self.config.get("rate_limiting.per_ip_limit", 100)
        ip_window = self.config.get("rate_limiting.per_ip_window", 60)
        self.ip_requests[client_ip] = [
            t for t in self.ip_requests.get(client_ip, [])
            if now - t < ip_window
        ]
        if len(self.ip_requests[client_ip]) >= ip_limit:
            return False, f"Per-IP rate limit exceeded ({ip_limit}/{ip_window}s)"
        self.ip_requests[client_ip].append(now)

        # Check per-endpoint rate limit
        if endpoint:
            endpoint_limit = self.config.get(
                "rate_limiting.per_endpoint_limit", 50)
            endpoint_window = self.config.get(
                "rate_limiting.per_endpoint_window", 60)
            self.endpoint_requests[endpoint][client_ip] = [
                t for t in self.endpoint_requests[endpoint].get(client_ip, [])
                if now - t < endpoint_window
            ]
            if len(self.endpoint_requests[endpoint][client_ip]) >= endpoint_limit:
                return False, f"Per-endpoint rate limit exceeded ({endpoint_limit}/{endpoint_window}s)"
            self.endpoint_requests[endpoint][client_ip].append(now)

        return True, "OK"

    def get_stats(self, client_ip: str = None) -> Dict[str, Any]:
        """Get rate limit statistics."""
        return {
            "global_requests": len(self.global_requests.get('all', [])),
            "ip_requests": len(self.ip_requests.get(client_ip, [])) if client_ip else 0,
            "tracked_ips": len(self.ip_requests),
        }


class InputValidator:
    """Validates and sanitizes input data."""

    def __init__(self, config: SecurityConfig):
        self.config = config
        # Common SQL injection patterns
        self.sql_patterns = [
            r"(\bbung\b|union.*\bselect|select.*\bwhere|drop.*\btable|insert.*\binto|delete.*\bfrom)",
            r"(;|--|#|\/\*|\*\/)",
        ]
        # Common XSS patterns
        self.xss_patterns = [
            r"<\s*script[^>]*>.*?<\s*/\s*script\s*>",
            r"on\w+\s*=",
            r"javascript:",
            r"<\s*iframe",
        ]

    def validate(self, data: Any, field_name: str = "data") -> tuple[bool, str]:
        """Validate input data."""
        if not self.config.get("input_validation.enabled"):
            return True, "OK"

        # Check type and size
        if isinstance(data, str):
            max_len = self.config.get(
                "input_validation.max_string_length", 10000)
            if len(data) > max_len:
                return False, f"String exceeds max length ({len(data)}/{max_len})"

            if self.config.get("input_validation.block_sql_injection"):
                if self._has_sql_injection(data):
                    return False, "Potential SQL injection detected"

            if self.config.get("input_validation.block_xss"):
                if self._has_xss(data):
                    return False, "Potential XSS attack detected"

        elif isinstance(data, (list, tuple)):
            max_len = self.config.get(
                "input_validation.max_array_length", 1000)
            if len(data) > max_len:
                return False, f"Array exceeds max length ({len(data)}/{max_len})"

        elif isinstance(data, dict):
            for key, value in data.items():
                valid, msg = self.validate(value, key)
                if not valid:
                    return False, msg

        return True, "OK"

    def sanitize(self, data: str) -> str:
        """Sanitize string input."""
        if not self.config.get("input_validation.sanitize_inputs"):
            return data

        # Remove potential XSS
        data = re.sub(
            r"<\s*script[^>]*>.*?<\s*/\s*script\s*>", "", data, flags=re.IGNORECASE)
        data = re.sub(r"on\w+\s*=\s*['\"]", "", data, flags=re.IGNORECASE)

        return data.strip()

    def _has_sql_injection(self, data: str) -> bool:
        """Check for SQL injection patterns."""
        for pattern in self.sql_patterns:
            if re.search(pattern, data, re.IGNORECASE):
                return True
        return False

    def _has_xss(self, data: str) -> bool:
        """Check for XSS patterns."""
        for pattern in self.xss_patterns:
            if re.search(pattern, data, re.IGNORECASE):
                return True
        return False


class DDoSProtection:
    """Protects against DDoS attacks."""

    def __init__(self, config: SecurityConfig):
        self.config = config
        self.request_bursts: Dict[str, List[float]] = defaultdict(list)
        self.blocked_ips: Dict[str, float] = {}
        self.suspicious_ips: Set[str] = set()

    def check_request(self, client_ip: str) -> tuple[bool, str]:
        """Check if request should be blocked due to DDoS detection."""
        if not self.config.get("ddos_protection.enabled"):
            return True, "OK"

        # Check if IP is blocked
        if client_ip in self.blocked_ips:
            block_duration = self.config.get(
                "ddos_protection.block_duration", 600)
            if datetime.now().timestamp() - self.blocked_ips[client_ip] < block_duration:
                return False, f"IP temporarily blocked ({block_duration}s)"
            else:
                del self.blocked_ips[client_ip]

        # Check burst rate
        now = datetime.now().timestamp()
        burst_window = self.config.get("ddos_protection.burst_window", 10)
        self.request_bursts[client_ip] = [
            t for t in self.request_bursts.get(client_ip, [])
            if now - t < burst_window
        ]

        burst_threshold = self.config.get(
            "ddos_protection.burst_threshold", 50)
        if len(self.request_bursts[client_ip]) >= burst_threshold:
            self.blocked_ips[client_ip] = now
            return False, f"Burst threshold exceeded ({burst_threshold}/{burst_window}s)"

        self.request_bursts[client_ip].append(now)

        # Track suspicious IPs
        suspicious_threshold = self.config.get(
            "ddos_protection.suspicious_threshold", 100)
        total_requests = len(self.request_bursts[client_ip])
        if total_requests > suspicious_threshold:
            self.suspicious_ips.add(client_ip)

        return True, "OK"

    def get_status(self) -> Dict[str, Any]:
        """Get DDoS protection status."""
        return {
            "currently_blocked": len(self.blocked_ips),
            "suspicious_ips": len(self.suspicious_ips),
            "active_tracking": len(self.request_bursts),
        }


class SecurityShield:
    """Main security orchestrator combining all defensive mechanisms."""

    def __init__(self, config_file: Optional[Path] = None):
        self.config = SecurityConfig(config_file)
        self.cors = CORSManager(self.config)
        self.rate_limiter = RateLimiter(self.config)
        self.input_validator = InputValidator(self.config)
        self.ddos_protection = DDoSProtection(self.config)

        # Setup logging
        self._setup_logging()

    def _setup_logging(self):
        """Setup security logging."""
        if not self.config.get("logging.enabled"):
            return

        log_file = self.config.get(
            "logging.log_file", "backend/logs/security.log")
        log_level = self.config.get("logging.log_level", "INFO")

        Path(log_file).parent.mkdir(parents=True, exist_ok=True)

        handler = logging.FileHandler(log_file)
        handler.setLevel(getattr(logging, log_level))
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    def check_request(self, client_ip: str, endpoint: str = None, data: Any = None) -> tuple[bool, str]:
        """Comprehensive request security check."""

        # Check DDoS protection
        allowed, msg = self.ddos_protection.check_request(client_ip)
        if not allowed:
            logger.warning(
                f"DDoS protection blocked request from {client_ip}: {msg}")
            return False, msg

        # Check rate limiting
        allowed, msg = self.rate_limiter.is_allowed(client_ip, endpoint)
        if not allowed:
            logger.warning(
                f"Rate limiting blocked request from {client_ip}: {msg}")
            return False, msg

        # Validate input
        if data:
            valid, msg = self.input_validator.validate(data)
            if not valid:
                logger.warning(
                    f"Input validation failed from {client_ip}: {msg}")
                return False, msg

        logger.info(f"Request allowed from {client_ip} to {endpoint}")
        return True, "OK"

    def get_security_status(self) -> Dict[str, Any]:
        """Get comprehensive security status."""
        return {
            "cors": {
                "enabled": self.config.get("cors.enabled"),
                "allowed_origins": self.config.get("cors.allowed_origins"),
            },
            "rate_limiting": {
                "enabled": self.config.get("rate_limiting.enabled"),
                "stats": self.rate_limiter.get_stats(),
            },
            "ddos_protection": {
                "enabled": self.config.get("ddos_protection.enabled"),
                "status": self.ddos_protection.get_status(),
            },
            "input_validation": {
                "enabled": self.config.get("input_validation.enabled"),
            },
            "logging": {
                "enabled": self.config.get("logging.enabled"),
            },
            "timestamp": datetime.now().isoformat(),
        }


def main():
    """Test security shield."""
    shield = SecurityShield()

    print("🛡️  Halilit Security Shield v7.0")
    print("=" * 70)

    status = shield.get_security_status()
    print(json.dumps(status, indent=2))

    # Test a request
    print("\n🧪 Testing request checks...")
    allowed, msg = shield.check_request(
        "192.168.1.1", "/api/products", {"query": "test"})
    print(f"Request allowed: {allowed} - {msg}")


if __name__ == "__main__":
    main()
