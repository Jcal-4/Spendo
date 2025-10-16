# Integrating OpenAI ChatKit with Django Backend

This guide documents the steps taken to connect OpenAI ChatKit to a Django backend and resolve common integration issues.

## 1. Install Required Python Packages

Install the `requests` library to make HTTP requests to the OpenAI ChatKit REST API:

```bash
pip install requests
```

Add `requests` to your `requirements.txt` if using Docker or a requirements file:

```
requests
```

## 2. Django Backend Endpoint for ChatKit Session

Create a Django API endpoint to generate a ChatKit session and return a client secret. Example code:

```python
import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['POST'])
def create_chatkit_session(request):
    openai_api_key = os.getenv('OPENAI_API_KEY')
    workflow_id = 'wf_68ee92d551ac819096e06e9789e4accf05c17f1103e9f72d'  # Replace with your workflow ID
    url = "https://api.openai.com/v1/chatkit/sessions"
    headers = {
        "Authorization": f"Bearer {openai_api_key}",
        "Content-Type": "application/json",
        "OpenAI-Beta": "chatkit_beta=v1"
    }
    # Use authenticated user's username if available, otherwise use a placeholder
    user_id = request.user.username if request.user and request.user.is_authenticated else "anonymous"
    data = {
        "workflow": { "id": workflow_id },
        "user": user_id,
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        client_secret = response.json().get("client_secret")
        return Response({"client_secret": client_secret})
    else:
        print("ChatKit session creation error:", response.text)
        return Response({"error": response.text}, status=response.status_code)
```

## 3. Common Errors and Solutions

### a. 500 Internal Server Error / ModuleNotFoundError

- **Error:** `No module named 'requests'`
- **Solution:** Install the `requests` package.

### b. 400 Bad Request: Missing Required Parameters

- **Error:** `Missing required parameter: 'workflow'.`
- **Solution:** Pass the workflow as an object: `{ "workflow": { "id": workflow_id } }`
- **Error:** `Missing required parameter: 'user'.`
- **Solution:** Pass the user parameter: `{ "user": user_id }`
- **Error:** `Invalid type for 'workflow': expected an object, but got a string instead.`
- **Solution:** See above for correct format.

### c. 400 Bad Request: Missing Beta Header

- **Error:** `You must provide the 'OpenAI-Beta' header to access the Chatkit API.`
- **Solution:** Add header: `"OpenAI-Beta": "chatkit_beta=v1"`

### d. 401 Unauthorized

- **Error:** Unauthorized from OpenAI API.
- **Solution:** Ensure your `OPENAI_API_KEY` is valid and has ChatKit access.

### e. net::ERR_EMPTY_RESPONSE

- **Error:** Backend not responding.
- **Solution:** Check backend logs for errors and ensure the endpoint is reachable.

## 4. Environment Variables

Set the following environment variables in your backend:

- `OPENAI_API_KEY`: Your OpenAI API key
- `OPENAI_WORKFLOW_ID`: Your ChatKit workflow ID (if not hardcoded)

## 5. Frontend Endpoint Usage

Ensure your frontend POSTs to the correct endpoint with a trailing slash:

```
http://localhost:8000/api/api/chatkit/session/
```

## 6. Debugging

Check backend logs for error messages printed from the ChatKit session creation response. Use these messages to resolve any issues with parameters or authentication.

---

**This document summarizes the integration and troubleshooting steps for connecting OpenAI ChatKit to a Django backend.**
