[app]

# (str) Title of your application
title = BMS Monitor Pro

# (str) Package name
package.name = bmsmonitor

# (str) Package domain (needed for android/ios packaging)
package.domain = org.bms

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include
source.include_exts = py,png,jpg,kv,atlas

# (str) Application versioning
version = 1.0

# (list) Application requirements
# PENTING: Versi kivy dan kivymd diset stabil agar tidak konflik dengan Cython di Colab
requirements = python3,kivy==2.2.1,kivymd==1.1.1,pyjnius,cython==0.29.33

# (list) Supported orientations
orientation = portrait

#
# Android specific
#

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
# Menambahkan izin lengkap untuk Bluetooth Classic dan BLE (Android 12+)
android.permissions = BLUETOOTH, BLUETOOTH_ADMIN, BLUETOOTH_SCAN, BLUETOOTH_CONNECT, BLUETOOTH_ADVERTISE, ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION

# (int) Target Android API (API 31/33 adalah standar saat ini)
android.api = 31

# (int) Minimum API
android.minapi = 21

# (str) Android NDK version (NDK r25b sangat stabil untuk API 31)
android.ndk = 25b

# (int) Android NDK API (Samakan dengan minapi)
android.ndk_api = 21

# (bool) If True, then automatically accept SDK license
android.accept_sdk_license = True

# (bool) Enable AndroidX support (Diperlukan untuk KivyMD terbaru)
android.enable_androidx = True

# (list) The Android archs to build for
# arm64-v8a untuk HP modern, armeabi-v7a untuk HP lama
android.archs = arm64-v8a, armeabi-v7a

# (bool) Indicate whether the screen should stay on
# Sangat penting untuk monitoring agar layar tidak mati (WAKE_LOCK)
android.wakelock = True

[buildozer]

# (int) Log level (2 = debug untuk melihat error detail di Colab)
log_level = 2

# (int) Display warning if buildozer is run as root
warn_on_root = 1
