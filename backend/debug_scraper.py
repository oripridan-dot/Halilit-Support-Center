
import requests
from bs4 import BeautifulSoup
import sys

url = "https://www.halilit.com/23648-synth"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
}

try:
    res = requests.get(url, headers=headers, timeout=10)
    print(f"Status Code: {res.status_code}")
    
    soup = BeautifulSoup(res.text, 'html.parser')
    product_nodes = soup.select('.layout_list_item')
    
    print(f"Found {len(product_nodes)} products")
    
    if product_nodes:
        node = product_nodes[0]
        price_container = node.select_one('.price')
        
        print("\n--- Product 1 Price Container HTML ---")
        if price_container:
            print(price_container.prettify())
        else:
            print("No .price container found")
            
        print("\n--- Full Node Snippet ---")
        print(str(node)[:1000])

except Exception as e:
    print(e)
