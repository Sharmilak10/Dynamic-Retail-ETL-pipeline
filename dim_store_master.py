from faker import Faker
import oracledb
import random

# Initialize Faker
fake = Faker()

# Connect to Oracle DB
connection = oracledb.connect(
    user="system",
    password="oracle123",
    dsn="host.docker.internal/orcl"   # change if needed
)

cursor = connection.cursor()

# Function to generate one store record
def generate_store(store_id):
    is_chain = random.choice(['Y', 'N'])
    chain_name = fake.company() if is_chain == 'Y' else None

    return (
        store_id,
        fake.company(),
        fake.street_address(),
        fake.secondary_address(),
        fake.city(),
        fake.postcode(),
        fake.state(),
        random.choice(['Retail', 'Wholesale', 'Convenience', 'Supermarket']),
        is_chain,
        chain_name
    )

# Insert query
insert_query = """
INSERT INTO dim_store_master (
    store_id,
    store_name,
    store_address_lane_1,
    store_address_lane_2,
    store_city,
    store_zip,
    store_state,
    store_class_of_trade,
    is_chain,
    chain_name
) VALUES (
    :1, :2, :3, :4, :5, :6, :7, :8, :9, :10
)
"""

# Generate 1000 rows
data = []
for i in range(1, 1001):  
    data.append(generate_store(i))

# Bulk insert
cursor.executemany(insert_query, data)
connection.commit()

print("✅ 1000 rows inserted successfully!")

# Close connections
cursor.close()
connection.close()
