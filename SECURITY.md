# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in any of the plugins, please report it by:

1. **Do not** open a public issue
2. Send an email to **shaggybackend@gmail.com** with:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

## Security Considerations for Plugins

### Command Execution

- Plugins may execute shell commands via `allowed_tools: [Bash]`
- Review commands before running in production environments
- Be cautious with plugins that modify files or execute arbitrary code

### Sensitive Data

- Never commit secrets, API keys, or credentials
- Use environment variables for sensitive configuration
- Review generated code for hardcoded values

### Best Practices

1. Review plugin source code before installation
2. Keep plugins updated to the latest versions
3. Use plugins from trusted sources only
4. Report any suspicious behavior

## Plugin Security Guidelines

Plugin authors should:

1. Minimize use of shell commands
2. Validate all user inputs
3. Avoid storing sensitive data
4. Document any security considerations
5. Keep dependencies minimal and updated
