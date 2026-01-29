# build_assistant.py
"""
Скрипт для сборки голосового ассистента в единый EXE файл
"""

import os
import sys
import subprocess
import shutil
import platform
from pathlib import Path

def check_pyinstaller():
    """Проверяет установлен ли PyInstaller"""
    try:
        import PyInstaller
        print("✅ PyInstaller установлен")
        return True
    except ImportError:
        print("❌ PyInstaller не установлен")
        print("Установите его командой: pip install pyinstaller")
        return False

def create_spec_file():
    """Создает spec файл для сборки"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Файлы и данные для включения
added_files = []

# Если есть файлы тем, добавьте их
for theme_file in ['jarvis_theme.py', 'evlampiy_theme.py', 'vazelina_theme.py', 'lena_theme.py']:
    if os.path.exists(theme_file):
        added_files.append((theme_file, '.'))

# Если есть иконки, добавьте их
icons = []
for icon in ['assistant_icon.ico', 'jarvis_icon.ico', 'evlampiy_icon.ico', 'vazelina_icon.ico', 'lena_icon.ico']:
    if os.path.exists(icon):
        icons.append(icon)

a = Analysis(
    ['main_with_theme.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=[
        # Основные зависимости
        'speech_recognition',
        'pyttsx3',
        'pyaudio',
        'tkinter',
        'queue',
        'json',
        'os',
        'sys',
        'threading',
        'subprocess',
        'datetime',
        're',
        'traceback',
        'pathlib',
        'math',
        'time',
        'random',
        'webbrowser',
        
        # Дополнительные импорты для pyttsx3
        'pyttsx3.drivers',
        'pyttsx3.drivers.sapi5',
        'pyttsx3.drivers.nsss',
        'pyttsx3.drivers.espeak',
        
        # Для speech_recognition
        'pocketsphinx' if 'pocketsphinx' in sys.modules else '',
        
        # Для обработки звука
        'wave',
        'audioop',
        'collections.abc',
        
        # Для работы с путями
        'pathlib',
        'ntpath',
        'posixpath',
        
        # Системные
        'win32api' if platform.system() == 'Windows' else '',
        'win32com' if platform.system() == 'Windows' else '',
        'win32comext' if platform.system() == 'Windows' else '',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Исключаем ненужные библиотеки для уменьшения размера
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'sklearn',
        'sqlalchemy',
        'django',
        'flask',
        'torch',
        'tensorflow',
        'keras',
        'PIL',
        'pillow',
        'pygame',
        'pyqt5',
        'wx',
        'gtk',
        'cryptography',
        'requests',
        'bs4',
        'lxml',
        'html5lib',
        'selenium',
        'scrapy',
        'asyncio',
        'tornado',
        'twisted',
        'cython',
        'jupyter',
        'notebook',
        'ipython',
        'spyder',
        'pytest',
        'unittest',
        'doctest',
        'nose',
        'coverage',
        'sphinx',
        'docutils',
        'setuptools',
        'pip',
        'wheel',
        'virtualenv',
        'conda',
    ],
    noarchive=False,
    optimize=1,  # Уровень оптимизации
)

# Настройки для exe
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='VoiceAssistant',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Использовать UPX для сжатия
    runtime_tmpdir=None,
    console=False,  # Измените на True если хотите видеть консоль
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assistant_icon.ico' if os.path.exists('assistant_icon.ico') else None,
)

# Если нужно собрать как один файл
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='VoiceAssistant',
)
'''
    
    with open('assistant.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ Создан spec файл: assistant.spec")

def create_requirements_file():
    """Создает файл requirements.txt"""
    requirements = '''SpeechRecognition==3.10.0
pyttsx3==2.90
PyAudio==0.2.11
'''
    
    with open('requirements.txt', 'w', encoding='utf-8') as f:
        f.write(requirements)
    
    print("✅ Создан файл requirements.txt")

def install_dependencies():
    """Устанавливает зависимости"""
    print("📦 Устанавливаю зависимости...")
    
    dependencies = [
        'SpeechRecognition==3.10.0',
        'pyttsx3==2.90',
        'PyAudio==0.2.11',
        'PyInstaller==5.13.0'
    ]
    
    for dep in dependencies:
        print(f"📥 Устанавливаю {dep}...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', dep])
            print(f"✅ {dep} установлен")
        except subprocess.CalledProcessError:
            print(f"⚠️ Не удалось установить {dep}")
            print("Попробуйте установить вручную: pip install PyAudio")
            print("Примечание: PyAudio может требовать установки дополнительных системных библиотек")
            print("Для Windows: pip install pipwin затем pipwin install pyaudio")
            print("Для Linux: sudo apt-get install python3-pyaudio")
            print("Для Mac: brew install portaudio затем pip install pyaudio")

def create_windows_bat():
    """Создает BAT файл для Windows"""
    bat_content = '''@echo off
chcp 65001 > nul
title Voice Assistant Builder
echo ========================================
echo    СБОРКА ГОЛОСОВОГО АССИСТЕНТА
echo ========================================
echo.

:: Проверка Python
python --version > nul 2>&1
if errorlevel 1 (
    echo ❌ Python не найден!
    echo Установите Python с официального сайта:
    echo https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Проверка pip
python -m pip --version > nul 2>&1
if errorlevel 1 (
    echo ❌ pip не найден!
    echo Переустановите Python с опцией "Add Python to PATH"
    pause
    exit /b 1
)

:: Создание виртуального окружения
echo 📁 Создаю виртуальное окружение...
python -m venv venv
if errorlevel 1 (
    echo ❌ Не удалось создать виртуальное окружение
    echo Установите virtualenv: pip install virtualenv
    pause
    exit /b 1
)

:: Активация виртуального окружения
echo 🔧 Активирую виртуальное окружение...
call venv\\Scripts\\activate.bat
if errorlevel 1 (
    echo ❌ Не удалось активировать виртуальное окружение
    pause
    exit /b 1
)

:: Установка зависимостей
echo 📦 Устанавливаю зависимости...
pip install SpeechRecognition==3.10.0
pip install pyttsx3==2.90

:: PyAudio может требовать особой установки
echo 📥 Устанавливаю PyAudio...
python -m pip install pipwin
pipwin install pyaudio
if errorlevel 1 (
    echo ⚠️ PyAudio не установлен автоматически
    echo Попробуйте установить вручную
)

:: Установка PyInstaller
echo 🛠️ Устанавливаю PyInstaller...
pip install pyinstaller==5.13.0

:: Сборка
echo 🔨 Начинаю сборку...
pyinstaller --onefile --windowed --icon=assistant_icon.ico --name="VoiceAssistant" main_with_theme.py

if errorlevel 1 (
    echo ❌ Ошибка при сборке!
    pause
    exit /b 1
)

echo.
echo ✅ Сборка завершена успешно!
echo 📁 Исполняемый файл: dist\\VoiceAssistant.exe
echo.
echo 💡 Советы по использованию:
echo 1. Для голосового управления нужен микрофон
echo 2. Для синтеза речи нужны голосовые движки Windows
echo 3. Для поиска в интернете нужен браузер
echo.
pause
'''
    
    with open('build_windows.bat', 'w', encoding='utf-8') as f:
        f.write(bat_content)
    
    print("✅ Создан BAT файл для Windows: build_windows.bat")

def create_linux_sh():
    """Создает SH файл для Linux"""
    sh_content = '''#!/bin/bash

echo "========================================"
echo "   СБОРКА ГОЛОСОВОГО АССИСТЕНТА"
echo "========================================"
echo

# Проверка Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не найден!"
    echo "Установите Python3:"
    echo "sudo apt-get install python3  # Ubuntu/Debian"
    echo "sudo yum install python3      # CentOS/RHEL"
    exit 1
fi

# Проверка pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 не найден!"
    echo "Установите pip3:"
    echo "sudo apt-get install python3-pip  # Ubuntu/Debian"
    exit 1
fi

# Создание виртуального окружения
echo "📁 Создаю виртуальное окружение..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "❌ Не удалось создать виртуальное окружение"
    echo "Установите virtualenv: pip3 install virtualenv"
    exit 1
fi

# Активация виртуального окружения
echo "🔧 Активирую виртуальное окружение..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "❌ Не удалось активировать виртуальное окружение"
    exit 1
fi

# Установка системных зависимостей для PyAudio
echo "📦 Устанавливаю системные зависимости..."
if command -v apt-get &> /dev/null; then
    sudo apt-get update
    sudo apt-get install -y python3-dev portaudio19-dev
elif command -v yum &> /dev/null; then
    sudo yum install -y python3-devel portaudio-devel
elif command -v dnf &> /dev/null; then
    sudo dnf install -y python3-devel portaudio-devel
fi

# Установка Python зависимостей
echo "📥 Устанавливаю Python зависимости..."
pip install SpeechRecognition==3.10.0
pip install pyttsx3==2.90
pip install pyaudio==0.2.11
pip install pyinstaller==5.13.0

# Сборка
echo "🔨 Начинаю сборку..."
pyinstaller --onefile --windowed --name="VoiceAssistant" main_with_theme.py

if [ $? -ne 0 ]; then
    echo "❌ Ошибка при сборке!"
    exit 1
fi

echo
echo "✅ Сборка завершена успешно!"
echo "📁 Исполняемый файл: dist/VoiceAssistant"
echo
echo "💡 Советы по использованию:"
echo "1. Для голосового управления нужен микрофон"
echo "2. Для синтеза речи: sudo apt-get install espeak"
echo "3. Для поиска в интернете нужен браузер"
echo
'''
    
    with open('build_linux.sh', 'w', encoding='utf-8') as f:
        f.write(sh_content)
    
    # Делаем файл исполняемым
    os.chmod('build_linux.sh', 0o755)
    
    print("✅ Создан SH файл для Linux: build_linux.sh")

def create_mac_sh():
    """Создает SH файл для macOS"""
    sh_content = '''#!/bin/bash

echo "========================================"
echo "   СБОРКА ГОЛОСОВОГО АССИСТЕНТА"
echo "========================================"
echo

# Проверка Homebrew
if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew не найден!"
    echo "Установите Homebrew:"
    echo '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
    exit 1
fi

# Проверка Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не найден!"
    echo "Установите Python3: brew install python@3.9"
    exit 1
fi

# Установка системных зависимостей
echo "📦 Устанавливаю системные зависимости..."
brew install portaudio

# Создание виртуального окружения
echo "📁 Создаю виртуальное окружение..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "❌ Не удалось создать виртуальное окружение"
    exit 1
fi

# Активация виртуального окружения
echo "🔧 Активирую виртуальное окружение..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "❌ Не удалось активировать виртуальное окружение"
    exit 1
fi

# Установка Python зависимостей
echo "📥 Устанавливаю Python зависимости..."
pip install SpeechRecognition==3.10.0
pip install pyttsx3==2.90
pip install pyaudio==0.2.11
pip install pyinstaller==5.13.0

# Сборка для macOS
echo "🔨 Начинаю сборку..."
pyinstaller --onefile --windowed --name="VoiceAssistant" main_with_theme.py

if [ $? -ne 0 ]; then
    echo "❌ Ошибка при сборке!"
    exit 1
fi

echo
echo "✅ Сборка завершена успешно!"
echo "📁 Исполняемый файл: dist/VoiceAssistant"
echo
echo "💡 Советы по использованию:"
echo "1. Для голосового управления нужен микрофон"
echo "2. Возможно потребуется разрешить доступ к микрофону в настройках"
echo "3. Для поиска в интернете нужен браузер"
echo
'''
    
    with open('build_mac.sh', 'w', encoding='utf-8') as f:
        f.write(sh_content)
    
    # Делаем файл исполняемым
    os.chmod('build_mac.sh', 0o755)
    
    print("✅ Создан SH файл для macOS: build_mac.sh")

def build_with_pyinstaller():
    """Собирает проект с помощью PyInstaller"""
    print("🔨 Начинаю сборку проекта...")
    
    # Базовые параметры сборки
    base_cmd = [
        'pyinstaller',
        '--onefile',           # Один файл
        '--windowed',          # Без консоли (измените на --console если нужна консоль)
        '--clean',             # Очистить кэш
    ]
    
    # Добавляем иконку если она существует
    if os.path.exists('assistant_icon.ico'):
        base_cmd.extend(['--icon', 'assistant_icon.ico'])
    
    # Имя выходного файла
    base_cmd.extend(['--name', 'VoiceAssistant'])
    
    # Основной файл
    base_cmd.append('main_with_theme.py')
    
    # Дополнительные скрытые импорты
    base_cmd.extend([
        '--hidden-import', 'pyttsx3.drivers',
        '--hidden-import', 'pyttsx3.drivers.sapi5',
        '--hidden-import', 'pyttsx3.drivers.nsss',
        '--hidden-import', 'pyttsx3.drivers.espeak',
        '--hidden-import', 'pyaudio',
        '--hidden-import', 'speech_recognition',
        '--hidden-import', 'webbrowser',
    ])
    
    # Для Windows добавляем дополнительные импорты
    if platform.system() == 'Windows':
        base_cmd.extend([
            '--hidden-import', 'win32api',
            '--hidden-import', 'win32com',
            '--hidden-import', 'win32comext',
        ])
    
    # Исключаем ненужные библиотеки для уменьшения размера
    exclude_list = [
        'matplotlib', 'numpy', 'pandas', 'scipy', 'sklearn',
        'sqlalchemy', 'django', 'flask', 'torch', 'tensorflow',
        'keras', 'PIL', 'pillow', 'pygame', 'pyqt5', 'wx', 'gtk',
        'cryptography', 'requests', 'bs4', 'lxml', 'html5lib',
    ]
    
    for exclude in exclude_list:
        base_cmd.extend(['--exclude-module', exclude])
    
    # Запускаем сборку
    try:
        print("🚀 Команда сборки:")
        print(' '.join(base_cmd))
        print()
        
        result = subprocess.run(base_cmd, check=True, capture_output=True, text=True)
        print("✅ Сборка завершена успешно!")
        print(f"📁 Файл создан: dist/VoiceAssistant{'.exe' if platform.system() == 'Windows' else ''}")
        
        # Проверяем размер файла
        exe_path = f"dist/VoiceAssistant{'.exe' if platform.system() == 'Windows' else ''}"
        if os.path.exists(exe_path):
            size = os.path.getsize(exe_path) / (1024 * 1024)  # В МБ
            print(f"📊 Размер файла: {size:.2f} MB")
        
    except subprocess.CalledProcessError as e:
        print("❌ Ошибка при сборке!")
        print(f"Код ошибки: {e.returncode}")
        print(f"Вывод: {e.stderr}")
        return False
    
    return True

def create_readme():
    """Создает README файл"""
    readme_content = '''# Голосовой ассистент - Multi-Assistant Edition

## Описание
Многофункциональный голосовой ассистент с поддержкой 4 различных персонажей:
- **J.A.R.V.I.S.** - футуристичный AI ассистент
- **Евлампий** - классический русский помощник
- **Вазилина** - энергичная современная помощница
- **Лена** - доброжелательная и заботливая помощница

## Возможности
- 📢 Голосовое управление
- 🎤 Распознавание речи
- 🔊 Синтез речи
- 💾 Создание заметок
- 🖥️ Управление приложениями
- 🔍 Поиск в интернете
- ⏰ Время и дата
- ⚙️ Настройка параметров
- 🎨 Уникальный интерфейс для каждого ассистента

## Системные требования
- **ОС**: Windows 7/8/10/11, Linux, macOS
- **Python**: 3.7 или выше
- **Память**: 512 MB RAM минимум
- **Место на диске**: 100 MB
- **Микрофон** (для голосового управления)
- **Динамики/наушники** (для синтеза речи)

## Установка

### 1. Сборка из исходного кода
```bash
# Установите зависимости
pip install SpeechRecognition pyttsx3 pyaudio

# Запустите программу
python main_with_theme.py

'''