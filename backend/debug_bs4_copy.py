from bs4 import BeautifulSoup
import copy
import re

html = """
<span class="price center-price-in-grid text-center">
 <span class="items_show_price_text" style="display: none;">
  מחיר
 </span>
 367 ₪
 <div class="show_eilat_price">
  <span class="items_show_eilat_price_text">
   מחיר באילת
  </span>
  <span class="items_show_eilat_price_price">
   311 ₪
  </span>
 </div>
</span>
"""

soup = BeautifulSoup(html, 'html.parser')
price_container = soup.select_one('.price')

print("--- Original ---")
print(price_container.prettify())

print("\n--- Cloning and cleaning ---")
container_clone = copy.copy(price_container)

for bad_child in container_clone.select('.show_eilat_price, .items_show_price_text, .old-price, strike, del'):
    print(f"Decomposing: {bad_child.name} class={bad_child.get('class')}")
    bad_child.decompose()

print("\n--- Clone Result ---")
print(container_clone.prettify())
print(f"Clone Text: '{container_clone.get_text(strip=True)}'")

def _parse_price_text(text: str):
    if not text: return None
    try:
        clean = re.sub(r'[^\d.]', '', text.replace(',', ''))
        val = float(clean)
        return val if val > 0 else None
    except:
        return None

price = _parse_price_text(container_clone.get_text())
print(f"Parsed Price: {price}")
