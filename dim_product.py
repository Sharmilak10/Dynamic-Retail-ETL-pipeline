from faker import Faker
import oracledb
import random

fake = Faker()

print("Script started")


connection = oracledb.connect(
    user="system",
    password="oracle123",
    dsn="host.docker.internal/orcl"
)

cursor = connection.cursor()
print("✅ Connected to Oracle")

# Sample business values
categories = {
    "Grocery": [
        "Rice", "Wheat Flour", "Pulses", "Edible Oil",
        "Spices", "Sugar", "Salt", "Snacks"
    ],
    "Beverage": [
        "Soft Drink", "Fruit Juice", "Energy Drink",
        "Tea", "Coffee", "Mineral Water"
    ],
    "Dairy": [
        "Milk", "Curd", "Butter", "Cheese",
        "Paneer", "Ice Cream"
    ],
    "PersonalCare": [
        "Soap", "Shampoo", "Toothpaste",
        "Face Wash", "Hair Oil", "Body Lotion"
    ],
    "HomeCare": [
        "Detergent", "Dishwash Liquid",
        "Floor Cleaner", "Fabric Conditioner"
    ],
    "BabyCare": [
        "Baby Food", "Diapers", "Baby Soap",
        "Baby Lotion"
    ]
}


flavours = [
    "Vanilla", "Chocolate", "Strawberry",
    "Mango", "Orange", "Masala",
    "Elaichi", "Plain", None
]

sizes = [
    "50g", "100g", "200g", "250g", "500g",
    "1kg", "2kg", "5kg",
    "100ml", "200ml", "500ml", "1L", "2L"
]

sqc_list = [
    "EA",    # Each
    "PK",    # Pack
    "BOX",   # Box
    "BAG",   # Bag
    "BTL",   # Bottle
    "CAN"
]

uoms = [
    "KG", "G",
    "LTR", "ML",
    "PCS",
    "BOX",
    "PK"
]


insert_sql = """
INSERT INTO dim_product (
    product_id,
    product_name,
    category,
    sub_category,
    brand,
    flavour,
    product_size,
    sqc,
    uom,
    unit_price
) VALUES (
    :1, :2, :3, :4, :5, :6, :7, :8, :9, :10
)
"""

data = []

for pid in range(1, 1001):
    category = random.choice(list(categories.keys()))
    sub_category = random.choice(categories[category])

    data.append((
        pid,
        f"{fake.word().capitalize()} {sub_category}",
        category,
        sub_category,
        fake.company()[:50],    
        random.choice(flavours),
        random.choice(sizes),
        random.choice(sqc_list),
        random.choice(uoms),
        round(random.uniform(10, 500), 2)
    ))

print(f" Rows prepared: {len(data)}")

cursor.executemany(insert_sql, data)
connection.commit()

print("✅ 1000 rows inserted into DIM_PRODUCT")

cursor.close()
connection.close()