# Airtable Integration Setup

## ✅ What's Done

1. ✅ **Slider Fixed** - Now shows 1 product per slide (12 slides total)
2. ✅ **Recipe Grid Working** - All 6 recipes displaying with images
3. ✅ **Airtable Script Created** - `airtable_sync.py` ready to use
4. ✅ **Security Configured** - Credentials stored securely (not in git)

## 🔧 How to Complete Airtable Setup

### Step 1: Find Your Airtable Base ID

1. Open your Airtable workspace
2. Look at the URL - it will look like:
   ```
   https://airtable.com/appXXXXXXXXXXXXXX/tblYYYYYYYYYYYYYY/...
   ```
3. Copy the part that starts with `app` (e.g., `appAbCd1234567890`)

### Step 2: Update Configuration

1. Open `airtable_config.json` in this folder
2. Replace the empty `base_id` with your actual Base ID:
   ```json
   {
     "airtable_token": "pat1wfGCQZYDR7FyX...",
     "base_id": "appYourActualBaseID",
     "products_table": "Products",
     "recipes_table": "Recipes"
   }
   ```
3. Update table names if they're different in your Airtable

### Step 3: Test the Connection

Run the sync script to test:
```bash
python3 airtable_sync.py
```

This will:
- ✅ Test your connection
- ✅ Show all tables in your base
- ✅ Fetch sample products and recipes
- ✅ Display the data structure

### Step 4: Sync Your Data

Once the test works, you can:

**Option A: Manual Sync (whenever you need)**
```bash
python3 airtable_sync.py
```

**Option B: Auto-regenerate pages from Airtable**
We can integrate this with `generate_cms_pages.py` to:
1. Pull data from Airtable
2. Generate all product/recipe pages
3. Update homepage slider/grid
4. All in one command!

## 📊 Expected Airtable Structure

### Products Table
Required fields:
- `Product Name` or `Name`
- `Product Handle` or `Handle` (URL-friendly slug)
- `Main Variant Image` or `Image` (URL to image)
- `Product Description` or `Description`

Optional fields:
- `Price`
- `SKU`
- `Categories`

### Recipes Table
Required fields:
- `Recipe Name` or `Name`
- `Slug` (URL-friendly)
- `Thumbnail Image` or `Thumbnail` (URL to image)

Optional fields:
- `Ingredients`
- `Instructions`
- `Prep Time`
- `Cook Time`

## 🔄 Workflow Options

### Current Workflow (CSV-based)
```
CSV files → Python scripts → HTML pages → Git commit
```

### With Airtable (Available Now!)
```
Airtable → airtable_sync.py → Python scripts → HTML pages → Git commit
```

### Benefits of Airtable Integration
- ✅ Edit content in a nice UI (no CSV editing)
- ✅ Collaborate with team members
- ✅ Add images via Airtable
- ✅ Organize with filters/views
- ✅ Track changes with revisions
- ✅ One-command sync and regenerate

## 🚀 Next Steps

1. Find your Airtable Base ID (see Step 1 above)
2. Update `airtable_config.json` with your Base ID
3. Run `python3 airtable_sync.py` to test
4. Let me know if you want to integrate this into the page generation workflow!

## 📝 Notes

- Your Airtable token is already configured ✅
- `airtable_config.json` is gitignored (secure) 🔒
- The script can handle multiple variants per product
- Images must be publicly accessible URLs

