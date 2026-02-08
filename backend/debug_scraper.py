import requests
from bs4 import BeautifulSoup

url = "https://www.halilit.com/search?q=Nord"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}
resp = requests.get(url, headers=headers)
print(f"Status: {resp.status_code}")
soup = BeautifulSoup(resp.text, 'html.parser')
items = soup.select(".box, .item, .product_item, .product_box")
print(f"Items found: {len(items)}")

if items:
    print("First Item HTML:")
    print(items[0].prettify())
