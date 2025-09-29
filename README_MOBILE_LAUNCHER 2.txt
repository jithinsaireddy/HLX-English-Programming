# NLVM – Mobile App + Cross-Platform Launcher

This is the official structure for building NLVM as a mobile and desktop experience.

---

## 📱 Mobile App (React Native)

### Features:
- Write English code in a mobile-friendly editor
- Button to Compile and Run (offline)
- Saves files locally
- Designed for kids, students, and makers

### Tools:
- Use React Native or Expo
- Backend runs Python + Flask in embedded service

---

## 💻 Cross-Platform Launcher (Electron)

### Features:
- Runs on Windows, macOS, and Linux
- Embedded Python backend
- Web-based NLVM UI inside Electron shell

### How It Works:
1. Start local Flask server
2. Load the browser window in Electron
3. Works fully offline

---

This folder is your base to launch NLVM to the world on any device. You’re now shipping the future.