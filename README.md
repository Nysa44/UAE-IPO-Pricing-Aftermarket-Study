# UAE IPO Pricing & Aftermarket Study

An educational equity capital markets (ECM) research project examining IPO offer pricing, subscription demand and post-listing trading performance across UAE listings.

> **Data integrity:** The included demo dataset is synthetic and is labelled `ILLUSTRATIVE` throughout. It is only for demonstrating the workflow and testing the calculations. Replace it with verified prospectus, exchange and licensed/public market data before making factual claims or publishing results.

## What this project does

- Calculates first-day, 1-week, 1-month and 3-month IPO returns from offer price.
- Calculates matched market-index returns and market-adjusted (excess) returns.
- Measures post-listing annualised volatility and average daily traded value.
- Compares offer valuation multiples with peer valuation multiples.
- Examines the relationship between oversubscription and first-day returns.
- Produces an Excel workbook, CSV summary tables, charts and a three-slide PowerPoint deck.
- Validates the calculation functions with pytest.

## Quick start

Python 3.10+ is recommended.

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
python run_analysis.py --demo
pytest -q
```

Outputs are written to `outputs/`:
- `UAE_IPO_Analysis.xlsx`
- `ipo_summary.csv`
- `peer_valuation_comparison.csv`
- `charts/*.png`
- `UAE_ECM_Market_Review.pptx`

## Replace demo data with verified data

1. Populate `data/raw/ipo_master.csv` with one row per IPO.
2. Add daily price and volume observations to `data/raw/ipo_prices.csv`.
3. Add matched index closes to `data/raw/market_index.csv`.
4. Populate `data/raw/peer_valuations.csv` with peer multiples observed around the IPO pricing date.
5. Change `data_mode` to `RESEARCH` in `config.json`.
6. Run `python run_analysis.py`.

The CSV templates contain field descriptions and example rows. Remove all rows marked `ILLUSTRATIVE` before research use.

## Data fields and definitions

- `offer_price`: IPO offer price per share in the listing currency.
- `shares_offered`: shares sold in the offering.
- `gross_proceeds`: gross proceeds in local currency. Use the prospectus figure and record whether it includes any secondary sale.
- `subscription_multiple`: reported subscription coverage, e.g. 18.4 means 18.4x.
- `offer_pe`: offer price-to-earnings multiple, if disclosed/calculable on a consistent basis.
- `peer_pe`: peer P/E observed near the offer date; peer methodology and date should be documented.
- `date`: trading date, ISO format `YYYY-MM-DD`.
- `close`: daily closing price.
- `volume`: shares traded.
- `index_close`: relevant broad-market index close on the same date.

Return windows use the first available trading close on or after the target calendar date (7, 30 or 90 calendar days after listing). This is a transparent approximation of 1-week, 1-month and 3-month horizons; explain this convention in any write-up. IPO first-day return is `(first trading-day close / offer price) - 1`.

Market-adjusted return is IPO holding-period return minus the matched index holding-period return over the same dates. This is a simple excess-return measure, not a factor model.

Annualised volatility is the standard deviation of daily simple returns multiplied by `sqrt(252)`. Average daily traded value is the mean of `close * volume`. The measure is not free-float turnover and should not be described as such.

## Source and verification protocol

Use official exchange listing notices and issuer prospectuses for offer price, offer size, shares offered, market capitalisation and published subscription data. Record the exact document title, URL, access date and page/section in `ipo_master.csv`.

Use market-data sources whose terms permit your intended use. Record provider, download date, currency, adjustment basis and any limitations. Do not scrape or redistribute data contrary to provider terms.

For each IPO, verify at least:
- Offer price against the prospectus or official listing notice.
- First trading date and first-day close against the exchange record.
- Share volume and index observations against the selected market-data source.

## Important limitations

- Small sample sizes (8–12 IPOs) limit statistical inference.
- IPO selection and availability of historical data can create survivorship and selection bias.
- Market regimes, sector mix, free float, lock-ups, allocation rules and deal structure differ.
- Subscription multiples are not always directly comparable across retail and institutional tranches or across exchanges.
- Peer multiples depend on accounting periods, capital structures and peer selection.
- Calendar-day return horizons may land on non-trading days; the script uses the next available trading observation.
- Results are descriptive and do not establish causation.

## Suggested research selection rule

Select all UAE IPOs listed on ADX or DFM within a clearly specified 24–36 month window for which the required offer and post-listing data can be verified. Publish the inclusion/exclusion log and do not select deals based on performance.

## Project structure

```text
UAE_IPO_Pricing_Aftermarket_Study/
├── config.json
├── run_analysis.py
├── requirements.txt
├── data/
│   ├── raw/                 # source-ready CSVs (demo rows are synthetic)
│   └── processed/
├── src/
│   ├── analysis.py
│   ├── workbook.py
│   └── presentation.py
├── tests/
└── outputs/
```

## Disclaimer

This project is for educational and portfolio demonstration purposes only. It is not investment research, an offer, a solicitation or investment advice. Confirm all figures against original sources before relying on them.
