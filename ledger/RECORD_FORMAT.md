# Ledger record format

Each file under `records/` holds `records:` — a list of entries of exactly this shape (see `schema/record.schema.json`):

```yaml
- id: ab.tier.floor                 # required, from the task list
  jurisdiction: AB                  # required: FED|AB|"ON"|BC|QC  (always quote "ON")
  instrument: tier                  # required, short slug
  parameter: minimum_transfer_price # required, short slug
  value: {2030: 60, 2031: 63}       # required: number | {year: number} series | {key: number|string} table
  unit: CAD/t                       # required, one of: CAD/t, CAD/GJ, CAD/MWh, cents/kWh, fraction, g/kWh, t/GJ, kt, CAD, text
  currency_basis: nominal           # nominal | real-2026 | n/a
  effective_from: 2030-01-01        # required ISO date (valid-time start)
  effective_to: null                # ISO date or null
  legal_status: announced           # announced|proposed|enacted|in_force|superseded|repealed|observation
  confidence: high                  # high|medium|low
  freshness: statute                # statute|guidance|announcement|market_observation|statistic
  sources:                          # >=1; enacted/in_force need >=1 primary_legal or primary_gov
    - url: https://...
      title: "..."
      publisher: "..."
      published: 2026-06-03         # ISO date, or null if the page shows none
      retrieved: 2026-09-29         # the date you fetched it
      locator: "section / table / paragraph"
      excerpt: "verbatim, <= 25 words, supports the value"
      source_type: primary_legal    # primary_legal | primary_gov | secondary
  notes: "one or two sentences: caveats, how value was read"
```

Rules
- Every number must be read from a page you fetched in this task. Never from memory.
- If a record cannot be verified within 2 fetches, return `UNVERIFIED: <id>: <reason>` instead of YAML.
- Excerpts verbatim and <= 25 words. No other prose in the answer.
