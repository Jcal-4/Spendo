# Complete OpenAI ChatKit Integration Guide

This guide documents the complete setup for integrating OpenAI ChatKit with both Django backend and React frontend, including all necessary configuration and troubleshooting steps.

## 1. Backend Setup

### 1.1 Install Required Python Packages

Install the `requests` library to make HTTP requests to the OpenAI ChatKit REST API:

```bash
pip install requests
```

Add `requests` to your `requirements.txt` if using Docker or a requirements file:

```
requests
```

### 1.2 Django Backend Endpoint for ChatKit Session

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

### 1.3 Django URL Configuration

Add the ChatKit endpoint to your Django URLs:

```python
# In your api/urls.py
from .views import create_chatkit_session

urlpatterns = [
    # ... other patterns
    path('chatkit/session/', create_chatkit_session, name='create_chatkit_session'),
]
```

## 2. Frontend Setup

### 2.1 Install Frontend Dependencies

Install the OpenAI ChatKit React package:

```bash
npm install @openai/chatkit-react
```

### 2.2 HTML Configuration

Add the required meta tag and script to your `index.html`:

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <!-- OpenAI ChatKit domain verification -->
    <meta name="openai-domain-verify" content="your_domain_verification_key" />
    <script src="https://cdn.platform.openai.com/deployments/chatkit/chatkit.js" async></script>
    <!-- ... other head content -->
  </head>
  <!-- ... rest of HTML -->
</html>
```

**Important:** Replace `your_domain_verification_key` with your actual domain verification key from OpenAI.

### 2.3 Environment Variables

Create a `.env` file in your frontend root directory:

```env
VITE_API_URL=http://localhost:8000/api
```

For production, update the URL to your production backend URL.

### 2.4 React Component Implementation

Create a ChatKit component (`MyChat.tsx`):

```tsx
import { ChatKit, useChatKit } from '@openai/chatkit-react';

const apiUrl = import.meta.env.VITE_API_URL;

export function MyChat() {
  // Utility to get cookie value for CSRF protection
  function getCookie(name: string) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop()?.split(';').shift();
  }
  
  const { control } = useChatKit({
    api: {
      async getClientSecret(existing) {
        const csrftoken = getCookie('csrftoken');
        if (existing) {
          // implement session refresh if needed
        }

        const res = await fetch(`${apiUrl}/chatkit/session/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken || '',
          },
        });
        const { client_secret } = await res.json();
        return client_secret;
      },
    },
  });

  return <ChatKit control={control} className="min-h-[500px] w-[400px]" />;
}

export default MyChat;
```

### 2.5 Component Integration

Use the ChatKit component in your main application:

```tsx
import MyChat from './components/chatbot/MyChat';

function App() {
  return (
    <div>
      {/* Your other components */}
      <MyChat />
    </div>
  );
}
```

## 3. Common Errors and Solutions

### 3.1 Backend Errors

#### a. 500 Internal Server Error / ModuleNotFoundError

- **Error:** `No module named 'requests'`
- **Solution:** Install the `requests` package.

#### b. 400 Bad Request: Missing Required Parameters

- **Error:** `Missing required parameter: 'workflow'.`
- **Solution:** Pass the workflow as an object: `{ "workflow": { "id": workflow_id } }`
- **Error:** `Missing required parameter: 'user'.`
- **Solution:** Pass the user parameter: `{ "user": user_id }`
- **Error:** `Invalid type for 'workflow': expected an object, but got a string instead.`
- **Solution:** See above for correct format.

#### c. 400 Bad Request: Missing Beta Header

- **Error:** `You must provide the 'OpenAI-Beta' header to access the Chatkit API.`
- **Solution:** Add header: `"OpenAI-Beta": "chatkit_beta=v1"`

#### d. 401 Unauthorized

- **Error:** Unauthorized from OpenAI API.
- **Solution:** Ensure your `OPENAI_API_KEY` is valid and has ChatKit access.

#### e. net::ERR_EMPTY_RESPONSE

- **Error:** Backend not responding.
- **Solution:** Check backend logs for errors and ensure the endpoint is reachable.

### 3.2 Frontend Errors

#### a. Module Not Found Error

- **Error:** `Module not found: Can't resolve '@openai/chatkit-react'`
- **Solution:** Install the package: `npm install @openai/chatkit-react`

#### b. CORS Errors

- **Error:** `Access to fetch at 'http://localhost:8000/api/chatkit/session/' from origin 'http://localhost:5173' has been blocked by CORS policy`
- **Solution:** Ensure CORS is properly configured in Django settings:
  ```python
  CORS_ALLOWED_ORIGINS = [
      "http://localhost:5173",  # Your frontend URL
  ]
  CORS_ALLOW_CREDENTIALS = True
  ```

#### c. CSRF Token Errors

- **Error:** `CSRF token missing or incorrect`
- **Solution:** Ensure CSRF token is included in requests and CSRF middleware is enabled in Django.

#### d. Environment Variable Not Found

- **Error:** `VITE_API_URL is not defined`
- **Solution:** Create a `.env` file with `VITE_API_URL=http://localhost:8000/api`

#### e. Domain Verification Error

- **Error:** `Domain verification failed`
- **Solution:** Ensure the correct domain verification key is in your HTML meta tag.

## 4. Environment Variables

### 4.1 Backend Environment Variables

Set the following environment variables in your backend:

- `OPENAI_API_KEY`: Your OpenAI API key
- `OPENAI_WORKFLOW_ID`: Your ChatKit workflow ID (if not hardcoded)

### 4.2 Frontend Environment Variables

Create a `.env` file in your frontend root directory:

```env
VITE_API_URL=http://localhost:8000/api
```

For production, update the URL to your production backend URL.

## 5. Complete Integration Checklist

### 5.1 Backend Checklist

- [ ] Install `requests` package
- [ ] Create ChatKit session endpoint
- [ ] Add URL routing for the endpoint
- [ ] Set environment variables (`OPENAI_API_KEY`, `OPENAI_WORKFLOW_ID`)
- [ ] Configure CORS settings
- [ ] Test endpoint with Postman/curl

### 5.2 Frontend Checklist

- [ ] Install `@openai/chatkit-react` package
- [ ] Add domain verification meta tag to HTML
- [ ] Add ChatKit script to HTML
- [ ] Create `.env` file with `VITE_API_URL`
- [ ] Implement ChatKit React component
- [ ] Add CSRF token handling
- [ ] Integrate component into your app
- [ ] Test the complete flow

## 6. Testing the Integration

### 6.1 Backend Testing

Test your backend endpoint:

```bash
curl -X POST http://localhost:8000/api/chatkit/session/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: your_csrf_token"
```

### 6.2 Frontend Testing

1. Start your frontend development server
2. Navigate to the page with the ChatKit component
3. Check browser console for any errors
4. Verify the chat interface loads correctly

## 7. Production Deployment

### 7.1 Backend Deployment

- Ensure all environment variables are set in production
- Configure CORS for your production domain
- Test the endpoint in production environment

### 7.2 Frontend Deployment

- Update `VITE_API_URL` to production backend URL
- Ensure domain verification key is correct for production domain
- Test the complete integration in production

## 8. Debugging

### 8.1 Backend Debugging

Check backend logs for error messages printed from the ChatKit session creation response. Use these messages to resolve any issues with parameters or authentication.

### 8.2 Frontend Debugging

- Check browser developer tools console for errors
- Verify network requests are being made correctly
- Ensure CSRF tokens are being sent properly
- Check that environment variables are loaded correctly

---

**This document provides a complete guide for integrating OpenAI ChatKit with both Django backend and React frontend, including all necessary setup steps, configuration, and troubleshooting.**
