# Outlaw Spice - CMS Pages Documentation

## Overview

This document explains how the CMS pages were recreated after exporting from Webflow. Since Webflow's CMS functionality is lost on export, we've created a Python-based solution to generate static pages from CSV data.

## What Was Created

### Pages Generated

**Product Pages** (12 total):
- `products/apple-honey-hoedown.html`
- `products/hoppin-honey-mustard.html`
- `products/jerky-seasoning.html`
- `products/roadhouse-rub.html`
- `products/spice-1.html`
- `products/spice-2.html`
- `products/spice-3.html`
- `products/spice-4.html`
- `products/spice-5.html`
- `products/spice-6.html`
- `products/where-theres-hickory-smoke-copy.html`
- `products/where-theres-hickory-smoke.html`

**Recipe Pages** (6 total):
- `recipes/grilled-chicken-garlic-herb.html`
- `recipes/grilled-chicken-smoky-paprika.html`
- `recipes/grilled-pork-chili-lime.html`
- `recipes/grilled-steak-black-pepper.html`
- `recipes/grilled-steak-cumin.html`
- `recipes/grilled-vegetable-zaatar.html`

**Grid/Listing Pages**:
- `products.html` - Shows all products in a grid layout
- `recipes.html` - Shows all recipes in a grid layout

### Scripts Created

1. **`generate_cms_pages.py`** - Generates individual product and recipe pages from CSV data
2. **`create_grid_pages.py`** - Creates grid/listing pages showing all products and recipes

## How To Update Pages

### When You Need to Add/Edit Products or Recipes

1. **Update your CSV files** with the new/changed data:
   - Products: `Outlaw Spice 2025 - Products.csv`
   - Recipes: `Outlaw Spice 2025 - Recipes (1).csv`
   - Ingredients: `Outlaw Spice 2025 - Ingredients.csv`

2. **Run the generation scripts**:
   ```bash
   # Navigate to your website directory
   cd "/Users/elombe.kisala/Library/Mobile Documents/com~apple~CloudDocs/Work - Core Home/CORE HOME/Brands : Projects/SPICES/Outlaw Spice/outlaw-spice-website"
   
   # Generate individual pages
   python3 generate_cms_pages.py
   
   # Generate grid pages
   python3 create_grid_pages.py
   ```

3. **Commit and push to GitHub**:
   ```bash
   git add products/ recipes/ products.html recipes.html
   git commit -m "Update CMS pages with latest product/recipe data"
   git push origin main
   ```

## File Structure

```
outlaw-spice-website/
├── products/              # Individual product pages
│   ├── spice-1.html
│   ├── spice-2.html
│   └── ...
├── recipes/               # Individual recipe pages
│   ├── grilled-chicken-garlic-herb.html
│   ├── grilled-steak-black-pepper.html
│   └── ...
├── products.html          # Products grid/listing page
├── recipes.html           # Recipes grid/listing page
├── generate_cms_pages.py  # Script to generate individual pages
├── create_grid_pages.py   # Script to generate grid pages
└── CMS_PAGES_README.md    # This file
```

## Data Source Files

The scripts read data from these CSV files:
- `/Users/elombe.kisala/Downloads/Outlaw Spice 2025 - Products.csv`
- `/Users/elombe.kisala/Downloads/Outlaw Spice 2025 - Recipes (1).csv`
- `/Users/elombe.kisala/Downloads/Outlaw Spice 2025 - Ingredients.csv`

**Important**: If you move these CSV files, update the paths in both Python scripts.

## Product Data Fields Used

From `Products.csv`:
- Product Handle (URL slug)
- Product Name
- Product Description
- Product Categories
- Main Variant Image
- More Variant Images
- Variant Price
- Variant Compare-at Price
- Product Type
- Option1 Name/Value (e.g., Material)
- Option2 Name/Value (e.g., Color)

## Recipe Data Fields Used

From `Recipes.csv`:
- Name
- Slug (URL)
- Main Image
- Thumbnail Image
- Recipe History
- Ingredients (as HTML/rich text)
- Instructions (as HTML/rich text)
- Tools/Equipment Needed
- Number of Servings
- Prep Time
- Cook Time
- Total Time
- Number of Ingredients
- Color (for styling)
- Video Link

## Template Pages

The scripts use these existing pages as templates:
- `detail_product.html` - Template for individual product pages
- `detail_recipe.html` - Template for individual recipe pages
- `index.html` - Base template for grid pages

## Customization

### To modify the product page layout:
1. Edit `detail_product.html`
2. Update the `create_product_page()` function in `generate_cms_pages.py` to match your changes
3. Re-run the script

### To modify the recipe page layout:
1. Edit `detail_recipe.html`
2. Update the `create_recipe_page()` function in `generate_cms_pages.py` to match your changes
3. Re-run the script

### To modify the grid page layouts:
1. Update the `create_products_grid_page()` or `create_recipes_grid_page()` functions in `create_grid_pages.py`
2. Re-run the script

## Benefits of This Approach

✅ **No CMS subscription needed** - All pages are static HTML
✅ **Fast loading** - No database queries
✅ **Version controlled** - All pages in git
✅ **Easy updates** - Just edit CSV and re-run scripts
✅ **SEO friendly** - All content is in HTML
✅ **Hosting flexibility** - Can host anywhere (GitHub Pages, Netlify, etc.)

## Troubleshooting

### Script fails with "File not found"
- Check that CSV file paths in the scripts are correct
- Make sure CSV files exist in the specified locations

### Pages look broken
- Ensure `css/` and `images/` directories are in the correct location
- Check that image URLs in CSV are valid and accessible

### New products/recipes don't appear
- Make sure you ran both scripts:
  1. `generate_cms_pages.py` (creates individual pages)
  2. `create_grid_pages.py` (updates listing pages)

## Future Enhancements

Potential improvements:
- [ ] Add search functionality to grid pages
- [ ] Add category filtering
- [ ] Add pagination for large product catalogs
- [ ] Generate sitemap.xml automatically
- [ ] Add related products section
- [ ] Add recipe ratings/reviews
- [ ] Create ingredient detail pages

## Questions?

If you need to modify the page generation logic or have questions, the Python scripts are well-commented and can be edited to suit your needs.

---
*Generated: October 28, 2025*
*Last Updated: October 28, 2025*

