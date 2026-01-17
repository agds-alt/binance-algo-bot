# 📱 PWA (Progressive Web App) Guide

BotX now supports **Progressive Web App (PWA)** features! Install it on your device for a native app experience.

---

## ✨ Features

### 📱 **Mobile-Friendly**
- Responsive design for **Phone**, **Tablet**, and **Desktop**
- Touch-optimized UI with larger tap targets
- Adaptive layouts based on screen size
- Optimized for both portrait and landscape modes

### 🚀 **Install as App**
- **Add to Home Screen** on mobile devices
- **Install as Desktop App** on PC
- Works **offline** with cached data
- Full-screen mode (no browser UI)
- Fast loading with service worker caching

### 🔔 **Push Notifications** (Coming Soon)
- Trade alerts
- Price notifications
- Signal updates
- System notifications

### 💾 **Offline Support**
- Basic features work without internet
- Cached UI and assets
- Automatic sync when online

---

## 📲 Installation Guide

### **Android (Chrome, Edge, Samsung Internet)**

1. Open **https://botx.railway.app** in browser
2. Tap **☰ Menu** → **"Add to Home Screen"** or **"Install App"**
3. Tap **"Add"** or **"Install"**
4. Done! Find **BotX** icon on your home screen

**Alternative:**
- Look for **"⬇️ Install"** banner at bottom of page
- Tap **"Install"** button

### **iOS (Safari)**

1. Open **https://botx.railway.app** in Safari
2. Tap **Share** button (📤)
3. Scroll down and tap **"Add to Home Screen"**
4. Tap **"Add"**
5. Done! Find **BotX** icon on your home screen

**Note:** iOS doesn't support full PWA features, but you can still add to home screen.

### **Desktop (Chrome, Edge, Opera)**

1. Open **https://botx.railway.app** in browser
2. Look for **"⬇️ Install"** icon in address bar
3. Click **"Install BotX"**
4. Done! BotX launches in app window

**Alternative:**
- Chrome: **☰ Menu** → **"Install BotX"**
- Edge: **⚙️ Settings** → **"Apps"** → **"Install BotX"**

---

## 📐 Responsive Layouts

BotX automatically adapts to your screen size:

### 📱 **Mobile (320px - 767px)**
- **Compact layout** with single-column design
- **Collapsible sidebar** (swipe from left to open)
- **Large touch targets** (min 44px)
- **Stacked metrics** for easy reading
- **Responsive tables** with horizontal scroll
- **Optimized font sizes** for mobile

### 📲 **Tablet (768px - 1023px)**
- **Two-column layout** for efficiency
- **Persistent sidebar** with 250px width
- **Medium-sized UI** elements
- **Balanced spacing** for touch and precision
- **Optimized charts** for tablet screens

### 💻 **Desktop (1024px+)**
- **Full-width layout** (max 1400px)
- **Wide sidebar** (300px) with all features
- **Large metrics** and charts
- **Multi-column grids** for data
- **Mouse-optimized** interactions
- **Keyboard shortcuts** support

---

## 🎨 Dark Theme Optimizations

### **Mobile-Specific**
- **Reduced glow effects** to save battery
- **OLED-optimized** pure black (#000000)
- **High contrast** for outdoor readability
- **Night mode** friendly

### **Desktop-Specific**
- **Full glow animations** on headers
- **Hover effects** on buttons
- **Rich gradients** and shadows
- **Smooth transitions**

---

## 🔧 Technical Details

### **PWA Manifest**
```json
{
  "name": "BotX - Binance Algo Trading Bot",
  "short_name": "BotX",
  "theme_color": "#00ff41",
  "background_color": "#000000",
  "display": "standalone"
}
```

### **Service Worker**
- **Cache-first strategy** for static assets
- **Network-first** for API calls
- **Offline fallback** page
- **Auto-update** on new version

### **Responsive Breakpoints**
```css
Mobile:  320px - 767px
Tablet:  768px - 1023px
Desktop: 1024px+
```

---

## 🆚 PWA vs Web App

| Feature | PWA (Installed) | Web App (Browser) |
|---------|-----------------|-------------------|
| **Install** | ✅ Yes | ❌ No |
| **Home Screen Icon** | ✅ Yes | ❌ No |
| **Full Screen** | ✅ Yes | ❌ No |
| **Offline Mode** | ✅ Yes | ❌ No |
| **Push Notifications** | ✅ Yes | ⚠️ Limited |
| **Faster Loading** | ✅ Yes (cached) | ⚠️ Depends on network |
| **Updates** | ✅ Auto | ✅ Auto |

---

## 🔍 Testing Responsive Layout

### **Browser DevTools**
1. Open DevTools (F12)
2. Click **"Toggle Device Toolbar"** (Ctrl+Shift+M)
3. Select device:
   - iPhone 12 Pro (390x844)
   - iPad Air (820x1180)
   - Desktop (1920x1080)

### **Real Devices**
Test on actual devices for best accuracy:
- **Mobile:** iPhone, Samsung Galaxy, OnePlus
- **Tablet:** iPad, Samsung Tab, Surface
- **Desktop:** Windows, macOS, Linux

---

## 📊 Performance

### **Lighthouse Scores (Target)**
- **Performance:** 90+
- **Accessibility:** 95+
- **Best Practices:** 95+
- **SEO:** 90+
- **PWA:** 100

### **Load Times**
- **First Load:** < 3 seconds
- **Cached Load:** < 1 second
- **Mobile (4G):** < 5 seconds

---

## 🐛 Troubleshooting

### **"Install" button not showing**
- Make sure you're using **HTTPS** (not HTTP)
- Try **Chrome** or **Edge** (better PWA support)
- Clear browser cache and reload

### **Offline mode not working**
- Ensure service worker is registered (check DevTools → Application → Service Workers)
- May take 1-2 visits to fully cache

### **Layout broken on mobile**
- Clear browser cache
- Update browser to latest version
- Check if JavaScript is enabled

### **Icons not loading**
- Upload custom icons to `.streamlit/static/icons/`
- Or use default browser icons

---

## 🚀 Future Enhancements

- [ ] **Push notifications** for trades and alerts
- [ ] **Background sync** for offline trades
- [ ] **Share target** (share to BotX from other apps)
- [ ] **Shortcuts** for quick actions
- [ ] **Dark/Light mode toggle**
- [ ] **Custom theme colors** per user
- [ ] **Multi-language support**

---

## 📞 Support

**Issues with PWA?**
- Check browser compatibility: https://caniuse.com/pwa
- Report issues on GitHub
- Contact support

---

## ✅ Browser Compatibility

| Browser | PWA Support | Install | Offline |
|---------|-------------|---------|---------|
| **Chrome (Android)** | ✅ Full | ✅ Yes | ✅ Yes |
| **Chrome (Desktop)** | ✅ Full | ✅ Yes | ✅ Yes |
| **Edge** | ✅ Full | ✅ Yes | ✅ Yes |
| **Safari (iOS)** | ⚠️ Limited | ⚠️ Home Screen Only | ❌ No |
| **Firefox** | ⚠️ Limited | ❌ No | ⚠️ Partial |
| **Samsung Internet** | ✅ Full | ✅ Yes | ✅ Yes |

**Recommended:** Chrome or Edge for best PWA experience

---

**Last Updated:** 2026-01-17
**Version:** 1.0.0
**Platform:** Streamlit + Railway
