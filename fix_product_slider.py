#!/usr/bin/env python3
"""
Script to fix the product slider section on the homepage
"""

import csv
import re
from collections import defaultdict
from html import escape

# Paths
PRODUCTS_CSV = "/Users/elombe.kisala/Downloads/Outlaw Spice 2025 - Products.csv"
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
            
            product_cards += f'''
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
            
        if slide_idx < num_slides - 1:
            right_arrow = '''
                  <div class="arrow-right">
                    <a href="#" class="slider-right w-inline-block"><img alt="" src="https://uploads-ssl.webflow.com/615c56b91f3527264e223357/615c56ba1f35277341223374_arrow-right.svg" class="arrow-3"></a>
                  </div>'''
        else:
            right_arrow = '\n                  <div class="arrow-right"></div>'
        
        slide_html = f'''
              <div class="product-slide w-slide">
                <div class="product-wrap">
                  <div role="list" class="collection-list-3">{product_cards}
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
    
    print("Generating product slides...")
    product_slides = create_product_slides(products)
    
    # Replace product slider section
    # Find the slider mask and replace ALL its slide content
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
    print(f"   - Added {len(products)} products across {len(product_slides.split('product-slide w-slide'))-1} slides")

if __name__ == '__main__':
    update_homepage()

