# AI And Agentic Search Readiness

This project tracks AI search and agentic browsing as practical audit areas, while keeping Google Search claims grounded in official guidance.

## Google Generative AI Search

Google's current guidance for AI Overviews and AI Mode is that core SEO remains the foundation. Pages still need to be crawlable, indexable, eligible for snippets, technically clear, and useful to people.

Recommended checks for this analyzer:

- Confirm important pages are crawlable and indexable.
- Verify pages can be shown with snippets when snippet visibility matters.
- Review JavaScript-rendered content using normal JavaScript SEO checks.
- Keep structured data valid where it supports rich result eligibility.
- Prioritize helpful, expert-led, non-commodity content over AI-only rewrites.
- For ecommerce and local businesses, check Merchant Center, product feeds, product structured data, and Google Business Profile completeness where relevant.

Google also explicitly calls out tactics that are not required for Google generative AI search:

- `llms.txt` and other special AI text files are not required for Google Search AI features.
- There is no requirement to split pages into small "AI chunks".
- There is no special schema.org markup required for generative AI search.
- Rewriting content only for AI systems is not necessary.

Sources:

- [Google Search Central: Optimizing your website for generative AI features on Google Search](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide)
- [Google Search Central: Creating helpful, reliable, people-first content](https://developers.google.com/search/docs/fundamentals/creating-helpful-content)
- [Google Search Central: Structured data introduction](https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data)

## llms.txt

This repository includes a root [llms.txt](../llms.txt) as an optional machine-readable project summary. It helps agents and coding assistants quickly identify the purpose, entry points, test command, and docs for this open-source project.

Use `llms.txt` carefully:

- Treat it as optional documentation, not a Google Search ranking or AI visibility requirement.
- Keep it short and source-of-truth oriented.
- Link to canonical docs instead of duplicating long documentation.
- Update it when entry points, tests, or maintenance policies change.

### Generating an llms.txt for an analyzed site

The analyzer can also generate a recommended `llms.txt` **for the site being audited** (not for this repository). Run step 9 in `run_analysis.py`, or:

```bash
python generate_site_llms.py
```

This reads the latest sitemap analysis (`analysis_data_*.json`) and writes `reports/<project>/<domain>-llms.txt`, a short curated index of the site's canonical entry points grouped by type (key pages, products/services, categories, content). To use it, host the file at `/<domain>/llms.txt` on the audited site, typically as `/llms.txt`.

The same caveats apply: it is optional, is **not** a Google Search requirement, and does not affect ranking. It exists to help AI agents and LLM tools discover a site's most important pages.

Source:

- [llms.txt proposal](https://llmstxt.org/)

## WebMCP

WebMCP is a proposed Chrome web standard for exposing structured browser tools to AI agents. It can be useful when a website has tasks that require reliable action in the browser, such as checkout, booking, form submission, support routing, diagnostics, or dashboard workflows.

For analyzer roadmap purposes, WebMCP checks should focus on whether an analyzed website has action-oriented flows where explicit tools could improve agent reliability:

- Search or filtering tools.
- Quote, signup, booking, demo request, or checkout forms.
- Account, support, or diagnostics workflows.
- Any sensitive action that should require visible user confirmation.

Implementation caveats:

- WebMCP is experimental and based on proposed standards.
- Chrome currently documents origin isolation and Permissions Policy requirements for WebMCP APIs.
- WebMCP is a progressive enhancement; the human-facing UI still needs to work normally.

### WebMCP opportunity analyzer

`webmcp_analyzer.py` (step 10) implements a first-pass opportunity detector. It is heuristic and offline (no API cost): it scans the collected sitemap sample for action-oriented URL patterns (checkout/cart, signup, booking, lead/enquiry forms, account/dashboard, search, support) and infers commerce flows from detected technology (e.g. Shopify implies checkout/cart even when those pages are absent from the sitemap). It writes `webmcp_analysis.json` and surfaces a score, level, and flagged pages in the HTML report.

Because action pages such as checkout and login are frequently excluded from sitemaps, treat the score as a floor on real opportunity, not a ceiling.

Sources:

- [Chrome for Developers: WebMCP](https://developer.chrome.com/docs/ai/webmcp)
- [GoogleChromeLabs/webmcp-tools](https://github.com/GoogleChromeLabs/webmcp-tools)

## Lighthouse Agentic Browsing

Chrome documents an experimental Lighthouse Agentic Browsing category. It does not provide a traditional weighted 0-100 score. Instead, it reports readiness signals such as fractional pass ratios, pass/fail audit status, and informational counts.

Useful signals to track:

- WebMCP tool registration and schema validity.
- Agent-centric accessibility: names, labels, roles, tree integrity, and visibility.
- Layout stability, especially Cumulative Layout Shift.
- Presence of a root `llms.txt` file.

Use these signals as engineering feedback, not as a confirmed search ranking factor.

### Agentic-browsing checker

`agentic_browsing_check.py` (step 11) runs the **local** Lighthouse CLI for the `agentic-browsing` category against the site's homepage and writes `agentic_browsing.json`. It is designed to degrade gracefully:

- If Lighthouse is not installed, Chrome cannot launch, the run times out, or the installed Lighthouse version does not expose the category, it records `available: false` with a clear reason instead of failing.
- When the category is available, it captures the category score (often pass/fail rather than 0-100) and per-audit readiness signals.

Results are surfaced in the HTML report as an "Agentic Browsing" section (with the graceful "not available" state shown when the runtime lacks the category).

Source:

- [Chrome for Developers: Lighthouse agentic browsing scoring](https://developer.chrome.com/docs/lighthouse/agentic-browsing/scoring)

## Future Analyzer Enhancements

- Add a crawler check for root `llms.txt` presence and freshness.
- ~~Add a WebMCP opportunity detector for action-oriented site flows.~~ Done (`webmcp_analyzer.py`).
- ~~Add Lighthouse agentic browsing results to performance reports when the category is available in the local Lighthouse runtime.~~ Done (`agentic_browsing_check.py`).
- Add accessibility-tree checks that matter for both humans and agents.
- Add ecommerce and local business checks for Merchant Center, product feeds, Product schema, Organization schema, and Google Business Profile readiness.
