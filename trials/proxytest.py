# %%
import json
import os
import re
# import subprocess
import markdown
from flask import Flask, url_for, request, Response , render_template , make_response
import requests 
app = Flask(__name__)

SITE_NAME = 'http://gov.uk/'

from flask import Flask, request, Response
import requests

app = Flask(__name__)

# URL of the third-party site
TARGET_URL = 'http://gov.uk/'  # Replace with the desired URL

@app.route('/proxy/', defaults={'path': ''}, methods=['GET', 'POST'])
@app.route('/proxy/<path:path>', methods=['GET','POST','DELETE'])
def proxy(path):
    # Construct the URL to the third-party site
    target_url = f"{request.path}"
    target_url = target_url[7:]
    # Forward request headers and data as needed
    headers = {key: value for key, value in request.headers if key != 'Host'}
    if request.method == 'POST':
        resp = requests.post(target_url, headers=headers, data=request.get_data(), cookies=request.cookies)
    else:
        resp = requests.get(target_url)

    # Modify headers to allow embedding
    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]
    headers.append(('x-frame-options', 'ALLOWALL'))
    headers.append(('content-security-policy', ''))

    # Return the response to the client
    return Response(resp.content, resp.status_code, headers)

if __name__ == '__main__':
    app.run(port=5000)
