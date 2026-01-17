"""
PWA Support Module
Add Progressive Web App capabilities to Streamlit
"""

PWA_HEAD_HTML = """
<!-- PWA Meta Tags -->
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="BotX">
<meta name="application-name" content="BotX">
<meta name="theme-color" content="#00ff41">
<meta name="msapplication-TileColor" content="#000000">
<meta name="msapplication-navbutton-color" content="#00ff41">

<!-- PWA Manifest -->
<link rel="manifest" href="/static/manifest.json">

<!-- iOS Icons -->
<link rel="apple-touch-icon" sizes="72x72" href="/static/icons/icon-72x72.png">
<link rel="apple-touch-icon" sizes="96x96" href="/static/icons/icon-96x96.png">
<link rel="apple-touch-icon" sizes="128x128" href="/static/icons/icon-128x128.png">
<link rel="apple-touch-icon" sizes="144x144" href="/static/icons/icon-144x144.png">
<link rel="apple-touch-icon" sizes="152x152" href="/static/icons/icon-152x152.png">
<link rel="apple-touch-icon" sizes="192x192" href="/static/icons/icon-192x192.png">
<link rel="apple-touch-icon" sizes="384x384" href="/static/icons/icon-384x384.png">
<link rel="apple-touch-icon" sizes="512x512" href="/static/icons/icon-512x512.png">

<!-- Favicon -->
<link rel="icon" type="image/png" sizes="32x32" href="/static/icons/icon-32x32.png">
<link rel="icon" type="image/png" sizes="16x16" href="/static/icons/icon-16x16.png">

<!-- Service Worker Registration -->
<script>
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register('/static/service-worker.js')
        .then((registration) => {
          console.log('ServiceWorker registered:', registration.scope);
        })
        .catch((error) => {
          console.log('ServiceWorker registration failed:', error);
        });
    });
  }
</script>

<!-- PWA Install Prompt Handler -->
<script>
  let deferredPrompt;

  window.addEventListener('beforeinstallprompt', (e) => {
    // Prevent default install prompt
    e.preventDefault();
    deferredPrompt = e;

    // Show install button (can be customized in Streamlit)
    console.log('PWA install prompt ready');
  });

  // Function to trigger install (call from Streamlit)
  function installPWA() {
    if (deferredPrompt) {
      deferredPrompt.prompt();
      deferredPrompt.userChoice.then((choiceResult) => {
        if (choiceResult.outcome === 'accepted') {
          console.log('User accepted the install prompt');
        }
        deferredPrompt = null;
      });
    }
  }

  // Detect if running as PWA
  function isPWA() {
    return window.matchMedia('(display-mode: standalone)').matches ||
           window.navigator.standalone === true;
  }

  // Show PWA status
  if (isPWA()) {
    console.log('Running as PWA');
  }
</script>
"""


def inject_pwa_support():
    """Inject PWA support into Streamlit page"""
    import streamlit as st
    import streamlit.components.v1 as components

    # Inject meta tags and scripts
    components.html(PWA_HEAD_HTML, height=0)


def show_install_button():
    """Show PWA install button"""
    import streamlit as st
    import streamlit.components.v1 as components

    install_html = """
    <div style="position: fixed; bottom: 20px; right: 20px; z-index: 9999;">
        <button onclick="installPWA()" style="
            background: linear-gradient(135deg, #003300 0%, #006600 100%);
            color: #00ff41;
            border: 2px solid #00ff41;
            padding: 12px 24px;
            border-radius: 8px;
            font-weight: bold;
            cursor: pointer;
            box-shadow: 0 0 15px rgba(0, 255, 65, 0.3);
            font-size: 14px;
        ">
            📱 Install App
        </button>
    </div>
    <script>
        // Check if already installed
        if (window.matchMedia('(display-mode: standalone)').matches) {
            document.querySelector('button').style.display = 'none';
        }
    </script>
    """
    components.html(install_html, height=0)
