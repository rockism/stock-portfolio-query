---
name: portfolio-value-query
description: Estimate Taiwan and US stock portfolio value from a user-provided private JSON file.
---

# Portfolio value query

Ask the user for the path to their private portfolio JSON file. Read README.md for the schema and limitations. Run `python3 portfolio_value.py --portfolio PATH --json`. Report quote source and timestamps, missing quotes, cash, loan, total assets, and net assets. If `valuation_complete` is false, do not present aggregate values as complete. Do not store holdings or prices in agent memory, publish the private input, or place trades.

## Updating from broker screenshots

When the user provides broker app screenshots, transcribe each visible holding's symbol, market, shares, and pledged status. Treat ordinary and pledged shares of the same symbol as separate rows. Read any loan balance from a clearly identified loan page; never infer it from buying power or collateral value. Compare visible rows with the existing private JSON. For unambiguous rows in a clearly identified account, back up the private JSON, update it, validate with `load_portfolio`, run the valuation, and report the changes. The screenshot request itself authorizes this reversible local update. A screenshot may show only one account or part of a list: keep unseen existing rows. Mark cropped, ambiguous, or unreadable fields as needing confirmation. Ask before resolving conflicting figures, uncertain account scope, or ordinary-versus-pledged classification. Keep screenshots and account identifiers out of the public repository.

Report `pledge_coverage_percent` as an estimate: pledged Taiwan stock market value / current loan balance × 100. If loan balance is unknown, zero, or a pledged quote is missing, report that the ratio cannot be calculated. Distinguish this estimate from the broker's official maintenance ratio, which may use different collateral and loan rules.
