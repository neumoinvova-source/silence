[app]

title = SILENCE
package.name = silence
package.domain = org.silence

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,wav,mp3

version = 0.1

requirements = python3,kivy,requests

orientation = portrait
fullscreen = 0

android.arch = arm64-v8a,armeabi-v7a
android.api = 35
android.minapi = 21
android.accept_sdk_license = True

android.allow_backup = True
