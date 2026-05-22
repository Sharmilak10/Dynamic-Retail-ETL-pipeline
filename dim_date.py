from faker import Faker
import oracledb
from datetime import datetime, timedelta

fake = Faker()

print(" Script started")

connection = oracledb.connect(
    user="system",
    password="oracle123",
    dsn="host.docker.internal/orcl"
)

cursor = connection.cursor()
print("✅ Connected to Oracle")

insert_sql = """
INSERT INTO dim_date (
    date_id,
    full_date,
    day,
    day_name,
    week_of_year,
    month,
    month_name,
    quarter,
    year,
    is_weekend
) VALUES (
    :1, :2, :3, :4, :5, :6, :7, :8, :9, :10
)
"""

start_date = datetime(2022, 1, 1)
data = []

for i in range(1000):
    current_date = start_date + timedelta(days=i)

    date_id = int(current_date.strftime("%Y%m%d"))
    day = current_date.day
    day_name = current_date.strftime("%A").upper()
    week_of_year = int(current_date.strftime("%U"))
    month = current_date.month
    month_name = current_date.strftime("%B").upper()
    quarter = (month - 1) // 3 + 1
    year = current_date.year
    is_weekend = 'Y' if current_date.weekday() >= 5 else 'N'

    data.append((
        date_id,
        current_date,
        day,
        day_name,
        week_of_year,
        month,
        month_name,
        quarter,
        year,
        is_weekend
    ))

print(f"Rows prepared: {len(data)}")

cursor.executemany(insert_sql, data)
connection.commit()

print("✅ 1000 rows inserted into DIM_DATE")

cursor.close()
connection.close()
