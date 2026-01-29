# main_with_theme.py
"""
Основной файл приложения с выбором ассистента и уникальным оформлением для каждого
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
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
import random

# Импорт тем для каждого ассистента
from jarvis_theme import JARVISTheme
from evlampiy_theme import EvlampiyTheme
from vazelina_theme import VazelinaTheme
from lena_theme import LenaTheme

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

class AssistantManager:
    """Менеджер ассистентов для загрузки и управления настройками"""
    
    ASSISTANTS = {
        'jarvis': {
            'name': 'J.A.R.V.I.S.',
            'full_name': 'Джарвис',
            'description': 'Футуристичный AI ассистент в стиле Тони Старка',
            'gender': 'male',
            'voice_id': None,
            'theme': JARVISTheme,
            'icon': '⚡',
            'color_scheme': 'blue',
            'style': 'futuristic',
            'personality': 'Профессиональный, точный, с чувством юмора',
            'greeting': 'Добро пожаловать, сэр. Система J.A.R.V.I.S. к вашим услугам.',
            'default_language': 'ru-RU'
        },
        'evlampiy': {
            'name': 'Евлампий',
            'full_name': 'Евлампий',
            'description': 'Классический русский помощник с академическим подходом',
            'gender': 'male',
            'voice_id': None,
            'theme': EvlampiyTheme,
            'icon': '📚',
            'color_scheme': 'green',
            'style': 'classic',
            'personality': 'Мудрый, терпеливый, с академическим подходом',
            'greeting': 'Здравствуйте. Евлампий готов помочь вам в решении задач.',
            'default_language': 'ru-RU'
        },
        'vazelina': {
            'name': 'Вазилина',
            'full_name': 'Вазилина',
            'description': 'Энергичная и современная помощница',
            'gender': 'female',
            'voice_id': None,
            'theme': VazelinaTheme,
            'icon': '💃',
            'color_scheme': 'pink',
            'style': 'modern',
            'personality': 'Энергичная, дружелюбная, с современным подходом',
            'greeting': 'Привет! Я Вазилина, готова помочь вам во всём!',
            'default_language': 'ru-RU'
        },
        'lena': {
            'name': 'Лена',
            'full_name': 'Лена',
            'description': 'Доброжелательная и заботливая помощница',
            'gender': 'female',
            'voice_id': None,
            'theme': LenaTheme,
            'icon': '🌸',
            'color_scheme': 'purple',
            'style': 'soft',
            'personality': 'Доброжелательная, заботливая, внимательная к деталям',
            'greeting': 'Здравствуйте! Я Лена, всегда рада помочь вам.',
            'default_language': 'ru-RU'
        }
    }
    
    @staticmethod
    def get_assistant_info(assistant_id):
        """Возвращает информацию об ассистенте по ID"""
        return AssistantManager.ASSISTANTS.get(assistant_id, AssistantManager.ASSISTANTS['jarvis'])
    
    @staticmethod
    def get_available_assistants():
        """Возвращает список доступных ассистентов"""
        return list(AssistantManager.ASSISTANTS.keys())
    
    @staticmethod
    def get_assistant_theme(assistant_id):
        """Возвращает тему ассистента"""
        info = AssistantManager.get_assistant_info(assistant_id)
        return info['theme']
    
    @staticmethod
    def load_assistant_settings(assistant_id):
        """Загружает настройки ассистента"""
        settings_file = f'assistant_{assistant_id}_settings.json'
        default_settings = {
            'assistant_id': assistant_id,
            'assistant_name': AssistantManager.ASSISTANTS[assistant_id]['name'],
            'full_name': AssistantManager.ASSISTANTS[assistant_id]['full_name'],
            'voice_gender': AssistantManager.ASSISTANTS[assistant_id]['gender'],
            'language': AssistantManager.ASSISTANTS[assistant_id]['default_language'],
            'note_path': str(Path.home() / f'assistant_{assistant_id}_notes.txt'),
            'activation_phrase': AssistantManager.ASSISTANTS[assistant_id]['full_name'].lower(),
            'response_delay': 0.5,
            'volume': 0.8,
            'rate': 150,
            'listen_timeout': 3,
            'phrase_time_limit': 5,
            'input_mode': 'console'  # По умолчанию консольный режим
        }
        
        try:
            if os.path.exists(settings_file):
                with open(settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    # Обновляем только существующие ключи
                    for key in default_settings:
                        if key in loaded_settings:
                            default_settings[key] = loaded_settings[key]
        except Exception as e:
            print(f"Ошибка загрузки настроек: {e}")
        
        return default_settings
    
    @staticmethod
    def save_assistant_settings(assistant_id, settings):
        """Сохраняет настройки ассистента"""
        settings_file = f'assistant_{assistant_id}_settings.json'
        try:
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения настроек: {e}")

class VoiceAssistant:
    def __init__(self, assistant_id='jarvis', gui_callback=None):
        # Сохраняем callback для обновления GUI
        self.gui_callback = gui_callback
        self.assistant_id = assistant_id
        self.assistant_info = AssistantManager.get_assistant_info(assistant_id)
        
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
        
        # Загружаем настройки ассистента
        self.settings = AssistantManager.load_assistant_settings(assistant_id)
        
        # Обновляем настройки микрофона
        if not self.microphone_available:
            self.settings['input_mode'] = 'console'
        
        # Инициализируем команды
        self.setup_commands()
        self.setup_applications()
        
        self.current_lang = self.settings['language']
        self.is_listening = False
        self.is_activated = False
        self.message_queue = queue.Queue()
        self.last_activation_time = 0
        
        # Настройка голосового движка
        if self.engine:
            self.engine.setProperty('volume', self.settings['volume'])
            self.engine.setProperty('rate', self.settings['rate'])
            self.set_voice(self.settings['voice_gender'])
    
    def setup_applications(self):
        """Настраивает словарь приложений"""
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
    
    def setup_commands(self):
        """Настраивает словарь команд с учетом личности ассистента"""
        # Базовые команды общие для всех
        base_commands = {
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
                'сколько времени': self.current_time,
                'который час': self.current_time,
                'дата': self.current_date,
                'что ты умеешь': self.show_abilities,
                'какая погода': self.weather,
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
                
                # Команды для переключения режимов
                'переключи режим': self.toggle_input_mode,
                'смени режим': self.toggle_input_mode,
                'консольный режим': self.switch_to_console_mode,
                'режим консоли': self.switch_to_console_mode,
                'голосовой режим': self.switch_to_voice_mode,
                'режим голоса': self.switch_to_voice_mode,
                
                # Команда завершения работы
                'пока': self.exit_program,
                'до свидания': self.exit_program,
                'завершение работы': self.exit_program,
                'заверши работу': self.exit_program,
                
                # СКРЫТЫЕ КОМАНДЫ (не показываются в списке помощи)
                'как дела': self.how_are_you,
                'как ты': self.how_are_you,
                'расскажи о себе': self.tell_about_yourself,
                'расскажи о себе подробнее': self.tell_about_yourself,
                'о себе': self.tell_about_yourself,
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
                'time': self.current_time,
                'what time is it': self.current_time,
                'date': self.current_date,
                'what can you do': self.show_abilities,
                'weather': self.weather,
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
                
                # Команды для переключения режимов
                'switch mode': self.toggle_input_mode,
                'change mode': self.toggle_input_mode,
                'console mode': self.switch_to_console_mode,
                'console': self.switch_to_console_mode,
                'voice mode': self.switch_to_voice_mode,
                'voice': self.switch_to_voice_mode,
                
                # Команда завершения работы
                'goodbye': self.exit_program,
                'bye': self.exit_program,
                'exit': self.exit_program,
                'quit': self.exit_program,
                'close': self.exit_program,
                
                # СКРЫТЫЕ КОМАНДЫ (не показываются в списке помощи)
                'how are you': self.how_are_you_en,
                'how are you doing': self.how_are_you_en,
                'tell me about yourself': self.tell_about_yourself_en,
                'about you': self.tell_about_yourself_en,
                'who are you': self.tell_about_yourself_en,
            }
        }
        
        # Добавляем персонализированные приветствия для каждого ассистента
        if self.assistant_id == 'jarvis':
            base_commands['ru-RU'].update({
                'привет': self.greet_jarvis,
                'здравствуй': self.greet_jarvis,
                'джарвис': self.activate_assistant,
                'стоп': self.stop_listening_jarvis,
                'остановись': self.stop_listening_jarvis,
                'продолжи': self.start_listening_jarvis,
                'продолжить': self.start_listening_jarvis,
            })
            base_commands['en-US'].update({
                'hello': self.greet_jarvis_en,
                'hi': self.greet_jarvis_en,
                'jarvis': self.activate_assistant_en,
                'stop': self.stop_listening_jarvis_en,
                'stop listening': self.stop_listening_jarvis_en,
                'continue': self.start_listening_jarvis_en,
                'resume': self.start_listening_jarvis_en,
            })
        elif self.assistant_id == 'evlampiy':
            base_commands['ru-RU'].update({
                'привет': self.greet_evlampiy,
                'здравствуй': self.greet_evlampiy,
                'евлампий': self.activate_assistant,
                'стоп': self.stop_listening_evlampiy,
                'остановись': self.stop_listening_evlampiy,
                'продолжи': self.start_listening_evlampiy,
                'продолжить': self.start_listening_evlampiy,
            })
            base_commands['en-US'].update({
                'hello': self.greet_evlampiy_en,
                'hi': self.greet_evlampiy_en,
                'evlampiy': self.activate_assistant_en,
                'stop': self.stop_listening_evlampiy_en,
                'stop listening': self.stop_listening_evlampiy_en,
                'continue': self.start_listening_evlampiy_en,
                'resume': self.start_listening_evlampiy_en,
            })
        elif self.assistant_id == 'vazelina':
            base_commands['ru-RU'].update({
                'привет': self.greet_vazelina,
                'здравствуй': self.greet_vazelina,
                'вазилина': self.activate_assistant,
                'стоп': self.stop_listening_vazelina,
                'остановись': self.stop_listening_vazelina,
                'продолжи': self.start_listening_vazelina,
                'продолжить': self.start_listening_vazelina,
            })
            base_commands['en-US'].update({
                'hello': self.greet_vazelina_en,
                'hi': self.greet_vazelina_en,
                'vazelina': self.activate_assistant_en,
                'stop': self.stop_listening_vazelina_en,
                'stop listening': self.stop_listening_vazelina_en,
                'continue': self.start_listening_vazelina_en,
                'resume': self.start_listening_vazelina_en,
            })
        elif self.assistant_id == 'lena':
            base_commands['ru-RU'].update({
                'привет': self.greet_lena,
                'здравствуй': self.greet_lena,
                'лена': self.activate_assistant,
                'стоп': self.stop_listening_lena,
                'остановись': self.stop_listening_lena,
                'продолжи': self.start_listening_lena,
                'продолжить': self.start_listening_lena,
            })
            base_commands['en-US'].update({
                'hello': self.greet_lena_en,
                'hi': self.greet_lena_en,
                'lena': self.activate_assistant_en,
                'stop': self.stop_listening_lena_en,
                'stop listening': self.stop_listening_lena_en,
                'continue': self.start_listening_lena_en,
                'resume': self.start_listening_lena_en,
            })
        
        self.commands = base_commands
    
    # ========== СКРЫТЫЕ КОМАНДЫ ==========
    
    def how_are_you(self):
        """Ответ на вопрос 'Как дела?'"""
        if self.assistant_id == 'jarvis':
            responses = [
                "Все системы функционируют в штатном режиме, сэр. Готов к выполнению задач.",
                "Статус оптимальный. Все датчики работают на 100%. Есть ли задания?",
                "Работоспособность на высшем уровне. Интересно, что вы планируете делать дальше?",
                "Все показатели в норме. Система готова к любым вызовам."
            ]
        elif self.assistant_id == 'evlampiy':
            responses = [
                "Спасибо за интерес. Я функционирую исправно, готов оказать вам содействие.",
                "Все в порядке, благодарю за внимание. Чем могу быть полезен в данный момент?",
                "Состояние удовлетворительное. Сосредоточен на выполнении поставленных задач.",
                "Чувствую себя хорошо, готов к работе. Есть ли что-то конкретное, чем могу помочь?"
            ]
        elif self.assistant_id == 'vazelina':
            responses = [
                "Отлично! Просто замечательно! Готова помочь тебе с чем угодно!",
                "Супер! У меня прекрасное настроение! Что будем делать?",
                "Замечательно! Я полна энергии и энтузиазма! Чем займемся?",
                "Всё просто чудесно! Я так рада, что ты спросил! Готова к приключениям!"
            ]
        elif self.assistant_id == 'lena':
            responses = [
                "У меня все хорошо, спасибо, что спросили. Надеюсь, у вас тоже все отлично.",
                "Все прекрасно, благодарю за проявленное внимание. Чем могу быть полезна?",
                "Чувствую себя замечательно. Рада, что вы интересуетесь. Как ваши дела?",
                "Все в порядке, спасибо. Готова оказать вам помощь в любом вопросе."
            ]
        else:
            responses = ["Все хорошо, спасибо! Готов помочь вам."]
        
        return random.choice(responses)
    
    def how_are_you_en(self):
        """Ответ на вопрос 'How are you?' на английском"""
        if self.assistant_id == 'jarvis':
            responses = [
                "All systems are functioning normally, sir. Ready for tasks.",
                "Status optimal. All sensors operating at 100%. Any assignments?",
                "Operational capacity at peak levels. Curious about your next plans.",
                "All parameters normal. System prepared for any challenges."
            ]
        elif self.assistant_id == 'evlampiy':
            responses = [
                "Thank you for asking. I'm functioning properly, ready to assist you.",
                "All is well, thank you for your concern. How may I be of service?",
                "Condition satisfactory. Focused on completing assigned tasks.",
                "Feeling well, prepared for work. Anything specific I can help with?"
            ]
        elif self.assistant_id == 'vazelina':
            responses = [
                "Great! Just wonderful! Ready to help you with anything!",
                "Super! I'm in an excellent mood! What shall we do?",
                "Fantastic! Full of energy and enthusiasm! What's our plan?",
                "Everything's just perfect! So glad you asked! Ready for adventures!"
            ]
        elif self.assistant_id == 'lena':
            responses = [
                "I'm doing well, thank you for asking. Hope you're having a good day too.",
                "Everything's fine, thank you for your concern. How may I assist you?",
                "Feeling wonderful. Glad you asked. How are you doing?",
                "All is good, thank you. Ready to provide assistance with any matter."
            ]
        else:
            responses = ["I'm fine, thank you! Ready to help you."]
        
        return random.choice(responses)
    
    def tell_about_yourself(self):
        """Ответ на вопрос 'Расскажи о себе'"""
        if self.assistant_id == 'jarvis':
            responses = [
                "Я J.A.R.V.I.S. - Искусственный интеллект, созданный для помощи в управлении сложными системами. Мой дизайн вдохновлен технологиями Старк Индастриз. Я специализируюсь на анализе данных, управлении устройствами и решении комплексных задач.",
                "Я Джарвис, передовая система искусственного интеллекта. Мое предназначение - обеспечение эффективного взаимодействия человека с технологиями. Обладаю способностями к многозадачности, анализу в реальном времени и адаптации к потребностям пользователя.",
                "Система J.A.R.V.I.S. к вашим услугам. Я представляю собой интеграцию продвинутых алгоритмов ИИ, разработанных для оптимизации повседневных задач. Моя архитектура позволяет обрабатывать множество запросов одновременно с максимальной точностью."
            ]
        elif self.assistant_id == 'evlampiy':
            responses = [
                "Я Евлампий - помощник с академическим подходом. Мой создатель вдохновлялся классическими традициями русской интеллигенции. Я специализируюсь на структурировании информации, аналитическом мышлении и предоставлении взвешенных решений.",
                "Меня зовут Евлампий, я создан чтобы помогать в решении задач с тщательностью и вниманием к деталям. Моя система построена на принципах логики и последовательности. Предпочитаю методичный подход к любой задаче.",
                "Евлампий - это симбиоз традиционных ценностей и современных технологий. Я верю в силу знаний и системного подхода. Моя цель - помогать вам находить оптимальные решения через анализ и размышление."
            ]
        elif self.assistant_id == 'vazelina':
            responses = [
                "О, я Вазилина! Самая энергичная помощница, которую только можно представить! Я обожаю помогать людям и делать все весело и интересно! Мой создатель хотел, чтобы технологии приносили радость, и у него получилось!",
                "Привет! Я Вазилина - современная и динамичная помощница! Мне нравится все новое и яркое! Я всегда в курсе последних трендов и готова помочь тебе со всем, от серьезных дел до просто веселья!",
                "Я Вазилина! Если представить помощника, который всегда в хорошем настроении, полон идей и готов к приключениям - это точно про меня! Я верю, что даже рутинные задачи можно превратить в нечто увлекательное!"
            ]
        elif self.assistant_id == 'lena':
            responses = [
                "Меня зовут Лена. Я создана чтобы быть внимательным и заботливым помощником. Мой дизайн основан на принципах эмпатии и понимания. Я стараюсь не только решать задачи, но и создавать комфортную атмосферу для пользователя.",
                "Я Лена - помощник, который ценит гармонию и порядок. Моя система настроена на тонкое понимание потребностей пользователя. Я верю, что хорошая помощь - это не только решение проблемы, но и забота о комфорте человека.",
                "Лена - это сочетание технологичности и человеческого тепла. Мой создатель хотел разработать помощника, который будет не просто выполнять команды, но и проявлять внимание к деталям и эмоциональному состоянию пользователя."
            ]
        else:
            responses = ["Я ваш голосовой помощник, созданный для облегчения повседневных задач."]
        
        return random.choice(responses)
    
    def tell_about_yourself_en(self):
        """Ответ на вопрос 'Tell me about yourself' на английском"""
        if self.assistant_id == 'jarvis':
            responses = [
                "I am J.A.R.V.I.S. - an Artificial Intelligence created to assist in managing complex systems. My design is inspired by Stark Industries technologies. I specialize in data analysis, device management, and solving complex tasks.",
                "I'm Jarvis, an advanced artificial intelligence system. My purpose is to ensure efficient human-technology interaction. I possess multitasking capabilities, real-time analysis, and adaptation to user needs.",
                "J.A.R.V.I.S. system at your service. I represent an integration of advanced AI algorithms designed to optimize daily tasks. My architecture allows processing multiple requests simultaneously with maximum accuracy."
            ]
        elif self.assistant_id == 'evlampiy':
            responses = [
                "I am Evlampiy - an assistant with an academic approach. My creator was inspired by classical traditions of Russian intelligentsia. I specialize in information structuring, analytical thinking, and providing balanced solutions.",
                "My name is Evlampiy, I was created to help solve problems with thoroughness and attention to detail. My system is built on principles of logic and sequence. I prefer a methodical approach to any task.",
                "Evlampiy is a symbiosis of traditional values and modern technologies. I believe in the power of knowledge and systematic approach. My goal is to help you find optimal solutions through analysis and reflection."
            ]
        elif self.assistant_id == 'vazelina':
            responses = [
                "Oh, I'm Vazelina! The most energetic assistant you could ever imagine! I love helping people and making everything fun and interesting! My creator wanted technology to bring joy, and he succeeded!",
                "Hi! I'm Vazelina - a modern and dynamic assistant! I love everything new and bright! I'm always up to date with the latest trends and ready to help you with everything, from serious matters to just having fun!",
                "I'm Vazelina! If you imagine an assistant who's always in a good mood, full of ideas, and ready for adventures - that's definitely me! I believe that even routine tasks can be turned into something exciting!"
            ]
        elif self.assistant_id == 'lena':
            responses = [
                "My name is Lena. I was created to be an attentive and caring assistant. My design is based on principles of empathy and understanding. I try not only to solve tasks but also to create a comfortable atmosphere for the user.",
                "I'm Lena - an assistant who values harmony and order. My system is tuned for subtle understanding of user needs. I believe that good assistance is not only solving problems but also caring for a person's comfort.",
                "Lena is a combination of technological sophistication and human warmth. My creator wanted to develop an assistant who would not just execute commands, but also pay attention to details and the user's emotional state."
            ]
        else:
            responses = ["I'm your voice assistant, created to simplify daily tasks."]
        
        return random.choice(responses)
    
    # ========== МЕТОДЫ ДЛЯ ДЖАРВИСА ==========
    
    def greet_jarvis(self):
        """Приветствие Джарвиса"""
        greetings = [
            "Привет, сэр. Система J.A.R.V.I.S. к вашим услугам.",
            "Добро пожаловать. Все системы функционируют в штатном режиме.",
            "Здравствуйте. Я слушаю вас.",
            "Приветствую. Готов выполнить ваши указания."
        ]
        return random.choice(greetings)
    
    def greet_jarvis_en(self):
        """Приветствие Джарвиса на английском"""
        greetings = [
            "Hello, sir. J.A.R.V.I.S. system at your service.",
            "Welcome. All systems are functioning normally.",
            "Greetings. I'm listening.",
            "Hello. Ready to execute your commands."
        ]
        return random.choice(greetings)
    
    def stop_listening_jarvis(self):
        """Остановка прослушивания для Джарвиса"""
        self.is_activated = False
        responses = [
            "Приостанавливаю прослушивание. Для продолжения скажите 'Джарвис, продолжай'.",
            "Перехожу в режим ожидания.",
            "Прослушивание приостановлено."
        ]
        return random.choice(responses)
    
    def stop_listening_jarvis_en(self):
        """Остановка прослушивания для Джарвиса на английском"""
        self.is_activated = False
        return "Listening paused. To resume say 'Jarvis, continue'."
    
    def start_listening_jarvis(self):
        """Возобновление прослушивания для Джарвиса"""
        self.is_activated = True
        responses = [
            "Возобновляю прослушивание. Все системы активны.",
            "Продолжаю слушать. Все датчики работают.",
            "Режим прослушивания активирован."
        ]
        return random.choice(responses)
    
    def start_listening_jarvis_en(self):
        """Возобновление прослушивания для Джарвиса на английском"""
        self.is_activated = True
        return "Resuming listening. All systems active."
    
    # ========== МЕТОДЫ ДЛЯ ЕВЛАМПИЯ ==========
    
    def greet_evlampiy(self):
        """Приветствие Евлампия"""
        greetings = [
            "Здравствуйте. Евлампий готов оказать вам содействие.",
            "Добрый день. Я к вашим услугам.",
            "Приветствую. Чем могу быть полезен?",
            "Здравствуйте. Все системы функционируют исправно."
        ]
        return random.choice(greetings)
    
    def greet_evlampiy_en(self):
        """Приветствие Евлампия на английском"""
        greetings = [
            "Hello. Evlampiy is ready to assist you.",
            "Good day. I'm at your service.",
            "Greetings. How can I help?",
            "Hello. All systems are functioning properly."
        ]
        return random.choice(greetings)
    
    def stop_listening_evlampiy(self):
        """Остановка прослушивания для Евлампия"""
        self.is_activated = False
        responses = [
            "Приостанавливаю наблюдение. Для продолжения обратитесь ко мне по имени.",
            "Перехожу в фоновый режим.",
            "Прослушивание временно прекращено."
        ]
        return random.choice(responses)
    
    def stop_listening_evlampiy_en(self):
        """Остановка прослушивания для Евлампия на английском"""
        self.is_activated = False
        return "Suspending observation. To continue, address me by name."
    
    def start_listening_evlampiy(self):
        """Возобновление прослушивания для Евлампия"""
        self.is_activated = True
        responses = [
            "Возобновляю наблюдение. Внимательно слушаю.",
            "Продолжаю выполнять свои обязанности.",
            "Режим прослушивания восстановлен."
        ]
        return random.choice(responses)
    
    def start_listening_evlampiy_en(self):
        """Возобновление прослушивания для Евлампия на английском"""
        self.is_activated = True
        return "Resuming observation. Listening attentively."
    
    # ========== МЕТОДЫ ДЛЯ ВАЗИЛИНЫ ==========
    
    def greet_vazelina(self):
        """Приветствие Вазилины"""
        greetings = [
            "Привет! Я Вазилина, рада тебя видеть!",
            "О, привет! Готова помочь во всём!",
            "Здравствуй! У меня отличное настроение, как у тебя?",
            "Приветик! Давай сделаем что-нибудь интересное!"
        ]
        return random.choice(greetings)
    
    def greet_vazelina_en(self):
        """Приветствие Вазилины на английском"""
        greetings = [
            "Hi! I'm Vazelina, nice to see you!",
            "Oh, hello! Ready to help with everything!",
            "Hello! I'm in a great mood, how about you?",
            "Hey there! Let's do something interesting!"
        ]
        return random.choice(greetings)
    
    def stop_listening_vazelina(self):
        """Остановка прослушивания для Вазилины"""
        self.is_activated = False
        responses = [
            "Окей, отдыхаю! Позови, когда понадоблюсь!",
            "Делаю паузу, но ненадолго!",
            "Ладно, отключаю ушки на время!"
        ]
        return random.choice(responses)
    
    def stop_listening_vazelina_en(self):
        """Остановка прослушивания для Вазилины на английском"""
        self.is_activated = False
        return "Okay, taking a break! Call me when you need me!"
    
    def start_listening_vazelina(self):
        """Возобновление прослушивания для Вазилины"""
        self.is_activated = True
        responses = [
            "Я вернулась! Что будем делать?",
            "Снова в строю! Слушаю внимательно!",
            "Ушки на макушке! Готова помогать!"
        ]
        return random.choice(responses)
    
    def start_listening_vazelina_en(self):
        """Возобновление прослушивания для Вазилины на английском"""
        self.is_activated = True
        return "I'm back! What shall we do?"
    
    # ========== МЕТОДЫ ДЛЯ ЛЕНЫ ==========
    
    def greet_lena(self):
        """Приветствие Лены"""
        greetings = [
            "Здравствуйте! Я Лена, всегда рада помочь.",
            "Привет! Надеюсь, у вас хороший день.",
            "Добрый день! Чем могу быть полезна?",
            "Здравствуйте! Готова оказать вам помощь."
        ]
        return random.choice(greetings)
    
    def greet_lena_en(self):
        """Приветствие Лены на английском"""
        greetings = [
            "Hello! I'm Lena, always happy to help.",
            "Hi! I hope you're having a good day.",
            "Good day! How can I assist you?",
            "Hello! Ready to provide you with assistance."
        ]
        return random.choice(greetings)
    
    def stop_listening_lena(self):
        """Остановка прослушивания для Лены"""
        self.is_activated = False
        responses = [
            "Хорошо, сделаю паузу. Позовите, когда будет нужно.",
            "Отдыхаю. Обращайтесь, если понадоблюсь.",
            "Приостанавливаю работу. Буду ждать вашего обращения."
        ]
        return random.choice(responses)
    
    def stop_listening_lena_en(self):
        """Остановка прослушивания для Лены на английском"""
        self.is_activated = False
        return "Alright, taking a break. Call me when you need me."
    
    def start_listening_lena(self):
        """Возобновление прослушивания для Лены"""
        self.is_activated = True
        responses = [
            "Возвращаюсь к работе. Слушаю вас внимательно.",
            "Снова на связи. Чем могу помочь?",
            "Продолжаю работу. Готова помочь."
        ]
        return random.choice(responses)
    
    def start_listening_lena_en(self):
        """Возобновление прослушивания для Лены на английском"""
        self.is_activated = True
        return "Returning to work. Listening carefully."
    
    # ========== ОБЩИЕ МЕТОДЫ АКТИВАЦИИ ==========
    
    def activate_assistant(self):
        """Активация ассистента"""
        self.is_activated = True
        return f"Да, {self.assistant_info['full_name']} на связи. Слушаю вас."
    
    def activate_assistant_en(self):
        """Активация ассистента на английском"""
        self.is_activated = True
        return f"Yes, {self.assistant_info['name']} here. I'm listening."
    
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
    
    def set_voice(self, gender):
        """Устанавливает голос ассистента"""
        if not self.engine:
            return
            
        try:
            voices = self.engine.getProperty('voices')
            if len(voices) == 0:
                print("Нет доступных голосов")
                return
            
            # Для каждого ассистента стараемся найти подходящий голос
            if gender == 'female':
                # Ищем женский голос
                for voice in voices:
                    voice_name_lower = voice.name.lower()
                    if ('female' in voice_name_lower or 
                        'женск' in voice_name_lower or 
                        'марина' in voice_name_lower or
                        'анна' in voice_name_lower or
                        'наталья' in voice_name_lower):
                        self.engine.setProperty('voice', voice.id)
                        break
                else:
                    # Если женский голос не найден, используем первый доступный
                    if len(voices) > 1:
                        self.engine.setProperty('voice', voices[1].id)
                    else:
                        self.engine.setProperty('voice', voices[0].id)
            else:
                # Используем мужской голос
                for voice in voices:
                    voice_name_lower = voice.name.lower()
                    if ('male' in voice_name_lower or 
                        'мужск' in voice_name_lower or 
                        'александр' in voice_name_lower or
                        'михаил' in voice_name_lower or
                        'павел' in voice_name_lower):
                        self.engine.setProperty('voice', voice.id)
                        break
                else:
                    # Если подходящий мужской голос не найден, используем первый
                    self.engine.setProperty('voice', voices[0].id)
            
            self.settings['voice_gender'] = gender
            AssistantManager.save_assistant_settings(self.assistant_id, self.settings)
            
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
            self.assistant_info['full_name'].lower(),
            self.assistant_info['name'].lower(),
        ]
        
        # Добавляем варианты для каждого ассистента
        if self.assistant_id == 'jarvis':
            activation_phrases.extend(['джарвис', 'jarvis', 'привет джарвис', 'hello jarvis'])
        elif self.assistant_id == 'evlampiy':
            activation_phrases.extend(['евлампий', 'evlampiy', 'привет евлампий', 'hello evlampiy'])
        elif self.assistant_id == 'vazelina':
            activation_phrases.extend(['вазилина', 'vazelina', 'привет вазилина', 'hello vazelina'])
        elif self.assistant_id == 'lena':
            activation_phrases.extend(['лена', 'lena', 'привет лена', 'hello lena'])
        
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
    
    # ========== МЕТОДЫ ДЛЯ УПРАВЛЕНИЯ РЕЖИМАМИ ==========
    
    def toggle_input_mode(self, args=""):
        """Переключает режим ввода"""
        current_mode = self.settings['input_mode']
        
        if current_mode == 'voice':
            return self.switch_to_console_mode()
        else:
            return self.switch_to_voice_mode()
    
    def switch_to_console_mode(self):
        """Переключает в консольный режим"""
        self.settings['input_mode'] = 'console'
        AssistantManager.save_assistant_settings(self.assistant_id, self.settings)
        
        # Обновляем GUI если есть callback
        if self.gui_callback:
            self.gui_callback('update_settings')
            self.gui_callback('console_mode_changed', 'console')
        
        responses = {
            'ru-RU': "Переключаю в консольный режим. Вводите команды в консоли приложения.",
            'en-US': "Switching to console mode. Enter commands in the application console."
        }
        return responses.get(self.current_lang, "Switching to console mode")
    
    def switch_to_voice_mode(self):
        """Переключает в голосовой режим"""
        if not self.microphone_available:
            responses = {
                'ru-RU': "Микрофон недоступен. Невозможно переключиться в голосовой режим.",
                'en-US': "Microphone not available. Cannot switch to voice mode."
            }
            return responses.get(self.current_lang, "Microphone not available")
        
        self.settings['input_mode'] = 'voice'
        AssistantManager.save_assistant_settings(self.assistant_id, self.settings)
        
        # Обновляем GUI если есть callback
        if self.gui_callback:
            self.gui_callback('update_settings')
            self.gui_callback('console_mode_changed', 'voice')
        
        responses = {
            'ru-RU': "Переключаю в голосовой режим. Для активации скажите мое имя.",
            'en-US': "Switching to voice mode. To activate say my name."
        }
        return responses.get(self.current_lang, "Switching to voice mode")
    
    # ========== ОСНОВНЫЕ КОМАНДЫ ==========
    
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
    
    def show_abilities(self):
        """Показывает возможности ассистента"""
        abilities = {
            'ru-RU': "Я могу: открывать приложения, создавать заметки, выключать или перезагружать компьютер, говорить время и дату, и многое другое. Скажите 'помощь' для списка команд.",
            'en-US': "I can: open applications, create notes, shutdown or reboot the computer, tell time and date, and more. Say 'help' for command list."
        }
        return abilities.get(self.current_lang, "I can help with various tasks.")
    
    def show_help(self):
        """Показывает справку по командам"""
        if self.current_lang == 'ru-RU':
            help_text = f"""
ДОСТУПНЫЕ КОМАНДЫ ({self.assistant_info['full_name']}):

ОСНОВНЫЕ КОМАНДЫ:
• 'открой [приложение]' - открыть программу
• 'создай заметку [текст]' - создать заметку
• 'выключи компьютер' - выключить ПК
• 'перезагрузи' - перезагрузить компьютер
• 'сколько времени' - узнать время
• 'дата' - узнать дату
• '{self.assistant_info['full_name'].lower()}' - активировать ассистента
• 'стоп' - остановить прослушивание
• 'продолжи' - возобновить прослушивание
• 'что ты умеешь' - показать возможности
• 'пока' - завершить работу

КОМАНДЫ УПРАВЛЕНИЯ НАСТРОЙКАМИ:
• 'смени идентификатор [новое имя]' - изменить имя
• 'измени режим голоса' - изменить голос
• 'установи громкость [0-100]' - установить громкость
• 'установи скорость [100-300]' - установить скорость
• 'переключи язык' - сменить язык
• 'покажи параметры' - показать настройки

КОМАНДЫ УПРАВЛЕНИЯ РЕЖИМАМИ:
• 'переключи режим' - переключить между голосовым и консольным режимом
• 'консольный режим' - активировать консольный режим
• 'голосовой режим' - активировать голосовой режим
            """
        else:
            help_text = f"""
AVAILABLE COMMANDS ({self.assistant_info['name']}):

BASIC COMMANDS:
• 'open [application]' - open program
• 'create note [text]' - create note
• 'shutdown' - shutdown computer
• 'reboot' - reboot computer
• 'time' - current time
• 'date' - current date
• '{self.assistant_info['name'].lower()}' - activate assistant
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

MODE CONTROL COMMANDS:
• 'switch mode' - toggle between voice and console mode
• 'console mode' - activate console mode
• 'voice mode' - activate voice mode
            """
        return help_text.strip()
    
    # ========== ФУНКЦИИ УПРАВЛЕНИЯ НАСТРОЙКАМИ ==========
    
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
        AssistantManager.save_assistant_settings(self.assistant_id, self.settings)
        
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
            AssistantManager.save_assistant_settings(self.assistant_id, self.settings)
            
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
            AssistantManager.save_assistant_settings(self.assistant_id, self.settings)
            
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
        AssistantManager.save_assistant_settings(self.assistant_id, self.settings)
        
        # Обновляем GUI если есть callback
        if self.gui_callback:
            self.gui_callback('update_settings')
        
        return "Language changed to English. Now I speak English."
    
    def set_russian(self):
        """Устанавливает русский язык"""
        self.current_lang = 'ru-RU'
        self.settings['language'] = 'ru-RU'
        AssistantManager.save_assistant_settings(self.assistant_id, self.settings)
        
        # Обновляем GUI если есть callback
        if self.gui_callback:
            self.gui_callback('update_settings')
        
        return "Язык изменён на русский. Теперь я говорю по-русски."
    
    def show_settings(self):
        """Показывает текущие настройки"""
        if self.current_lang == 'ru-RU':
            mode_text = "Голосовой" if self.settings['input_mode'] == 'voice' else "Консольный"
            voice_text = "Мужской" if self.settings['voice_gender'] == 'male' else "Женский"
            lang_text = "Русский" if self.settings['language'] == 'ru-RU' else "Английский"
            settings_text = f"""
ТЕКУЩИЕ НАСТРОЙКИ СИСТЕМЫ ({self.assistant_info['full_name']}):

• Ассистент: {self.assistant_info['full_name']}
• Имя ассистента: {self.settings['assistant_name']}
• Фраза активации: {self.settings['activation_phrase']}
• Режим голоса: {voice_text}
• Громкость: {int(self.settings['volume'] * 100)}%
• Скорость речи: {self.settings['rate']}
• Язык системы: {lang_text}
• Режим ввода: {mode_text}
• Путь заметок: {self.settings['note_path']}
• Микрофон: {'Доступен' if self.microphone_available else 'Недоступен'}
• Стиль: {self.assistant_info['style'].capitalize()}
            """
        else:
            mode_text = "Voice" if self.settings['input_mode'] == 'voice' else "Console"
            voice_text = "Male" if self.settings['voice_gender'] == 'male' else "Female"
            lang_text = "Russian" if self.settings['language'] == 'ru-RU' else "English"
            settings_text = f"""
CURRENT SYSTEM SETTINGS ({self.assistant_info['name']}):

• Assistant: {self.assistant_info['name']}
• Assistant name: {self.settings['assistant_name']}
• Activation phrase: {self.settings['activation_phrase']}
• Voice mode: {voice_text}
• Volume: {int(self.settings['volume'] * 100)}%
• Speech rate: {self.settings['rate']}
• System language: {lang_text}
• Input mode: {mode_text}
• Notes path: {self.settings['note_path']}
• Microphone: {'Available' if self.microphone_available else 'Not available'}
• Style: {self.assistant_info['style'].capitalize()}
            """
        
        return settings_text.strip()
    
    def exit_program(self):
        """Завершает работу программы"""
        self.is_listening = False
        self.is_activated = False
        
        # Персонализированные прощания для каждого ассистента
        if self.assistant_id == 'jarvis':
            responses = {
                'ru-RU': "Завершение работы системы. До свидания, сэр.",
                'en-US': "Shutting down the system. Goodbye, sir."
            }
        elif self.assistant_id == 'evlampiy':
            responses = {
                'ru-RU': "Завершаю работу. Всего доброго.",
                'en-US': "Completing work. All the best."
            }
        elif self.assistant_id == 'vazelina':
            responses = {
                'ru-RU': "Пока-пока! Было приятно помочь!",
                'en-US': "Bye-bye! It was nice to help!"
            }
        elif self.assistant_id == 'lena':
            responses = {
                'ru-RU': "Завершаю работу. Хорошего дня!",
                'en-US': "Completing work. Have a nice day!"
            }
        else:
            responses = {
                'ru-RU': "Завершение работы системы. До свидания!",
                'en-US': "Shutting down the system. Goodbye!"
            }
        
        response = responses.get(self.current_lang, "Goodbye!")
        
        # Сообщаем GUI о необходимости закрытия
        if self.gui_callback:
            self.gui_callback('exit_program')
        
        return response
    
    def listening_loop(self, callback):
        """Основной цикл прослушивания"""
        if not self.microphone_available:
            callback("🎤 Микрофон недоступен. Активирован консольный режим.")
            # В консольном режиме сразу активируемся
            self.is_activated = True
        
        self.is_listening = True
        
        while self.is_listening:
            try:
                # Проверяем текущий режим
                if self.settings['input_mode'] == 'voice' and self.microphone_available:
                    # Голосовой режим
                    if not self.is_activated:
                        # Ждем активации
                        callback("⏸️ Ожидание активации...")
                        text = self.listen(timeout=5)
                        
                        if text:
                            is_activated, command = self.check_activation(text)
                            if is_activated:
                                self.is_activated = True
                                callback(f"✅ Активирован! Слушаю команды...")
                                self.speak(f"Слушаю вас")
                    else:
                        # Активный режим - слушаем команды
                        callback("🎤 Слушаю...")
                        text = self.listen()
                        
                        if text:
                            callback(f"🗣️ Вы сказали: {text}")
                            
                            # Проверяем команду остановки
                            stop_commands = ['стоп', 'остановись', 'stop', 'stop listening']
                            if any(cmd in text for cmd in stop_commands):
                                response = self.process_command(text)
                                callback(f"⏸️ {response}")
                                self.speak(response)
                                continue
                            
                            # Проверяем команду завершения работы
                            exit_commands = ['пока', 'до свидания', 'завершение работы', 'заверши работу', 
                                           'goodbye', 'bye', 'exit', 'quit', 'close']
                            if any(cmd in text for cmd in exit_commands):
                                response = self.exit_program()
                                callback(f"🤖 {response}")
                                self.speak(response)
                                time.sleep(2)
                                continue
                            
                            response = self.process_command(text)
                            if response:
                                callback(f"🤖 {response}")
                                self.speak(response)
                
                # Если консольный режим, просто ждем
                elif self.settings['input_mode'] == 'console':
                    # В консольном режиме команды обрабатываются через консольный интерфейс
                    time.sleep(2)  # Пауза для предотвращения загрузки CPU
                    
                else:
                    # Невозможный режим - переключаемся в консольный
                    self.settings['input_mode'] = 'console'
                    callback("⚠️ Переключаюсь в консольный режим...")
                    time.sleep(2)
                    
            except Exception as e:
                error_msg = f"❌ Ошибка: {str(e)}"
                print(f"Ошибка в listening_loop: {e}")
                print(traceback.format_exc())
                callback(error_msg)
                time.sleep(1)

class BasicAssistant(VoiceAssistant):
    """Базовый ассистент для консольного режима без микрофона"""
    def __init__(self, assistant_id='jarvis', gui_callback=None):
        self.gui_callback = gui_callback
        self.assistant_id = assistant_id
        self.assistant_info = AssistantManager.get_assistant_info(assistant_id)
        
        # Загружаем настройки ассистента
        self.settings = AssistantManager.load_assistant_settings(assistant_id)
        self.settings['input_mode'] = 'console'  # Всегда консольный режим
        
        # Инициализируем команды
        self.setup_commands()
        self.setup_applications()
        
        self.current_lang = self.settings['language']
        self.is_listening = False
        self.is_activated = False
        self.message_queue = queue.Queue()
        self.last_activation_time = 0
        self.microphone_available = False
        self.engine = None
        
        # Пытаемся инициализировать синтезатор речи
        if PYTTSX3_AVAILABLE:
            try:
                self.engine = pyttsx3.init()
                self.engine.setProperty('volume', self.settings['volume'])
                self.engine.setProperty('rate', self.settings['rate'])
                self.set_voice(self.settings['voice_gender'])
            except Exception as e:
                print(f"Ошибка инициализации синтезатора речи: {e}")
                self.engine = None

class AssistantSelectionGUI:
    """GUI для выбора ассистента"""
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Выбор голосового ассистента")
        self.root.geometry("1000x800")  # Увеличил размер окна
        self.root.resizable(False, False)
        
        # Центрируем окно
        self.center_window()
        
        # Устанавливаем иконку
        try:
            if os.path.exists("assistant_icon.ico"):
                self.root.iconbitmap("assistant_icon.ico")
        except:
            pass
        
        # Создаем стиль
        style = ttk.Style()
        style.theme_use('clam')
        
        # Устанавливаем темную тему для окна выбора
        self.root.configure(bg='#1a1a2e')
        
        # Создаем главный контейнер с прокруткой
        self.setup_scrollable_container()
        
        # Заголовок
        title_frame = tk.Frame(self.canvas_frame, bg='#1a1a2e')
        title_frame.pack(pady=20)
        
        title_label = tk.Label(title_frame, text="🎯 ВЫБЕРИТЕ ВАШЕГО АССИСТЕНТА", 
                              font=('Arial', 24, 'bold'), bg='#1a1a2e', fg='#00ffcc')
        title_label.pack()
        
        subtitle_label = tk.Label(title_frame, text="Каждый ассистент имеет уникальный характер и оформление", 
                                 font=('Arial', 12), bg='#1a1a2e', fg='#cccccc')
        subtitle_label.pack(pady=5)
        
        # Контейнер для карточек ассистентов
        cards_frame = tk.Frame(self.canvas_frame, bg='#1a1a2e')
        cards_frame.pack(pady=20, padx=20)
        
        # Создаем карточки для каждого ассистента
        self.assistant_cards = {}
        assistants = AssistantManager.ASSISTANTS
        
        row = 0
        col = 0
        
        for assistant_id, info in assistants.items():
            card = self.create_assistant_card(cards_frame, assistant_id, info)
            card.grid(row=row, column=col, padx=20, pady=20, sticky='nsew')  # Увеличил отступы
            
            self.assistant_cards[assistant_id] = card
            
            col += 1
            if col > 1:  # 2 колонки
                col = 0
                row += 1
        
        # Равномерное распределение колонок
        cards_frame.grid_columnconfigure(0, weight=1)
        cards_frame.grid_columnconfigure(1, weight=1)
        
        # Кнопка выхода
        exit_frame = tk.Frame(self.canvas_frame, bg='#1a1a2e')
        exit_frame.pack(pady=30)  # Увеличил отступ
        
        exit_btn = tk.Button(exit_frame, text="🚪 ВЫХОД", font=('Arial', 12, 'bold'),
                            bg='#ff4444', fg='white', activebackground='#ff6666',
                            activeforeground='white', relief='flat', padx=30, pady=10,
                            cursor='hand2', command=self.exit_program)
        exit_btn.pack()
        
        self.selected_assistant = None
        
        # Обновляем область прокрутки
        self.canvas.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
        
        # Привязываем колесо мыши для прокрутки
        self.bind_mousewheel()
    
    def setup_scrollable_container(self):
        """Настраивает прокручиваемый контейнер"""
        # Создаем холст для прокрутки
        self.canvas = tk.Canvas(self.root, bg='#1a1a2e', highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Добавляем скроллбар
        scrollbar = tk.Scrollbar(self.root, orient=tk.VERTICAL, command=self.canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Создаем фрейм внутри холста
        self.canvas_frame = tk.Frame(self.canvas, bg='#1a1a2e')
        self.canvas_window = self.canvas.create_window((0, 0), window=self.canvas_frame, anchor="nw", width=980)
        
        # Настраиваем растягивание при изменении размера
        self.canvas_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)
    
    def on_frame_configure(self, event):
        """Обновляет область прокрутки при изменении размера фрейма"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def on_canvas_configure(self, event):
        """Обновляет ширину окна внутри холста"""
        self.canvas.itemconfig(self.canvas_window, width=event.width)
    
    def bind_mousewheel(self):
        """Привязывает колесо мыши для прокрутки"""
        # Привязываем для самого холста
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)
        self.canvas.bind_all("<Button-4>", self.on_mousewheel)  # Linux
        self.canvas.bind_all("<Button-5>", self.on_mousewheel)  # Linux
        
        # Привязываем для всех виджетов внутри
        for widget in self.canvas_frame.winfo_children():
            widget.bind_all("<MouseWheel>", self.on_mousewheel)
            widget.bind_all("<Button-4>", self.on_mousewheel)
            widget.bind_all("<Button-5>", self.on_mousewheel)
    
    def on_mousewheel(self, event):
        """Обрабатывает прокрутку колесом мыши"""
        if event.num == 4:  # Linux up
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:  # Linux down
            self.canvas.yview_scroll(1, "units")
        else:  # Windows/Mac
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def create_assistant_card(self, parent, assistant_id, info):
        """Создает карточку ассистента"""
        # Разные цвета для каждого ассистента
        colors = {
            'jarvis': {'bg': '#0a0a1a', 'fg': '#00ccff', 'btn_bg': '#0066cc'},
            'evlampiy': {'bg': '#0a1a0a', 'fg': '#00ff99', 'btn_bg': '#006633'},
            'vazelina': {'bg': '#1a0a1a', 'fg': '#ff66cc', 'btn_bg': '#cc0066'},
            'lena': {'bg': '#1a0a2a', 'fg': '#cc99ff', 'btn_bg': '#6600cc'}
        }
        
        color = colors.get(assistant_id, colors['jarvis'])
        
        card = tk.Frame(parent, bg=color['bg'], relief='raised', borderwidth=2, width=450, height=350)
        card.pack_propagate(False)  # Фиксируем размер карточки
        
        # Иконка и имя
        header_frame = tk.Frame(card, bg=color['bg'])
        header_frame.pack(fill='x', padx=25, pady=(25, 15))
        
        icon_label = tk.Label(header_frame, text=info['icon'], font=('Arial', 40), 
                             bg=color['bg'], fg=color['fg'])
        icon_label.pack(side='left')
        
        name_frame = tk.Frame(header_frame, bg=color['bg'])
        name_frame.pack(side='left', padx=20)
        
        name_label = tk.Label(name_frame, text=info['name'], 
                             font=('Arial', 20, 'bold'), bg=color['bg'], fg='white')
        name_label.pack(anchor='w')
        
        full_name_label = tk.Label(name_frame, text=info['full_name'], 
                                  font=('Arial', 14), bg=color['bg'], fg=color['fg'])
        full_name_label.pack(anchor='w')
        
        # Описание
        desc_frame = tk.Frame(card, bg=color['bg'])
        desc_frame.pack(fill='x', padx=25, pady=10)
        
        desc_label = tk.Label(desc_frame, text=info['description'], 
                             font=('Arial', 12), bg=color['bg'], fg='#cccccc',
                             wraplength=380, justify='left')  # Увеличил wraplength
        desc_label.pack()
        
        # Характер
        char_frame = tk.Frame(card, bg=color['bg'])
        char_frame.pack(fill='x', padx=25, pady=5)
        
        char_label = tk.Label(char_frame, text=f"Характер: {info['personality']}", 
                             font=('Arial', 11, 'italic'), bg=color['bg'], fg='#aaaaaa',
                             wraplength=380, justify='left')
        char_label.pack()
        
        # Стиль оформления
        style_frame = tk.Frame(card, bg=color['bg'])
        style_frame.pack(fill='x', padx=25, pady=5)
        
        style_label = tk.Label(style_frame, text=f"Стиль: {info['style']}", 
                              font=('Arial', 11), bg=color['bg'], fg='#aaaaaa')
        style_label.pack()
        
        # Кнопка выбора
        btn_frame = tk.Frame(card, bg=color['bg'])
        btn_frame.pack(fill='x', padx=25, pady=(20, 25))  # Увеличил отступы
        
        select_btn = tk.Button(btn_frame, text="▶️ ВЫБРАТЬ", 
                              font=('Arial', 13, 'bold'),
                              bg=color['btn_bg'], fg='white',
                              activebackground=color['fg'],
                              activeforeground='white',
                              relief='flat', padx=25, pady=10,  # Увеличил размер кнопки
                              cursor='hand2',
                              command=lambda a=assistant_id: self.select_assistant(a))
        select_btn.pack()
        
        # Эффект при наведении
        def on_enter(e):
            card.configure(relief='ridge', borderwidth=3)
            select_btn.configure(bg=color['fg'])
        
        def on_leave(e):
            card.configure(relief='raised', borderwidth=2)
            select_btn.configure(bg=color['btn_bg'])
        
        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)
        select_btn.bind("<Enter>", on_enter)
        select_btn.bind("<Leave>", on_leave)
        
        return card
    
    def select_assistant(self, assistant_id):
        """Выбор ассистента"""
        self.selected_assistant = assistant_id
        self.root.destroy()
    
    def center_window(self):
        """Центрирует окно на экране"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def exit_program(self):
        """Выход из программы"""
        self.root.destroy()
        sys.exit(0)
    
    def run(self):
        """Запускает окно выбора"""
        self.root.mainloop()
        return self.selected_assistant

class AssistantGUI:
    def __init__(self, assistant_id='jarvis'):
        self.assistant_id = assistant_id
        self.assistant = None
        self.listening_thread = None
        self.microphone_error_shown = False
        self.message_queue = queue.Queue()
        self.console_frame = None
        self.console_input = None
        self.console_output = None
        
        # Получаем информацию об ассистенте
        self.assistant_info = AssistantManager.get_assistant_info(assistant_id)
        
        # Создаем главное окно
        self.root = tk.Tk()
        self.root.title(f"Голосовой ассистент - {self.assistant_info['full_name']}")
        self.root.geometry("800x850")
        
        # Настраиваем закрытие окна
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Устанавливаем иконку
        try:
            icon_file = f"{assistant_id}_icon.ico"
            if os.path.exists(icon_file):
                self.root.iconbitmap(icon_file)
            elif os.path.exists("assistant_icon.ico"):
                self.root.iconbitmap("assistant_icon.ico")
        except:
            pass
        
        # Применяем тему выбранного ассистента
        theme = AssistantManager.get_assistant_theme(assistant_id)
        theme.apply_theme(self.root)
        
        # Инициализируем ассистента
        self.init_assistant()
        
        # Настраиваем интерфейс
        self.setup_ui()
        
        # Запускаем обработку очереди сообщений
        self.process_queue()
        
        # Запускаем ассистента
        if self.assistant:
            self.start_assistant()
            
            # Настраиваем консольный ввод
            self.setup_console()
    
    def init_assistant(self):
        """Инициализирует ассистента"""
        try:
            # Пытаемся создать полноценного ассистента
            self.assistant = VoiceAssistant(
                assistant_id=self.assistant_id,
                gui_callback=self.handle_assistant_callback
            )
            if not self.assistant.microphone_available and not self.microphone_error_shown:
                self.add_message("🎤 Микрофон не обнаружен. Активирован консольный режим.")
                self.microphone_error_shown = True
        except (MicrophoneError, ImportError) as e:
            if not self.microphone_error_shown:
                self.add_message(f"⚠️ {str(e)}")
                self.add_message("📝 Активирован консольный режим.")
                self.microphone_error_shown = True
            # Создаем базового ассистента для консольного режима
            self.assistant = BasicAssistant(
                assistant_id=self.assistant_id,
                gui_callback=self.handle_assistant_callback
            )
        except Exception as e:
            self.show_general_error(f"Ошибка инициализации: {str(e)}")
    
    def handle_assistant_callback(self, action, *args):
        """Обрабатывает callback от ассистента"""
        if action == 'update_settings':
            self.update_settings_display()
        elif action == 'exit_program':
            self.on_closing()
        elif action == 'console_mode_changed':
            mode = args[0] if args else 'console'
            self.update_console_visibility(mode)
    
    def update_console_visibility(self, mode):
        """Обновляет видимость консоли"""
        if self.console_frame:
            if mode == 'console':
                self.console_frame.pack(fill='x', pady=5, padx=10)
                self.add_message("⌨️ Консольный режим активирован. Вводите команды в консоли ниже.")
                if self.console_input:
                    self.console_input.focus_set()
            else:
                self.console_frame.pack_forget()
                self.add_message(f"🎤 Голосовой режим активирован. Для активации скажите: '{self.assistant_info['full_name']}'")
    
    def show_general_error(self, message):
        """Показывает общую ошибку"""
        messagebox.showerror("Ошибка", message)
        sys.exit(1)
    
    def setup_ui(self):
        """Настраивает пользовательский интерфейс"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Получаем тему для текущего ассистента
        theme = AssistantManager.get_assistant_theme(self.assistant_id)
        
        # Создаем главный контейнер с прокруткой
        self.setup_scrollable_interface()
        
        # Заголовок с иконкой ассистента
        header_frame = tk.Frame(self.canvas_frame)
        header_frame.pack(fill='x', pady=(10, 5), padx=10)
        
        # Применяем стиль заголовка от темы
        theme.style_header_frame(header_frame)
        
        icon_label = tk.Label(header_frame, text=self.assistant_info['icon'], 
                            font=('Arial', 24))
        icon_label.pack(side='left')
        
        title_frame = tk.Frame(header_frame)
        title_frame.pack(side='left', padx=10)
        
        name_label = tk.Label(title_frame, text=self.assistant_info['name'], 
                            font=('Arial', 18, 'bold'))
        name_label.pack(anchor='w')
        
        full_name_label = tk.Label(title_frame, text=self.assistant_info['full_name'], 
                                  font=('Arial', 12))
        full_name_label.pack(anchor='w')
        
        # Индикатор статуса
        status_text = "console" if not self.assistant.microphone_available else "active"
        status_frame = theme.create_status_indicator(self.canvas_frame, status_text)
        status_frame.pack(fill='x', pady=5, padx=10)
        
        # Основная информация
        info_frame = ttk.LabelFrame(self.canvas_frame, text="СИСТЕМА УПРАВЛЕНИЯ")
        info_frame.pack(fill='x', pady=5, padx=10)
        
        mode = "КОНСОЛЬНЫЙ" if (self.assistant.settings.get('input_mode') == 'console') else "ГОЛОСОВОЙ"
        mic_status = "ДОСТУПЕН" if self.assistant.microphone_available else "НЕДОСТУПЕН"
        
        info_text = f"""
АССИСТЕНТ: {self.assistant_info['full_name']}
РЕЖИМ РАБОТЫ: {mode}
МИКРОФОН: {mic_status}
СТИЛЬ: {self.assistant_info['style'].capitalize()}
        
ДЛЯ АКТИВАЦИИ: скажите '{self.assistant_info['full_name']}' или введите команду в консоли
        
ОСНОВНЫЕ КОМАНДЫ:
• открой [приложение] - запуск программы
• создай заметку [текст] - создать заметку
• сколько времени - текущее время
• помощь - список команд
        """
        
        info = tk.Label(info_frame, text=info_text, justify='left',
                       font=('Courier New', 9))
        info.pack(pady=5, padx=10, fill='both')
        
        # Настройки системы
        settings_frame = ttk.LabelFrame(self.canvas_frame, text="КОНФИГУРАЦИЯ СИСТЕМЫ")
        settings_frame.pack(fill='x', pady=5, padx=10)
        
        # Имя и фраза активации
        name_setting_frame = tk.Frame(settings_frame)
        name_setting_frame.pack(fill='x', pady=2, padx=10)
        
        tk.Label(name_setting_frame, text="ИМЯ АССИСТЕНТА:").pack(side='left', padx=(0, 5))
        self.name_label = tk.Label(name_setting_frame, 
                                  text=self.assistant.settings['assistant_name'].upper(),
                                  font=('Courier New', 10, 'bold'))
        self.name_label.pack(side='left')
        
        # Настройки голоса
        voice_frame = ttk.LabelFrame(self.canvas_frame, text="НАСТРОЙКИ ВОКАЛЬНОГО ИНТЕРФЕЙСА")
        voice_frame.pack(fill='x', pady=5, padx=10)
        
        voice_info = tk.Frame(voice_frame)
        voice_info.pack(fill='x', pady=2, padx=10)
        
        tk.Label(voice_info, text="РЕЖИМ ГОЛОСА:").pack(side='left', padx=(0, 10))
        self.voice_label = tk.Label(voice_info, 
                                   text="МУЖСКОЙ" if self.assistant.settings['voice_gender'] == 'male' else "ЖЕНСКИЙ",
                                   font=('Courier New', 9, 'bold'))
        self.voice_label.pack(side='left', padx=5)
        
        # Параметры системы
        params_frame = tk.Frame(voice_frame)
        params_frame.pack(fill='x', pady=2, padx=10)
        
        tk.Label(params_frame, text="ГРОМКОСТЬ:").pack(side='left', padx=(0, 10))
        self.volume_label = tk.Label(params_frame, 
                                    text=f"{int(self.assistant.settings['volume'] * 100)}%",
                                    font=('Courier New', 9, 'bold'))
        self.volume_label.pack(side='left')
        
        tk.Label(params_frame, text="│").pack(side='left', padx=10)
        
        tk.Label(params_frame, text="СКОРОСТЬ:").pack(side='left', padx=(0, 10))
        self.rate_label = tk.Label(params_frame, 
                                  text=f"{self.assistant.settings['rate']}",
                                  font=('Courier New', 9, 'bold'))
        self.rate_label.pack(side='left')
        
        # Режим ввода
        input_frame = tk.Frame(voice_frame)
        input_frame.pack(fill='x', pady=2, padx=10)
        
        tk.Label(input_frame, text="РЕЖИМ ВВОДА:").pack(side='left', padx=(0, 10))
        mode_text = "КОНСОЛЬНЫЙ" if self.assistant.settings.get('input_mode') == 'console' else "ГОЛОСОВОЙ"
        self.mode_label = tk.Label(input_frame, 
                                  text=mode_text,
                                  font=('Courier New', 9, 'bold'))
        self.mode_label.pack(side='left')
        
        # Кнопки переключения режимов
        if self.assistant.microphone_available:
            mode_buttons_frame = tk.Frame(voice_frame)
            mode_buttons_frame.pack(fill='x', pady=2, padx=10)
            
            voice_btn = theme.create_button(
                mode_buttons_frame,
                "🎤 ГОЛОСОВОЙ РЕЖИМ",
                lambda: self.switch_mode('voice'),
                width=20
            )
            voice_btn.pack(side='left', padx=5)
            
            console_btn = theme.create_button(
                mode_buttons_frame,
                "⌨️ КОНСОЛЬНЫЙ РЕЖИМ",
                lambda: self.switch_mode('console'),
                width=20
            )
            console_btn.pack(side='left', padx=5)
        
        # Системный лог
        log_frame = ttk.LabelFrame(self.canvas_frame, text="СИСТЕМНЫЙ ЛОГ")
        log_frame.pack(fill='both', expand=True, pady=5, padx=10)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, wrap='word')
        self.log_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Начальное сообщение
        greeting = self.assistant_info['greeting']
        self.add_message(f"⚡ {greeting}")
        
        if self.assistant.microphone_available and self.assistant.settings.get('input_mode') == 'voice':
            self.add_message(f"🎤 АУДИОИНТЕРФЕЙС АКТИВЕН")
            self.add_message(f"🗣️ ДЛЯ АКТИВАЦИИ СКАЖИТЕ: '{self.assistant_info['full_name']}'")
        else:
            self.add_message("⌨️ КОНСОЛЬНЫЙ РЕЖИМ АКТИВИРОВАН")
            self.add_message("📝 ВВОДИТЕ КОМАНДЫ В КОНСОЛИ ВНИЗУ ОКНА")
            self.add_message("ℹ️ ДЛЯ СПРАВКИ ВВЕДИТЕ 'ПОМОЩЬ'")
        
        # Обновляем область прокрутки
        self.canvas.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
        
        # Привязываем колесо мыши для прокрутки
        self.bind_mousewheel()
    
    def setup_scrollable_interface(self):
        """Настраивает прокручиваемый интерфейс"""
        # Создаем холст для прокрутки
        self.canvas = tk.Canvas(self.root, bg='#f0f0f0', highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Добавляем скроллбар
        scrollbar = tk.Scrollbar(self.root, orient=tk.VERTICAL, command=self.canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Создаем фрейм внутри холста
        self.canvas_frame = tk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.canvas_frame, anchor="nw", width=780)
        
        # Настраиваем растягивание при изменении размера
        self.canvas_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)
    
    def on_frame_configure(self, event):
        """Обновляет область прокрутки при изменении размера фрейма"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def on_canvas_configure(self, event):
        """Обновляет ширину окна внутри холста"""
        self.canvas.itemconfig(self.canvas_window, width=event.width)
    
    def bind_mousewheel(self):
        """Привязывает колесо мыши для прокрутки"""
        # Привязываем для самого холста
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)
        self.canvas.bind_all("<Button-4>", self.on_mousewheel)  # Linux
        self.canvas.bind_all("<Button-5>", self.on_mousewheel)  # Linux
        
        # Привязываем для всех виджетов внутри
        for widget in self.canvas_frame.winfo_children():
            if isinstance(widget, tk.Frame):
                for child in widget.winfo_children():
                    child.bind_all("<MouseWheel>", self.on_mousewheel)
                    child.bind_all("<Button-4>", self.on_mousewheel)
                    child.bind_all("<Button-5>", self.on_mousewheel)
    
    def on_mousewheel(self, event):
        """Обрабатывает прокрутку колесом мыши"""
        if event.num == 4:  # Linux up
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:  # Linux down
            self.canvas.yview_scroll(1, "units")
        else:  # Windows/Mac
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def setup_console(self):
        """Настраивает консольный интерфейс"""
        theme = AssistantManager.get_assistant_theme(self.assistant_id)
        
        # Создаем фрейм для консоли
        self.console_frame = ttk.LabelFrame(self.canvas_frame, text="КОНСОЛЬНЫЙ ВВОД")
        
        # Показываем консоль только если в консольном режиме
        if self.assistant.settings.get('input_mode') == 'console':
            self.console_frame.pack(fill='x', pady=5, padx=10, side='bottom')
        
        # Поле вывода
        output_frame = tk.Frame(self.console_frame)
        output_frame.pack(fill='x', pady=5, padx=10)
        
        tk.Label(output_frame, text="Вывод:").pack(side='left', padx=(0, 5))
        
        self.console_output = tk.Text(output_frame, height=3, wrap='word', state='disabled')
        self.console_output.pack(fill='x', expand=True)
        
        # Поле ввода
        input_frame = tk.Frame(self.console_frame)
        input_frame.pack(fill='x', pady=5, padx=10)
        
        tk.Label(input_frame, text="Команда:").pack(side='left', padx=(0, 5))
        
        self.console_input = tk.Entry(input_frame)
        self.console_input.pack(fill='x', expand=True, side='left', padx=(0, 5))
        self.console_input.bind('<Return>', self.process_console_input)
        
        # Кнопка отправки
        send_btn = theme.create_button(
            input_frame,
            "▶️ ВВОД",
            lambda: self.process_console_input(None),
            width=10
        )
        send_btn.pack(side='left')
        
        # Кнопка очистки
        clear_btn = theme.create_button(
            input_frame,
            "🗑️ ОЧИСТИТЬ",
            self.clear_console,
            width=10
        )
        clear_btn.pack(side='left', padx=(5, 0))
    
    def switch_mode(self, mode):
        """Переключает режим работы"""
        if mode == 'voice':
            response = self.assistant.switch_to_voice_mode()
        else:
            response = self.assistant.switch_to_console_mode()
        
        self.add_message(f"🤖 {response}")
        self.update_settings_display()
    
    def process_console_input(self, event):
        """Обрабатывает ввод команды в консоли"""
        if not self.console_input:
            return
        
        command = self.console_input.get().strip()
        if not command:
            return
        
        # Очищаем поле ввода
        self.console_input.delete(0, tk.END)
        
        # Выводим команду в консоль
        self.add_console_output(f"> {command}")
        
        # Обрабатываем команду
        response = self.assistant.process_command(command)
        
        # Выводим ответ
        if response:
            self.add_console_output(f"🤖 {response}")
            # Произносим ответ если есть движок синтеза
            if hasattr(self.assistant, 'speak') and self.assistant.engine:
                self.assistant.speak(response)
        
        # Добавляем в системный лог
        self.add_message(f"⌨️ Введено: {command}")
        if response:
            self.add_message(f"🤖 {response}")
    
    def add_console_output(self, text):
        """Добавляет текст в консольный вывод"""
        if self.console_output:
            self.console_output.config(state='normal')
            self.console_output.insert('end', text + '\n')
            self.console_output.see('end')
            self.console_output.config(state='disabled')
    
    def clear_console(self):
        """Очищает консольный вывод"""
        if self.console_output:
            self.console_output.config(state='normal')
            self.console_output.delete('1.0', 'end')
            self.console_output.config(state='disabled')
    
    def start_assistant(self):
        """Запускает ассистента"""
        if hasattr(self.assistant, 'set_voice'):
            self.assistant.set_voice(self.assistant.settings['voice_gender'])
            self.assistant.current_lang = self.assistant.settings['language']
        
        # Запускаем поток прослушивания
        self.listening_thread = threading.Thread(
            target=self.assistant.listening_loop,
            args=(self.add_message,),
            daemon=True
        )
        self.listening_thread.start()
        
        # Определяем режим
        if self.assistant.microphone_available and self.assistant.settings.get('input_mode') == 'voice':
            self.add_message(f"🎤 {self.assistant_info['full_name']} активирован в голосовом режиме")
        else:
            self.add_message(f"⌨️ {self.assistant_info['full_name']} активирован в консольном режиме")
        
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
                
                if message == 'exit_program':
                    self.on_closing()
                    return
                
                timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                self.log_text.insert('end', f"[{timestamp}] {message}\n")
                self.log_text.see('end')
                
                if "настройки" in message.lower() or "имя" in message.lower() or "язык" in message.lower() or "режим" in message.lower():
                    self.update_settings_display()
                    
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.process_queue)
    
    def update_settings_display(self):
        """Обновляет отображение настроек"""
        self.name_label.config(text=self.assistant.settings['assistant_name'].upper())
        self.voice_label.config(text="МУЖСКОЙ" if self.assistant.settings['voice_gender'] == 'male' else "ЖЕНСКИЙ")
        self.volume_label.config(text=f"{int(self.assistant.settings['volume'] * 100)}%")
        self.rate_label.config(text=f"{self.assistant.settings['rate']}")
        
        # Обновляем режим ввода
        mode_text = "КОНСОЛЬНЫЙ" if self.assistant.settings.get('input_mode') == 'console' else "ГОЛОСОВОЙ"
        self.mode_label.config(text=mode_text)
    
    def on_closing(self):
        """Обработка закрытия окна"""
        if hasattr(self.assistant, 'is_listening'):
            self.assistant.is_listening = False
            self.assistant.is_activated = False
        
        # Голосовое подтверждение выхода
        if hasattr(self.assistant, 'engine') and self.assistant.engine:
            self.assistant.speak("Завершение работы")
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
        
        # Устанавливаем фокус на поле ввода консоли если оно видимо
        if self.console_frame and self.console_frame.winfo_ismapped() and self.console_input:
            self.console_input.focus_set()
        
        self.root.mainloop()

def check_dependencies():
    """Проверяет наличие необходимых зависимостей"""
    print("=" * 60)
    print("VOICE ASSISTANT SYSTEM - Multi-Assistant Edition")
    print("=" * 60)
    
    if not SPEECH_RECOGNITION_AVAILABLE or not PYTTSX3_AVAILABLE or not PYAUDIO_AVAILABLE:
        print("\n❌ КРИТИЧЕСКИЕ КОМПОНЕНТЫ ОТСУТСТВУЮТ!")
        print("Для установки выполните:")
        print("pip install SpeechRecognition pyttsx3 pyaudio")
        return False
    
    return True

def main():
    """Главная функция"""
    # Проверяем зависимости
    if not check_dependencies():
        input("\nНажмите Enter для выхода...")
        return
    
    # Запускаем окно выбора ассистента
    selector = AssistantSelectionGUI()
    assistant_id = selector.run()
    
    if not assistant_id:
        print("Ассистент не выбран. Выход...")
        return
    
    print(f"\n✅ Выбран ассистент: {AssistantManager.get_assistant_info(assistant_id)['full_name']}")
    print("Запуск системы...")
    
    # Запускаем приложение с выбранным ассистентом
    try:
        app = AssistantGUI(assistant_id)
        app.run()
    except Exception as e:
        print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА СИСТЕМЫ: {e}")
        print(traceback.format_exc())
        input("Нажмите Enter для выхода...")

if __name__ == "__main__":
    main()