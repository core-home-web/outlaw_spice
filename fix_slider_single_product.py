#!/usr/bin/env python3
"""
Script to fix the product slider to show ONE product per slide
"""

import csv
import re
from collections import defaultdict
from html import escape

# Paths
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AIRTABLE_EXPORTS = os.path.join(BASE_DIR, "airtable_exports")

# Use Airtable exports if available, otherwise use original CSV
if os.path.exists(os.path.join(AIRTABLE_EXPORTS, "products.csv")):
    PRODUCTS_CSV = os.path.join(AIRTABLE_EXPORTS, "products.csv")
else:
    PRODUCTS_CSV = "/Users/elombe.kisala/Downloads/Outlaw Spice 2025 - Products.csv"

INDEX_HTML = os.path.join(BASE_DIR, "index.html")

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

def create_product_slides(products):
    """Generate HTML for product slider slides - ONE product per slide"""
    slides_html = ""
    
    # Create one slide per product
    product_list = list(products.items())
    
    for slide_idx, (handle, product) in enumerate(product_list):
        name = product.get('Product Name', '')
        image = product.get('Main Variant Image', 'images/49764_L_Group1.JPG')
        
        # Use placeholder if no image
        if not image or image.strip() == '':
            image = 'images/49764_L_Group1.JPG'
        
        # Determine arrow placement for this slide
        left_arrow = ""
        right_arrow = ""
        
        if slide_idx > 0:
            left_arrow = '''
                  <div class="arrow-left">
                    <a href="#" class="slider-left w-inline-block"><img alt="" src="https://uploads-ssl.webflow.com/615c56b91f3527264e223357/615c56ba1f3527821f223375_arrow-left.svg" class="arrow-3"></a>
                  </div>'''
        else:
            left_arrow = '\n                  <div class="arrow-left"></div>'
            
        if slide_idx < len(product_list) - 1:
            right_arrow = '''
                  <div class="arrow-right">
                    <a href="#" class="slider-right w-inline-block"><img alt="" src="https://uploads-ssl.webflow.com/615c56b91f3527264e223357/615c56ba1f35277341223374_arrow-right.svg" class="arrow-3"></a>
                  </div>'''
        else:
            right_arrow = '\n                  <div class="arrow-right"></div>'
        
        slide_html = f'''
              <div class="product-slide w-slide">
                <div class="product-wrap">
                  <div role="list" class="collection-list-3">
                        <div role="listitem" class="collection-item-3 w-dyn-item">
                          <div class="product-card">
                            <div class="title-wrap">
                              <h1 class="slider-product-title">{escape(name)}</h1>
                            </div>
                            <div class="w-layout-hflex hflex">
                              <a href="products/{escape(handle)}.html" class="product-base w-inline-block"><img src="{escape(image)}" alt="{escape(name)}" class="product-image"></a>
                            </div>
                          </div>
                        </div>
                  </div>{right_arrow}{left_arrow}
                </div>
              </div>'''
        
        slides_html += slide_html
    
    return slides_html

def update_homepage():
    """Update the homepage product slider"""
    
    print("Loading products...")
    products = load_products()
    
    print(f"Loaded {len(products)} products")
    
    # Read index.html
    with open(INDEX_HTML, 'r', encoding='utf-8') as f:
        html = f.read()
    
    print("Generating product slides (1 product per slide)...")
    product_slides = create_product_slides(products)
    
    # Replace product slider section
    slider_pattern = r'(<div class="mask-2 w-slider-mask">)(.*?)(</div>\s*<div class="left-arrow w-slider-arrow-left">)'
    
    replacement = f'\\1{product_slides}\n            \\3'
    
    html_updated = re.sub(
        slider_pattern,
        replacement,
        html,
        flags=re.DOTALL
    )
    
    if html_updated == html:
        print("❌ ERROR: Pattern didn't match. Slider not updated.")
        return
    
    # Write updated HTML
    with open(INDEX_HTML, 'w', encoding='utf-8') as f:
        f.write(html_updated)
    
    print(f"\n✅ Product slider updated successfully!")
    print(f"   - Created {len(products)} slides (1 product per slide)")

if __name__ == '__main__':
    update_homepage()

