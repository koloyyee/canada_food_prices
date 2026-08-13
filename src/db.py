import sqlite3
import pandas as pd

def piping_prices():
	farm_raw = pd.read_csv("datasets/farm_prod_price.csv", low_memory=False)
	retail_raw = pd.read_csv("datasets/retail_price.csv", low_memory=False)

	farm = farm_raw[["REF_DATE", "GEO", "Farm products", "UOM", "VALUE"]].rename(
		columns={"REF_DATE": "month", "Farm products": "product", "UOM": "uom","VALUE": "price_per_unit" }
	)

	retail = retail_raw[["REF_DATE", "GEO", "Products", "UOM", "VALUE"]].rename(
		columns={"REF_DATE": "month", "Products": "product","UOM": "uom", "VALUE": "price_per_unit" }
	)

	# NOTE: Coerce missing/flagged values to NaN so SQLite stores them as NULL/float
	farm["price_per_unit"] = pd.to_numeric(farm["price_per_unit"], errors ="coerce")
	retail["price_per_unit"] = pd.to_numeric(retail["price_per_unit"], errors ="coerce")

	conn = sqlite3.connect("food_prices.db")
	retail.to_sql("retail_prices", conn, if_exists="replace", index=False)
	farm.to_sql("farm_prod_prices", conn, if_exists="replace", index=False)
	conn.close()

def create_ont_protein_view():
	conn = sqlite3.connect("food_prices.db")
	cursor = conn.cursor()

	with open("sql/01_ontario_protein_view.sql") as f:
		sql_scripts = f.read()

	cursor.executescript(sql_scripts)	
	conn.commit()
	conn.close()

def view_to_csv(filename: str , view: str  ):

	"""
	e.g: 
	filename - ontario_protein_prices
	view - ontario_protein_prices

	"""
	conn = sqlite3.connect("food_prices.db")

	query = f"select * from {view} "
	df = pd.read_sql_query(query, conn)

	output_f = f"export/{filename}.csv"
	df.to_csv(output_f, index=False)

	conn.close()