#!/usr/bin/env python3
"""
Airtable Sync Script for Outlaw Spice
Syncs products and recipes from Airtable to generate static pages
"""

import requests
import json
import os
from collections import defaultdict

# Load configuration from file
def load_config():
    """Load Airtable configuration from airtable_config.json"""
    config_file = "airtable_config.json"
    
    if not os.path.exists(config_file):
        print(f"\n⚠️  Configuration file not found: {config_file}")
        print("   Please create it from airtable_config.example.json")
        return None
    
    with open(config_file, 'r') as f:
        return json.load(f)

# Load configuration
config = load_config()
if not config:
    AIRTABLE_TOKEN = ""
    AIRTABLE_BASE_ID = ""
    PRODUCTS_TABLE = "Products"
    RECIPES_TABLE = "Recipes"
else:
    AIRTABLE_TOKEN = config.get('airtable_token', '')
    AIRTABLE_BASE_ID = config.get('base_id', '')
    PRODUCTS_TABLE = config.get('products_table', 'Products')
    RECIPES_TABLE = config.get('recipes_table', 'Recipes')

def get_airtable_data(base_id, table_name):
    """Fetch data from Airtable"""
    url = f"https://api.airtable.com/v0/{base_id}/{table_name}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_TOKEN}",
        "Content-Type": "application/json"
    }
    
    all_records = []
    offset = None
    
    while True:
        params = {"offset": offset} if offset else {}
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code != 200:
            print(f"❌ Error fetching from Airtable: {response.status_code}")
            print(f"   Response: {response.text}")
            return []
        
        data = response.json()
        all_records.extend(data.get('records', []))
        
        offset = data.get('offset')
        if not offset:
            break
    
    return all_records

def sync_products(base_id):
    """Sync products from Airtable"""
    print(f"\n📦 Syncing products from Airtable...")
    
    records = get_airtable_data(base_id, PRODUCTS_TABLE)
    
    if not records:
        print("   No products found or error occurred")
        return
    
    print(f"   Found {len(records)} product records")
    
    # Group by product (in case there are variants)
    products = defaultdict(list)
    for record in records:
        fields = record.get('fields', {})
        handle = fields.get('Handle', fields.get('Product Handle', ''))
        if handle:
            products[handle].append(fields)
    
    print(f"   Grouped into {len(products)} unique products")
    
    # Display sample product
    if products:
        sample_handle = list(products.keys())[0]
        sample = products[sample_handle][0]
        print(f"\n   Sample product:")
        print(f"   - Name: {sample.get('Name', sample.get('Product Name', 'N/A'))}")
        print(f"   - Handle: {sample_handle}")
        print(f"   - Image: {sample.get('Image', sample.get('Main Variant Image', 'N/A'))[:50]}...")
    
    return products

def sync_recipes(base_id):
    """Sync recipes from Airtable"""
    print(f"\n🍽️  Syncing recipes from Airtable...")
    
    records = get_airtable_data(base_id, RECIPES_TABLE)
    
    if not records:
        print("   No recipes found or error occurred")
        return
    
    print(f"   Found {len(records)} recipe records")
    
    recipes = []
    for record in records:
        fields = record.get('fields', {})
        if fields.get('Name') or fields.get('Recipe Name'):
            recipes.append(fields)
    
    # Display sample recipe
    if recipes:
        sample = recipes[0]
        print(f"\n   Sample recipe:")
        print(f"   - Name: {sample.get('Name', sample.get('Recipe Name', 'N/A'))}")
        print(f"   - Slug: {sample.get('Slug', 'N/A')}")
        print(f"   - Image: {sample.get('Thumbnail', sample.get('Thumbnail Image', 'N/A'))[:50]}...")
    
    return recipes

def test_connection(base_id):
    """Test Airtable connection"""
    print("🔗 Testing Airtable connection...")
    
    url = f"https://api.airtable.com/v0/meta/bases/{base_id}/tables"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_TOKEN}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        tables = data.get('tables', [])
        print(f"✅ Connection successful!")
        print(f"   Found {len(tables)} tables:")
        for table in tables:
            print(f"   - {table.get('name')} (ID: {table.get('id')})")
        return True
    else:
        print(f"❌ Connection failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False

def main():
    """Main sync function"""
    print("=" * 60)
    print("OUTLAW SPICE - AIRTABLE SYNC")
    print("=" * 60)
    
    # Check if base ID is set
    if not AIRTABLE_BASE_ID:
        print("\n⚠️  SETUP REQUIRED:")
        print("   1. Find your Airtable Base ID from the URL:")
        print("      https://airtable.com/appXXXXXXXXXXXXXX/...")
        print("      (The part that starts with 'app')")
        print("   2. Update AIRTABLE_BASE_ID in this script")
        print("   3. Run this script again")
        return
    
    # Test connection
    if not test_connection(AIRTABLE_BASE_ID):
        return
    
    # Sync data
    products = sync_products(AIRTABLE_BASE_ID)
    recipes = sync_recipes(AIRTABLE_BASE_ID)
    
    print("\n" + "=" * 60)
    print("SYNC COMPLETE")
    print("=" * 60)
    print("\n💡 Next steps:")
    print("   1. Review the data above")
    print("   2. Integrate with generate_cms_pages.py")
    print("   3. Regenerate all pages")

if __name__ == '__main__':
    main()

