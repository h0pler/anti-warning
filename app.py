from flask import Flask, render_template, request, jsonify, redirect, make_response
from bs4 import BeautifulSoup
import requests
import urllib.parse

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/proxy', methods=['GET'])
def proxy():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'URL is required'})

    try:
        if not url.startswith(('http://', 'https://')):
            base_url = request.host_url
            parsed_url = urllib.parse.urljoin(base_url, url)
        else:
            parsed_url = url
    
        response = requests.get(parsed_url)
        proxy_url = request.base_url
        response = modify_html(response, parsed_url)
        return response.content
    except requests.RequestException as e:
        return jsonify({'error': str(e)})

@app.route('/reset', methods=['GET'])
def reset():
    response = make_response(redirect('/'))
    response.set_cookie('base_url', '', expires=0)
    return response

def modify_html(response, origin_url):
    soup = BeautifulSoup(response.content, 'html.parser')
    for tag in soup.find_all(['a', 'link', 'form', 'img', 'input'], href=True):
        if tag.name == 'img' and tag.get('src'):
            if not tag['src'].startswith(('http://', 'https://')):
                src = tag.get('src')
                tag['src'] = urllib.parse.urljoin(origin_url+"/"+src, tag['src'])

        # elif not tag['href'].startswith(('http://', 'https://')):
        #     tag['src'] = urllib.parse.urljoin(origin_url+"/"+src, tag['src'])

    # Uncomment to modify form actions
    # for form in soup.find_all('form'):
    #     action = form.get('action')
    #     if action:
    #         form['action'] = urllib.parse.urljoin(proxy_url, action)

    response._content = str(soup)
    return response

if __name__ == '__main__':
    app.run(debug=True)
