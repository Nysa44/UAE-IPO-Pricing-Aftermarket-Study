# Data dictionary and collection guide

All files in `data/raw/` are CSV inputs. The included rows are synthetic examples to make the pipeline runnable. They are not actual UAE IPOs or market observations.

## ipo_master.csv
One row per IPO. Keep the official prospectus/listing announcement URL and page reference in the source columns. Do not estimate unpublished subscription figures; leave them blank.

## ipo_prices.csv
One row per IPO per trading day. Use unadjusted or consistently adjusted closing prices, clearly document which, and include traded share volume. Ensure dates are exchange trading dates.

## market_index.csv
One row per date for the benchmark index selected for the IPO/exchange. For a mixed ADX/DFM sample, consider exchange-specific indices and add an `index_id` field if needed; this starter project uses one shared illustrative index for simplicity.

## peer_valuations.csv
One row per peer company. Use peers selected on business model and geography, and record the valuation observation date and source. Avoid mixing LTM and forward multiples without disclosure.

## Data hygiene
- Dates must be ISO `YYYY-MM-DD`.
- Numeric fields must be numeric; blanks are allowed where a metric is unavailable.
- `ipo_id` must match across files.
- Do not overwrite source files; retain downloaded originals separately and document transformations.
