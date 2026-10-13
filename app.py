"""
PayPal LXNORO Agent - AI Shopping Assistant (Refined Professional UI + Channel3 Integration)
Built for PayPal AI Hackathon 2026.
Customer-facing shopping assistant UI integrating live Channel3 product search with graceful fallback.
"""

import streamlit as st
from dotenv import load_dotenv
from channel3_client import search_products

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="PayPal LXNORO Agent | AI Shopping Assistant",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling: Polished futuristic gaming-inspired interface with clean white/near-white bg, electric blue & deep navy accents
st.markdown(
    """
    <style>
    /* Global Theme */
    .stApp {
        background-color: #F8FAFC;
        color: #0A192F;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Header Container */
    .hero-header {
        background: linear-gradient(135deg, #0A192F 0%, #1E3A8A 100%);
        color: #FFFFFF;
        padding: 2.25rem 2rem;
        border-radius: 14px;
        margin-bottom: 1.75rem;
        box-shadow: 0 10px 25px -5px rgba(37, 99, 235, 0.15);
        border: 1px solid rgba(59, 130, 246, 0.25);
    }
    .hero-title {
        font-size: 2.1rem;
        font-weight: 800;
        letter-spacing: -0.025em;
        margin-bottom: 0.4rem;
        background: linear-gradient(90deg, #FFFFFF 0%, #93C5FD 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero-subtitle {
        font-size: 1.05rem;
        color: #94A3B8;
        font-weight: 400;
        max-width: 680px;
        line-height: 1.5;
    }
    .badge {
        display: inline-block;
        background-color: rgba(37, 99, 235, 0.2);
        color: #60A5FA;
        padding: 0.2rem 0.65rem;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-bottom: 0.75rem;
        border: 1px solid rgba(96, 165, 250, 0.3);
    }

    /* Roadmap / Progress Indicator */
    .roadmap-container {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1.75rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
    }
    .roadmap-title {
        font-size: 0.95rem;
        font-weight: 700;
        color: #0A192F;
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .stage-pill {
        display: inline-block;
        padding: 0.3rem 0.65rem;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        margin: 0.15rem;
    }
    .stage-active {
        background-color: #2563EB;
        color: #FFFFFF;
    }
    .stage-pending {
        background-color: #F1F5F9;
        color: #64748B;
        border: 1px solid #E2E8F0;
    }

    /* Illustrative Data Banner */
    .illustrative-banner {
        background-color: #F1F5F9;
        border: 1px solid #CBD5E1;
        color: #334155;
        padding: 0.75rem 1rem;
        border-radius: 8px;
        font-size: 0.85rem;
        margin-bottom: 1.5rem;
        line-height: 1.5;
    }

    /* Product Cards */
    .product-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1.5rem;
        height: 100%;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.03);
        transition: all 0.2s ease;
    }
    .product-card:hover {
        border-color: #2563EB;
        box-shadow: 0 8px 12px -2px rgba(37, 99, 235, 0.08);
    }
    .product-brand {
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        color: #2563EB;
        letter-spacing: 0.05em;
        margin-bottom: 0.25rem;
    }
    .product-name {
        font-size: 1.1rem;
        font-weight: 700;
        color: #0A192F;
        margin-bottom: 0.4rem;
    }
    .product-price {
        font-size: 1.25rem;
        font-weight: 800;
        color: #0F172A;
        margin-bottom: 0.75rem;
    }
    .spec-item {
        font-size: 0.85rem;
        color: #475569;
        margin-bottom: 0.2rem;
    }
    .tradeoff-box {
        background-color: #F8FAFC;
        border-left: 3px solid #2563EB;
        padding: 0.5rem 0.75rem;
        font-size: 0.8rem;
        color: #334155;
        margin-top: 0.75rem;
        border-radius: 0 6px 6px 0;
        line-height: 1.4;
    }

    /* Checkout Preview Box */
    .checkout-preview-box {
        background-color: #EFF6FF;
        border: 1px solid #BFDBFE;
        color: #1E40AF;
        padding: 1.25rem;
        border-radius: 10px;
        font-size: 0.9rem;
        margin-top: 1.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --- 1. Isolated Demo Product Data Structure & Retrieval (Fallback) ---
def get_demo_products() -> list:
    """Returns structured illustrative sample product data separated from UI rendering logic."""
    return [
        {
            "id": "demo-1",
            "brand": "Nexus Audio",
            "title": "Quantum Pro Wireless ANC Headphones",
            "price": 249.99,
            "currency": "USD",
            "condition": "Brand New",
            "rating": 4.8,
            "reviews_count": 1420,
            "specs": {
                "Battery Life": "40 Hours",
                "Noise Cancellation": "Active Hybrid ANC",
                "Connectivity": "Bluetooth 5.3 / Aux",
                "Weight": "250g",
            },
            "pros": "Exceptional battery life and ultra-comfortable memory foam earcups.",
            "cons": "Slightly bulky carrying case.",
            "emoji": "🎧",
        },
        {
            "id": "demo-2",
            "brand": "SoundWave",
            "title": "AeroSphere Studio Wireless Headphones",
            "price": 199.50,
            "currency": "USD",
            "condition": "Brand New",
            "rating": 4.6,
            "reviews_count": 890,
            "specs": {
                "Battery Life": "30 Hours",
                "Noise Cancellation": "Adaptive ANC",
                "Connectivity": "Bluetooth 5.2",
                "Weight": "220g",
            },
            "pros": "Lightweight design with studio-grade balanced sound profile.",
            "cons": "Touch controls can be sensitive in cold weather.",
            "emoji": "🎧",
        },
        {
            "id": "demo-3",
            "brand": "Titan Tech",
            "title": "HyperBeat Gaming & Travel Headset",
            "price": 179.99,
            "currency": "USD",
            "condition": "Certified Refurbished",
            "rating": 4.5,
            "reviews_count": 610,
            "specs": {
                "Battery Life": "50 Hours (Mic detached)",
                "Noise Cancellation": "ENC Mic + Passive Isolation",
                "Connectivity": "2.4GHz Wireless + BT",
                "Weight": "275g",
            },
            "pros": "Zero-latency wireless dongle included, rugged build quality.",
            "cons": "Heavier profile for extended casual listening.",
            "emoji": "🎧",
        },
        {
            "id": "demo-4",
            "brand": "Aura Sound",
            "title": "PulsePure Executive ANC Cans",
            "price": 299.00,
            "currency": "USD",
            "condition": "Brand New",
            "rating": 4.9,
            "reviews_count": 2150,
            "specs": {
                "Battery Life": "35 Hours",
                "Noise Cancellation": "Industry-Leading ANC",
                "Connectivity": "Bluetooth 5.3 Multipoint",
                "Weight": "235g",
            },
            "pros": "Luxurious leather finish, stellar multipoint device switching.",
            "cons": "Premium price tier.",
            "emoji": "🎧",
        },
    ]


# --- Session State Initialization ---
if "search_submitted" not in st.session_state:
    st.session_state.search_submitted = False
if "selected_product_id" not in st.session_state:
    st.session_state.selected_product_id = None


# --- Hero Header ---
st.markdown(
    """
    <div class="hero-header">
        <div class="badge">AI Shopping Assistant</div>
        <div class="hero-title">PayPal LXNORO Agent</div>
        <div class="hero-subtitle">
            Discover, compare, and evaluate products effortlessly with intelligent natural-language guidance and secure checkout integration.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# --- Compact 7-Stage Visual Roadmap ---
st.markdown(
    """
    <div class="roadmap-container">
        <div class="roadmap-title">
            <span>🗺️</span> User Journey Roadmap
        </div>
        <div>
            <span class="stage-pill stage-active">1. Request</span>
            <span class="stage-pill stage-active">2. Budget</span>
            <span class="stage-pill stage-active">3. Preferences</span>
            <span class="stage-pill stage-active">4. Catalog Search</span>
            <span class="stage-pill stage-pending">5. Comparison</span>
            <span class="stage-pill stage-pending">6. Secure Checkout</span>
            <span class="stage-pill stage-pending">7. Verification</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# --- Sidebar / Configuration Controls ---
with st.sidebar:
    st.markdown("### ⚙️ Search Preferences")
    st.markdown("Customize your product search parameters.")

    currency = st.selectbox(
        "Currency", ["USD ($)", "EUR (€)", "GBP (£)", "JPY (¥)"], index=0
    )
    currency_code = currency.split(" ")[0]

    min_price = st.number_input(
        "Minimum Budget", min_value=0, value=50, step=10, format="%d"
    )
    max_price = st.number_input(
        "Maximum Budget", min_value=0, value=350, step=10, format="%d"
    )

    with st.expander("Advanced Filters", expanded=False):
        preferred_brand = st.selectbox(
            "Preferred Brand", ["Any", "Nexus Audio", "SoundWave", "Titan Tech", "Aura Sound"]
        )
        condition_filter = st.selectbox(
            "Condition", ["Any", "Brand New", "Certified Refurbished"]
        )
        delivery_priority = st.selectbox(
            "Delivery Speed", ["Standard", "Express (2-Day)", "Overnight"]
        )
        warranty_pref = st.checkbox("Minimum 1-Year Warranty", value=True)


# --- Main Shopping Request Form ---
st.markdown("#### What are you looking for today?")
user_query = st.text_area(
    "Shopping Request",
    placeholder="e.g., Wireless noise-canceling headphones with 30+ hour battery life for travel and daily work.",
    height=85,
    label_visibility="collapsed",
)

col_search, _ = st.columns([1, 3])
with col_search:
    find_clicked = st.button("Find My Products", type="primary", use_container_width=True)

if find_clicked:
    if not user_query.strip():
        st.error("Please enter a shopping request before searching.")
        st.session_state.search_submitted = False
    elif min_price > max_price:
        st.error("Minimum budget cannot exceed maximum budget.")
        st.session_state.search_submitted = False
    else:
        st.session_state.search_submitted = True


# --- Results Section ---
if st.session_state.search_submitted:
    st.markdown("---")
    
    # Attempt live Channel3 API search
    api_result = search_products(
        query=user_query,
        min_price=float(min_price),
        max_price=float(max_price),
        limit=10,
    )

    is_live_catalog = False
    if api_result["success"]:
        is_live_catalog = True
        # Live Channel3 Results Banner
        st.markdown(
            """
            <div style="background-color: #ECFDF5; border: 1px solid #10B981; color: #065F46; padding: 0.75rem 1rem; border-radius: 8px; font-size: 0.85rem; margin-bottom: 1.5rem; line-height: 1.5;">
                <b>Live Channel3 Search Results:</b> Showing products retrieved dynamically from the live Channel3 catalog matching your search request and budget.
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("#### Curated Recommendations (Live Catalog)")
        
        raw_live_products = api_result.get("products", [])
        filtered_live = []
        for p in raw_live_products:
            p_price = p.get("price")
            try:
                numeric_price = float(p_price)
            except (TypeError, ValueError):
                continue
            if float(min_price) <= numeric_price <= float(max_price):
                p["price"] = numeric_price
                filtered_live.append(p)
        display_products = filtered_live
    else:
        # Graceful Fallback to Illustrative Demo Data (only when live API call fails or is unconfigured)
        error_msg = api_result.get("error", "API unavailable")
        if api_result.get("source") != "unconfigured":
            st.warning(f"Live catalog search unavailable ({error_msg}). Showing illustrative sample data as a fallback.")
        
        st.markdown(
            """
            <div class="illustrative-banner">
                <b>Illustrative Sample Data (Fallback):</b> The items below are fixed sample products because live catalog search is currently unavailable or unconfigured. They are not dynamically retrieved or matched against your specific search request.
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("#### Curated Sample Recommendations")
        demo_products = get_demo_products()
        display_products = [
            p for p in demo_products if min_price <= p["price"] <= max_price
        ]

    # State consistency: clear selected product if no longer in filtered/displayed results
    if st.session_state.selected_product_id:
        if not any(p["id"] == st.session_state.selected_product_id for p in display_products):
            st.session_state.selected_product_id = None

    if not display_products:
        if is_live_catalog:
            st.info(
                f"No live Channel3 products match your selected budget range ({currency_code} {min_price} – {max_price}). Please try adjusting your budget or search query."
            )
        else:
            st.info(
                f"No sample products found within the specified budget range ({currency_code} {min_price} – {max_price}). Please adjust your budget to view available items."
            )
    else:
        cols = st.columns(2)
        for idx, product in enumerate(display_products):
            col = cols[idx % 2]
            with col:
                rating = product.get("rating")
                reviews_count = product.get("reviews_count")
                rating_display = f"★ {rating}" if rating else ""
                reviews_display = f"({reviews_count} ratings)" if reviews_count else ""
                stats_str = f"{rating_display} {reviews_display}".strip()
                if not stats_str:
                    stats_str = "Verified Catalog Item"

                st.markdown(
                    f"""
                    <div class="product-card">
                        <div style="font-size: 1.75rem; margin-bottom: 0.35rem;">{product.get('emoji', '🛍️')}</div>
                        <div class="product-brand">{product['brand']} • {product['condition']}</div>
                        <div class="product-name">{product['title']}</div>
                        <div class="product-price">{currency_code} {product['price']:.2f}</div>
                        <div style="font-size: 0.8rem; color: #64748B; margin-bottom: 0.75rem;">
                            {stats_str}
                        </div>
                    """,
                    unsafe_allow_html=True,
                )

                specs = product.get("specs", {})
                if isinstance(specs, dict):
                    for spec_key, spec_val in specs.items():
                        st.markdown(
                            f"<div class='spec-item'><b>{spec_key}:</b> {spec_val}</div>",
                            unsafe_allow_html=True,
                        )

                pros = product.get("pros")
                cons = product.get("cons")
                if pros or cons:
                    pros_text = pros if pros else "Curated catalog match."
                    cons_text = f"Consideration: {cons}" if cons else ""
                    st.markdown(
                        f"""
                        <div class="tradeoff-box">
                            <b>Key Advantage:</b> {pros_text}<br/>
                            {f'<span style="color: #64748B;">{cons_text}</span>' if cons_text else ''}
                        </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown("</div>", unsafe_allow_html=True)

                # Review Selection Button
                btn_key = f"select_{product['id']}"
                if st.button("Review Selection", key=btn_key, use_container_width=True):
                    st.session_state.selected_product_id = product["id"]

                st.markdown("<div style='margin-bottom: 0.75rem;'></div>", unsafe_allow_html=True)

        # --- Selection Review & Integration Status Section ---
        if st.session_state.selected_product_id:
            selected_prod = next(
                (p for p in display_products if p["id"] == st.session_state.selected_product_id),
                None,
            )
            if selected_prod:
                st.markdown("---")
                st.markdown("#### Selection Review & Integration Status")
                st.markdown(
                    f"""
                    <div class="checkout-preview-box">
                        <div style="font-weight: 600; color: #0A192F; margin-bottom: 0.35rem;">
                            Selected Item: {selected_prod['brand']} - {selected_prod['title']} ({currency_code} {selected_prod['price']:.2f})
                        </div>
                        <div style="font-size: 0.875rem; color: #475569; line-height: 1.5;">
                            <b>PayPal Integration Status:</b> Payment processing is not implemented in this interface milestone. No transaction will be processed, and no order confirmation or receipt can be generated.
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
else:
    # Professional Empty State
    st.markdown(
        """
        <div style="text-align: center; padding: 3.5rem 2rem; background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; margin-top: 1rem;">
            <div style="font-size: 2.5rem; margin-bottom: 0.75rem;">🛍️</div>
            <h4 style="color: #0A192F; font-weight: 600; margin-bottom: 0.35rem;">Enter a request to begin</h4>
            <p style="color: #64748B; font-size: 0.9rem; max-width: 420px; margin: 0 auto;">
                Describe what you are looking for above, set your budget range, and click <b>Find My Products</b> to explore curated options.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# --- Footer ---
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #94A3B8; font-size: 0.8rem; padding-bottom: 1.5rem;">
        PayPal LXNORO Agent • AI Shopping Assistant Interface
    </div>
    """,
    unsafe_allow_html=True,
)
