# Add CSP middleware for Gemini compatibility
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

class CSPMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add Content Security Policy header for Gemini AI
        csp_policy = (
            "default-src 'self'; "
            "connect-src 'self' https://*.google.com https://*.googleapis.com https://*.gstatic.com https://*.googleusercontent.com; "
            "img-src 'self' https://*.google.com https://*.gstatic.com https://*.googleusercontent.com https://*.ggpht.com data: blob:; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://*.google.com https://*.gstatic.com; "
            "style-src 'self' 'unsafe-inline' https://*.google.com https://*.gstatic.com; "
            "font-src 'self' https://*.gstatic.com data:; "
            "frame-src 'self' https://*.google.com; "
            "media-src 'self' https://*.google.com https://*.googleapis.com https://*.gstatic.com https://*.googleusercontent.com blob:; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "form-action 'self';"
        )
        
        response.headers['Content-Security-Policy'] = csp_policy
        return response

app.add_middleware(CSPMiddleware)