import random
import oracledb

print("FACT_SALES load started")

# ---------------------------------
# Oracle DB connection
# ---------------------------------
connection = oracledb.connect(
    user="system",
    password="oracle123",
    dsn="host.docker.internal/orcl"
)

cursor = connection.cursor()
print("✅ Connected to Oracle")

# ---------------------------------
# Get next sales_id
# ---------------------------------
cursor.execute("SELECT NVL(MAX(sales_id), 0) FROM fact_sales")
start_sales_id = cursor.fetchone()[0] + 1

# ---------------------------------
# Fetch dimension keys
# ---------------------------------
cursor.execute("SELECT date_id FROM dim_date")
date_ids = [r[0] for r in cursor.fetchall()]

cursor.execute("SELECT store_id FROM dim_store_master")
store_ids = [r[0] for r in cursor.fetchall()]

cursor.execute("SELECT product_id, unit_price FROM dim_product")
products = cursor.fetchall()  # (product_id, unit_price)

cursor.execute("SELECT distributor_id FROM dim_distributor")
distributor_ids = [r[0] for r in cursor.fetchall()]

# ---------------------------------
# Insert SQL
# ---------------------------------
insert_sql = """
INSERT INTO fact_sales (
    sales_id,
    date_id,
    store_id,
    product_id,
    distributor_id,
    quantity_sold,
    unit_price,
    gross_amount,
    discount_amount,
    net_amount
) VALUES (
    :1, :2, :3, :4, :5,
    :6, :7, :8, :9, :10
)
"""

data = []

# ---------------------------------
# Generate 10,000 FACT rows
# ---------------------------------
for i in range(10000):

    sales_id = start_sales_id + i
    date_id = random.choice(date_ids)
    store_id = random.choice(store_ids)
    distributor_id = random.choice(distributor_ids)

    product_id, unit_price = random.choice(products)
    quantity = random.randint(1, 25)

    gross_amount = round(quantity * unit_price, 2)

   
    # Discount 
  
    if gross_amount >= 8000:
        discount_pct = 0.15      
    elif gross_amount >= 4000:
        discount_pct = 0.10      
    elif gross_amount >= 2000:
        discount_pct = 0.05      
    else:
        discount_pct = 0.00     

    discount_amount = round(gross_amount * discount_pct, 2)
    net_amount = round(gross_amount - discount_amount, 2)

    data.append((
        sales_id,
        date_id,
        store_id,
        product_id,
        distributor_id,
        quantity,
        unit_price,
        gross_amount,
        discount_amount,
        net_amount
    ))

print(f"Rows prepared: {len(data)}")

# ---------------------------------
# Bulk insert
# ---------------------------------
cursor.executemany(insert_sql, data)
connection.commit()

print("✅ 10,000 rows inserted into FACT_SALES successfully")

cursor.close()
connection.close()
