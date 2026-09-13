# Security Policy

## Supported Versions

| Version | Supported |
| ------- | --------- |
| 0.1.x   | Yes       |

## Reporting a Vulnerability

If you discover a security vulnerability in AutoSub-AI, please report it responsibly:

1. **Do not** create a public issue for security vulnerabilities
2. Email: rosan-f@users.noreply.github.com
3. Include:
   - Description of the vulnerability
   - Reproduction steps
   - Potential impact
   - Suggested fix (if applicable)

## Response Timeline

- **24 hours**: Acknowledgment of report
- **72 hours**: Initial assessment and remediation plan
- **7 days**: Security patch release

## Security Measures

AutoSub-AI implements the following security practices:

- Input validation with URL domain whitelist and path traversal guard
- Output filename sanitization against injection attacks
- No shell injection — all subprocess calls use list arguments
- Environment variables for sensitive configuration
- Dependency audit via `pip-audit` and `bandit`
- Custom exception hierarchy that does not expose stack traces
