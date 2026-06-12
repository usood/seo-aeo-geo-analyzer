# Changelog

All notable project changes are documented here.

## Unreleased

- No unreleased changes.

## 2026-06-12

### Added

- Added run history summaries, run-to-run comparison CLI, keyword rank snapshots, and a static dashboard generator (#14).
- Added scheduled analysis support for cron/CI runs, including a manual GitHub Actions workflow and artifact upload path (#13).
- Added deterministic report UI localization with English and Spanish locale catalogs (#12).
- Added site-branding auto-detection for report headers, including detected logo/color metadata from collected site data (#11).
- Added Lighthouse agentic-browsing readiness checks with graceful fallback when the local Lighthouse runtime lacks the experimental category (#10).
- Added WebMCP opportunity analysis for action-oriented flows such as checkout, signup, booking, forms, support, account, and search experiences (#9).
- Added a recommended `llms.txt` generator for analyzed websites (#7).
- Added open-source issue templates, pull request template, and Release Drafter workflow (#6).
- Added lightweight CI for Markdown/link validation and security hygiene checks (#5).
- Added maintenance, security, and AI readiness documentation, including a root `llms.txt` for project orientation (#4).

### Changed

- Replaced brand-specific examples with public DTC, SaaS, and consumer app examples (#12).
- Expanded README positioning for agencies, growth teams, DTC brands, SaaS companies, consumer apps, technical marketers, and Snezzi done-for-you implementation (#12).
- Documented Google AI search guidance, WebMCP, Lighthouse agentic browsing, and `llms.txt` caveats with source links (#4, #9, #10).
- Updated example configs and `config.example.yaml` for report language, scheduled runs, AI-readiness steps, and tracking settings (#12, #13, #14).

### Security

- Hardened generated report HTML rendering and report path handling with regression tests (#3).
- Hardened site `llms.txt` generation against untrusted input (#8).
- Added CI security hygiene scans using `pip-audit` and Bandit (#5).

## 2026-06-11

- Hardened generated report HTML handling and `.latest_project` path resolution.
- Fixed CLI export/menu dispatch issues.
- Improved test suite reliability.
- Replaced brand-specific examples with public DTC, SaaS, and consumer app examples.
