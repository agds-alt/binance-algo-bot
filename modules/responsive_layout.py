"""
Responsive Layout Module
Optimize layout for PC, Tablet, and Mobile devices
"""

RESPONSIVE_CSS = """
<style>
    /* ===== RESPONSIVE LAYOUT ===== */

    /* Mobile First Approach */
    /* Mobile (320px - 767px) */
    @media (max-width: 767px) {
        /* Full width on mobile */
        .main .block-container {
            padding: 1rem !important;
            max-width: 100% !important;
        }

        /* Stack columns vertically */
        [data-testid="column"] {
            width: 100% !important;
            min-width: 100% !important;
            flex: 100% !important;
        }

        /* Smaller headers */
        h1 { font-size: 1.8rem !important; }
        h2 { font-size: 1.5rem !important; }
        h3 { font-size: 1.3rem !important; }

        /* Compact metrics */
        [data-testid="stMetricValue"] {
            font-size: 1.5rem !important;
        }

        [data-testid="stMetricLabel"] {
            font-size: 0.9rem !important;
        }

        /* Smaller buttons */
        .stButton>button {
            padding: 0.5rem 1rem !important;
            font-size: 0.9rem !important;
            width: 100% !important;
        }

        /* Hide sidebar by default on mobile */
        [data-testid="stSidebar"] {
            display: none;
        }

        [data-testid="stSidebar"][aria-expanded="true"] {
            display: block;
            position: fixed;
            left: 0;
            top: 0;
            width: 80% !important;
            max-width: 280px !important;
            height: 100vh;
            z-index: 999999;
        }

        /* Compact inputs */
        .stTextInput>div>div>input,
        .stNumberInput>div>div>input,
        .stSelectbox>div>div>select {
            font-size: 0.9rem !important;
            padding: 0.5rem !important;
        }

        /* Smaller dataframes */
        .stDataFrame {
            font-size: 0.8rem !important;
            overflow-x: auto !important;
        }

        /* Compact forms */
        [data-testid="stForm"] {
            padding: 1rem !important;
        }

        /* Stack charts vertically */
        .js-plotly-plot {
            max-width: 100% !important;
        }

        /* Mobile navigation */
        .stTabs [data-baseweb="tab-list"] {
            overflow-x: auto !important;
            flex-wrap: nowrap !important;
        }

        .stTabs [data-baseweb="tab"] {
            font-size: 0.85rem !important;
            padding: 0.5rem 0.75rem !important;
        }
    }

    /* Tablet (768px - 1023px) */
    @media (min-width: 768px) and (max-width: 1023px) {
        /* Medium width container */
        .main .block-container {
            padding: 2rem 1.5rem !important;
            max-width: 95% !important;
        }

        /* Two column layout */
        [data-testid="column"] {
            min-width: 45% !important;
        }

        /* Medium headers */
        h1 { font-size: 2.2rem !important; }
        h2 { font-size: 1.8rem !important; }
        h3 { font-size: 1.5rem !important; }

        /* Sidebar optimized */
        [data-testid="stSidebar"] {
            width: 250px !important;
        }

        /* Medium buttons */
        .stButton>button {
            padding: 0.6rem 1.5rem !important;
            font-size: 0.95rem !important;
        }

        /* Metrics size */
        [data-testid="stMetricValue"] {
            font-size: 1.8rem !important;
        }

        /* Responsive dataframes */
        .stDataFrame {
            font-size: 0.9rem !important;
        }

        /* Compact tabs */
        .stTabs [data-baseweb="tab"] {
            font-size: 0.9rem !important;
            padding: 0.6rem 1rem !important;
        }
    }

    /* Desktop (1024px+) */
    @media (min-width: 1024px) {
        /* Wide container */
        .main .block-container {
            padding: 3rem 2rem !important;
            max-width: 1400px !important;
        }

        /* Full sidebar */
        [data-testid="stSidebar"] {
            width: 300px !important;
        }

        /* Large headers */
        h1 { font-size: 2.6rem !important; }
        h2 { font-size: 2.1rem !important; }
        h3 { font-size: 1.7rem !important; }

        /* Full size buttons */
        .stButton>button {
            padding: 0.7rem 2rem !important;
            font-size: 1rem !important;
        }

        /* Large metrics */
        [data-testid="stMetricValue"] {
            font-size: 2.2rem !important;
        }

        /* Full dataframes */
        .stDataFrame {
            font-size: 1rem !important;
        }

        /* Wide charts */
        .js-plotly-plot {
            min-width: 100% !important;
        }
    }

    /* ===== TOUCH OPTIMIZATION ===== */

    /* Larger touch targets on mobile */
    @media (max-width: 767px) {
        button, a, input, select {
            min-height: 44px !important;
            min-width: 44px !important;
        }

        /* Prevent text selection on touch */
        .stButton>button {
            -webkit-tap-highlight-color: transparent;
            -webkit-touch-callout: none;
            user-select: none;
        }
    }

    /* ===== LANDSCAPE MODE ===== */

    /* Mobile landscape */
    @media (max-width: 767px) and (orientation: landscape) {
        .main .block-container {
            padding: 0.5rem !important;
        }

        h1 { font-size: 1.5rem !important; }
        h2 { font-size: 1.3rem !important; }

        [data-testid="stMetricValue"] {
            font-size: 1.3rem !important;
        }
    }

    /* ===== ACCESSIBILITY ===== */

    /* Focus indicators */
    button:focus, input:focus, select:focus {
        outline: 2px solid #00ff41 !important;
        outline-offset: 2px !important;
    }

    /* High contrast mode support */
    @media (prefers-contrast: high) {
        * {
            border-width: 2px !important;
        }
    }

    /* Reduced motion support */
    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }
    }

    /* ===== PRINT OPTIMIZATION ===== */

    @media print {
        /* Hide unnecessary elements */
        [data-testid="stSidebar"],
        .stButton,
        [data-testid="stHeader"] {
            display: none !important;
        }

        /* Black text on white background */
        * {
            background: white !important;
            color: black !important;
            text-shadow: none !important;
            box-shadow: none !important;
        }
    }

    /* ===== SAFE AREA (iOS Notch) ===== */

    /* Padding for iOS safe areas */
    @supports (padding: max(0px)) {
        .main .block-container {
            padding-left: max(1rem, env(safe-area-inset-left)) !important;
            padding-right: max(1rem, env(safe-area-inset-right)) !important;
            padding-top: max(1rem, env(safe-area-inset-top)) !important;
            padding-bottom: max(1rem, env(safe-area-inset-bottom)) !important;
        }
    }

    /* ===== PERFORMANCE ===== */

    /* Hardware acceleration */
    .stButton>button,
    [data-testid="stSidebar"],
    .js-plotly-plot {
        transform: translateZ(0);
        will-change: transform;
    }

    /* Smooth scrolling */
    html {
        scroll-behavior: smooth;
    }

    /* ===== PWA FULLSCREEN ===== */

    /* Hide UI chrome in PWA mode */
    @media (display-mode: standalone) {
        /* Full height */
        .main {
            min-height: 100vh !important;
        }

        /* Add status bar padding */
        .main .block-container {
            padding-top: max(1rem, env(safe-area-inset-top, 20px)) !important;
        }
    }
</style>
"""


def apply_responsive_layout():
    """Apply responsive layout to the current page"""
    import streamlit as st
    st.markdown(RESPONSIVE_CSS, unsafe_allow_html=True)


def get_device_type():
    """Detect device type from viewport width"""
    import streamlit.components.v1 as components

    device_detect_js = """
    <script>
        const width = window.innerWidth;
        const deviceType = width < 768 ? 'mobile' : (width < 1024 ? 'tablet' : 'desktop');

        // Store in sessionStorage
        sessionStorage.setItem('deviceType', deviceType);

        // Send to Streamlit (if needed)
        console.log('Device Type:', deviceType);
    </script>
    """
    components.html(device_detect_js, height=0)


def show_device_indicator():
    """Show current device type indicator (for debugging)"""
    import streamlit as st

    indicator_html = """
    <div id="device-indicator" style="
        position: fixed;
        bottom: 10px;
        left: 10px;
        background: rgba(0, 255, 65, 0.1);
        border: 1px solid #00ff41;
        padding: 5px 10px;
        border-radius: 5px;
        font-size: 0.8rem;
        color: #00ff41;
        z-index: 9998;
    ">
        📱 <span id="device-type"></span>
    </div>
    <script>
        const width = window.innerWidth;
        const type = width < 768 ? 'Mobile' : (width < 1024 ? 'Tablet' : 'Desktop');
        document.getElementById('device-type').textContent = type + ' (' + width + 'px)';
    </script>
    """

    st.markdown(indicator_html, unsafe_allow_html=True)
