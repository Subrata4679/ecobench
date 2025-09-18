# Security Policy

## Supported Versions

We actively support the following versions of EcoBench with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of EcoBench seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### How to Report

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to: security@ecobench.com

You should receive a response within 48 hours. If for some reason you do not, please follow up via email to ensure we received your original message.

### What to Include

Please include the requested information listed below (as much as you can provide) to help us better understand the nature and scope of the possible issue:

* Type of issue (e.g. buffer overflow, SQL injection, cross-site scripting, etc.)
* Full paths of source file(s) related to the manifestation of the issue
* The location of the affected source code (tag/branch/commit or direct URL)
* Any special configuration required to reproduce the issue
* Step-by-step instructions to reproduce the issue
* Proof-of-concept or exploit code (if possible)
* Impact of the issue, including how an attacker might exploit the issue

This information will help us triage your report more quickly.

### Preferred Languages

We prefer all communications to be in English.

## Security Update Process

When we receive a security bug report, we will:

1. Confirm the problem and determine the affected versions
2. Audit code to find any potential similar problems
3. Prepare fixes for all releases still under maintenance
4. Release new versions as soon as possible

## Security Best Practices

### For Users

* Always use the latest supported version
* Keep your dependencies up to date
* Use strong, unique passwords for all accounts
* Enable two-factor authentication where available
* Regularly review access logs and user permissions
* Follow the principle of least privilege
* Keep your deployment environment secure and updated

### For Developers

* Follow secure coding practices
* Validate all inputs
* Use parameterized queries to prevent SQL injection
* Implement proper authentication and authorization
* Use HTTPS for all communications
* Keep dependencies updated
* Regular security testing and code reviews
* Follow OWASP guidelines

## Known Security Considerations

### Data Protection

* All sensitive data is encrypted at rest and in transit
* API keys and secrets are stored securely using environment variables
* Database connections use SSL/TLS encryption
* User passwords are hashed using bcrypt

### Authentication & Authorization

* JWT tokens are used for API authentication
* Tokens have appropriate expiration times
* Role-based access control (RBAC) is implemented
* Session management follows security best practices

### Input Validation

* All user inputs are validated and sanitized
* File uploads are restricted by type and size
* SQL injection protection through parameterized queries
* XSS protection through proper output encoding

### Infrastructure Security

* Docker containers run with non-root users
* Network policies restrict unnecessary communication
* Regular security updates are applied
* Monitoring and logging are in place

## Compliance

EcoBench is designed to help organizations meet various compliance requirements:

* SOC 2 Type II controls
* ISO 27001 security standards
* GDPR data protection requirements
* Industry-specific ESG reporting standards

## Security Tools and Scanning

We use various automated tools to maintain security:

* **CodeQL** - Static analysis for code vulnerabilities
* **Dependabot** - Automated dependency updates
* **Trivy** - Container vulnerability scanning
* **Safety** - Python dependency vulnerability checking
* **npm audit** - Node.js dependency vulnerability checking
* **TruffleHog** - Secrets detection

## Contact

For any security-related questions or concerns, please contact:

* Security Team: security@ecobench.com
* General Support: support@ecobench.com

## Acknowledgments

We would like to thank the security researchers and community members who help keep EcoBench secure by responsibly disclosing vulnerabilities.

---

This security policy is effective as of the date of the latest commit to this file and will be updated as needed.
