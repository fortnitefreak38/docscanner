[app]
title = DocScanner Pro
package.name = docscanner
package.domain = com.nousresearch

source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0.0

requirements = python3,kivy==2.3.0,opencv-python,pillow,pytesseract,reportlab,android
orientation = portrait
android.permissions = CAMERA,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,INTERNET
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True

build.kivy_args = --orientation=portrait
build.profile = armeabi-v7a,arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 0