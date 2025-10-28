#!/usr/bin/env python3
"""
Script to update the homepage with product slider and recipe grid content
"""

import csv
import re
from collections import defaultdict
from html import escape

# Paths
PRODUCTS_CSV = "/Users/elombe.kisala/Downloads/Outlaw Spice 2025 - Products.csv"
RECIPES_CSV = "/Users/elombe.kisala/Downloads/Outlaw Spice 2025 - Recipes (1).csv"
INDEX_HTML = "/Users/elombe.kisala/Library/Mobile Documents/com~apple~CloudDocs/Work - Core Home/CORE HOME/Brands : Projects/SPICES/Outlaw Spice/outlaw-spice-website/index.html"

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

def create_product_slides(products):
    """Generate HTML for product slider slides"""
    slides_html = ""
    
    # Create 4 slides with 3 products each
    product_list = list(products.items())
    products_per_slide = 3
    num_slides = (len(product_list) + products_per_slide - 1) // products_per_slide
    
    for slide_idx in range(num_slides):
        start_idx = slide_idx * products_per_slide
        end_idx = min(start_idx + products_per_slide, len(product_list))
        slide_products = product_list[start_idx:end_idx]
        
        product_cards = ""
        for handle, product in slide_products:
            name = product.get('Product Name', '')
            image = product.get('Main Variant Image', '')
            
            card_html = f'''
                        <div role="listitem" class="collection-item-3 w-dyn-item">
                          <div class="product-card">
                            <div class="title-wrap">
                              <h1 class="slider-product-title">{escape(name)}</h1>
                            </div>
                            <div class="w-layout-hflex hflex">
                              <a href="products/{escape(handle)}.html" class="product-base w-inline-block"><img src="{escape(image)}" alt="{escape(name)}" class="product-image"></a>
                            </div>
                          </div>
                        </div>'''
            product_cards += card_html
        
        # Determine arrow placement for this slide
        left_arrow = ""
        right_arrow = ""
        
        if slide_idx > 0:
            left_arrow = '''<div class="arrow-left">
                      <a href="#" class="slider-left w-inline-block"><img alt="" src="https://uploads-ssl.webflow.com/615c56b91f3527264e223357/615c56ba1f3527821f223375_arrow-left.svg" class="arrow-3"></a>
                    </div>'''
        else:
            left_arrow = '<div class="arrow-left"></div>'
            
        if slide_idx < num_slides - 1:
            right_arrow = '''<div class="arrow-right">
                      <a href="#" class="slider-right w-inline-block"><img alt="" src="https://uploads-ssl.webflow.com/615c56b91f3527264e223357/615c56ba1f35277341223374_arrow-right.svg" class="arrow-3"></a>
                    </div>'''
        else:
            right_arrow = '<div class="arrow-right"></div>'
        
        slide_html = f'''
              <div class="product-slide w-slide">
                <div class="product-wrap">
                  <div class="w-dyn-list">
                    <div role="list" class="collection-list-3 w-dyn-items">{product_cards}
                    </div>
                  </div>
                  {right_arrow}
                  {left_arrow}
                </div>
              </div>'''
        
        slides_html += slide_html
    
    return slides_html

def create_recipe_grid(recipes):
    """Generate HTML for recipe grid"""
    grid_items = ""
    
    for recipe in recipes:
        name = recipe.get('Name', '')
        slug = recipe.get('Slug', '')
        image = recipe.get('Thumbnail Image', '')
        
        item_html = f'''
                  <div role="listitem" class="grid_item w-dyn-item">
                    <a href="recipes/{escape(slug)}.html" class="grid_link w-inline-block">
                      <div class="photo_height"><img loading="lazy" src="{escape(image)}" alt="{escape(name)}" class="img-2">
                        <div class="recipe-overlay">
                          <h1 class="recipe-title-grid">{escape(name)}</h1>
                        </div>
                      </div>
                    </a>
                  </div>'''
        grid_items += item_html
    
    return grid_items

def update_homepage():
    """Update the homepage with product and recipe content"""
    
    print("Loading data...")
    products = load_products()
    recipes = load_recipes()
    
    print(f"Loaded {len(products)} products and {len(recipes)} recipes")
    
    # Read index.html
    with open(INDEX_HTML, 'r', encoding='utf-8') as f:
        html = f.read()
    
    print("Generating product slides...")
    product_slides = create_product_slides(products)
    
    print("Generating recipe grid...")
    recipe_grid = create_recipe_grid(recipes)
    
    # Replace product slider section
    # Find the slider mask and replace its contents
    slider_pattern = r'(<div class="mask-2 w-slider-mask">)(.*?)(</div>\s*<div class="arrow-navigation w-slider-nav w-round">)'
    
    html = re.sub(
        slider_pattern,
        f'\\1{product_slides}\\3',
        html,
        flags=re.DOTALL
    )
    
    # Replace recipe grid section
    # Find the grid_list and replace its contents
    grid_pattern = r'(<div role="list" class="grid_list w-dyn-items">)(.*?)(</div>\s*<div class="w-dyn-empty">)'
    
    html = re.sub(
        grid_pattern,
        f'\\1{recipe_grid}\\3',
        html,
        flags=re.DOTALL
    )
    
    # Write updated HTML
    with open(INDEX_HTML, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"\n✅ Homepage updated successfully!")
    print(f"   - Added {len(products)} products to slider")
    print(f"   - Added {len(recipes)} recipes to grid")

if __name__ == '__main__':
    update_homepage()

