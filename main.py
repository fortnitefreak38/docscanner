# DocScanner Pro - Hauptanwendung
# Dokumentenscanner mit Kamera, OCR und PDF-Export

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.camera import Camera
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.clock import Clock
from kivy.properties import ObjectProperty, StringProperty
from kivy.metrics import dp
import os
import cv2
import numpy as np
from PIL import Image as PILImage
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import datetime

class DocScannerUI(BoxLayout):
    """Haupt-UI der Scanner-App"""
    
    camera = ObjectProperty(None)
    captured_image = ObjectProperty(None)
    status_label = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(10)
        self.spacing = dp(10)
        
        # Kamera-View
        self.camera_box = BoxLayout(orientation='vertical', size_hint=(1, 0.7))
        self.camera = Camera(
            play=True,
            index=0,
            resolution=(640, 480),
            size_hint=(1, 1)
        )
        self.camera_box.add_widget(self.camera)
        self.add_widget(self.camera_box)
        
        # Kontroll-Buttons
        self.button_box = BoxLayout(
            orientation='horizontal',
            size_hint=(1, 0.15),
            spacing=dp(10)
        )
        
        # Capture Button (groß, zentral)
        self.capture_btn = Button(
            text='📷 SCAN',
            font_size=dp(24),
            bold=True,
            background_color=(0.2, 0.6, 1, 1),
            size_hint=(0.6, 1)
        )
        self.capture_btn.bind(on_press=self.capture_document)
        self.button_box.add_widget(self.capture_btn)
        
        # Galerie Button
        self.gallery_btn = Button(
            text='📁',
            font_size=dp(20),
            size_hint=(0.2, 1)
        )
        self.gallery_btn.bind(on_press=self.open_gallery)
        self.button_box.add_widget(self.gallery_btn)
        
        # Einstellungen Button
        self.settings_btn = Button(
            text='⚙️',
            font_size=dp(20),
            size_hint=(0.2, 1)
        )
        self.button_box.add_widget(self.settings_btn)
        
        self.add_widget(self.button_box)
        
        # Status-Anzeige
        self.status_label = Label(
            text='Bereit zum Scannen',
            size_hint=(1, 0.08),
            font_size=dp(14),
            color=(0.5, 0.5, 0.5, 1)
        )
        self.add_widget(self.status_label)
        
        # Vorschau-Bereich (versteckt bis Scan)
        self.preview_box = BoxLayout(
            orientation='vertical',
            size_hint=(1, 0.7),
            opacity=0
        )
        self.preview_image = Image()
        self.preview_box.add_widget(self.preview_image)
        self.add_widget(self.preview_box)
        
        # Verarbeitete Bilder
        self.scanned_docs = []
        self.current_image_path = None
        
    def capture_document(self, instance):
        """Dokument fotografieren und verarbeiten"""
        if self.camera.texture:
            # Bild speichern
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            self.current_image_path = f'/sdcard/DocScanner/scans/scan_{timestamp}.png'
            
            # Sicherstellen dass Verzeichnis existiert
            os.makedirs('/sdcard/DocScanner/scans', exist_ok=True)
            
            self.camera.texture.save(self.current_image_path)
            self.status_label.text = 'Bild wird verarbeitet...'
            
            # Verarbeitung starten (in nächstem Frame)
            Clock.schedule_once(lambda dt: self.process_document(), 0.1)
    
    def process_document(self):
        """Dokument verarbeiten: Kanten erkennen, Perspektive korrigieren"""
        if not self.current_image_path or not os.path.exists(self.current_image_path):
            self.status_label.text = 'Fehler: Bild nicht gefunden'
            return
        
        try:
            # Bild laden
            img = cv2.imread(self.current_image_path)
            if img is None:
                raise ValueError('Bild konnte nicht geladen werden')
            
            # Graustufen
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Weichzeichnen und Kanten erkennen
            gray = cv2.GaussianBlur(gray, (5, 5), 0)
            edged = cv2.Canny(gray, 75, 200)
            
            # Konturen finden
            contours, _ = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            contours = sorted(contours, key=cv2.contourArea, reverse=True)
            
            # Größte rechteckige Kontur finden
            doc_contour = None
            for contour in contours:
                perimeter = cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)
                if len(approx) == 4:
                    doc_contour = approx
                    break
            
            # Perspektive korrigieren falls Kontur gefunden
            if doc_contour is not None:
                warped = self.four_point_transform(img, doc_contour.reshape(4, 2))
                # Speichern
                warped_path = self.current_image_path.replace('.png', '_processed.png')
                cv2.imwrite(warped_path, warped)
                self.current_image_path = warped_path
                self.status_label.text = '✓ Dokument erkannt und korrigiert'
            else:
                self.status_label.text = 'Dokument erkannt (automatisch)'
            
            # Vorschau aktualisieren
            self.preview_image.source = self.current_image_path
            self.preview_box.opacity = 1
            self.camera_box.opacity = 0
            
            self.scanned_docs.append(self.current_image_path)
            
            # Buttons umschalten
            self.update_buttons_for_review()
            
        except Exception as e:
            self.status_label.text = f'Fehler: {str(e)[:30]}'
    
    def four_point_transform(self, image, pts):
        """Perspektivische Korrektur (4-Punkt-Transformation)"""
        # Punkte sortieren
        rect = self.order_points(pts)
        (tl, tr, br, bl) = rect
        
        # Breite berechnen
        widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        maxWidth = max(int(widthA), int(widthB))
        
        # Höhe berechnen
        heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        maxHeight = max(int(heightA), int(heightB))
        
        # Zielpunkte
        dst = np.array([
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1]
        ], dtype="float32")
        
        # Transformationsmatrix und anwenden
        M = cv2.getPerspectiveTransform(rect, dst)
        warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
        
        return warped
    
    def order_points(self, pts):
        """Punkte sortieren: tl, tr, br, bl"""
        rect = np.zeros((4, 2), dtype="float32")
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]  # tl
        rect[2] = pts[np.argmax(s)]  # br
        
        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]  # tr
        rect[3] = pts[np.argmax(diff)]  # bl
        
        return rect
    
    def update_buttons_for_review(self):
        """Buttons nach Scan anpassen"""
        self.button_box.clear_widgets()
        
        # Neuer Scan
        new_scan_btn = Button(
            text='➕ WEITER',
            font_size=dp(18),
            background_color=(0.3, 0.7, 0.3, 1)
        )
        new_scan_btn.bind(on_press=self.new_scan)
        self.button_box.add_widget(new_scan_btn)
        
        # PDF erstellen
        pdf_btn = Button(
            text='📄 PDF',
            font_size=dp(18),
            background_color=(0.8, 0.3, 0.3, 1)
        )
        pdf_btn.bind(on_press=self.create_pdf)
        self.button_box.add_widget(pdf_btn)
        
        # OCR Button
        ocr_btn = Button(
            text='📝 TEXT',
            font_size=dp(18),
            background_color=(0.8, 0.6, 0.2, 1)
        )
        ocr_btn.bind(on_press=self.perform_ocr)
        self.button_box.add_widget(ocr_btn)
    
    def new_scan(self, instance):
        """Zurück zur Kamera"""
        self.camera.play = True
        self.camera_box.opacity = 1
        self.preview_box.opacity = 0
        self.status_label.text = 'Bereit zum nächsten Scan'
        self.update_buttons_default()
    
    def update_buttons_default(self):
        """Standard Buttons wiederherstellen"""
        self.button_box.clear_widgets()
        
        self.capture_btn = Button(
            text='📷 SCAN',
            font_size=dp(24),
            bold=True,
            background_color=(0.2, 0.6, 1, 1),
            size_hint=(0.6, 1)
        )
        self.capture_btn.bind(on_press=self.capture_document)
        self.button_box.add_widget(self.capture_btn)
        
        self.gallery_btn = Button(
            text='📁',
            font_size=dp(20),
            size_hint=(0.2, 1)
        )
        self.gallery_btn.bind(on_press=self.open_gallery)
        self.button_box.add_widget(self.gallery_btn)
        
        self.settings_btn = Button(
            text='⚙️',
            font_size=dp(20),
            size_hint=(0.2, 1)
        )
        self.button_box.add_widget(self.settings_btn)
    
    def open_gallery(self, instance):
        """Galerie öffnen"""
        self.status_label.text = 'Galerie öffnet...'
        # TODO: Galerie-Integration
    
    def create_pdf(self, instance):
        """PDF aus gescannten Dokumenten erstellen"""
        if len(self.scanned_docs) == 0:
            self.status_label.text = 'Keine Scans zum Erstellen'
            return
        
        try:
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            pdf_path = f'/sdcard/DocScanner/output/scan_{timestamp}.pdf'
            os.makedirs('/sdcard/DocScanner/output', exist_ok=True)
            
            c = canvas.Canvas(pdf_path, pagesize=A4)
            width, height = A4
            
            for i, img_path in enumerate(self.scanned_docs):
                if i > 0:
                    c.showPage()
                
                # Bild skalieren um auf A4 zu passen
                pil_img = PILImage.open(img_path)
                img_width, img_height = pil_img.size
                
                # Seitenverhältnis beibehalten
                scale = min(width / img_width, height / img_height)
                new_width = img_width * scale
                new_height = img_height * scale
                
                # Zentriert platzieren
                x = (width - new_width) / 2
                y = (height - new_height) / 2
                
                c.drawImage(img_path, x, y, new_width, new_height)
            
            c.save()
            
            self.status_label.text = f'✓ PDF erstellt ({len(self.scanned_docs)} Seiten)'
            
            # Erfolg-Popup
            popup = Popup(
                title='PDF erstellt!',
                content=Label(text=f'Datei gespeichert unter:\n{pdf_path}'),
                size_hint=(0.8, 0.4)
            )
            popup.open()
            
            # Reset
            self.scanned_docs = []
            self.new_scan(None)
            
        except Exception as e:
            self.status_label.text = f'PDF Fehler: {str(e)[:25]}'
    
    def perform_ocr(self, instance):
        """OCR auf gescannten Dokumenten durchführen"""
        if len(self.scanned_docs) == 0:
            self.status_label.text = 'Keine Scans für OCR'
            return
        
        try:
            # Tesseract OCR (braucht tesseract auf Android)
            # Für die APK wird pytesseract gebündelt
            from PIL import Image as PILImage
            import pytesseract
            
            all_text = []
            for img_path in self.scanned_docs:
                img = PILImage.open(img_path)
                # Zuerst Deutsch, dann Englisch als Fallback
                try:
                    text = pytesseract.image_to_string(img, lang='deu')
                except:
                    text = pytesseract.image_to_string(img, lang='eng')
                all_text.append(text)
            
            full_text = '\n\n---\n\n'.join(all_text)
            
            # Text im Popup anzeigen
            popup = Popup(
                title='OCR Ergebnis',
                content=Label(
                    text=full_text[:500] + '...' if len(full_text) > 500 else full_text,
                    size_hint_y=None,
                    height=dp(300)
                ),
                size_hint=(0.9, 0.6)
            )
            popup.open()
            
            # Text speichern
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            txt_path = f'/sdcard/DocScanner/output/ocr_{timestamp}.txt'
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(full_text)
            
            self.status_label.text = '✓ OCR abgeschlossen'
            
        except Exception as e:
            self.status_label.text = f'OCR Fehler: {str(e)[:25]}'

class DocScannerApp(App):
    """DocScanner Pro App"""
    
    def build(self):
        self.title = 'DocScanner Pro'
        return DocScannerUI()
    
    def on_start(self):
        """App-Start: Verzeichnisse erstellen"""
        try:
            os.makedirs('/sdcard/DocScanner/scans', exist_ok=True)
            os.makedirs('/sdcard/DocScanner/output', exist_ok=True)
        except:
            pass

if __name__ == '__main__':
    DocScannerApp().run()