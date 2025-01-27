import uuid
import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants and Configuration
TOTAL_TRANSACTIONS = 100_000
TOTAL_CUSTOMERS = 10_000
TOTAL_PRODUCTS = 2_000
FILES_TO_SPLIT = 10
OUTPUT_DIR = Path("output")

# Store Locations with weights
STORE_LOCATIONS = {
    "Downtown": 0.4,
    "Suburb North": 0.25,
    "Suburb South": 0.25,
    "Coastal": 0.1
}

# Product Categories with base price ranges and realistic names
PRODUCT_CATEGORIES = {
    "Dairy": {
        "price_range": (2.99, 8.99),
        "items": ["Whole Milk", "Greek Yogurt", "Cheddar Cheese", "Butter", "Cream"]
    },
    "Bakery": {
        "price_range": (1.99, 12.99),
        "items": ["Whole Wheat Bread", "Croissants", "Bagels", "Muffins", "Danish"]
    },
    "Produce": {
        "price_range": (0.99, 7.99),
        "items": ["Bananas", "Apples", "Carrots", "Spinach", "Tomatoes"]
    },
    "Meat": {
        "price_range": (5.99, 25.99),
        "items": ["Chicken Breast", "Ground Beef", "Salmon", "Pork Chops", "Turkey"]
    },
    "Frozen Foods": {
        "price_range": (3.99, 15.99),
        "items": ["Ice Cream", "Frozen Pizza", "Frozen Vegetables", "TV Dinner", "Fish Sticks"]
    },
    "Snacks": {
        "price_range": (1.99, 6.99),
        "items": ["Potato Chips", "Pretzels", "Popcorn", "Trail Mix", "Cookies"]
    },
    "Beverages": {
        "price_range": (2.99, 9.99),
        "items": ["Cola", "Coffee", "Orange Juice", "Energy Drink", "Water"]
    },
    "Organic": {
        "price_range": (3.99, 15.99),
        "items": ["Organic Eggs", "Organic Milk", "Organic Quinoa", "Organic Berries", "Organic Honey"]
    },
    "Pantry": {
        "price_range": (1.99, 12.99),
        "items": ["Pasta", "Rice", "Cereal", "Peanut Butter", "Soup"]
    },
    "Personal Care": {
        "price_range": (2.99, 19.99),
        "items": ["Shampoo", "Toothpaste", "Soap", "Deodorant", "Lotion"]
    }
}

PAYMENT_METHODS = ["Credit Card", "Debit Card", "Cash", "Mobile Wallet"]
DISCOUNT_RATES = [0.05, 0.10, 0.15]

class GroceryDataGenerator:
    def __init__(self):
        self.customers = self._generate_customers()
        self.products = self._generate_products()
        self.holiday_weeks = self._get_holiday_weeks()
        
        # Create output directory if it doesn't exist
        OUTPUT_DIR.mkdir(exist_ok=True)
        
    def _generate_customers(self):
        logging.info("Generating customer data...")
        customers = []
        for _ in range(TOTAL_CUSTOMERS):
            customer_id = str(uuid.uuid4())
            is_loyalty = random.random() < 0.3
            customers.append({
                'customer_id': customer_id,
                'is_loyalty': is_loyalty
            })
        return customers
    
    def _generate_products(self):
        logging.info("Generating product data...")
        products = []
        high_demand_count = int(TOTAL_PRODUCTS * 0.2)
        
        for i in range(TOTAL_PRODUCTS):
            category = random.choice(list(PRODUCT_CATEGORIES.keys()))
            base_name = random.choice(PRODUCT_CATEGORIES[category]["items"])
            min_price, max_price = PRODUCT_CATEGORIES[category]["price_range"]
            
            # Add 20% premium for organic products
            if category == "Organic":
                min_price *= 1.2
                max_price *= 1.2
                
            is_high_demand = i < high_demand_count
            
            products.append({
                'product_id': f"PROD_{str(i+1).zfill(4)}",
                'product_name': f"{base_name} {i+1}",
                'category': category,
                'base_price': round(random.uniform(min_price, max_price), 2),
                'is_high_demand': is_high_demand
            })
        return products
    
    def _get_holiday_weeks(self):
        holidays = [
            "2023-01-01",  # New Year's
            "2023-12-25",  # Christmas
            "2023-11-23",  # Thanksgiving
            "2023-07-04",  # Independence Day
            "2023-05-29",  # Memorial Day
            "2023-09-04"   # Labor Day
        ]
        holiday_weeks = []
        for holiday in holidays:
            date = datetime.strptime(holiday, "%Y-%m-%d")
            week_start = date - timedelta(days=date.weekday())
            week_end = week_start + timedelta(days=6)
            holiday_weeks.append((week_start, week_end))
        return holiday_weeks

    def _is_holiday_week(self, date):
        for start, end in self.holiday_weeks:
            if start <= date <= end:
                return True
        return False

    def generate_transaction(self):
        # Select customer
        customer = random.choice(self.customers)
        is_loyalty = customer['is_loyalty']
        
        # Generate datetime with patterns
        start_date = datetime(2023, 1, 1)
        end_date = datetime(2023, 12, 31)
        
        while True:
            transaction_date = start_date + timedelta(
                seconds=random.randint(0, int((end_date - start_date).total_seconds()))
            )
            
            # Apply weekend and holiday patterns
            is_weekend = transaction_date.weekday() >= 5
            is_holiday = self._is_holiday_week(transaction_date)
            
            if is_weekend and random.random() < 0.3:
                break
            elif is_holiday and random.random() < 0.2:
                break
            elif random.random() < 0.5:  # Regular days
                break
        
        # Generate transaction details
        num_items = np.random.choice(
            [random.randint(1, 15)],
            p=[1.0]
        )
        
        # Select products with bias towards high-demand items
        transaction_products = []
        for _ in range(num_items):
            if random.random() < 0.3:  # 30% chance of high-demand product
                product = random.choice([p for p in self.products if p['is_high_demand']])
            else:
                product = random.choice(self.products)
            
            # Determine quantity
            quantity = random.randint(1, 10)
            if random.random() < 0.1:  # 10% chance of higher quantity
                quantity = random.randint(6, 10)
            
            # Add anomalies (0.1% chance)
            if random.random() < 0.001:
                quantity = random.randint(50, 100)
            
            transaction_products.append({
                'product': product,
                'quantity': quantity
            })
        
        # Calculate discount
        discount_chance = 0.4 if is_loyalty else 0.2
        discount = random.choice(DISCOUNT_RATES) if random.random() < discount_chance else 0
        
        return {
            'transaction_id': str(uuid.uuid4()),
            'customer_id': customer['customer_id'],
            'transaction_datetime': transaction_date,
            'store_location': random.choices(
                list(STORE_LOCATIONS.keys()),
                weights=list(STORE_LOCATIONS.values())
            )[0],
            'products': transaction_products,
            'payment_method': random.choice(PAYMENT_METHODS),
            'loyalty_member': is_loyalty,
            'discount_applied': discount
        }

    def generate_dataset(self):
        logging.info(f"Generating {TOTAL_TRANSACTIONS} transactions...")
        transactions = []
        
        for i in range(TOTAL_TRANSACTIONS):
            if i % 10000 == 0:
                logging.info(f"Generated {i} transactions...")
                
            transaction = self.generate_transaction()
            
            # Flatten products into individual rows
            for product_info in transaction['products']:
                product = product_info['product']
                quantity = product_info['quantity']
                unit_price = product['base_price']
                total_price = round(quantity * unit_price * (1 - transaction['discount_applied']), 2)
                
                transactions.append({
                    'transaction_id': transaction['transaction_id'],
                    'customer_id': transaction['customer_id'],
                    'transaction_datetime': transaction['transaction_datetime'],
                    'store_location': transaction['store_location'],
                    'product_id': product['product_id'],
                    'product_name': product['product_name'],
                    'product_category': product['category'],
                    'quantity': quantity,
                    'unit_price': unit_price,
                    'total_price': total_price,
                    'payment_method': transaction['payment_method'],
                    'loyalty_member': transaction['loyalty_member'],
                    'discount_applied': transaction['discount_applied']
                })
        
        df = pd.DataFrame(transactions)
        
        # Split into multiple files
        logging.info(f"Splitting data into {FILES_TO_SPLIT} files...")
        rows_per_file = len(df) // FILES_TO_SPLIT
        for i in range(FILES_TO_SPLIT):
            start_idx = i * rows_per_file
            end_idx = start_idx + rows_per_file if i < FILES_TO_SPLIT - 1 else None
            df_chunk = df.iloc[start_idx:end_idx]
            output_file = OUTPUT_DIR / f'grocery_transactions_{i+1}.csv'
            df_chunk.to_csv(output_file, index=False)
            logging.info(f"Saved file: {output_file}")

def main():
    try:
        generator = GroceryDataGenerator()
        generator.generate_dataset()
        logging.info("Data generation completed successfully!")
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    main() 