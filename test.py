# Ethan I changed the key to the right one, this should work for you now, we have 10k requests/month now
import requests
import mysql.connector
from mysql.connector import Error

# Define the API endpoint and headers
url = "https://grocery-pricing-api.p.rapidapi.com/searchGrocery"
headers = {
    "x-rapidapi-key": "5181258988msh2304c15205daf50p138250jsna63a8367bc9b",  # Replace with your actual RapidAPI key
    "x-rapidapi-host": "grocery-pricing-api.p.rapidapi.com"
}

# Test query with a known item and zip code
querystring = {"keyword": "steak", "perPage": "10", "page": "1", "zipcode": "92804"}

response = requests.get(url, headers=headers, params=querystring)

# Set up MySQL connection
def create_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",      # Replace with your MySQL username
            password="bellaella",  # Replace with your MySQL password
            database="grocery_db"
        )
        if connection.is_connected():
            print("Connected to MySQL database")
        return connection
    except Error as e:
        print("Error connecting to MySQL", e)
        return None

# Function to insert product into the MySQL database
def insert_product(cursor, product):
    sql = """
    INSERT INTO products (id, name, description, price, was_price, unit_price, image_url)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE 
        name=VALUES(name), 
        description=VALUES(description), 
        price=VALUES(price), 
        was_price=VALUES(was_price), 
        unit_price=VALUES(unit_price), 
        image_url=VALUES(image_url)
    """
    # Extracting fields from product data
    data = (
        product['id'],
        product['name'],
        product.get('shortDescription', ''),
        float(product['priceInfo'].get('linePrice', '0').replace('$', '')) if product['priceInfo'].get('linePrice') else None,
        float(product['priceInfo'].get('wasPrice', '0').replace('$', '')) if product['priceInfo'].get('wasPrice') else None,
        product['priceInfo'].get('unitPrice', ''),
        product['image']
    )
    cursor.execute(sql, data)

# Main function to fetch data from API and insert into MySQL
def fetch_and_store_products():
    connection = create_connection()
    if connection is None:
        return

    cursor = connection.cursor()

    # Example query with a specific keyword and pagination
    querystring = {"keyword": "steak", "perPage": "10", "page": "1", "zipcode": "YOUR_ZIP_CODE"}

    # Make the API request
    response = requests.get(url, headers=headers, params=querystring)

    # Check if the response is successful
    if response.status_code != 200:
        print("Error fetching data from API:", response.status_code, response.text)
        return

    # Parse the JSON data
    products = response.json().get('hits', [])
    if not products:
        print("No products found.")
        return

    # Insert each product into the database
    for product in products:
        try:
            insert_product(cursor, product)
        except Error as e:
            print("Error inserting product:", e)

    # Commit the transaction after inserting all products
    connection.commit()
    print("Products inserted successfully.")

    # Close the database connection
    cursor.close()
    connection.close()
    print("Data fetching and insertion completed.")

# Run the function
fetch_and_store_products()
