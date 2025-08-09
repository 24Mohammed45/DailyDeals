import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template_string

app = Flask(__name__)

MARKUP_PERCENT = 0.35  # 35% markup

def scrape_deals():
    url = 'https://www.onedayonly.co.za/today-only'
    headers = {'User-Agent': 'Mozilla/5.0'}
    resp = requests.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, 'html.parser')

    products = []
    items = soup.select('div.product-tile')

    for item in items:
        title_tag = item.select_one('h2.product-name a')
        price_tag = item.select_one('.price .value')
        img_tag = item.select_one('img.product-image-photo')

        if not title_tag or not price_tag or not img_tag:
            continue

        title = title_tag.get_text(strip=True)
        link = title_tag['href']
        image = img_tag['src']

        price_text = price_tag.get_text(strip=True).replace('R', '').replace(' ', '').replace(',', '')
        try:
            price = float(price_text)
        except:
            continue

        new_price = round(price * (1 + MARKUP_PERCENT), 2)
        products.append({
            'title': title,
            'price': f'R{new_price:.2f}',
            'image': image,
            'link': link
        })

    return products

@app.route('/')
def home():
    products = scrape_deals()
    html = '''
    <html>
    <head><title>DailyDeals - Today Only</title></head>
    <body>
    <h1>DailyDeals - OneDayOnly Products with 35% Markup</h1>
    <div style="display:flex; flex-wrap: wrap;">
    {% for p in products %}
        <div style="border:1px solid #ccc; margin:10px; width:200px; padding:10px;">
            <a href="{{ p.link }}" target="_blank">
                <img src="{{ p.image }}" style="width:100%; height:auto;">
                <h3>{{ p.title }}</h3>
                <p><strong>{{ p.price }}</strong></p>
            </a>
        </div>
    {% endfor %}
    </div>
    </body>
    </html>
    '''
    return render_template_string(html, products=products)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
Flask==3.0.3
requests==2.32.3
beautifulsoup4==4.12.3
services:
  - type: web
    name: dailydeals
    env: python
    buildCommand: ""
    startCommand: "python app.py"
    plan: free
