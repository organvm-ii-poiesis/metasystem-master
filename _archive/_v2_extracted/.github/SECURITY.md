# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.x.x   | :white_check_mark: |

## Reporting a Vulnerability

**Do not open public issues for security vulnerabilities.**

Email security concerns to the project maintainers directly.

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

We will acknowledge receipt within 48 hours and provide a detailed response within 7 days.

## Security Considerations

The Omni-Dromenon Engine handles real-time audience connections. Key security areas:

### 1. WebSocket Connections
- Rate limiting on connection attempts
- Origin validation for cross-origin requests
- Connection timeout enforcement

### 2. Input Sanitization
- All audience inputs validated server-side
- Parameter bounds checking (0.0 - 1.0 ranges enforced)
- Input type validation before consensus processing

### 3. Performer Authentication
- Override controls require authentication
- Session-based access for performer dashboard
- Configurable authentication providers

### 4. Data Privacy
- No persistent storage of audience data by default
- Session data cleared on performance end
- No personal identifiers required for audience participation
- GDPR-compliant data handling patterns

### 5. Network Security
- TLS encryption for all WebSocket connections in production
- Secure cookie handling for session management
- CORS configuration for API endpoints

## Security Best Practices for Deployment

```bash
# Production environment variables
NODE_ENV=production
SECURE_COOKIES=true
CORS_ORIGIN=https://your-domain.com
RATE_LIMIT_WINDOW_MS=60000
RATE_LIMIT_MAX_REQUESTS=100
```

## Dependency Security

We use automated security scanning via:
- GitHub Dependabot for dependency updates
- `npm audit` in CI pipelines
- Regular manual review of security advisories
