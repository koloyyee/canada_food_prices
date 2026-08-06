import sqlite3
import pandas as pd

farm_raw = pd.read_csv("datasets/farm_prod_price.csv", low_memory=False)
retail_raw = pd.read_csv("datasets/retail_price.csv", low_memory=False)

#retail_cols = retail_raw.columns.tolist()
#farm_cols = farm_raw.columns.tolist()
#print(retail_cols)
#print(farm_cols)
#print(retail_raw.head())
#print(farm_raw.head())

farm = farm_raw[["REF_DATE", "GEO", "Farm products", "UOM", "VALUE"]].rename(
	columns={"REF_DATE": "month", "Farm products": "product", "UOM": "uom","VALUE": "price_per_unit" }
)

retail = retail_raw[["REF_DATE", "GEO", "Products", "UOM", "VALUE"]].rename(
	columns={"REF_DATE": "month", "Products": "product","UOM": "uom", "VALUE": "price_per_unit" }
)

# NOTE: Coerce missing/flagged values to NaN so SQLite stores them as NULL/float
farm["price_per_unit"] = pd.to_numeric(farm["price_per_unit"], errors ="coerce")
retail["price_per_unit"] = pd.to_numeric(retail["price_per_unit"], errors ="coerce")

conn = sqlite3.connect("sql/food_prices.db")
retail.to_sql("retail_prices", conn, if_exists="replace", index=False)
farm.to_sql("farm_prod_prices", conn, if_exists="replace", index=False)
conn.close()