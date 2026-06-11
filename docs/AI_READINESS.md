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

Source:

- [Chrome for Developers: Lighthouse agentic browsing scoring](https://developer.chrome.com/docs/lighthouse/agentic-browsing/scoring)

## Future Analyzer Enhancements

- Add a crawler check for root `llms.txt` presence and freshness.
- Add a WebMCP opportunity detector for action-oriented site flows.
- Add Lighthouse agentic browsing results to performance reports when the category is available in the local Lighthouse runtime.
- Add accessibility-tree checks that matter for both humans and agents.
- Add ecommerce and local business checks for Merchant Center, product feeds, Product schema, Organization schema, and Google Business Profile readiness.
