from faker import Faker
import oracledb
import random
from datetime import date

fake = Faker()

print("Script started")


connection = oracledb.connect(
    user="system",
    password="oracle123",
    dsn="host.docker.internal/orcl"
)

cursor = connection.cursor()
print("✅ Connected to Oracle")

distributor_types = ["National", "Regional", "Local"]
states = [
    "Telangana", "Karnataka", "Maharashtra",
    "Tamil Nadu", "Kerala", "Delhi"
]

insert_sql = """
INSERT INTO dim_distributor (
    distributor_id,
    distributor_name,
    distributor_type,
    city,
    state,
    onboarding_date,
    active_flag
) VALUES (
    :1, :2, :3, :4, :5, :6, :7
)
"""

data = []

for did in range(1, 1001): 
    data.append((
        did,
        fake.company()[:100],                 # safe length
        random.choice(distributor_types),
        fake.city(),
        random.choice(states),
        fake.date_between(
            start_date=date(2015, 1, 1),
            end_date=date.today()
        ),
        random.choice(['Y', 'N'])
    ))

print(f"Rows prepared: {len(data)}")

cursor.executemany(insert_sql, data)
connection.commit()

print("✅ 1000 rows inserted into DIM_DISTRIBUTOR")

cursor.close()
connection.close()
