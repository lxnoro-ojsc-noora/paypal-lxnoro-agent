# PayPal LXNORO Agent

An AI-powered shopping assistant that helps users discover products, compare options, approve a selection, and complete checkout through PayPal.

## Technology Stack

- Python 3.11
- Streamlit
- Google Gemini Flash-Lite (`gemini-3.1-flash-lite` via official `google-genai` SDK) for natural-language query enhancement
- Channel3 API (`https://api.trychannel3.com/v1/search`) for product catalog discovery
- PayPal Sandbox API (`https://api-m.sandbox.paypal.com`) for test payment checkout flow implementation
- Git and GitHub for version control

## Shopping Workflow

1. Capture the user's natural-language shopping request.
2. Enhance and optimize the search query using Google Gemini Flash-Lite (with automatic fallback to the raw query if unconfigured or unavailable).
3. Collect the target price range and advanced preferences.
4. Search and filter the Channel3 product catalog.
5. Present matching products for manual selection review.
6. Initiate secure checkout through the official PayPal Sandbox payment flow.
7. Support server-side order creation, status verification, and order capture against PayPal Sandbox endpoints.

## Development Status

Gemini natural-language query enhancement and PayPal Sandbox checkout integration have been implemented in the codebase, but end-to-end live testing has not yet been executed in this environment.

## Local Setup

1. Create and activate a Python virtual environment.
2. Install dependencies: `pip install -r requirements.txt`.
3. Configure environment variables in `.env` (using `.env.example` as a template):
   - `GEMINI_API_KEY`
   - `CHANNEL3_API_KEY`
   - `PAYPAL_CLIENT_ID`
   - `PAYPAL_CLIENT_SECRET`
   - `PAYPAL_ENVIRONMENT=sandbox`
4. Run the Streamlit application: `streamlit run app.py`.

## PayPal Sandbox Configuration Update (October 23, 2026)

- On October 23, 2026, the project switched to newly created US Sandbox Personal and Business accounts, created a new REST app linked to the US Business account, and updated `PAYPAL_CLIENT_ID` and `PAYPAL_CLIENT_SECRET` in Streamlit Cloud Secrets.
- `PAYPAL_RETURN_URL` and `PAYPAL_CANCEL_URL` remain `https://paypal-lxnoro-agent.streamlit.app/`.
- **Security & Status Notice:** Credentials are stored in Streamlit Cloud Secrets and must never be committed to Git. No account emails, client IDs, secrets, tokens, or other sensitive values are included. Note that buyer approval and end-to-end checkout flow remain unresolved and require live validation.

## Security

Never commit API keys, payment credentials, access tokens, or customer secrets.
