# PayPal LXNORO Agent

**Research Center:** LXNORO OJSC  
**Creator & Copyright:** NOORA AL-MAOLAI  

An AI-powered shopping assistant that helps users discover products, compare options, approve selections, and complete secure checkout through PayPal.

---

## Problem Addressed & Solution

- **Problem:** E-commerce shoppers often face friction navigating fragmented product catalogs and integrating secure, trusted payment gateways without complex checkout overhead.
- **Solution:** PayPal LXNORO Agent streamlines conversational product discovery via Google Gemini and integrates robust, server-side PayPal Sandbox Orders v2 checkout workflows with strict monetary precision and security safeguards.

---

## Key MVP Features

1. **Conversational Query Enhancement:** Natural-language request optimization using Google Gemini Flash-Lite (`gemini-3.1-flash-lite`).
2. **Catalog Discovery & Filtering:** Real-time product search and catalog integration via the Channel3 API.
3. **Secure Server-Side PayPal Checkout:** OAuth2 authentication, strict input validation, Decimal monetary precision, strict approval URL domain validation, and server-side order capture verification against PayPal Sandbox endpoints.
4. **Resilient Error Diagnostics:** Structured logging of PayPal API HTTP status, error name, message, and `debug_id` for troubleshooting.

---

## User Checkout Flow

1. User enters a natural-language shopping request and budget preferences.
2. App queries the Channel3 product catalog and displays curated results.
3. User selects a product and initiates checkout.
4. The backend securely creates a PayPal Sandbox order and generates an approval link (`payer-action` / `approve`).
5. User completes approval in PayPal Sandbox and returns to the app. (Note: Sandbox test transactions can be verified in PayPal Sandbox Activity; the app currently returns to the order form upon completion).

---

## Technology Stack

- **Python 3.11**
- **Streamlit** (Web UI)
- **Google GenAI SDK** (`google-genai` for Gemini Flash-Lite)
- **Requests** (HTTP client for Channel3 & PayPal Sandbox REST APIs)
- **GitHub Actions** (CI syntax validation)

---

## Local Setup & Configuration

1. **Clone the repository and create a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\Activate.ps1
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   Copy `.env.example` to `.env` and configure required keys:
   - `GEMINI_API_KEY`
   - `CHANNEL3_API_KEY`
   - `PAYPAL_CLIENT_ID`
   - `PAYPAL_CLIENT_SECRET`
   - `PAYPAL_ENVIRONMENT=sandbox`
   - `PAYPAL_RETURN_URL` (Optional / configured for deployment)
   - `PAYPAL_CANCEL_URL` (Optional / configured for deployment)

4. **Run the Streamlit application locally:**
   ```bash
   streamlit run app.py
   ```

---

## Testing & Deployment

- **Automated Syntax CI:** Validated via GitHub Actions workflow (`.github/workflows/ci.yml`).
- **Local Testing:** Unit and integration test suites are included (`test_app_integration.py`, `test_paypal_client.py`, etc.).
- **Deployment:** Configured for Streamlit Cloud deployment with Streamlit Secrets bridging.

---

## Security Notice

Never commit API keys, payment credentials, access tokens, or customer secrets to version control. Credentials must be managed exclusively via environment variables or secure deployment secrets managers.

---

## License

MIT License — Copyright (c) 2026 NOORA AL-MAOLAI, LXNORO OJSC. See [LICENSE](LICENSE) for details.
