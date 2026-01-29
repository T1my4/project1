import subprocess
import sys

print("Установка зависимостей для голосового ассистента...")

# Список необходимых библиотек
packages = [
    'SpeechRecognition',
    'pyttsx3',
    'PyAudio',
    'colorama'
]

for package in packages:
    print(f"Устанавливаю {package}...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

print("Зависимости успешно установлены!")