#!/bin/bash
# Sync data from Airtable and regenerate all pages

echo "🔄 SYNCING FROM AIRTABLE TO WEBSITE"
echo "===================================="

BASE_DIR="/Users/elombe.kisala/Library/Mobile Documents/com~apple~CloudDocs/Work - Core Home/CORE HOME/Brands : Projects/SPICES/Outlaw Spice/outlaw-spice-website"
cd "$BASE_DIR"

# Airtable credentials from config
TOKEN=$(cat airtable_config.json | python3 -c "import sys, json; print(json.load(sys.stdin)['airtable_token'])")
BASE_ID=$(cat airtable_config.json | python3 -c "import sys, json; print(json.load(sys.stdin)['base_id'])")

# Create CSV export directory
mkdir -p airtable_exports

echo ""
echo "📥 Step 1: Fetching Products from Airtable..."
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://api.airtable.com/v0/$BASE_ID/Products" | \
  python3 -c "
import sys, json, csv

data = json.load(sys.stdin)
records = data.get('records', [])

# Define CSV columns (matching your existing CSV structure)
columns = [
    'Products Collection ID', 'Product ID', 'Variants Collection ID', 'Variant ID',
    'Product Handle', 'Product Name', 'Product Type', 'Product Description',
    'Product Categories', 'Main Variant Image', 'More Variant Images',
    'Variant Price', 'Variant Compare-at Price', 'Product Tax Class',
    'Variant Sku', 'Variant Inventory', 'Requires Shipping', 'Variant Weight',
    'Variant Width', 'Variant Height', 'Variant Length', 'Variant Download Name',
    'Variant Download URL', 'Option1 Name', 'Option1 Value', 'Option2 Name',
    'Option2 Value', 'Option3 Name', 'Option3 Value', 'Created On',
    'Updated On', 'Published On'
]

with open('airtable_exports/products.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=columns)
    writer.writeheader()
    
    for record in records:
        fields = record.get('fields', {})
        row = {col: fields.get(col, '') for col in columns}
        writer.writerow(row)

print(f'✓ Exported {len(records)} product records')
"

echo ""
echo "📥 Step 2: Fetching Recipes from Airtable..."
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://api.airtable.com/v0/$BASE_ID/Recipes" | \
  python3 -c "
import sys, json, csv

data = json.load(sys.stdin)
records = data.get('records', [])

# Define CSV columns for recipes
columns = [
    'Name', 'Slug', 'Collection ID', 'Locale ID', 'Item ID',
    'Created On', 'Updated On', 'Published On', 'Archived', 'Draft',
    'Description', 'Thumbnail Image', 'Main Image', 'Prep Time', 'Cook Time',
    'Servings', 'Difficulty', 'Ingredients', 'Instructions', 'Tags'
]

with open('airtable_exports/recipes.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=columns)
    writer.writeheader()
    
    for record in records:
        fields = record.get('fields', {})
        row = {col: fields.get(col, '') for col in columns}
        writer.writerow(row)

print(f'✓ Exported {len(records)} recipe records')
"

echo ""
echo "🔧 Step 3: Regenerating Product Pages..."
python3 generate_cms_pages.py

echo ""
echo "🔧 Step 4: Updating Homepage Slider..."
python3 fix_slider_single_product.py

echo ""
echo "✅ SYNC COMPLETE!"
echo ""
echo "📋 Summary:"
echo "   - Products exported to: airtable_exports/products.csv"
echo "   - Recipes exported to: airtable_exports/recipes.csv"
echo "   - Product pages regenerated in: products/"
echo "   - Recipe pages regenerated in: recipes/"
echo "   - Homepage updated with latest data"
echo ""
echo "💡 Next: Review changes and commit to git"

