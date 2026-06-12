# Security Policy

## Supported Versions

Security fixes are applied to the `main` branch. This project does not currently maintain separate release branches.

## Reporting A Vulnerability

Please report suspected vulnerabilities privately by opening a GitHub security advisory when available, or by contacting the repository maintainer through the GitHub profile linked from the repository.

Do not include API keys, private customer data, generated reports, or exploit details in public issues.

Helpful details for a security report:

- Affected file, command, or workflow.
- Steps to reproduce with sanitized inputs.
- Expected and actual behavior.
- Impact and any known workaround.

## Security Expectations

- Never commit `.env`, API keys, OAuth tokens, generated reports, or customer-specific data.
- Sanitize example configurations and docs.
- Escape untrusted data before rendering generated HTML reports or static dashboards.
- Keep `.latest_project` and report file access scoped to local report directories.
- Treat `reports/<domain>/<run_id>/` artifacts as generated output; store them as CI artifacts or external files, not source-controlled project data.
- Add regression tests for security-sensitive behavior when practical.
