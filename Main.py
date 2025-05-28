from flask import Flask, request, abort, Response
import requests
import os

app = Flask(__name__)

# Get VPS target URL from environment variable
# Example: "http://your_vps_ip:your_vps_port"
VPS_TARGET_URL = os.environ.get("VPS_TARGET_URL")

if not VPS_TARGET_URL:
    print("Error: VPS_TARGET_URL environment variable not set.")
    exit(1)

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD'])
def proxy(path):
    try:
        # Construct the full URL for the VPS
        vps_url = f"{VPS_TARGET_URL}/{path}"
        if request.query_string:
            vps_url += f"?{request.query_string.decode('utf-8')}"

        # Prepare headers to forward
        headers = {key: value for key, value in request.headers if key.lower() not in ['host', 'x-forwarded-for', 'x-cloud-trace-context', 'traceparent', 'user-agent']}
        headers['X-Forwarded-For'] = request.remote_addr # Add client IP

        # Forward the request to the VPS
        resp = requests.request(
            method=request.method,
            url=vps_url,
            headers=headers,
            data=request.get_data(),
            stream=True,  # Stream the response to handle large files
            allow_redirects=False # Generally, let the client handle redirects from the proxy
        )

        # Create a Flask response from the VPS response
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        resp_headers = [(name, value) for name, value in resp.raw.headers.items() if name.lower() not in excluded_headers]

        return Response(resp.raw.read(), resp.status_code, resp_headers)

    except requests.exceptions.RequestException as e:
        print(f"Error forwarding request to VPS: {e}")
        abort(502, description="Bad Gateway: Could not connect to the VPS.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        abort(500, description="Internal Server Error.")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
  
