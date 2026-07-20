# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | ✅ |

## What counts as a vulnerability

Please report:

- Path traversal when reading/writing under a project root
- Skill/install scripts writing outside expected config dirs without consent
- XSS in generated `story.html` from untrusted labels/paths
- Secret leakage if detect/extract ever reads `.env` / credential files into outputs

OKAD is a local developer tool. It should never phone home and never require an API key.

## How to report

**Do not open a public GitHub issue for security bugs.**

Email: `21007@esp.mr`  
Or open a [private security advisory](https://github.com/Abmstpha/OKAD/security/advisories/new) on GitHub.

Include:

- OKAD version (`okad version`)
- Steps to reproduce
- Impact (what an attacker could do)

You should hear back within 7 days.

## Safe harbor

We will not pursue legal action against good-faith research that:

- stays within your own machines / repos you own,
- avoids destructive testing on third-party systems,
- reports findings privately first.
