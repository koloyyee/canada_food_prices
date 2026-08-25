# Canadian Farm-to-Retail Food Price Trends

## Project overview

Food prices affect both household budgets and the people who buy ingredients professionally. After more than 15 years working as a chef—and tracking ingredient costs since becoming responsible for purchasing as a junior sous chef—I wanted to understand how price changes at the farm or producer level compare with the prices consumers see at retail.

This project combines Canadian food-price datasets to investigate how prices change across products, supply-chain stages, provinces, and years. Python and SQL provide a reusable data preparation workflow, while SQLite and Tableau support analysis and visualization.

The first case study examines **Ontario protein prices from 2019 through the latest available 2026 observations**. It establishes a starting framework that can later be extended to:

- Other provinces and territories
- National and interprovincial comparisons
- Other foods and agricultural commodities, such as fish and seafood, wheat and grains, fruit, and vegetables
- Additional producer, wholesale, and retail datasets
- New questions about inflation, volatility, regional differences, and price transmission

## Current case study: Ontario proteins

The current analysis compares farm-gate and retail price trends for five protein categories:

| Category | Farm-level proxy | Retail examples |
|---|---|---|
| Beef | Steers and heifers for slaughter | Ground beef, stewing beef, striploin, rib and sirloin cuts |
| Pork | Hogs | Pork loin, ribs, shoulder and bacon |
| Poultry | Chickens for meat | Whole chicken, breasts, thighs and drumsticks |
| Eggs | Eggs in shell | Retail eggs |
| Dairy | Unprocessed bovine milk | Retail milk in selected package sizes |

> The SQL dataset labels poultry as `chicken`, eggs as `egg`, and dairy as `milk`. “Dairy” in this project currently means milk only; it does not include cheese, butter, cream, or yogurt.

## Questions guiding the Ontario protein analysis

The project is intended to investigate the questions defined in [`ontario_proteins.md`](./ontario_proteins.md):

1. Which protein categories and stages—farm or retail—experienced the largest absolute and percentage price increases from 2022 to 2026?
2. How have the farm-to-retail price spread (`Retail - Farm`) and multiplier ratio (`Retail / Farm`) evolved over time?
3. Which category and stage exhibit the greatest month-to-month price volatility?
4. Is a widening farm-to-retail spread concentrated in particular supply chains, or does it occur across all five categories?
5. Following a farm-gate price shock, how many months does it take for a related change to appear in retail prices?

The current data pipeline prepares the information needed to explore these questions. The Tableau workbook includes price, spread, ratio, and change views. Formal volatility and pass-through lag models are areas for further analysis rather than completed findings.

## Data sources

Both datasets used by the current Ontario protein case study come from Statistics Canada:

1. [Farm product prices, crops and livestock (Table 32-10-0077-01)](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=3210007701)
2. [Monthly average retail prices for selected products (Table 18-10-0245-01)](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1810024501)

The current pipeline reads these local source files:

- `datasets/farm_prod_price.csv`
- `datasets/retail_price.csv`

The repository also contains source metadata and spreadsheet copies. The program does not download new data automatically, so the CSV files must be replaced manually when newer Statistics Canada releases are needed.

## Current analysis workflow

The repository currently implements the following workflow for the Ontario protein case study:

```text
Statistics Canada CSV files
          |
          v
Python / pandas cleaning
          |
          v
SQLite source tables
          |
          v
SQL filtering, category mapping, and unit normalization
          |
          v
Ontario protein SQL view
          |
          v
Analysis-ready CSV
          |
          v
Tableau dashboards
```

### How Python supports data cleaning

[`main.py`](./main.py) runs the pipeline, while [`db.py`](./db.py) contains the data preparation and database functions. Python and pandas are used to:

- Read the two raw Statistics Canada CSV files.
- Retain the fields required for analysis: month, geography, product, unit of measure, and price.
- Rename source-specific columns to a shared schema.
- Convert price values to numeric data; missing or flagged values become `NaN` in pandas and `NULL` in SQLite.
- Replace the `farm_prod_prices` and `retail_prices` tables in `food_prices.db`.
- Execute the SQL transformation script.
- Export the resulting SQL view to `export/ontario_protein_prices.csv`.

Python therefore acts mainly as the project's **extract, transform, and load (ETL) layer**. It turns two differently structured source files into consistent database tables and produces a reproducible export for visualization.

### How SQL supports data analysis

[`sql/01_ontario_protein_view.sql`](./sql/01_ontario_protein_view.sql) creates `view_ontario_protein_prices`. SQL is used to:

- Filter both datasets to Ontario and observations from January 2019 onward.
- Identify the relevant farm and retail products.
- Map individual products to beef, pork, chicken, egg, or milk categories.
- Label each observation as `farm` or `retail`.
- Combine farm and retail observations into one analysis-ready view.
- Normalize selected measurements for more meaningful comparison, including:
  - dollars per hundredweight to dollars per kilogram;
  - dollars per kilolitre to dollars per litre;
  - 500-gram bacon prices to prices per kilogram; and
  - two- and four-litre milk prices to prices per litre.

The resulting view contains both the original values and the normalized fields `normalised_price` and `normalised_uom`. This structure makes it easier to group results by month, stage, category, and product before calculating changes or building visual comparisons.

SQL currently prepares and standardizes the dataset. Measures such as endpoint percentage growth, volatility, and lagged farm-to-retail pass-through are not yet calculated in the SQL script.

### Visualization in Tableau

[`tableau/Canada_wholesale.twb`](./tableau/Canada_wholesale.twb) connects to the exported Ontario protein CSV. Its worksheets and dashboards support visual exploration of:

- Farm and retail prices over time
- Farm-to-retail price spreads
- Retail-to-farm price ratios
- Price changes and category comparisons

Because the workbook contains a local file connection, Tableau may ask you to repoint the data source to your cloned copy of `export/ontario_protein_prices.csv`.

## Project structure

```text
.
├── datasets/                         # Raw Statistics Canada data and metadata
├── export/
│   └── ontario_protein_prices.csv    # Reproducible analysis-ready export
├── sql/
│   └── 01_ontario_protein_view.sql   # Ontario filtering, mapping, and normalization
├── tableau/
│   └── Canada_wholesale.twb          # Tableau workbook
├── db.py                             # pandas and SQLite ETL functions
├── food_prices.db                    # Generated SQLite database
├── main.py                           # Pipeline entry point
├── ontario_proteins.md               # Research scope and questions
└── pyproject.toml                    # Python project configuration
```

## Running the pipeline

### Requirements

- Python 3.12 or later
- [`uv`](https://docs.astral.sh/uv/) for the recommended setup

From the repository root, install the dependencies and run the pipeline:

```bash
uv sync
uv run python main.py
```

The script uses paths relative to the repository root. It expects the `datasets/`, `sql/`, and `export/` directories to exist.

Running it will:

1. Read the farm and retail CSV source files.
2. Replace the source tables in `food_prices.db`.
3. Recreate `view_ontario_protein_prices`.
4. Replace `export/ontario_protein_prices.csv` with a fresh export.

To inspect the generated view directly with SQLite:

```bash
sqlite3 food_prices.db "SELECT * FROM view_ontario_protein_prices LIMIT 10;"
```

## Interpretation notes and limitations

- **The latest year is incomplete.** Farm observations currently extend through May 2026, while retail observations extend through June 2026. June 2026 cannot be used for a direct farm-versus-retail comparison, and 2026 should not be treated as a completed annual period.
- **Spread is not the same as retailer profit or margin.** The difference between a farm price and a retail price also reflects processing, transportation, packaging, labour, storage, waste, and differences between the products being compared.
- **The categories are proxies, not matched products.** A live-animal or farm commodity price is compared with an average across selected consumer products. For example, the beef category does not connect a particular animal directly to a specific retail cut.
- **Retail averages are not pure price indexes.** Product availability, package sizes, quality, brands, and retailer composition can change over time. Statistics Canada expanded the retail sample in January 2024, which may affect comparisons across that point.
- **Units require careful interpretation.** The SQL script normalizes several important unit differences, but every comparison should still be checked at the product and unit level before drawing conclusions.
- **Association does not prove pass-through causation.** Estimating how farm shocks reach retail prices requires lagged correlation, regression, or event-study analysis and control for other supply-chain factors.

## Extending the project

Ontario proteins are the first analysis module, not a fixed boundary for the repository. Future studies can follow the same general pattern:

1. Add or update raw source files in `datasets/`.
2. Use Python to select, clean, validate, and load the relevant fields.
3. Add a focused SQL view for the geography, food category, or research question.
4. Export an analysis-ready dataset.
5. Build a dedicated Tableau dashboard or another visualization.

For example, a fish and seafood study may require landing or wholesale datasets because the current farm dataset does not represent wild-caught products. A wheat study may compare farm crop prices with flour, bread, or cereal prices while carefully accounting for processing and unit differences. Provincial studies can reuse the existing geographic fields instead of filtering only for Ontario.

As the repository grows, new analyses can be organized as separate SQL views, exports, research-question documents, and dashboards so that the Ontario protein case study remains reproducible without limiting broader work.

## Possible next steps

### Ontario protein analysis

- Add SQL or Python calculations for 2022-to-2026 absolute and percentage changes.
- Measure month-over-month volatility by category and stage.
- Test lagged correlations between farm and retail price changes.
- Compare spread and ratio trends consistently across all five categories.

### Broader food-price research

- Compare farm and retail trends across multiple provinces.
- Add fish and seafood using suitable producer, landing, wholesale, or retail data.
- Analyze wheat and other grains from farm prices through processed retail products.
- Expand into fruit, vegetables, and other food groups.
- Add automated source downloads, data validation, and pipeline tests.
