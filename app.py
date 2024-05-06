from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse, urljoin
import os

api_key = os.getenv('GOOGLE_API_KEY') 
cse_id =  os.getenv('GOOGLE_CSE_ID')

if not api_key or not cse_id:
    raise ValueError("API key or CSE ID not set. Check your environment variables.")

print("api key value:",api_key)
print(type(api_key))

print("cse:",cse_id)
print(type(cse_id))

app = Flask(__name__)

@app.route('/')
def home():
    return "This is the vendor search app"

def google_search(query, num_results, api_key, cse_id):
    blacklist = ['eventbrite.com', 'reddit.com', 'tiktok.com', 'instagram.com','timeout.com',
                'linkedin.com','classpop.com', 'classbento.com', 'giftory.com', 'yelp.com',
                'coursehorse.com']
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

    response = requests.get(url, params=params)
    print(f"Requesting: {response.url}")  # Print the full URL requested
    response.raise_for_status()  # This will raise an exception for HTTP errors

    return response.json()
def find_emails(url):
    found_emails = set()
    try:
        main_response = requests.get(url, timeout=5)
        main_response.raise_for_status()  # Check if the main URL is accessible
        soup = BeautifulSoup(main_response.text, 'html.parser')
        # Look for common subpages directly linked from the homepage
        subpages = [link.get('href') for link in soup.find_all('a') if 'contact' in link.get('href', '').lower() or 'about' in link.get('href', '').lower()]
        subpages = set(subpages)  # Remove duplicates
        subpages.add('')  # Include the main page too
    except requests.exceptions.RequestException as e:
        print(f"Error fetching or parsing main page {url}: {e}")
        return list(found_emails)[:5]

    for subpage in subpages:
        full_url = urljoin(url, subpage)
        try:
            response = requests.get(full_url, timeout=5)
            response.raise_for_status()
            sub_soup = BeautifulSoup(response.text, 'html.parser')
            emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b', sub_soup.get_text(), re.IGNORECASE)
            found_emails.update(emails)
            if len(found_emails) >= 5:
                return list(found_emails)[:5]
        except requests.exceptions.RequestException as e:
            print(f"Error fetching or parsing {full_url}: {e}")
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
        try:
            num_results = int(num_results)  # Convert num_results to an integer
        except ValueError:
            return jsonify({'error': 'num_results must be an integer'}), 400
        print(query)
        print(num_results)
        urls = google_search(query, num_results, api_key, cse_id)
        results = []
        url_list = []
        email_list = []
        for url in urls:
            emails = find_emails(url)
            if emails:
                email_list.extend(emails)
                url_list.append(url)
            results.append({'url': url, 'emails': emails})
        return jsonify({'urls':url_list,'emails':email_list}), 200
    else:
        return jsonify({'error': 'Missing data'}), 400

if __name__ == '__main__':
    # app.run(debug=True, port=int(os.environ.get("PORT", 5000)))
    app.run(host='0.0.0.0', port=5000)
