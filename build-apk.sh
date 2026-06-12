#!/bin/bash
# build-apk.sh - Baut die DocScanner APK
# Kann auf Linux-PC, WSL, oder Cloud-Server (GitHub Actions, GitLab CI) laufen

set -e

echo "==================================="
echo "DocScanner Pro - APK Build Script"
echo "==================================="
echo ""

# Farbcodes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Prüfen ob Buildozer installiert ist
if ! command -v buildozer &> /dev/null; then
    echo -e "${YELLOW}Buildozer nicht gefunden. Installation...${NC}"
    pip install buildozer
fi

# In App-Verzeichnis wechseln
cd ~/doc-scanner

# Prüfen ob buildozer.spec existiert
if [ ! -f buildozer.spec ]; then
    echo -e "${RED}Fehler: buildozer.spec nicht gefunden!${NC}"
    echo "Erstelle buildozer.spec..."
    buildozer init
fi

# Dependencies prüfen
echo -e "${YELLOW}Prüfe dependencies...${NC}"
pip install -q kivy opencv-python-headless pillow reportlab pytesseract

# Buildozer-Konfiguration aktualisieren
echo -e "${YELLOW}Konfiguriere Buildozer...${NC}"
sed -i 's/requirements = python3/requirements = python3,kivy==2.3.0,opencv-python,pillow,pytesseract,reportlab/' buildozer.spec

# APK bauen
echo ""
echo -e "${GREEN}Starte APK Build...${NC}"
echo "Das kann 10-30 Minuten dauern (beim ersten Build)"
echo ""

# Clean Build (beim ersten Mal)
buildozer android clean
buildozer -v android debug

# Ergebnis prüfen
if [ -f "bin/docscanner-1.0.0-debug.apk" ]; then
    echo ""
    echo "==================================="
    echo -e "${GREEN}✓ APK erfolgreich erstellt!${NC}"
    echo "==================================="
    echo "Pfad: ~/doc-scanner/bin/docscanner-1.0.0-debug.apk"
    echo ""
    echo "Installation:"
    echo "  1. APK auf Android-Gerät kopieren"
    echo "  2. 'Unbekannte Quellen' in Settings aktivieren"
    echo "  3. APK installieren"
    echo ""
    
    # Größe anzeigen
    ls -lh bin/docscanner-1.0.0-debug.apk
else
    echo ""
    echo -e "${RED}✗ Build fehlgeschlagen!${NC}"
    echo "Prüfe .buildozer/android/platform/build-*/dists/docscanner/build/logs für Fehler"
    exit 1
fi

echo ""
echo -e "${YELLOW}Nächste Schritte:${NC}"
echo "  - APK auf deinem Samsung S23 testen"
echo "  - Release-APK bauen: buildozer android release"
echo "  - Für Play Store: AAB bauen: buildozer android release_aab"