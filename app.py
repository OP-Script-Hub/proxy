import requests
from flask import Flask, request, Response
import os

app = Flask(__name__)

# Load proxy target from environment variable for flexibility and security
TARGET_SERVER = os.getenv("TARGET_SERVER", "http://127.0.0.1:9999")


@app.before_request
def proxy_request():
    target_url = f"{TARGET_SERVER}{request.path}"
    
    try:
        response = requests.request(
            method=request.method,
            url=target_url,
            headers={key: value for key, value in request.headers if key != 'Host'},
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False,
        )
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for name, value in response.raw.headers.items()
                   if name.lower() not in excluded_headers]
        return Response(response.content, response.status_code, headers)
    except requests.exceptions.RequestException as e:
        return Response(f"Proxy error: {e}", status=502)

if __name__ == "__main__":
    app.run(debug=True)
