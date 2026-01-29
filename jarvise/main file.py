# main_with_theme.py
"""
Основной файл приложения с футуристичным оформлением в стиле Тони Старка
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import queue
import json
import os
import subprocess
import datetime
import sys
import re
import traceback
from pathlib import Path
import math
import time

# Импортируем футуристичную тему
from futuristic_theme import FuturisticStarkTheme

# Импорт для голосового управления с обработкой ошибок
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    print("Библиотека SpeechRecognition не установлена")

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False
    print("Библиотека pyttsx3 не установлена")

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    print("Библиотека PyAudio не установлена")

class MicrophoneError(Exception):
    """Исключение для ошибок микрофона"""
    pass

class VoiceAssistant:
    def __init__(self, gui_callback=None):
        # Сохраняем callback для обновления GUI
        self.gui_callback = gui_callback
        
        # Проверяем доступность библиотек
        if not SPEECH_RECOGNITION_AVAILABLE or not PYTTSX3_AVAILABLE:
            raise ImportError("Необходимые библиотеки не установлены")
        
        # Инициализируем распознаватель речи
        self.recognizer = sr.Recognizer()
        
        # Пытаемся найти микрофон
        self.microphone = None
        self.microphone_available = False
        self.setup_microphone()
        
        # Инициализируем синтезатор речи
        if PYTTSX3_AVAILABLE:
            try:
                self.engine = pyttsx3.init()
            except Exception as e:
                print(f"Ошибка инициализации синтезатора речи: {e}")
                self.engine = None
        else:
            self.engine = None
        
        # Настройки по умолчанию
        self.settings = {
            'voice_gender': 'male',
            'language': 'ru-RU',
            'note_path': str(Path.home() / 'assistant_notes.txt'),
            'assistant_name': 'джарвис',
            'activation_phrase': 'джарвис',
            'response_delay': 0.5,
            'volume': 0.8,
            'rate': 150,
            'listen_timeout': 3,
            'phrase_time_limit': 5
        }
        
        # Загружаем настройки
        self.load_settings()
        
        # Инициализируем команды
        self.setup_commands()
        
        self.current_lang = 'ru-RU'
        self.is_listening = False
        self.is_activated = False
        self.message_queue = queue.Queue()
        self.last_activation_time = 0
        
        # Приложения для запуска (остаются теми же)
        self.applications = {
            'ru-RU': {
                'блокнот': 'notepad.exe',
                'калькулятор': 'calc.exe',
                'браузер': 'start chrome',
                'google chrome': 'start chrome',
                'хром': 'start chrome',
                'проводник': 'explorer.exe',
                'проводник windows': 'explorer.exe',
                'word': 'winword.exe',
                'ворд': 'winword.exe',
                'excel': 'excel.exe',
                'эксель': 'excel.exe',
                'powerpoint': 'powerpnt.exe',
                'пауэрпоинт': 'powerpnt.exe',
                'пауэр поинт': 'powerpnt.exe',
                'камера': 'start microsoft.windows.camera:',
                'диспетчер задач': 'taskmgr.exe',
                'настройки': 'start ms-settings:',
                'параметры': 'start ms-settings:',
                'панель управления': 'control.exe',
                'cmd': 'cmd.exe',
                'командная строка': 'cmd.exe',
                'терминал': 'wt.exe',
                'windows terminal': 'wt.exe',
            },
            'en-US': {
                'notepad': 'notepad.exe',
                'calculator': 'calc.exe',
                'browser': 'start chrome',
                'chrome': 'start chrome',
                'firefox': 'start firefox',
                'edge': 'start msedge',
                'explorer': 'explorer.exe',
                'file explorer': 'explorer.exe',
                'word': 'winword.exe',
                'excel': 'excel.exe',
                'powerpoint': 'powerpnt.exe',
                'camera': 'start microsoft.windows.camera:',
                'task manager': 'taskmgr.exe',
                'settings': 'start ms-settings:',
                'control panel': 'control.exe',
                'cmd': 'cmd.exe',
                'command prompt': 'cmd.exe',
                'terminal': 'wt.exe',
                'powershell': 'powershell.exe',
                'paint': 'mspaint.exe',
            }
        }
        
        # Настройка голосового движка
        if self.engine:
            self.engine.setProperty('volume', self.settings['volume'])
            self.engine.setProperty('rate', self.settings['rate'])
    
    def setup_commands(self):
        """Настраивает словарь команд"""
        self.commands = {
            'ru-RU': {
                'открой': self.open_app,
                'запусти': self.open_app,
                'открыть': self.open_app,
                'создай заметку': self.create_note,
                'запиши': self.create_note,
                'записать': self.create_note,
                'выключи компьютер': self.shutdown_pc,
                'выключи пк': self.shutdown_pc,
                'перезагрузка': self.reboot_pc,
                'перезагрузи': self.reboot_pc,
                'перезагрузи компьютер': self.reboot_pc,
                'привет': self.greet,
                'здравствуй': self.greet,
                'пока': self.exit_program,  # Изменено для закрытия программы
                'до свидания': self.exit_program,  # Изменено для закрытия программы
                'завершение работы': self.exit_program,
                'заверши работу': self.exit_program,
                'как дела': self.how_are_you,
                'что ты умеешь': self.show_abilities,
                'стоп': self.stop_listening,
                'остановись': self.stop_listening,
                'продолжи': self.start_listening,
                'продолжить': self.start_listening,
                'какая погода': self.weather,
                'сколько времени': self.current_time,
                'который час': self.current_time,
                'дата': self.current_date,
                'спасибо': self.thank_you,
                'помощь': self.show_help,
                
                # Команды управления настройками
                'смени идентификатор': self.change_name,
                'измени имя': self.change_name,
                'новое имя': self.change_name,
                'смени имя на': self.change_name,
                'измени режим голоса': self.change_voice_mode,
                'смени голос': self.change_voice_mode,
                'женский голос': self.set_female_voice,
                'мужской голос': self.set_male_voice,
                'установи громкость': self.set_volume,
                'измени громкость': self.set_volume,
                'громкость': self.set_volume,
                'установи скорость': self.set_rate,
                'измени скорость': self.set_rate,
                'скорость': self.set_rate,
                'переключи язык': self.toggle_language,
                'смени язык': self.toggle_language,
                'английский язык': self.set_english,
                'русский язык': self.set_russian,
                'покажи параметры': self.show_settings,
                'параметры системы': self.show_settings,
                'настройки системы': self.show_settings,
            },
            'en-US': {
                'open': self.open_app,
                'start': self.open_app,
                'launch': self.open_app,
                'create note': self.create_note,
                'write': self.create_note,
                'take note': self.create_note,
                'shutdown': self.shutdown_pc,
                'shutdown computer': self.shutdown_pc,
                'reboot': self.reboot_pc,
                'restart': self.reboot_pc,
                'hello': self.greet,
                'hi': self.greet,
                'goodbye': self.exit_program,  # Изменено для закрытия программы
                'bye': self.exit_program,  # Изменено для закрытия программы
                'exit': self.exit_program,
                'quit': self.exit_program,
                'close': self.exit_program,
                'how are you': self.how_are_you,
                'what can you do': self.show_abilities,
                'stop': self.stop_listening,
                'stop listening': self.stop_listening,
                'continue': self.start_listening,
                'resume': self.start_listening,
                'weather': self.weather,
                'time': self.current_time,
                'what time is it': self.current_time,
                'date': self.current_date,
                'thank you': self.thank_you,
                'thanks': self.thank_you,
                'help': self.show_help,
                
                # Команды управления настройками
                'change name': self.change_name,
                'new name': self.change_name,
                'switch voice': self.change_voice_mode,
                'change voice': self.change_voice_mode,
                'female voice': self.set_female_voice,
                'male voice': self.set_male_voice,
                'set volume': self.set_volume,
                'change volume': self.set_volume,
                'volume': self.set_volume,
                'set rate': self.set_rate,
                'change rate': self.set_rate,
                'rate': self.set_rate,
                'switch language': self.toggle_language,
                'change language': self.toggle_language,
                'english': self.set_english,
                'russian': self.set_russian,
                'show settings': self.show_settings,
                'system settings': self.show_settings,
                'show parameters': self.show_settings,
            }
        }
    
    def setup_microphone(self):
        """Настраивает микрофон с обработкой ошибок"""
        try:
            # Проверяем доступность PyAudio
            if not PYAUDIO_AVAILABLE:
                raise MicrophoneError("PyAudio не установлен. Установите его командой: pip install pyaudio")
            
            # Пытаемся получить список микрофонов
            try:
                mic_list = sr.Microphone.list_microphone_names()
                if not mic_list:
                    raise MicrophoneError("Микрофоны не обнаружены в системе")
                
                print(f"Найдено микрофонов: {len(mic_list)}")
                for i, mic in enumerate(mic_list):
                    print(f"  {i}: {mic}")
                
                # Пытаемся использовать микрофон по умолчанию
                self.microphone = sr.Microphone()
                
                # Тестируем микрофон
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                self.microphone_available = True
                print("✅ Микрофон успешно настроен")
                
            except OSError as e:
                if "No Default Input Device Available" in str(e):
                    raise MicrophoneError("Микрофон по умолчанию не найден. Проверьте подключение микрофона.")
                else:
                    raise MicrophoneError(f"Ошибка доступа к микрофону: {str(e)}")
            except Exception as e:
                raise MicrophoneError(f"Ошибка настройки микрофона: {str(e)}")
                
        except MicrophoneError as e:
            self.microphone_available = False
            raise e
        except Exception as e:
            self.microphone_available = False
            raise MicrophoneError(f"Неизвестная ошибка микрофона: {str(e)}")
    
    def load_settings(self):
        """Загружает настройки из файла"""
        try:
            if os.path.exists('assistant_settings.json'):
                with open('assistant_settings.json', 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    self.settings.update(loaded_settings)
            else:
                self.save_settings()
        except Exception as e:
            print(f"Ошибка загрузки настроек: {e}")
    
    def save_settings(self):
        """Сохраняет настройки в файл"""
        try:
            with open('assistant_settings.json', 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения настроек: {e}")
    
    def set_voice(self, gender):
        """Устанавливает голос ассистента"""
        if not self.engine:
            return
            
        try:
            voices = self.engine.getProperty('voices')
            if len(voices) == 0:
                print("Нет доступных голосов")
                return
                
            if gender == 'female':
                # Ищем женский голос
                for voice in voices:
                    if 'female' in voice.name.lower() or 'женск' in voice.name.lower():
                        self.engine.setProperty('voice', voice.id)
                        break
                else:
                    # Если женский голос не найден, используем первый доступный
                    if len(voices) > 1:
                        self.engine.setProperty('voice', voices[1].id)
                    else:
                        self.engine.setProperty('voice', voices[0].id)
            else:
                # Используем мужской голос (обычно первый)
                self.engine.setProperty('voice', voices[0].id)
            
            self.settings['voice_gender'] = gender
            self.save_settings()
            
            # Обновляем GUI если есть callback
            if self.gui_callback:
                self.gui_callback('update_settings')
            
        except Exception as e:
            print(f"Ошибка установки голоса: {e}")
    
    def speak(self, text):
        """Произносит текст"""
        if not self.engine or not text:
            return
            
        def _speak():
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                print(f"Ошибка синтеза речи: {e}")
                
        threading.Thread(target=_speak, daemon=True).start()
    
    def listen(self, timeout=None, phrase_time_limit=None):
        """Слушает микрофон и распознает речь"""
        if not self.microphone_available or not self.microphone:
            return ""
            
        if timeout is None:
            timeout = self.settings['listen_timeout']
        if phrase_time_limit is None:
            phrase_time_limit = self.settings['phrase_time_limit']
        
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                text = self.recognizer.recognize_google(audio, language=self.current_lang)
                return text.lower()
                
        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            return ""
        except sr.RequestError as e:
            print(f"Ошибка сервиса распознавания: {e}")
            return ""
        except Exception as e:
            print(f"Ошибка распознавания речи: {e}")
            return ""
    
    def check_activation(self, text):
        """Проверяет, содержит ли текст активационную фразу"""
        if not text:
            return False, ""
        
        activation_phrases = [
            self.settings['activation_phrase'].lower(),
            self.settings['assistant_name'].lower(),
            'джарвис',
            'jarvis',
            'привет джарвис',
            'hello jarvis',
            'эй джарвис',
            'hey jarvis',
            'джарвис слушай',
            'jarvis listen'
        ]
        
        for phrase in activation_phrases:
            if phrase in text:
                # Удаляем активационную фразу из текста
                cleaned_text = text.replace(phrase, '').strip()
                # Удаляем запятые и лишние пробелы
                cleaned_text = re.sub(r'^[,\s]+', '', cleaned_text)
                return True, cleaned_text
        
        return False, text
    
    def process_command(self, command):
        """Обрабатывает команду"""
        if not command:
            return ""
        
        lang_commands = self.commands.get(self.current_lang, {})
        
        # Ищем точное совпадение команд
        for key, func in lang_commands.items():
            if command.startswith(key):
                args = command[len(key):].strip()
                
                # Команды с аргументами
                if key in ['открой', 'запусти', 'открыть', 'open', 'start', 'launch',
                          'создай заметку', 'запиши', 'записать', 'create note', 'write', 'take note',
                          'смени идентификатор', 'измени имя', 'новое имя', 'смени имя на', 'change name', 'new name',
                          'установи громкость', 'измени громкость', 'громкость', 'set volume', 'change volume', 'volume',
                          'установи скорость', 'измени скорость', 'скорость', 'set rate', 'change rate', 'rate']:
                    return func(args)
                else:
                    return func()
        
        # Ищем частичное совпадение
        for key, func in lang_commands.items():
            if key in command:
                args = command.replace(key, '').strip()
                
                if key in ['открой', 'запусти', 'открыть', 'open', 'start', 'launch',
                          'создай заметку', 'запиши', 'записать', 'create note', 'write', 'take note',
                          'смени идентификатор', 'измени имя', 'новое имя', 'смени имя на', 'change name', 'new name',
                          'установи громкость', 'измени громкость', 'громкость', 'set volume', 'change volume', 'volume',
                          'установи скорость', 'измени скорость', 'скорость', 'set rate', 'change rate', 'rate']:
                    return func(args)
                else:
                    return func()
        
        # Команда не распознана
        unknown_responses = {
            'ru-RU': "Не понял команду. Повторите, пожалуйста.",
            'en-US': "I didn't understand the command. Please repeat."
        }
        return unknown_responses.get(self.current_lang, "Command not understood.")
    
    # ========== НОВЫЕ ФУНКЦИИ ДЛЯ УПРАВЛЕНИЯ НАСТРОЙКАМИ ==========
    
    def change_name(self, new_name):
        """Изменяет имя ассистента"""
        if not new_name:
            responses = {
                'ru-RU': "Пожалуйста, укажите новое имя.",
                'en-US': "Please specify a new name."
            }
            return responses.get(self.current_lang, "Specify new name.")
        
        new_name = new_name.strip()
        self.settings['assistant_name'] = new_name
        self.settings['activation_phrase'] = new_name
        self.save_settings()
        
        # Обновляем GUI если есть callback
        if self.gui_callback:
            self.gui_callback('update_settings')
        
        responses = {
            'ru-RU': f"Имя изменено на {new_name}. Для активации говорите: {new_name}",
            'en-US': f"Name changed to {new_name}. To activate say: {new_name}"
        }
        return responses.get(self.current_lang, f"Name changed to {new_name}")
    
    def change_voice_mode(self, args=""):
        """Изменяет режим голоса"""
        current_gender = self.settings['voice_gender']
        
        if current_gender == 'male':
            new_gender = 'female'
            response = {
                'ru-RU': "Переключаю на женский голос",
                'en-US': "Switching to female voice"
            }
        else:
            new_gender = 'male'
            response = {
                'ru-RU': "Переключаю на мужской голос",
                'en-US': "Switching to male voice"
            }
        
        self.set_voice(new_gender)
        return response.get(self.current_lang, f"Switching to {new_gender} voice")
    
    def set_female_voice(self):
        """Устанавливает женский голос"""
        self.set_voice('female')
        responses = {
            'ru-RU': "Устанавливаю женский голос",
            'en-US': "Setting female voice"
        }
        return responses.get(self.current_lang, "Setting female voice")
    
    def set_male_voice(self):
        """Устанавливает мужской голос"""
        self.set_voice('male')
        responses = {
            'ru-RU': "Устанавливаю мужской голос",
            'en-US': "Setting male voice"
        }
        return responses.get(self.current_lang, "Setting male voice")
    
    def set_volume(self, volume_str):
        """Устанавливает громкость"""
        try:
            # Извлекаем число из строки
            volume_match = re.search(r'(\d+)', volume_str)
            if not volume_match:
                responses = {
                    'ru-RU': "Пожалуйста, укажите уровень громкости от 0 до 100",
                    'en-US': "Please specify volume level from 0 to 100"
                }
                return responses.get(self.current_lang, "Specify volume 0-100")
            
            volume = int(volume_match.group(1))
            
            # Проверяем диапазон
            if volume < 0:
                volume = 0
            elif volume > 100:
                volume = 100
            
            # Конвертируем в формат pyttsx3 (0.0 - 1.0)
            volume_normalized = volume / 100.0
            
            if self.engine:
                self.engine.setProperty('volume', volume_normalized)
            
            self.settings['volume'] = volume_normalized
            self.save_settings()
            
            # Обновляем GUI если есть callback
            if self.gui_callback:
                self.gui_callback('update_settings')
            
            responses = {
                'ru-RU': f"Громкость установлена на {volume}%",
                'en-US': f"Volume set to {volume}%"
            }
            return responses.get(self.current_lang, f"Volume set to {volume}%")
            
        except ValueError:
            responses = {
                'ru-RU': "Неверный формат громкости. Укажите число от 0 до 100",
                'en-US': "Invalid volume format. Please specify number from 0 to 100"
            }
            return responses.get(self.current_lang, "Invalid volume format")
    
    def set_rate(self, rate_str):
        """Устанавливает скорость речи"""
        try:
            # Извлекаем число из строки
            rate_match = re.search(r'(\d+)', rate_str)
            if not rate_match:
                responses = {
                    'ru-RU': "Пожалуйста, укажите скорость речи от 100 до 300",
                    'en-US': "Please specify speech rate from 100 to 300"
                }
                return responses.get(self.current_lang, "Specify rate 100-300")
            
            rate = int(rate_match.group(1))
            
            # Проверяем диапазон
            if rate < 100:
                rate = 100
            elif rate > 300:
                rate = 300
            
            if self.engine:
                self.engine.setProperty('rate', rate)
            
            self.settings['rate'] = rate
            self.save_settings()
            
            # Обновляем GUI если есть callback
            if self.gui_callback:
                self.gui_callback('update_settings')
            
            responses = {
                'ru-RU': f"Скорость речи установлена на {rate}",
                'en-US': f"Speech rate set to {rate}"
            }
            return responses.get(self.current_lang, f"Rate set to {rate}")
            
        except ValueError:
            responses = {
                'ru-RU': "Неверный формат скорости. Укажите число от 100 до 300",
                'en-US': "Invalid rate format. Please specify number from 100 to 300"
            }
            return responses.get(self.current_lang, "Invalid rate format")
    
    def toggle_language(self, args=""):
        """Переключает язык"""
        if self.current_lang == 'ru-RU':
            return self.set_english()
        else:
            return self.set_russian()
    
    def set_english(self):
        """Устанавливает английский язык"""
        self.current_lang = 'en-US'
        self.settings['language'] = 'en-US'
        self.save_settings()
        
        # Обновляем GUI если есть callback
        if self.gui_callback:
            self.gui_callback('update_settings')
        
        return "Language changed to English. Now I speak English."
    
    def set_russian(self):
        """Устанавливает русский язык"""
        self.current_lang = 'ru-RU'
        self.settings['language'] = 'ru-RU'
        self.save_settings()
        
        # Обновляем GUI если есть callback
        if self.gui_callback:
            self.gui_callback('update_settings')
        
        return "Язык изменён на русский. Теперь я говорю по-русски."
    
    def show_settings(self):
        """Показывает текущие настройки"""
        if self.current_lang == 'ru-RU':
            settings_text = f"""
ТЕКУЩИЕ НАСТРОЙКИ СИСТЕМЫ:

• Имя ассистента: {self.settings['assistant_name']}
• Фраза активации: {self.settings['activation_phrase']}
• Режим голоса: {'Мужской' if self.settings['voice_gender'] == 'male' else 'Женский'}
• Громкость: {int(self.settings['volume'] * 100)}%
• Скорость речи: {self.settings['rate']}
• Язык системы: {'Русский' if self.settings['language'] == 'ru-RU' else 'Английский'}
• Путь заметок: {self.settings['note_path']}
            """
        else:
            settings_text = f"""
CURRENT SYSTEM SETTINGS:

• Assistant name: {self.settings['assistant_name']}
• Activation phrase: {self.settings['activation_phrase']}
• Voice mode: {'Male' if self.settings['voice_gender'] == 'male' else 'Female'}
• Volume: {int(self.settings['volume'] * 100)}%
• Speech rate: {self.settings['rate']}
• System language: {'Russian' if self.settings['language'] == 'ru-RU' else 'English'}
• Notes path: {self.settings['note_path']}
            """
        
        return settings_text.strip()
    
    # ========== НОВАЯ ФУНКЦИЯ ДЛЯ ЗАКРЫТИЯ ПРОГРАММЫ ==========
    
    def exit_program(self):
        """Завершает работу программы"""
        self.is_listening = False
        self.is_activated = False
        
        responses = {
            'ru-RU': "Завершение работы системы. До свидания!",
            'en-US': "Shutting down the system. Goodbye!"
        }
        
        response = responses.get(self.current_lang, "Goodbye!")
        
        # Сообщаем GUI о необходимости закрытия
        if self.gui_callback:
            self.gui_callback('exit_program')
        
        return response
    
    # ========== СТАРЫЕ ФУНКЦИИ (остаются без изменений) ==========
    
    def open_app(self, app_name):
        """Открывает приложение"""
        if not app_name:
            responses = {
                'ru-RU': "Какое приложение открыть?",
                'en-US': "What application should I open?"
            }
            return responses.get(self.current_lang, "Specify application name.")
        
        apps = self.applications.get(self.current_lang, {})
        
        # Ищем приложение
        for key, command in apps.items():
            if key in app_name.lower():
                try:
                    # Заменяем переменные окружения
                    if '%USERNAME%' in command:
                        command = command.replace('%USERNAME%', os.getenv('USERNAME', ''))
                    
                    subprocess.Popen(command, shell=True)
                    responses = {
                        'ru-RU': f"Открываю {key}",
                        'en-US': f"Opening {key}"
                    }
                    return responses.get(self.current_lang, f"Opening {key}")
                except Exception as e:
                    print(f"Ошибка запуска приложения: {e}")
                    responses = {
                        'ru-RU': f"Не удалось открыть {key}",
                        'en-US': f"Failed to open {key}"
                    }
                    return responses.get(self.current_lang, f"Failed to open {key}")
        
        # Пытаемся запустить напрямую
        try:
            subprocess.Popen(app_name, shell=True)
            responses = {
                'ru-RU': f"Пытаюсь открыть {app_name}",
                'en-US': f"Trying to open {app_name}"
            }
            return responses.get(self.current_lang, f"Trying to open {app_name}")
        except Exception as e:
            print(f"Ошибка запуска: {e}")
            responses = {
                'ru-RU': f"Не могу открыть {app_name}",
                'en-US': f"Can't open {app_name}"
            }
            return responses.get(self.current_lang, f"Can't open {app_name}")
    
    def create_note(self, text):
        """Создает заметку"""
        if not text:
            responses = {
                'ru-RU': "Что записать в заметку?",
                'en-US': "What should I write in the note?"
            }
            return responses.get(self.current_lang, "Specify note text.")
        
        try:
            # Создаем директорию для заметок
            note_path = Path(self.settings['note_path'])
            note_dir = note_path.parent
            if not note_dir.exists():
                note_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            note_entry = f"[{timestamp}] {text}\n"
            
            with open(note_path, 'a', encoding='utf-8') as f:
                f.write(note_entry)
            
            responses = {
                'ru-RU': "Заметка сохранена",
                'en-US': "Note saved"
            }
            return responses.get(self.current_lang, "Note saved")
        except Exception as e:
            print(f"Ошибка сохранения заметки: {e}")
            responses = {
                'ru-RU': f"Ошибка сохранения: {str(e)}",
                'en-US': f"Save error: {str(e)}"
            }
            return responses.get(self.current_lang, f"Save error: {str(e)}")
    
    def shutdown_pc(self):
        """Выключает компьютер"""
        responses = {
            'ru-RU': "Выключаю компьютер через 10 секунд",
            'en-US': "Shutting down computer in 10 seconds"
        }
        self.speak(responses.get(self.current_lang, "Shutting down"))
        
        try:
            if os.name == 'nt':  # Windows
                subprocess.run(["shutdown", "/s", "/t", "10"], check=False)
            elif os.name == 'posix':  # Linux/Mac
                subprocess.run(["shutdown", "-h", "+10"], check=False)
        except Exception as e:
            print(f"Ошибка выключения: {e}")
        
        return responses.get(self.current_lang, "Shutting down computer")
    
    def reboot_pc(self):
        """Перезагружает компьютер"""
        responses = {
            'ru-RU': "Перезагружаю компьютер через 10 секунд",
            'en-US': "Rebooting computer in 10 seconds"
        }
        self.speak(responses.get(self.current_lang, "Rebooting"))
        
        try:
            if os.name == 'nt':
                subprocess.run(["shutdown", "/r", "/t", "10"], check=False)
            elif os.name == 'posix':
                subprocess.run(["shutdown", "-r", "+10"], check=False)
        except Exception as e:
            print(f"Ошибка перезагрузки: {e}")
        
        return responses.get(self.current_lang, "Rebooting computer")
    
    def greet(self):
        """Приветствие"""
        import random
        greetings = {
            'ru-RU': ["Привет! Чем могу помочь?", "Здравствуйте!", "Приветствую!", "Слушаю вас!"],
            'en-US': ["Hello! How can I help?", "Hi there!", "Greetings!", "I'm listening!"]
        }
        return random.choice(greetings.get(self.current_lang, ["Hello!"]))
    
    def goodbye(self):
        """Прощание"""
        farewells = {
            'ru-RU': "До свидания!",
            'en-US': "Goodbye!"
        }
        return farewells.get(self.current_lang, "Goodbye")
    
    def how_are_you(self):
        """Ответ на вопрос 'Как дела?'"""
        import random
        responses = {
            'ru-RU': ["Всё отлично, спасибо!", "Работаю в штатном режиме.", "Готов помогать!"],
            'en-US': ["Everything's great, thanks!", "Operating normally.", "Ready to help!"]
        }
        return random.choice(responses.get(self.current_lang, ["I'm fine, thank you!"]))
    
    def show_abilities(self):
        """Показывает возможности ассистента"""
        abilities = {
            'ru-RU': "Я могу: открывать приложения, создавать заметки, выключать или перезагружать компьютер, говорить время и дату, и многое другое. Скажите 'помощь' для списка команд.",
            'en-US': "I can: open applications, create notes, shutdown or reboot the computer, tell time and date, and more. Say 'help' for command list."
        }
        return abilities.get(self.current_lang, "I can help with various tasks.")
    
    def stop_listening(self):
        """Останавливает прослушивание"""
        self.is_activated = False
        responses = {
            'ru-RU': "Останавливаю прослушивание",
            'en-US': "Stopping listening"
        }
        return responses.get(self.current_lang, "Stopping")
    
    def start_listening(self):
        """Возобновляет прослушивание"""
        self.is_activated = True
        responses = {
            'ru-RU': "Продолжаю слушать",
            'en-US': "Resuming listening"
        }
        return responses.get(self.current_lang, "Resuming")
    
    def weather(self):
        """Информация о погоде"""
        responses = {
            'ru-RU': "Для получения погоды необходимо подключение к интернету и API сервиса погоды.",
            'en-US': "For weather information, internet connection and weather API are required."
        }
        return responses.get(self.current_lang, "Weather service not available")
    
    def current_time(self):
        """Текущее время"""
        now = datetime.datetime.now()
        if self.current_lang == 'ru-RU':
            time_str = now.strftime("%H:%M")
            return f"Сейчас {time_str}"
        else:
            time_str = now.strftime("%I:%M %p")
            return f"The time is {time_str}"
    
    def current_date(self):
        """Текущая дата"""
        now = datetime.datetime.now()
        if self.current_lang == 'ru-RU':
            date_str = now.strftime("%d %B %Y года")
            return f"Сегодня {date_str}"
        else:
            date_str = now.strftime("%B %d, %Y")
            return f"Today is {date_str}"
    
    def thank_you(self):
        """Ответ на благодарность"""
        responses = {
            'ru-RU': "Пожалуйста! Всегда рад помочь.",
            'en-US': "You're welcome! Always happy to help."
        }
        return responses.get(self.current_lang, "You're welcome!")
    
    def show_help(self):
        """Показывает справку по командам"""
        if self.current_lang == 'ru-RU':
            help_text = """
ДОСТУПНЫЕ КОМАНДЫ:

ОСНОВНЫЕ КОМАНДЫ:
• 'открой [приложение]' - открыть программу
• 'создай заметку [текст]' - создать заметку
• 'выключи компьютер' - выключить ПК
• 'перезагрузи' - перезагрузить компьютер
• 'сколько времени' - узнать время
• 'дата' - узнать дату
• 'стоп' - остановить прослушивание
• 'продолжи' - возобновить прослушивание
• 'что ты умеешь' - показать возможности
• 'пока' - завершить работу

КОМАНДЫ УПРАВЛЕНИЯ:
• 'смени идентификатор [новое имя]' - изменить имя
• 'измени режим голоса' - изменить голос
• 'установи громкость [0-100]' - установить громкость
• 'установи скорость [100-300]' - установить скорость
• 'переключи язык' - сменить язык
• 'покажи параметры' - показать настройки
            """
        else:
            help_text = """
AVAILABLE COMMANDS:

BASIC COMMANDS:
• 'open [application]' - open program
• 'create note [text]' - create note
• 'shutdown' - shutdown computer
• 'reboot' - reboot computer
• 'time' - current time
• 'date' - current date
• 'stop' - stop listening
• 'continue' - resume listening
• 'what can you do' - show abilities
• 'goodbye' - exit

SETTINGS COMMANDS:
• 'change name [new name]' - change assistant name
• 'change voice mode' - change voice gender
• 'set volume [0-100]' - set volume level
• 'set rate [100-300]' - set speech rate
• 'switch language' - change language
• 'show settings' - display current settings
            """
        return help_text.strip()
    
    def listening_loop(self, callback):
        """Основной цикл прослушивания"""
        if not self.microphone_available:
            callback("❌ Микрофон недоступен. Проверьте подключение микрофона.")
            return
        
        self.is_listening = True
        self.is_activated = True  # Начинаем в активном режиме
        
        while self.is_listening:
            try:
                if not self.is_activated:
                    # Ждем активации
                    callback("⏸️ Ожидание активации...")
                    text = self.listen(timeout=5)
                    
                    if text:
                        is_activated, command = self.check_activation(text)
                        if is_activated:
                            self.is_activated = True
                            callback("✅ Активирован! Слушаю команды...")
                            self.speak("Слушаю вас")
                else:
                    # Активный режим - слушаем команды
                    callback("🎤 Слушаю...")
                    text = self.listen()
                    
                    if text:
                        callback(f"🗣️ Вы сказали: {text}")
                        
                        # Проверяем команду остановки
                        if text in ['стоп', 'остановись', 'stop', 'stop listening']:
                            response = self.stop_listening()
                            callback(f"⏸️ {response}")
                            self.speak(response)
                            continue
                        
                        # Проверяем команду завершения работы
                        if text in ['пока', 'до свидания', 'завершение работы', 'заверши работу', 
                                   'goodbye', 'bye', 'exit', 'quit', 'close']:
                            response = self.exit_program()
                            callback(f"🤖 {response}")
                            self.speak(response)
                            time.sleep(2)  # Даем время на произнесение
                            # Сигнализируем о необходимости закрытия через callback
                            if 'exit_program' in text.lower() or 'close' in text.lower() or 'quit' in text.lower():
                                callback('exit_program')
                            continue
                        
                        response = self.process_command(text)
                        if response:
                            callback(f"🤖 {response}")
                            self.speak(response)
                    
            except Exception as e:
                error_msg = f"❌ Ошибка: {str(e)}"
                print(f"Ошибка в listening_loop: {e}")
                print(traceback.format_exc())
                callback(error_msg)
                # Пауза при ошибке
                time.sleep(1)
    
    def update_volume(self, volume):
        """Обновляет громкость"""
        if self.engine:
            try:
                self.engine.setProperty('volume', volume)
                self.settings['volume'] = volume
                self.save_settings()
            except Exception as e:
                print(f"Ошибка обновления громкости: {e}")
    
    def update_rate(self, rate):
        """Обновляет скорость речи"""
        if self.engine:
            try:
                self.engine.setProperty('rate', rate)
                self.settings['rate'] = rate
                self.save_settings()
            except Exception as e:
                print(f"Ошибка обновления скорости: {e}")

class ScrollableFrame(tk.Frame):
    """Прокручиваемый фрейм с поддержкой скролла мышью"""
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        # Создаем Canvas для скролла
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        
        self.scrollable_frame = tk.Frame(self.canvas)
        
        # Создаем окно на Canvas
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # Настройка скролла
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        # Настройка Canvas
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Размещаем Canvas и Scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Бинды для скролла мышью
        self.bind_mouse_scroll()
        
        # Устанавливаем фокус на Canvas для работы колесика мыши
        self.canvas.bind("<Enter>", lambda e: self.canvas.focus_set())
        
    def bind_mouse_scroll(self):
        """Привязывает события мыши для скролла"""
        # Скролл колесиком мыши
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)  # Linux
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)  # Linux
        
        # Скролл при наведении на любой элемент внутри
        def bind_to_children(widget):
            for child in widget.winfo_children():
                child.bind("<MouseWheel>", self._on_mousewheel)
                child.bind("<Button-4>", self._on_mousewheel)
                child.bind("<Button-5>", self._on_mousewheel)
                bind_to_children(child)
        
        # Привязываем скролл ко всем дочерним элементам
        bind_to_children(self.scrollable_frame)
        
    def _on_mousewheel(self, event):
        """Обработчик события колесика мыши"""
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")

class AssistantGUI:
    def __init__(self):
        self.assistant = None
        self.listening_thread = None
        self.microphone_error_shown = False
        self.message_queue = queue.Queue()  # Инициализируем очередь сообщений
        
        # Создаем главное окно
        self.root = tk.Tk()
        self.root.title("Голосовой ассистент J.A.R.V.I.S.")
        self.root.geometry("650x750")
        
        # Настраиваем закрытие окна
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Устанавливаем иконку
        try:
            if os.path.exists("jarvis_icon.ico"):
                self.root.iconbitmap("jarvis_icon.ico")
        except:
            pass
        
        # Инициализируем ассистента
        self.init_assistant()
        
        # Применяем футуристичную тему
        FuturisticStarkTheme.apply_theme(self.root)
        
        # Настраиваем интерфейс с прокручиваемым фреймом
        self.setup_ui()
        
        # Запускаем обработку очереди сообщений
        self.process_queue()
        
        # Запускаем ассистента если все ок
        if self.assistant and self.assistant.microphone_available:
            self.start_assistant()
    
    def init_assistant(self):
        """Инициализирует ассистента с обработкой ошибок"""
        try:
            self.assistant = VoiceAssistant(gui_callback=self.handle_assistant_callback)
            if not self.assistant.microphone_available and not self.microphone_error_shown:
                self.show_microphone_error("Микрофон не обнаружен. Проверьте подключение микрофона.")
        except MicrophoneError as e:
            if not self.microphone_error_shown:
                self.show_microphone_error(str(e))
        except ImportError as e:
            self.show_dependency_error(str(e))
        except Exception as e:
            self.show_general_error(f"Ошибка инициализации: {str(e)}")
    
    def handle_assistant_callback(self, action):
        """Обрабатывает callback от ассистента"""
        if action == 'update_settings':
            self.update_settings_display()
        elif action == 'exit_program':
            self.on_closing()
    
    def show_microphone_error(self, message=None):
        """Показывает ошибку микрофона в отдельном окне"""
        self.microphone_error_shown = True
        error_msg = message or "Микрофон не обнаружен. Проверьте подключение микрофона."
        
        # Создаем отдельное окно ошибки с футуристичным оформлением
        error_window = tk.Toplevel()
        error_window.title("ОШИБКА СИСТЕМЫ")
        error_window.geometry("500x300")
        
        # Применяем тему к окну ошибки
        FuturisticStarkTheme.apply_theme(error_window)
        
        # Центрируем окно
        error_window.update_idletasks()
        width = error_window.winfo_width()
        height = error_window.winfo_height()
        x = (error_window.winfo_screenwidth() // 2) - (width // 2)
        y = (error_window.winfo_screenheight() // 2) - (height // 2)
        error_window.geometry(f'{width}x{height}+{x}+{y}')
        
        # Запрещаем изменение размера
        error_window.resizable(False, False)
        
        # Содержимое окна ошибки
        frame = tk.Frame(error_window)
        frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Иконка ошибки в стиле Железного Человека
        error_icon = tk.Label(frame, text="⚡", font=('Arial', 48))
        error_icon.pack(pady=10)
        
        # Заголовок
        title_label = tk.Label(frame, text="СИСТЕМНАЯ ДИАГНОСТИКА", 
                              font=('Arial', 14, 'bold'))
        title_label.pack(pady=5)
        
        # Сообщение об ошибке
        error_label = tk.Label(frame, text=error_msg, font=('Arial', 11), 
                              wraplength=400, justify='center')
        error_label.pack(pady=10)
        
        # Кнопки в футуристичном стиле
        button_frame = tk.Frame(frame)
        button_frame.pack(pady=20)
        
        def retry():
            error_window.destroy()
            self.microphone_error_shown = False
            self.init_assistant()
            if self.assistant and self.assistant.microphone_available:
                self.start_assistant()
        
        retry_btn = FuturisticStarkTheme.create_futuristic_button(
            button_frame, 
            "🔄 ПЕРЕЗАПУСК СИСТЕМЫ", 
            retry
        )
        retry_btn.pack(side='left', padx=10)
        
        def continue_without_mic():
            error_window.destroy()
            self.add_message("⚠️ Ассистент запущен без микрофона")
            self.add_message("Используйте голосовые команды для управления")
        
        continue_btn = FuturisticStarkTheme.create_futuristic_button(
            button_frame,
            "▶️ ПРОДОЛЖИТЬ БЕЗ МИКРОФОНА",
            continue_without_mic
        )
        continue_btn.pack(side='left', padx=10)
        
        def exit_app():
            error_window.destroy()
            self.root.quit()
            sys.exit(0)
        
        exit_btn = FuturisticStarkTheme.create_futuristic_button(
            button_frame,
            "🚪 ЗАВЕРШЕНИЕ РАБОТЫ",
            exit_app
        )
        exit_btn.pack(side='left', padx=10)
        
        # Делаем окно модальным
        error_window.transient(self.root)
        error_window.grab_set()
        
        # Обработка закрытия окна
        error_window.protocol("WM_DELETE_WINDOW", exit_app)
        
        # Ждем, пока окно не закроется
        self.root.wait_window(error_window)
    
    def show_dependency_error(self, message):
        """Показывает ошибку зависимостей"""
        error_window = tk.Toplevel()
        error_window.title("СИСТЕМНАЯ ОШИБКА")
        error_window.geometry("500x200")
        
        # Применяем тему
        FuturisticStarkTheme.apply_theme(error_window)
        
        # Центрируем
        error_window.update_idletasks()
        width = error_window.winfo_width()
        height = error_window.winfo_height()
        x = (error_window.winfo_screenwidth() // 2) - (width // 2)
        y = (error_window.winfo_screenheight() // 2) - (height // 2)
        error_window.geometry(f'{width}x{height}+{x}+{y}')
        
        frame = tk.Frame(error_window)
        frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        tk.Label(frame, text="❌ ОТСУТСТВУЮТ КРИТИЧЕСКИЕ КОМПОНЕНТЫ", 
                font=('Arial', 14, 'bold')).pack(pady=10)
        
        tk.Label(frame, text=message, wraplength=400).pack(pady=10)
        
        def exit_app():
            error_window.destroy()
            self.root.quit()
            sys.exit(1)
        
        exit_btn = FuturisticStarkTheme.create_futuristic_button(
            frame,
            "🚪 ВЫХОД",
            exit_app
        )
        exit_btn.pack(pady=20)
        
        error_window.transient(self.root)
        error_window.grab_set()
        self.root.wait_window(error_window)
    
    def show_general_error(self, message):
        """Показывает общую ошибку"""
        error_window = tk.Toplevel()
        error_window.title("СИСТЕМНАЯ ОШИБКА")
        error_window.geometry("400x150")
        
        # Применяем тему
        FuturisticStarkTheme.apply_theme(error_window)
        
        frame = tk.Frame(error_window)
        frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        tk.Label(frame, text="❌ КРИТИЧЕСКИЙ СБОЙ", 
                font=('Arial', 14, 'bold')).pack(pady=10)
        
        tk.Label(frame, text=message, wraplength=350).pack(pady=10)
        
        def exit_app():
            error_window.destroy()
            self.root.quit()
            sys.exit(1)
        
        exit_btn = FuturisticStarkTheme.create_futuristic_button(
            frame,
            "🚪 ВЫХОД",
            exit_app
        )
        exit_btn.pack(pady=10)
        
        error_window.transient(self.root)
        error_window.grab_set()
        self.root.wait_window(error_window)
    
    def setup_ui(self):
        """Настраивает пользовательский интерфейс"""
        # Создаем стиль
        style = ttk.Style()
        style.theme_use('clam')
        
        # Создаем прокручиваемый фрейм
        self.scrollable_frame = ScrollableFrame(self.root)
        self.scrollable_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Получаем внутренний фрейм для добавления элементов
        inner_frame = self.scrollable_frame.scrollable_frame
        
        # Заголовок с логотипом
        title_frame = tk.Frame(inner_frame)
        title_frame.pack(fill='x', pady=(10, 5), padx=10)
        
        # Логотип J.A.R.V.I.S.
        logo_label = tk.Label(title_frame, text="⚡ J.A.R.V.I.S.", 
                            font=('Arial', 18, 'bold'))
        logo_label.pack(side='left')
        
        # Подзаголовок
        subtitle_label = tk.Label(title_frame, text="Голосовой ассистент", 
                                font=('Arial', 11))
        subtitle_label.pack(side='left', padx=(10, 0))
        
        # Индикатор статуса в футуристичном стиле
        status_frame = FuturisticStarkTheme.create_status_indicator(
            inner_frame, 
            "active" if (self.assistant and self.assistant.microphone_available) else "error"
        )
        status_frame.pack(fill='x', pady=5, padx=10)
        self.status_indicator = status_frame
        
        # Основная информация
        info_frame = ttk.LabelFrame(inner_frame, text="СИСТЕМА УПРАВЛЕНИЯ")
        info_frame.pack(fill='x', pady=5, padx=10)
        
        info_text = """
ДЛЯ АКТИВАЦИИ СКАЖИТЕ: "ДЖАРВИС"
        
ОСНОВНЫЕ КОМАНДЫ:
• ОТКРОЙ [ПРИЛОЖЕНИЕ] - запуск программы
• СОЗДАЙ ЗАМЕТКУ [ТЕКСТ] - создание записи
• СКОЛЬКО ВРЕМЕНИ - текущее время
• ДАТА - текущая дата
• СТОП - остановка прослушивания
• ПРОДОЛЖИ - возобновление работы
• ПОМОЩЬ - список команд
• ПОКА - завершение работы
        """
        
        info = tk.Label(info_frame, text=info_text, justify='left',
                       font=('Courier New', 9))
        info.pack(pady=5, padx=10, fill='both')
        
        # Настройки системы
        settings_frame = ttk.LabelFrame(inner_frame, text="КОНФИГУРАЦИЯ СИСТЕМЫ")
        settings_frame.pack(fill='x', pady=5, padx=10)
        
        # Имя и фраза активации
        name_frame = tk.Frame(settings_frame)
        name_frame.pack(fill='x', pady=2, padx=10)
        
        tk.Label(name_frame, text="ИДЕНТИФИКАТОР:").pack(side='left', padx=(0, 5))
        self.name_label = tk.Label(name_frame, 
                                  text=self.assistant.settings['assistant_name'].upper() if self.assistant else "J.A.R.V.I.S.",
                                  font=('Courier New', 10, 'bold'))
        self.name_label.pack(side='left')
        
        phrase_frame = tk.Frame(settings_frame)
        phrase_frame.pack(fill='x', pady=2, padx=10)
        
        tk.Label(phrase_frame, text="КОД АКТИВАЦИИ:").pack(side='left', padx=(0, 5))
        self.phrase_label = tk.Label(phrase_frame, 
                                    text=self.assistant.settings['activation_phrase'].upper() if self.assistant else "J.A.R.V.I.S.",
                                    font=('Courier New', 10, 'bold'))
        self.phrase_label.pack(side='left')
        
        # Настройки голоса
        voice_frame = ttk.LabelFrame(inner_frame, text="НАСТРОЙКИ ВОКАЛЬНОГО ИНТЕРФЕЙСА")
        voice_frame.pack(fill='x', pady=5, padx=10)
        
        voice_info = tk.Frame(voice_frame)
        voice_info.pack(fill='x', pady=2, padx=10)
        
        tk.Label(voice_info, text="РЕЖИМ ГОЛОСА:").pack(side='left', padx=(0, 10))
        self.voice_label = tk.Label(voice_info, 
                                   text="МУЖСКОЙ" if (self.assistant.settings['voice_gender'] if self.assistant else 'male') == 'male' else "ЖЕНСКИЙ",
                                   font=('Courier New', 9, 'bold'))
        self.voice_label.pack(side='left', padx=5)
        
        # Параметры системы
        params_frame = tk.Frame(voice_frame)
        params_frame.pack(fill='x', pady=2, padx=10)
        
        tk.Label(params_frame, text="ГРОМКОСТЬ:").pack(side='left', padx=(0, 10))
        self.volume_label = tk.Label(params_frame, 
                                    text=f"{int((self.assistant.settings['volume'] if self.assistant else 0.8) * 100)}%",
                                    font=('Courier New', 9, 'bold'))
        self.volume_label.pack(side='left')
        
        tk.Label(params_frame, text="│").pack(side='left', padx=10)
        
        tk.Label(params_frame, text="СКОРОСТЬ:").pack(side='left', padx=(0, 10))
        self.rate_label = tk.Label(params_frame, 
                                  text=f"{self.assistant.settings['rate'] if self.assistant else 150}",
                                  font=('Courier New', 9, 'bold'))
        self.rate_label.pack(side='left')
        
        # Язык системы
        lang_frame = ttk.LabelFrame(inner_frame, text="ЯЗЫКОВЫЕ НАСТРОЙКИ")
        lang_frame.pack(fill='x', pady=5, padx=10)
        
        self.lang_label = tk.Label(lang_frame, 
                                  text="РУССКИЙ 🇷🇺" if (self.assistant.settings['language'] if self.assistant else 'ru-RU') == 'ru-RU' else "ENGLISH 🇺🇸",
                                  font=('Courier New', 10, 'bold'))
        self.lang_label.pack(pady=5)
        
        # Система заметок
        note_frame = ttk.LabelFrame(inner_frame, text="СИСТЕМА ЗАПИСЕЙ")
        note_frame.pack(fill='x', pady=5, padx=10)
        
        note_info = tk.Frame(note_frame)
        note_info.pack(fill='x', pady=2, padx=10)
        
        tk.Label(note_info, text="ПУТЬ ХРАНЕНИЯ:").pack(side='left', padx=(0, 5))
        self.note_path_label = tk.Label(note_info, 
                                       text=self.assistant.settings['note_path'] if self.assistant else str(Path.home() / 'assistant_notes.txt'),
                                       font=('Courier New', 8), wraplength=300, justify='left')
        self.note_path_label.pack(side='left')
        
        # Расширенное управление
        control_frame = ttk.LabelFrame(inner_frame, text="РАСШИРЕННОЕ УПРАВЛЕНИЕ")
        control_frame.pack(fill='x', pady=5, padx=10)
        
        control_text = """
ДЛЯ ИЗМЕНЕНИЯ ПАРАМЕТРОВ СИСТЕМЫ СКАЖИТЕ:
• "СМЕНИ ИДЕНТИФИКАТОР НА [НОВОЕ ИМЯ]"
• "ИЗМЕНИ РЕЖИМ ГОЛОСА"
• "УСТАНОВИ ГРОМКОСТЬ [ОТ 0 ДО 100]"
• "УСТАНОВИ СКОРОСТЬ [ОТ 100 ДО 300]"
• "ПЕРЕКЛЮЧИ ЯЗЫК НА АНГЛИЙСКИЙ/РУССКИЙ"
• "ПОКАЖИ ПАРАМЕТРЫ СИСТЕМЫ"
        """
        
        control_label = tk.Label(control_frame, text=control_text, justify='left',
                               font=('Courier New', 8))
        control_label.pack(pady=5, padx=10, fill='both')
        
        # Системный лог (в самом низу)
        log_frame = ttk.LabelFrame(inner_frame, text="СИСТЕМНЫЙ ЛОГ")
        log_frame.pack(fill='x', pady=5, padx=10)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, wrap='word')
        self.log_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Добавляем прокрутку мышью к лог тексту
        self.bind_mouse_scroll_to_widget(self.log_text)
        
        # Добавляем начальное сообщение
        if self.assistant and self.assistant.microphone_available:
            self.add_message("⚡ СИСТЕМА J.A.R.V.I.S. ИНИЦИАЛИЗИРОВАНА")
            self.add_message("🎤 АУДИОИНТЕРФЕЙС АКТИВЕН")
            self.add_message("🗣️ ДЛЯ АКТИВАЦИИ СКАЖИТЕ: 'ДЖАРВИС'")
            self.add_message("🖱️ ИСПОЛЬЗУЙТЕ КОЛЕСИКО МЫШИ ДЛЯ ПРОКРУТКИ")
        else:
            self.add_message("⚠️ АУДИОИНТЕРФЕЙС НЕ ОБНАРУЖЕН")
            self.add_message("ℹ️ ИСПОЛЬЗУЙТЕ ГОЛОСОВЫЕ КОМАНДЫ")
            self.add_message("🗣️ ДЛЯ АКТИВАЦИИ СКАЖИТЕ: 'ДЖАРВИС'")
            self.add_message("🖱️ ИСПОЛЬЗУЙТЕ КОЛЕСИКО МЫШИ ДЛЯ ПРОКРУТКИ")
    
    def bind_mouse_scroll_to_widget(self, widget):
        """Привязывает скролл мышью к виджету"""
        widget.bind("<MouseWheel>", self._on_mousewheel)
        widget.bind("<Button-4>", self._on_mousewheel)  # Linux
        widget.bind("<Button-5>", self._on_mousewheel)  # Linux
    
    def _on_mousewheel(self, event):
        """Обработчик события колесика мыши для всего приложения"""
        # Передаем событие колесика мыши в Canvas для прокрутки
        if event.num == 4 or event.delta > 0:
            self.scrollable_frame.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.scrollable_frame.canvas.yview_scroll(1, "units")
    
    def start_assistant(self):
        """Запускает ассистента"""
        if self.assistant:
            # Устанавливаем голос
            self.assistant.set_voice(self.assistant.settings['voice_gender'])
            self.assistant.current_lang = self.assistant.settings['language']
            
            # Запускаем поток прослушивания
            self.listening_thread = threading.Thread(
                target=self.assistant.listening_loop,
                args=(self.add_message,),
                daemon=True
            )
            self.listening_thread.start()
            
            self.add_message("⚡ СИСТЕМА J.A.R.V.I.S. АКТИВИРОВАНА")
            
            # Обновляем отображение настроек
            self.update_settings_display()
    
    def add_message(self, message):
        """Добавляет сообщение в очередь"""
        self.message_queue.put(message)
    
    def process_queue(self):
        """Обрабатывает очередь сообщений"""
        try:
            while True:
                message = self.message_queue.get_nowait()
                
                # Проверяем, не является ли это сигналом о закрытии
                if message == 'exit_program':
                    self.on_closing()
                    return
                
                timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                self.log_text.insert('end', f"[{timestamp}] {message}\n")
                self.log_text.see('end')
                
                # Автоматическое обновление настроек при определенных сообщениях
                if "настройки" in message.lower() or "имя" in message.lower() or "язык" in message.lower():
                    self.update_settings_display()
                    
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.process_queue)
    
    def update_settings_display(self):
        """Обновляет отображение настроек"""
        if self.assistant:
            self.name_label.config(text=self.assistant.settings['assistant_name'].upper())
            self.phrase_label.config(text=self.assistant.settings['activation_phrase'].upper())
            self.voice_label.config(text="МУЖСКОЙ" if self.assistant.settings['voice_gender'] == 'male' else "ЖЕНСКИЙ")
            self.volume_label.config(text=f"{int(self.assistant.settings['volume'] * 100)}%")
            self.rate_label.config(text=f"{self.assistant.settings['rate']}")
            self.lang_label.config(text="РУССКИЙ 🇷🇺" if self.assistant.settings['language'] == 'ru-RU' else "ENGLISH 🇺🇸")
            self.note_path_label.config(text=self.assistant.settings['note_path'])
    
    def on_closing(self):
        """Обработка закрытия окна"""
        if self.assistant:
            self.assistant.is_listening = False
            self.assistant.is_activated = False
        
        # Используем голосовое подтверждение выхода
        if self.assistant and self.assistant.engine:
            self.assistant.speak("Завершение работы системы. До свидания")
            time.sleep(1)
        
        self.root.destroy()
        sys.exit(0)
    
    def run(self):
        """Запускает главный цикл"""
        # Центрируем окно
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
        self.root.mainloop()

def main():
    """Главная функция"""
    print("=" * 60)
    print("J.A.R.V.I.S. - Голосовой ассистент (версия Stark Industries)")
    print("=" * 60)
    
    # Проверяем зависимости
    if not SPEECH_RECOGNITION_AVAILABLE or not PYTTSX3_AVAILABLE or not PYAUDIO_AVAILABLE:
        print("\n❌ КРИТИЧЕСКИЕ КОМПОНЕНТЫ ОТСУТСТВУЮТ!")
        print("Для установки выполните:")
        print("pip install SpeechRecognition pyttsx3 pyaudio")
        input("\nНажмите Enter для выхода...")
        return
    
    # Запускаем приложение
    try:
        app = AssistantGUI()
        app.run()
    except Exception as e:
        print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА СИСТЕМЫ: {e}")
        print(traceback.format_exc())
        input("Нажмите Enter для выхода...")

if __name__ == "__main__":
    main()