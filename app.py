from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse, urljoin
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "This is the vendor search app"

def google_search(query, num_results, api_key, cse_id):
    api_key = os.getenv('GOOGLE_API_KEY')
    cse_id = os.getenv('GOOGLE_CSE_ID')
    blacklist = ['eventbrite.com', 'reddit.com', 'tiktok.com', 'instagram.com',
                 'classpop.com', 'classbento.com', 'giftory.com', 'yelp.com','coursehorse.com']
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'key': api_key,
        'cx': cse_id,
        'q': query,
        'num': 10  # Maximum allowed per request by Google
    }
    urls = []
    start = 1  # Start at the first result
    while len(urls) < num_results:
        params['start'] = start
        response = requests.get(url, params=params)
        response.raise_for_status()
        search_results = response.json()

        for item in search_results.get('items', []):
            parsed_url = urlparse(item['link'])
            root_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            if not any(domain in root_url for domain in blacklist) and root_url not in urls:
                urls.append(root_url)
                if len(urls) >= num_results:
                    return urls
        start += 10  # Proceed to the next set of results
    return urls

def find_emails(url):
    subpages = ['', 'contact', 'contact-us', 'about', 'about-us']
    found_emails = set()
    for subpage in subpages:
        full_url = urljoin(url, subpage)
        try:
            response = requests.get(full_url, timeout=5)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b', soup.get_text(), re.IGNORECASE)
            found_emails.update(emails)
            if len(found_emails) >= 5:
                return list(found_emails)[:5]
        except Exception as e:
            continue
    return list(found_emails)[:5]

@app.route('/trigger_search', methods=['POST'])
def trigger_search():
    # Get data from the webhook payload
    data = request.json
    query = data.get('query')
    num_results = data.get('num_results')
 
    # Perform the search
    if query and num_results:
        urls = google_search(query, num_results, api_key, cse_id)
        results = []
        for url in urls:
            emails = find_emails(url)
            results.append({'url': url, 'emails': emails})
        return jsonify(results), 200
    else:
        return jsonify({'error': 'Missing data'}), 400

if __name__ == '__main__':
    app.run(debug=True, port=int(os.environ.get("PORT", 5000)))