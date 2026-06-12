# DocScanner Pro 📱

**Dokumentenscanner mit Kamera, OCR und PDF-Export**

Eine native Android-App die Dokumente scannt, automatisch erkennt, Perspektiven korrigiert, Text extrahiert (OCR) und als PDF exportiert.

---

## 🚀 Features

- ✅ **One-Button Scan** - Einfach镜头里 halten und Button drücken
- ✅ **Automatische Dokumentenerkennung** - Findet Kanten und korrigiert Perspektive
- ✅ **OCR Texterkennung** - Extrahiert Text (Deutsch & Englisch)
- ✅ **PDF Export** - Multi-Page PDFs mit A4 Format
- ✅ **Offline First** - Alles läuft lokal, keine Cloud
- ✅ **Privatsphäre** - Keine Daten verlassen dein Gerät

---

## 📦 apk erstellen

### Option 1: Lokales Build (Linux/WSL/Termux)

```bash
# Buildozer installieren
pip install buildozer

# In den App-Ordder wechseln
cd ~/doc-scanner

# Buildozer initialisieren (falls noch nicht geschehen)
buildozer init

# APK bauen
buildozer -v android debug

# APK befindet sich in:
# bin/docscanner-1.0.0-debug.apk
```

### Option 2: GitHub Actions (Empfohlen)

Erstelle `.github/workflows/build-apk.yml`:

```yaml
name: Build APK

on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: 3.8
      
      - name: Install Buildozer
        run: |
          pip install buildozer
          sudo apt-get update
          sudo apt-get install -y python3-pip python3-setuptools \
            build-essential libffi-dev libssl-dev libjpeg-dev \
            libpng-dev libfreetype6-dev libharfbuzz-dev \
            autoconf automake libtool
      
      - name: Build APK
        run: buildozer -v android debug
      
      - name: Upload APK
        uses: actions/upload-artifact@v3
        with:
          name: app-release
          path: bin/*.apk
```

---

## 🔧 buildozer.spec anpassen

Falls du Probleme hast, passe `buildozer.spec` an:

```ini
# Für neuere Android Versionen
android.api = 33
android.minapi = 21
android.ndk = 25b

# Wenn Build fehlschlägt, versuche:
# requirements = python3,kivy==2.2.0,opencv-python,pillow,reportlab
```

---

## 🧪 App auf Termux testen (ohne APK)

```bash
cd ~/doc-scanner

# Dependencies installieren
pip install kivy opencv-python-headless pillow reportlab pytesseract

# App starten
python main.py
```

**Hinweis:** Auf Termux braucht die Kamera **Termux:API**:
```bash
pkg install termux-api
termux-setup-storage
```

---

## 📱 Installation auf Android

1. APK auf Android-Gerät kopieren
2. Einstellungen → Sicherheit → "Unbekannte Quellen" aktivieren
3. APK installieren
4. App öffnen und Kamera-Berechtigung erlauben

---

## 🎯 Nächste Schritte zur Kommerzialisierung

### 1. Google Play Store Vorbereitung
- Keystone generieren für signierte Release-APK
- Screenshots erstellen (5 Stück, verschiedene Formate)
- App-Beschreibung schreiben (kurz + lang)
- Preissystem festlegen (Einmalkauf ~$5-15)

### 2. Build Command für Release-APK
```bash
buildozer -v android release
# Signieren mit deinem Keystore
```

### 3. Monetarisierung
- Einmalkauf: $9.99 (empfohlen)
- Oder: Kostenlos mit In-App-Kauf ($4.99 für OCR, $9.99 für PDF)

### 4. Marketing
- "Privacy-First Scanner - Keine Cloud, kein Tracking"
- "Einmalkauf statt Abo-Zwang"
- "Besser als Adobe Scan - lokal, schnell, fair"

---

## 🛠 Problembehebung

### Buildozer findet Android SDK nicht
```bash
export ANDROID_HOME=$HOME/android-sdk
export PATH=$PATH:$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools
```

### Kivy Build-Fehler auf Termux
```bash
# System-Dependencies installieren
pkg install python pythran numpy cython pillow \
    libjpeg-turbo libpng freetype harfbuzz sdl2
```

### Kamera funktioniert nicht
- Stelle sicher dass `CAMERA` Permission in `buildozer.spec` ist
- Auf Android: Manuell Berechtigung in Settings erteilen

---

## 📄 Lizenz

MIT License - Frei verwendbar für kommerzielle Projekte

---

## 🤝 Support

Fragen oder Issues? Erstelle ein Issue auf GitHub.

**Viel Erfolg mit deiner Scanner-App!** 💰