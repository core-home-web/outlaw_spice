#!/usr/bin/env python3
"""
Script to create product and recipe grid pages with all items
"""

import csv
import os
import re
from html import escape
from collections import defaultdict

# Paths
PRODUCTS_CSV = "/Users/elombe.kisala/Downloads/Outlaw Spice 2025 - Products.csv"
RECIPES_CSV = "/Users/elombe.kisala/Downloads/Outlaw Spice 2025 - Recipes (1).csv"
TEMPLATE_DIR = "/Users/elombe.kisala/Library/Mobile Documents/com~apple~CloudDocs/Work - Core Home/CORE HOME/Brands : Projects/SPICES/Outlaw Spice/outlaw-spice-website"
OUTPUT_DIR = TEMPLATE_DIR

def parse_categories(categories_str):
    """Parse semicolon-separated categories"""
    if not categories_str:
        return []
    return [cat.strip() for cat in categories_str.split(';')]

def load_products():
    """Load and group products by Product Handle"""
    products = defaultdict(list)
    
    with open(PRODUCTS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            handle = row.get('Product Handle', '').strip()
            if handle:
                products[handle].append(row)
    
    # Convert to regular dict with first variant as main product
    result = {}
    for handle, variants in products.items():
        main = variants[0].copy()
        main['variants'] = variants
        result[handle] = main
    
    return result

def load_recipes():
    """Load recipes from CSV"""
    recipes = []
    with open(RECIPES_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('Name'):
                recipes.append(row)
    return recipes

def create_products_grid_page(products, output_dir):
    """Create a grid page showing all products"""
    
    # Read index.html as base template
    template_path = os.path.join(TEMPLATE_DIR, 'index.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()
    
    # Build product cards HTML
    product_cards = ""
    for handle, product in products.items():
        name = product.get('Product Name', '')
        image = product.get('Main Variant Image', '')
        price = product.get('Variant Price', '$0.00')
        description = product.get('Product Description', '')
        
        # Clean description (remove HTML tags and limit length)
        clean_desc = re.sub('<.*?>', '', description).strip()
        if len(clean_desc) > 100:
            clean_desc = clean_desc[:100] + '...'
        
        card_html = f'''
        <div role="listitem" class="product-card w-dyn-item">
          <a href="products/{escape(handle)}.html" class="cms-item-link w-inline-block">
            <div class="product-item">
              <div class="product-item-image-wrapper">
                <img loading="lazy" src="{escape(image)}" alt="{escape(name)}" class="product-item-image">
              </div>
              <div class="product-item-content">
                <div class="margin-bottom margin-tiny">
                  <div class="text-weight-semibold">{escape(name)}</div>
                </div>
                <p class="text-size-small">{escape(clean_desc)}</p>
                <div class="margin-top margin-xxsmall">
                  <div class="product-price">{escape(price)}</div>
                </div>
              </div>
            </div>
          </a>
        </div>
        '''
        product_cards += card_html
    
    # Create the products grid page
    html = template
    
    # Update title
    html = html.replace('<title>Outlaw Spice 2025</title>', '<title>All Products | Outlaw Spice</title>')
    
    # Write output file
    output_file = os.path.join(output_dir, 'products.html')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"Created products grid page: products.html")

def create_recipes_grid_page(recipes, output_dir):
    """Create a grid page showing all recipes"""
    
    # Read index.html as base template
    template_path = os.path.join(TEMPLATE_DIR, 'index.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()
    
    # Build recipe cards HTML
    recipe_cards = ""
    for recipe in recipes:
        name = recipe.get('Name', '')
        slug = recipe.get('Slug', '')
        image = recipe.get('Thumbnail Image', '')
        color = recipe.get('Color', '#000000')
        servings = recipe.get('Number of Servings', '')
        total_time = recipe.get('Total Time', '')
        
        card_html = f'''
        <div role="listitem" class="recipe-card w-dyn-item">
          <a href="recipes/{escape(slug)}.html" class="cms-item-link w-inline-block">
            <div class="recipe-item" style="border-color: {escape(color)}">
              <div class="recipe-item-image-wrapper">
                <img loading="lazy" src="{escape(image)}" alt="{escape(name)}" class="recipe-item-image">
              </div>
              <div class="recipe-item-content">
                <div class="margin-bottom margin-tiny">
                  <div class="text-weight-semibold">{escape(name)}</div>
                </div>
                <div class="recipe-meta">
                  <span>{escape(servings)}</span> · <span>{escape(total_time)}</span>
                </div>
              </div>
            </div>
          </a>
        </div>
        '''
        recipe_cards += card_html
    
    # Create the recipes grid page
    html = template
    
    # Update title
    html = html.replace('<title>Outlaw Spice 2025</title>', '<title>All Recipes | Outlaw Spice</title>')
    
    # Write output file
    output_file = os.path.join(output_dir, 'recipes.html')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"Created recipes grid page: recipes.html")

def main():
    """Main execution"""
    print("Loading CSV data...")
    products = load_products()
    recipes = load_recipes()
    
    print(f"\nFound {len(products)} unique products")
    print(f"Found {len(recipes)} recipes")
    
    print("\nCreating grid pages...")
    create_products_grid_page(products, OUTPUT_DIR)
    create_recipes_grid_page(recipes, OUTPUT_DIR)
    
    print("\n✅ Grid pages created successfully!")

if __name__ == '__main__':
    main()

