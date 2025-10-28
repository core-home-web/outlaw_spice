# Outlaw Spice Website - Quick Start Guide

## ✅ What's Set Up

### 🎨 Website Structure
- ✅ Homepage with product slider (1 product per slide)
- ✅ Homepage with recipe grid (6 recipes)
- ✅ 12 individual product detail pages
- ✅ 6 individual recipe detail pages
- ✅ All pages linked and functional

### 🔗 Airtable Integration (ACTIVE)
- ✅ Connected to: [Airtable Base appdJG7s8eu1jVWlZ](https://airtable.com/appdJG7s8eu1jVWlZ/shrBBQh4sqxexsjA0)
- ✅ Products table: 12 products (100 variants total)
- ✅ Recipes table: 6 recipes
- ✅ One-command sync ready to use

## 🚀 Quick Commands

### Update Website from Airtable
```bash
./sync_from_airtable.sh
```
This will:
1. Fetch latest products from Airtable
2. Fetch latest recipes from Airtable
3. Export to CSV
4. Regenerate all product pages
5. Regenerate all recipe pages
6. Update homepage slider
7. Update recipe grid

### Manual Page Generation (from CSV)
```bash
python3 generate_cms_pages.py
python3 fix_slider_single_product.py
```

### Deploy to GitHub
```bash
git add -A
git commit -m "Update from Airtable"
git push
```

## 📁 File Structure

```
outlaw-spice-website/
├── index.html                    # Homepage
├── products/                     # Generated product pages
│   ├── apple-honey-hoedown.html
│   ├── roadhouse-rub.html
│   └── ... (12 total)
├── recipes/                      # Generated recipe pages
│   ├── grilled-chicken-garlic-herb.html
│   └── ... (6 total)
├── images/                       # Product and recipe images
├── sync_from_airtable.sh        # Main sync script
├── generate_cms_pages.py        # Page generator
├── fix_slider_single_product.py # Slider updater
└── airtable_config.json         # Your credentials (not in git)
```

## 🔄 Typical Workflow

### When You Update Content in Airtable:

1. **Edit in Airtable**
   - Add/edit products
   - Add/edit recipes
   - Update images, descriptions, prices

2. **Sync to Website**
   ```bash
   ./sync_from_airtable.sh
   ```

3. **Review Changes**
   - Open `index.html` in browser
   - Check product/recipe pages

4. **Commit & Deploy**
   ```bash
   git add -A
   git commit -m "Updated products and recipes from Airtable"
   git push
   ```

## 🎯 Your Airtable Setup

**Base ID:** `appdJG7s8eu1jVWlZ`

**Tables:**
- **Products** (32 fields)
  - Product Name, Handle, Description
  - Main Variant Image
  - Price, SKU, Categories
  - etc.

- **Recipes** (28 fields)  
  - Name, Slug, Description
  - Thumbnail Image
  - Ingredients, Instructions
  - etc.

## 🔐 Security

- ✅ Airtable token stored locally in `airtable_config.json`
- ✅ Config file is gitignored (never committed)
- ✅ Token is secure and only on your machine

## 📞 Need Help?

- Full Airtable setup: See `AIRTABLE_SETUP.md`
- CMS pages documentation: See `CMS_PAGES_README.md`

## 🎉 You're All Set!

Your website is now powered by Airtable. Edit your content in Airtable's nice UI, run one command, and your website updates automatically!

