# Halilit Security Shield v7.0

## Overview

The Conductor now manages **all defensive aspects** of the application through the integrated **Security Shield (v7.0)**.

The Security Shield provides comprehensive protection with:

- ✅ **CORS Management** - Whitelist/blacklist allowed origins
- ✅ **Rate Limiting** - Global, per-IP, per-endpoint limits
- ✅ **DDoS Protection** - Burst detection and IP blocking
- ✅ **Input Validation** - SQL injection & XSS detection
- ✅ **Security Headers** - Standard security headers
- ✅ **Threat Detection** - Monitor suspicious patterns
- ✅ **Audit Logging** - Complete request/security logging

---

## CLI Commands

### Show Security Status

```bash
python backend/conductor_main.py shield
```

Displays comprehensive security overview:

- CORS configuration
- Rate limiting stats
- DDoS protection status
- Input validation state
- Security logging status

### CORS Management

```bash
# List allowed origins
python backend/conductor_main.py shield-cors list

# Allow a new origin
python backend/conductor_main.py shield-cors add https://example.com

# Remove an origin
python backend/conductor_main.py shield-cors remove https://example.com
```

### Rate Limiting Configuration

```bash
python backend/conductor_main.py shield-limits
```

Shows:

- Global request limits
- Per-IP limits
- Per-endpoint limits

### DDoS Protection Status

```bash
python backend/conductor_main.py shield-ddos
```

Shows:

- Burst detection thresholds
- Currently blocked IPs
- Suspicious activity monitoring
- Request size limits

### Security Audit Log

```bash
python backend/conductor_main.py shield-audit
```

Displays:

- Last 50 security events
- Blocked requests
- Validation failures
- Suspicious activities

---

## Configuration

Security settings are stored in `backend/security_config.json`:

```json
{
  "cors": {
    "enabled": true,
    "allowed_origins": ["http://localhost:5173", "http://localhost:3000"],
    "allowed_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    "allow_credentials": true
  },
  "rate_limiting": {
    "enabled": true,
    "global_limit": 1000,
    "global_window": 3600,
    "per_ip_limit": 100,
    "per_ip_window": 60,
    "per_endpoint_limit": 50,
    "per_endpoint_window": 60
  },
  "ddos_protection": {
    "enabled": true,
    "burst_threshold": 50,
    "burst_window": 10,
    "block_duration": 600,
    "max_request_size": 10485760
  },
  "input_validation": {
    "enabled": true,
    "block_sql_injection": true,
    "block_xss": true,
    "max_string_length": 10000,
    "max_array_length": 1000
  },
  "security_headers": {
    "enabled": true,
    "headers": {
      "X-Content-Type-Options": "nosniff",
      "X-Frame-Options": "DENY",
      "X-XSS-Protection": "1; mode=block",
      "Strict-Transport-Security": "max-age=31536000",
      "Content-Security-Policy": "default-src 'self'"
    }
  },
  "logging": {
    "enabled": true,
    "log_file": "backend/logs/security.log"
  }
}
```

---

## Security Features

### 1. CORS Management

Control cross-origin requests:

```python
from backend.security_shield import SecurityShield

shield = SecurityShield()

# Get CORS headers for an origin
cors_headers = shield.cors.get_cors_headers("https://example.com")

# Add/remove allowed origins
shield.cors.add_origin("https://production.example.com")
shield.cors.remove_origin("https://test.example.com")
```

### 2. Rate Limiting

Prevent excessive requests:

- **Global Rate Limit**: 1000 requests/hour (all IPs combined)
- **Per-IP Limit**: 100 requests/minute per IP
- **Per-Endpoint Limit**: 50 requests/minute per endpoint per IP

```python
# Check if request is allowed
allowed, message = shield.rate_limiter.is_allowed(
    client_ip="192.168.1.1",
    endpoint="/api/products"
)

if not allowed:
    print(f"Rate limit exceeded: {message}")
```

### 3. DDoS Protection

Detect and block DDoS attacks:

- **Burst Threshold**: 50 requests per 10 seconds = temporary block
- **Block Duration**: 600 seconds (10 minutes)
- **Request Size Limit**: 10 MB max

```python
# Check for DDoS patterns
allowed, message = shield.ddos_protection.check_request("192.168.1.1")

# Get status
status = shield.ddos_protection.get_status()
# {
#   "currently_blocked": 0,
#   "suspicious_ips": 0,
#   "active_tracking": 0
# }
```

### 4. Input Validation

Protect against injection attacks:

- **SQL Injection Detection**: Multiple pattern matching
- **XSS Detection**: Script tags and event handlers
- **Size Validation**: Max 10,000 char strings, 1,000 item arrays

```python
# Validate input
valid, message = shield.input_validator.validate(
    data=request.json,
    field_name="product_data"
)

# Sanitize strings
clean_data = shield.input_validator.sanitize(user_input)
```

### 5. Security Headers

Standard security headers automatically included:

```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000
Content-Security-Policy: default-src 'self'
Referrer-Policy: strict-origin-when-cross-origin
```

### 6. Audit Logging

All security events are logged:

```
2026-02-06 10:30:45 - security_shield - WARNING - Rate limiting blocked request from 192.168.1.1: Per-IP rate limit exceeded
2026-02-06 10:30:46 - security_shield - WARNING - Input validation failed from 192.168.1.2: Potential SQL injection detected
2026-02-06 10:30:47 - security_shield - INFO - Request allowed from 192.168.1.3 to /api/products
```

---

## FastAPI Integration

To integrate the Security Shield into your FastAPI application:

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from backend.security_shield import SecurityShield

app = FastAPI()
shield = SecurityShield()

@app.middleware("http")
async def security_middleware(request: Request, call_next):
    # Get client IP
    client_ip = request.client.host

    # Get request body for validation
    body = None
    if request.method in ["POST", "PUT", "PATCH"]:
        try:
            body = await request.json()
        except:
            pass

    # Check all security gates
    allowed, message = shield.check_request(
        client_ip=client_ip,
        endpoint=request.url.path,
        data=body
    )

    if not allowed:
        return JSONResponse(
            status_code=403,
            content={"error": message}
        )

    # Add security headers
    response = await call_next(request)

    cors_headers = shield.cors.get_cors_headers(
        request.headers.get("origin")
    )
    for header, value in cors_headers.items():
        response.headers[header] = value

    # Add security headers
    security_headers = shield.config.get("security_headers.headers", {})
    for header, value in security_headers.items():
        response.headers[header] = value

    return response
```

---

## Monitoring & Alerts

Check security status in your monitoring system:

```python
status = shield.get_security_status()

# Example output:
# {
#   "cors": {
#     "enabled": true,
#     "allowed_origins": ["http://localhost:5173"]
#   },
#   "rate_limiting": {
#     "enabled": true,
#     "stats": {
#       "tracked_ips": 0,
#       "global_requests": 0,
#       "ip_requests": 0
#     }
#   },
#   "ddos_protection": {
#     "enabled": true,
#     "status": {
#       "currently_blocked": 0,
#       "suspicious_ips": 0,
#       "active_tracking": 0
#     }
#   },
#   "input_validation": {"enabled": true},
#   "logging": {"enabled": true},
#   "timestamp": "2026-02-06T10:30:45.123456"
# }
```

---

## Production Deployment Checklist

Before deploying to production:

- [ ] Update `security_config.json` with production URLs
- [ ] Set proper rate limits based on expected traffic
- [ ] Enable all security features
- [ ] Configure security logging to persistent storage
- [ ] Set up log rotation and archival
- [ ] Test CORS with production domains
- [ ] Verify input validation rules match API schema
- [ ] Monitor security logs for false positives
- [ ] Set up alerting for DDoS patterns
- [ ] Document security incident response procedures

---

## Conductor Integration

The Security Shield is now managed through the Conductor CLI:

```bash
# Show full status
python backend/conductor_main.py shield

# Manage CORS
python backend/conductor_main.py shield-cors [list|add|remove] [origin]

# Show rate limiting config
python backend/conductor_main.py shield-limits

# Show DDoS protection
python backend/conductor_main.py shield-ddos

# Review security audit log
python backend/conductor_main.py shield-audit
```

All security management is centralized in the Conductor, ensuring consistent application of defensive policies across your entire infrastructure.

---

## Performance Impact

The Security Shield is designed for minimal overhead:

- **CORS Headers**: < 0.1ms per request
- **Rate Limiting**: Lightweight in-memory tracking
- **DDoS Detection**: O(1) lookup for IP blocking
- **Input Validation**: Regex-based, impact depends on payload size
- **Logging**: Async to avoid blocking requests

---

## Support & Documentation

For more information:

- See `backend/security_shield.py` for implementation details
- Review `backend/security_config.json` for all configuration options
- Check `backend/logs/security.log` for security events
