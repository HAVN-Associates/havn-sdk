"""
Example 05: Auth Login via Webhook

This example demonstrates how to login users from SaaS company to HAVN
via webhook authentication.

Flow:
1. User clicks "Login to HAVN" button in SaaS company app
2. SaaS company calls client.auth.login(email)
3. HAVN validates user and generates temporary token
4. HAVN returns redirect URL
5. SaaS company redirects user's browser to URL
6. HAVN frontend auto-logins user with token
"""

import os
from dotenv import load_dotenv
from havn import HAVNClient, HAVNAPIError, HAVNAuthError

# Load environment variables
load_dotenv()

# Initialize client
client = HAVNClient(
    api_key=os.getenv("HAVN_API_KEY"),
    webhook_secret=os.getenv("HAVN_WEBHOOK_SECRET"),
    base_url=os.getenv("HAVN_BASE_URL", "https://api.havn.com"),
)


def login_user_to_havn(email: str):
    """
    Login user to HAVN via webhook

    Args:
        email: User email address

    Returns:
        Redirect URL string
    """
    try:
        print(f"\n🔐 Logging in user: {email}")

        # Call login webhook
        redirect_url = client.auth.login(email=email)

        print(f"✅ Login successful!")
        print(f"📍 Redirect URL: {redirect_url}")
        print(f"\n💡 Redirect user's browser to this URL:")
        print(f"   {redirect_url}")

        return redirect_url

    except HAVNAuthError as e:
        print(f"❌ Authentication failed: {e.message}")
        print(f"   Check your API key and webhook secret")
        return None

    except HAVNAPIError as e:
        print(f"❌ Login failed: {e.message}")
        if e.status_code == 404:
            print(f"   User not found. Sync user first with client.users.sync()")
        elif e.status_code == 400:
            print(f"   User is inactive. Contact HAVN admin to activate.")
        return None

    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return None


# =============================================================================
# EXAMPLE USAGE IN DIFFERENT FRAMEWORKS
# =============================================================================


def flask_example():
    """Example usage in Flask"""
    print("\n" + "=" * 60)
    print("Flask Example")
    print("=" * 60)

    code = '''
from flask import Flask, redirect, request
from havn import HAVNClient

app = Flask(__name__)
client = HAVNClient(api_key="...", webhook_secret="...")

@app.route('/login-to-havn')
def login_to_havn():
    """Redirect user to HAVN"""
    user_email = request.args.get('email')
    
    try:
        redirect_url = client.auth.login(email=user_email)
        return redirect(redirect_url)
    except Exception as e:
        return f"Login failed: {str(e)}", 400
'''
    print(code)


def django_example():
    """Example usage in Django"""
    print("\n" + "=" * 60)
    print("Django Example")
    print("=" * 60)

    code = '''
from django.http import HttpResponseRedirect
from django.shortcuts import render
from havn import HAVNClient

client = HAVNClient(api_key="...", webhook_secret="...")

def login_to_havn(request):
    """Redirect user to HAVN"""
    user_email = request.GET.get('email')
    
    try:
        redirect_url = client.auth.login(email=user_email)
        return HttpResponseRedirect(redirect_url)
    except Exception as e:
        return render(request, 'error.html', {'error': str(e)})
'''
    print(code)


def fastapi_example():
    """Example usage in FastAPI"""
    print("\n" + "=" * 60)
    print("FastAPI Example")
    print("=" * 60)

    code = '''
from fastapi import FastAPI, Query
from fastapi.responses import RedirectResponse
from havn import HAVNClient

app = FastAPI()
client = HAVNClient(api_key="...", webhook_secret="...")

@app.get("/login-to-havn")
async def login_to_havn(email: str = Query(...)):
    """Redirect user to HAVN"""
    try:
        redirect_url = client.auth.login(email=email)
        return RedirectResponse(url=redirect_url)
    except Exception as e:
        return {"error": str(e)}
'''
    print(code)


# =============================================================================
# RUN EXAMPLES
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("HAVN SDK - Auth Login Example")
    print("=" * 60)

    # Example 1: Login existing user
    redirect_url = login_user_to_havn(email="user@example.com")

    # Example 2: Login with validation error
    print("\n" + "-" * 60)
    print("Example: Invalid email")
    print("-" * 60)
    try:
        client.auth.login(email="invalid-email")
    except Exception as e:
        print(f"✅ Validation caught: {str(e)}")

    # Show framework examples
    flask_example()
    django_example()
    fastapi_example()

    print("\n" + "=" * 60)
    print("✅ Examples completed!")
    print("=" * 60)
