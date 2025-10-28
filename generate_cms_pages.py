#!/usr/bin/env python3
"""
Script to generate static product and recipe pages from CSV data.
This recreates the Webflow CMS functionality after export.
"""

import csv
import os
import re
from html import escape
from collections import defaultdict

# Paths
PRODUCTS_CSV = "/Users/elombe.kisala/Downloads/Outlaw Spice 2025 - Products.csv"
RECIPES_CSV = "/Users/elombe.kisala/Downloads/Outlaw Spice 2025 - Recipes (1).csv"
INGREDIENTS_CSV = "/Users/elombe.kisala/Downloads/Outlaw Spice 2025 - Ingredients.csv"
TEMPLATE_DIR = "/Users/elombe.kisala/Library/Mobile Documents/com~apple~CloudDocs/Work - Core Home/CORE HOME/Brands : Projects/SPICES/Outlaw Spice/outlaw-spice-website"
OUTPUT_DIR = TEMPLATE_DIR

def slugify(text):
    """Convert text to URL-friendly slug"""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text

def parse_categories(categories_str):
    """Parse semicolon-separated categories"""
    if not categories_str:
        return []
    return [cat.strip() for cat in categories_str.split(';')]

def parse_more_images(images_str):
    """Parse semicolon-separated image URLs"""
    if not images_str:
        return []
    return [img.strip() for img in images_str.split(';')]

def strip_html_tags(html_text):
    """Remove HTML tags from text"""
    if not html_text:
        return ""
    clean = re.sub('<.*?>', '', html_text)
    return clean.replace('&nbsp;', ' ').strip()

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

def load_ingredients():
    """Load ingredients from CSV"""
    ingredients = {}
    with open(INGREDIENTS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get('Name', '').strip()
            if name:
                ingredients[name] = row
    return ingredients

def create_product_page(handle, product, output_dir):
    """Generate a product detail page"""
    
    # Read the template
    template_path = os.path.join(TEMPLATE_DIR, 'detail_product.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()
    
    # Extract product data
    name = product.get('Product Name', '')
    description = product.get('Product Description', '')
    main_image = product.get('Main Variant Image', '')
    more_images = parse_more_images(product.get('More Variant Images', ''))
    price = product.get('Variant Price', '$0.00')
    compare_price = product.get('Variant Compare-at Price', '')
    categories = parse_categories(product.get('Product Categories', ''))
    
    # Get all variants
    variants = product.get('variants', [product])
    
    # Build variant options HTML
    variants_html = ""
    option1_values = list(set([v.get('Option1 Value', '') for v in variants if v.get('Option1 Value')]))
    option2_values = list(set([v.get('Option2 Value', '') for v in variants if v.get('Option2 Value')]))
    
    # Replace template placeholders
    html = template
    
    # Update title and meta
    html = html.replace('<title>Outlaw Spice 2025</title>', f'<title>{escape(name)} | Outlaw Spice</title>')
    
    # Update product name (find h1 or heading with w-dyn-bind-empty class)
    html = re.sub(
        r'<h1[^>]*class="[^"]*w-dyn-bind-empty[^"]*"[^>]*></h1>',
        f'<h1 class="hero-header">{escape(name)}</h1>',
        html
    )
    
    # Update main image
    if main_image:
        html = re.sub(
            r'src=""[^>]*class="[^"]*w-dyn-bind-empty[^"]*image[^"]*"',
            f'src="{escape(main_image)}" alt="{escape(name)}"',
            html
        )
    
    # Update price
    html = re.sub(
        r'<div[^>]*class="[^"]*text-weight-semibold w-dyn-bind-empty[^"]*"[^>]*></div>',
        f'<div class="text-weight-semibold">{escape(price)}</div>',
        html,
        count=1
    )
    
    # Update description
    clean_description = strip_html_tags(description)
    html = re.sub(
        r'<p[^>]*class="[^"]*text-size-small w-dyn-bind-empty[^"]*"[^>]*></p>',
        f'<p class="text-size-small">{escape(clean_description)}</p>',
        html,
        count=1
    )
    
    # Write output file
    output_file = os.path.join(output_dir, 'products', f'{handle}.html')
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"Created product page: products/{handle}.html")
    return f'products/{handle}.html'

def create_recipe_page(recipe, output_dir):
    """Generate a recipe detail page"""
    
    # Read the template
    template_path = os.path.join(TEMPLATE_DIR, 'detail_recipe.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()
    
    # Extract recipe data
    name = recipe.get('Name', '')
    slug = recipe.get('Slug', slugify(name))
    history = recipe.get('Recipe History', '')
    ingredients_text = recipe.get('Ingredients', '')
    instructions = recipe.get('Instructions', '')
    servings = recipe.get('Number of Servings', '')
    prep_time = recipe.get('Prep Time', '')
    cook_time = recipe.get('Cook Time', '')
    total_time = recipe.get('Total Time', '')
    num_ingredients = recipe.get('Number of Ingredients', '')
    equipment = recipe.get('Tools/Equipment Needed', '')
    main_image = recipe.get('Main Image', '')
    video_link = recipe.get('Video Link', '')
    
    # Replace template placeholders
    html = template
    
    # Update title
    html = html.replace('<title>Outlaw Spice 2025</title>', f'<title>{escape(name)} | Outlaw Spice</title>')
    
    # Update recipe name
    html = re.sub(
        r'<h1[^>]*class="hero-header w-dyn-bind-empty"[^>]*></h1>',
        f'<h1 class="hero-header">{escape(name)}</h1>',
        html
    )
    
    # Update servings
    html = re.sub(
        r'<div[^>]*class="recipe-detail-small w-dyn-bind-empty"[^>]*></div>',
        f'<div class="recipe-detail-small">{escape(servings)}</div>',
        html,
        count=1
    )
    
    # Update prep time
    html = re.sub(
        r'(<div class="recipe-detail">.*?<h5 class="content-h5">Prep Time</h5>.*?)<div[^>]*class="recipe-detail-small w-dyn-bind-empty"[^>]*></div>',
        f'\\1<div class="recipe-detail-small">{escape(prep_time)}</div>',
        html,
        count=1,
        flags=re.DOTALL
    )
    
    # Update cook time
    html = re.sub(
        r'(<div class="recipe-detail">.*?<h5 class="content-h5">Cook Time</h5>.*?)<div[^>]*class="recipe-detail-small w-dyn-bind-empty"[^>]*></div>',
        f'\\1<div class="recipe-detail-small">{escape(cook_time)}</div>',
        html,
        count=1,
        flags=re.DOTALL
    )
    
    # Update total time
    html = re.sub(
        r'(<div class="recipe-detail">.*?<h5 class="content-h5">Total Time</h5>.*?)<div[^>]*class="recipe-detail-small w-dyn-bind-empty"[^>]*></div>',
        f'\\1<div class="recipe-detail-small">{escape(total_time)}</div>',
        html,
        count=1,
        flags=re.DOTALL
    )
    
    # Update number of ingredients
    html = re.sub(
        r'(<div class="recipe-detail">.*?<h5 class="content-h5">Ingredients</h5>.*?)<div[^>]*class="recipe-detail-small w-dyn-bind-empty"[^>]*></div>',
        f'\\1<div class="recipe-detail-small">{escape(num_ingredients)}</div>',
        html,
        count=1,
        flags=re.DOTALL
    )
    
    # Update equipment - find the Equipment section
    html = re.sub(
        r'(<h3 class="content-h3">Equipment</h3>.*?)<div[^>]*class="list-article w-dyn-bind-empty w-richtext"[^>]*></div>',
        f'\\1<div class="list-article w-richtext">{equipment}</div>',
        html,
        count=1,
        flags=re.DOTALL
    )
    
    # Update ingredients list
    html = re.sub(
        r'(<div class="recipe-list-block">.*?<h3 class="content-h3">Ingredients</h3>.*?)<div[^>]*class="list-article w-dyn-bind-empty w-richtext"[^>]*></div>',
        f'\\1<div class="list-article w-richtext">{ingredients_text}</div>',
        html,
        count=1,
        flags=re.DOTALL
    )
    
    # Update instructions
    html = re.sub(
        r'(<h3 class="content-h3">Instructions</h3>.*?)<div[^>]*class="article w-dyn-bind-empty w-richtext"[^>]*></div>',
        f'\\1<div class="article w-richtext">{instructions}</div>',
        html,
        count=1,
        flags=re.DOTALL
    )
    
    # Write output file
    output_file = os.path.join(output_dir, 'recipes', f'{slug}.html')
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"Created recipe page: recipes/{slug}.html")
    return f'recipes/{slug}.html'

def main():
    """Main execution"""
    print("Loading CSV data...")
    products = load_products()
    recipes = load_recipes()
    ingredients = load_ingredients()
    
    print(f"\nFound {len(products)} unique products")
    print(f"Found {len(recipes)} recipes")
    print(f"Found {len(ingredients)} ingredients")
    
    print("\nGenerating product pages...")
    product_pages = []
    for handle, product in products.items():
        page_path = create_product_page(handle, product, OUTPUT_DIR)
        product_pages.append({
            'path': page_path,
            'name': product.get('Product Name', ''),
            'handle': handle,
            'image': product.get('Main Variant Image', ''),
            'price': product.get('Variant Price', ''),
            'categories': parse_categories(product.get('Product Categories', ''))
        })
    
    print("\nGenerating recipe pages...")
    recipe_pages = []
    for recipe in recipes:
        page_path = create_recipe_page(recipe, OUTPUT_DIR)
        recipe_pages.append({
            'path': page_path,
            'name': recipe.get('Name', ''),
            'slug': recipe.get('Slug', ''),
            'image': recipe.get('Thumbnail Image', ''),
            'color': recipe.get('Color', '#000000')
        })
    
    print(f"\n✅ Generated {len(product_pages)} product pages")
    print(f"✅ Generated {len(recipe_pages)} recipe pages")
    print("\nDone!")

if __name__ == '__main__':
    main()

