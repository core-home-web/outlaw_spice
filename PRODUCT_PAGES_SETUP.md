# Product Pages Setup Guide

## ✅ What's Working Now

Your product pages are now fully functional with:
- ✅ Main product images displaying
- ✅ Product descriptions in accordion sections
- ✅ Ingredients sections (ready for when you add them)
- ✅ Fallback text for missing data
- ✅ All CSS and JS properly linked

## 📸 Image System

The system now supports **two image workflows**:

### Current (Working Now)
Your existing `.avif` images from Airtable's `Main Variant Image` field are being used for:
- Homepage slider
- Product detail hero images

### Enhanced (When You Add New Fields)
When you add these fields to Airtable, they'll automatically be used:

1. **Transparent Product Image** - For slider/overlays (transparent PNG/AVIF)
2. **Main Product Image** - For product page hero (with background)
3. **More Images 1-3** - For bottom gallery (3 lifestyle shots)

## 🚀 Next Steps to Complete Product Pages

### Step 1: Add New Fields to Airtable

Go to your Products table and add these columns:

| Field Name | Type | Purpose | Example |
|------------|------|---------|---------|
| Transparent Product Image | Single line text | Slider image (transparent) | https://cdn.../bottle-transparent.avif |
| Main Product Image | Single line text | Product hero (with background) | https://cdn.../bottle-hero-smoky.avif |
| More Images 1 | Single line text | Gallery image 1 | https://cdn.../ingredients-1.jpg |
| More Images 2 | Single line text | Gallery image 2 | https://cdn.../lifestyle-1.jpg |
| More Images 3 | Single line text | Gallery image 3 | https://cdn.../cooking-scene.jpg |
| Product Ingredients | Long text | Ingredients list | Paprika, Brown Sugar, Garlic... |

### Step 2: Upload Your Product Images

You have local images in `images/Outlaw_Spice_Product_Photos/`. You need to:

1. **Upload to Webflow Assets** (or Cloudflare)
   - Upload your `.avif` files to get public URLs
   - Get the URLs for each image

2. **Add URLs to Airtable**
   - Paste the image URLs into the corresponding fields
   - Example: `https://cdn.prod.website-files.com/.../49771_01.avif`

### Step 3: Sync & Deploy

Once images are in Airtable:

```bash
# Sync latest data from Airtable
./sync_from_airtable.sh

# Review changes
git status

# Commit and push
git add -A
git commit -m "Add product images and descriptions from Airtable"
git push
```

## 📖 How the Image System Works

```
Airtable Field Priority (Slider):
└─ Transparent Product Image (preferred)
   └─ Main Variant Image (fallback)

Airtable Field Priority (Product Page):
└─ Main Product Image (hero)
   └─ Transparent Product Image (fallback)
      └─ Main Variant Image (fallback)

Gallery Images:
└─ More Images 1, 2, 3 (in order)
```

## 🎨 Matching Your Webflow Design

Your product pages now match the structure from:
`https://outlaw-spice.webflow.io/product/where-theres-hickory-smoke`

Structure:
```
[ Main Hero Image ] ← Main Product Image
      |
      v
[ Product Name + Price ]
      |
      v
[ 3 Gallery Images ] ← More Images 1, 2, 3
      |
      v
[ Description Accordion ] ← Product Description
[ Ingredients Accordion ] ← Product Ingredients
```

## 🐛 Troubleshooting

**Black screen / No images?**
- Check that image URLs in Airtable are publicly accessible
- Verify URLs end in `.avif`, `.jpg`, or `.png`
- Run `./sync_from_airtable.sh` after updating Airtable

**Descriptions not showing?**
- Make sure `Product Description` field exists in Airtable
- Check that descriptions have actual text content
- Sync again with `./sync_from_airtable.sh`

**Styling looks wrong?**
- Product pages use relative paths: `../css/`, `../images/`
- This is correct for pages in `products/` subdirectory
- Don't change these paths!

## 📝 Example Product Entry

Here's a complete product entry in Airtable:

```
Product Name: Roadhouse Rub
Product Handle: roadhouse-rub
Transparent Product Image: https://cdn.../49771_01.avif
Main Product Image: https://cdn.../49771_hero.avif
More Images 1: https://cdn.../ingredients-bowl.jpg
More Images 2: https://cdn.../grilling-scene.jpg
More Images 3: https://cdn.../spice-closeup.jpg
Product Description: A smoky blend of paprika and brown sugar...
Product Ingredients: Paprika, Brown Sugar, Garlic Powder, Onion...
Variant Price: $11.12
Variant Compare-at Price: $22.22
```

## 💡 Pro Tips

1. **Image Specs** (for best results):
   - Transparent images: 500x500px AVIF with transparency
   - Hero images: 1000x1000px AVIF/JPG
   - Gallery images: 800x600px JPG

2. **Webflow Upload**:
   - Upload to Webflow Assets
   - Copy the CDN URL (starts with `https://cdn.prod.website-files.com/`)
   - Paste into Airtable

3. **Quick Test**:
   - Add images to just ONE product first
   - Sync and test
   - Once working, add to all products

---

Need help? Check `AIRTABLE_PRODUCT_FIELDS.md` for detailed field reference.

