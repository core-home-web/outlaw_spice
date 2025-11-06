#!/usr/bin/env python3
"""
Add Google Analytics tag to all HTML files
"""
import os
import re
from pathlib import Path

# Google Analytics tag to insert
GOOGLE_TAG = '''<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-LXRS43EWS6"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-LXRS43EWS6');
</script>
'''

def add_google_tag_to_file(file_path):
    """Add Google Analytics tag to an HTML file if not already present"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if tag already exists
        if 'G-LXRS43EWS6' in content:
            print(f"⏭️  Skipping {file_path} - Google tag already exists")
            return False
        
        # Find <head> tag and insert Google tag immediately after it
        # Pattern: <head> or <head followed by whitespace/newline
        pattern = r'(<head[^>]*>)'
        replacement = r'\1\n' + GOOGLE_TAG
        
        new_content = re.sub(pattern, replacement, content, count=1, flags=re.IGNORECASE)
        
        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"✅ Added Google tag to {file_path}")
            return True
        else:
            print(f"⚠️  Could not find <head> tag in {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False

def main():
    """Find all HTML files and add Google Analytics tag"""
    root_dir = Path('.')
    
    # Directories to process (skip deploy_to_cloudflare)
    html_files = []
    
    # Root directory HTML files
    for html_file in root_dir.glob('*.html'):
        html_files.append(html_file)
    
    # Products directory
    products_dir = root_dir / 'products'
    if products_dir.exists():
        for html_file in products_dir.glob('*.html'):
            html_files.append(html_file)
    
    # Recipes directory
    recipes_dir = root_dir / 'recipes'
    if recipes_dir.exists():
        for html_file in recipes_dir.glob('*.html'):
            html_files.append(html_file)
    
    print(f"Found {len(html_files)} HTML files to process\n")
    
    updated_count = 0
    for html_file in sorted(html_files):
        if add_google_tag_to_file(html_file):
            updated_count += 1
    
    print(f"\n✨ Complete! Updated {updated_count} files")

if __name__ == '__main__':
    main()

