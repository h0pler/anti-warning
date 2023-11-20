from flask import Flask, request, jsonify, render_template, make_response
import requests

app = Flask(__name__)

@app.route('/proxy', methods=['GET'])
def proxy():
    url = request.args.get('url')
    query = request.query_string.decode('utf-8')  # 클라이언트가 보낸 쿼리 문자열 가져오기
    if query:
        url += '?' + query  # 원래 URL에 클라이언트 쿼리 추가

    if not url:
        return jsonify({'error': 'NO URL PROVIDED'})

    try:
        response = requests.get(url)
        content_type = response.headers.get('content-type')
        
        # 리소스 타입에 따라 다른 처리
        if content_type.startswith('text/css'):
            proxy_response = make_response(response.content)
            proxy_response.headers['Content-Type'] = 'text/css'
            return proxy_response
        elif content_type.startswith('image'):
            proxy_response = make_response(response.content)
            proxy_response.headers['Content-Type'] = content_type
            return proxy_response
        else:
            return response.content

    except requests.RequestException as e:
        return jsonify({'error': str(e)})

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
