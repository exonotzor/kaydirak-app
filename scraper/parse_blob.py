import re
import json

with open("scraper/amazon_deals_blob.js", "r", encoding="utf-8") as f:
    content = f.read()

# Let's search for JSON data in window.Globals or JSON.parse or similar
match = re.search(r'data\s*=\s*(\{.*?\});\s*(?:window|return|\n)', content, re.DOTALL)
if not match:
    # let's look for {"dealDetails"
    print("Searching for raw JSON blocks...")
    # Find all occurrences of "dealDetails"
    positions = [m.start() for m in re.finditer(r'\{[^{}]*"dealDetails"', content)]
    print(f"Found {len(positions)} dealDetails occurrences")
else:
    print("Found data = {...}")

# Let's inspect around position 22000
idx = content.find('"dealDetails"')
if idx != -1:
    print("Context around dealDetails:")
    start = max(0, idx - 400)
    end = min(len(content), idx + 600)
    print(content[start:end])
