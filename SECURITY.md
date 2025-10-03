# Security Policy

## Supported Versions

We release security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

If you discover a security vulnerability in this project, please report it privately to help us address it before public disclosure.

### How to Report

1. **Email:** Send details to [matthew.truscott@turintech.ai]
2. **Include:**
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Any suggested fixes (optional)

### Response Timeline

- **Initial Response:** Within 48 hours
- **Status Update:** Within 7 days
- **Fix Timeline:** Depends on severity
  - Critical: 1-3 days
  - High: 1-2 weeks
  - Medium: 2-4 weeks
  - Low: Next scheduled release

## Security Best Practices

### For Users

#### API Key Management

1. **Never commit API keys** to version control
2. **Use environment variables** or `.env` files (ensure `.env` is in `.gitignore`)
3. **Rotate keys regularly** - at least every 90 days
4. **Use separate keys** for development and production
5. **Set spending limits** in your OpenAI dashboard
6. **Monitor usage** regularly for unexpected activity

#### Safe Configuration

```bash
# Create .env from template
cp .env.example .env

# Edit .env with your actual credentials
nano .env

# Verify .env is not tracked by git
git status  # Should not show .env
```

#### Running Securely

```bash
# Development mode (local only)
export DEBUG=true
python file-v1-main.py

# Production mode (recommended)
export DEBUG=false
export USE_RELOADER=false
python file-v1-main.py
```

### For Contributors

#### Before Committing Code

1. **Never commit secrets**
   ```bash
   # Check for potential secrets
   git diff | grep -i "api_key\|password\|secret\|token"
   ```

2. **Validate user input**
   - Always validate URLs, file paths, and user-provided data
   - Use allowlists for known-good values when possible
   - Implement input length limits

3. **Safe subprocess usage**
   ```python
   # ✅ GOOD: Use list of arguments, no shell=True
   subprocess.run(["yt-dlp", "--version"])
   
   # ❌ BAD: shell=True with user input
   subprocess.run(f"yt-dlp {user_url}", shell=True)
   ```

4. **Run security checks**
   ```bash
   # Install security tools
   poetry add --group dev safety bandit
   
   # Run checks before committing
   poetry run safety check
   poetry run bandit -r . -ll
   ```

#### Security Review Checklist

Before submitting a pull request:

- [ ] No hardcoded secrets, API keys, or passwords
- [ ] All user input is validated and sanitized
- [ ] Subprocess calls use argument lists (not shell=True)
- [ ] Error messages don't leak sensitive information
- [ ] Dependencies are up to date (`poetry update`)
- [ ] Security checks pass (`safety check` and `bandit`)
- [ ] New code includes appropriate input validation
- [ ] Authentication/authorization is properly implemented
- [ ] Sensitive data is encrypted at rest and in transit

## Known Security Considerations

### 1. Subprocess Usage

The YouTube downloader utilities use `subprocess` to call `yt-dlp`. While we don't use `shell=True`, users should:
- Only download from trusted sources
- Validate URLs before processing
- Keep `yt-dlp` updated

### 2. API Keys

The Taipy chat demo requires an OpenAI API key. Users should:
- Store keys in environment variables or `.env` files
- Never commit keys to version control
- Set spending limits in OpenAI dashboard
- Monitor API usage regularly

### 3. Debug Mode

The `file-v1-main.py` application can run in debug mode. Users should:
- **Never** enable debug mode in production
- Use `DEBUG=false` in production environments
- Be aware that debug mode may expose sensitive information

### 4. Dependencies

This project relies on external dependencies that may have vulnerabilities:
- Run `poetry update` regularly
- Monitor security advisories
- Use `safety check` to scan for known vulnerabilities

## Security Updates

We take security seriously and will:

1. **Promptly address** reported vulnerabilities
2. **Release security patches** as soon as possible
3. **Notify users** of critical security updates
4. **Credit reporters** (if desired) in security advisories

### Staying Informed

- Watch this repository for security announcements
- Check the [SECURITY_RECOMMENDATIONS.md](SECURITY_RECOMMENDATIONS.md) for detailed security guidance
- Subscribe to dependency security alerts (Dependabot)

## Scope

### In Scope

- Command injection vulnerabilities
- Secrets/credential exposure
- Authentication/authorization issues
- Cross-site scripting (XSS) in web interfaces
- SQL injection (if applicable)
- Dependency vulnerabilities
- Information disclosure

### Out of Scope

- Social engineering attacks
- Physical security
- Issues in third-party services (OpenAI, YouTube, etc.)
- Denial of service requiring significant resources
- Issues requiring physical access to the host system

## Security Tools

We recommend using these tools to maintain security:

```bash
# Add to dev dependencies
poetry add --group dev safety bandit

# Run security checks
poetry run safety check          # Check for vulnerable dependencies
poetry run bandit -r . -ll       # Security linting for Python code

# Keep dependencies updated
poetry update
```

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)
- [OpenAI Security Best Practices](https://platform.openai.com/docs/guides/safety-best-practices)
- [CWE Top 25 Most Dangerous Software Weaknesses](https://cwe.mitre.org/top25/)

## License

This security policy is licensed under the same terms as the project (MIT License).

---

**Last Updated:** 2025  
**Policy Version:** 1.0
