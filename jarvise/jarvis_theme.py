"""
Тема для ассистента Джарвис - футуристичный стиль Тони Старка
"""

import tkinter as tk
from tkinter import ttk

class JARVISTheme:
    """Футуристичная тема в стиле Железного Человека"""
    
    @staticmethod
    def apply_theme(root):
        """Применяет футуристичную тему к окну"""
        # Основные цвета стиля Железного Человека
        colors = {
            'bg_dark': '#0a0a0f',
            'bg_medium': '#1a1a2e',
            'bg_light': '#2a2a3e',
            'accent_blue': '#00ccff',
            'accent_cyan': '#00ffff',
            'text_primary': '#ffffff',
            'text_secondary': '#cccccc',
            'success': '#00ff00',
            'warning': '#ffff00',
            'error': '#ff4444'
        }
        
        # Настраиваем основное окно
        root.configure(bg=colors['bg_dark'])
        
        # Создаем стиль для ttk виджетов
        style = ttk.Style()
        style.theme_use('clam')
        
        # Настройка стилей
        style.configure('TFrame', background=colors['bg_medium'])
        style.configure('TLabelFrame', background=colors['bg_medium'], foreground=colors['accent_blue'])
        style.configure('TLabelFrame.Label', background=colors['bg_medium'], foreground=colors['accent_blue'])
        
        # Настройка кнопок
        style.configure('TButton', 
                       background=colors['bg_light'],
                       foreground=colors['text_primary'],
                       borderwidth=1,
                       focusthickness=3,
                       focuscolor='none')
        style.map('TButton',
                 background=[('active', colors['accent_blue'])],
                 foreground=[('active', colors['bg_dark'])])
    
    @staticmethod
    def create_button(parent, text, command, **kwargs):
        """Создает футуристичную кнопку"""
        btn = tk.Button(parent, text=text, command=command,
                       bg='#0066cc', fg='white',
                       activebackground='#00ccff',
                       activeforeground='black',
                       font=('Arial', 10, 'bold'),
                       relief='raised',
                       borderwidth=2,
                       cursor='hand2',
                       **kwargs)
        return btn
    
    @staticmethod
    def create_status_indicator(parent, status="active"):
        """Создает индикатор статуса в футуристичном стиле"""
        frame = tk.Frame(parent, bg='#1a1a2e')
        
        # Индикатор
        indicator = tk.Label(frame, text="●", font=('Arial', 16))
        
        if status == "active":
            indicator.config(text="⚡", fg='#00ff00', bg='#1a1a2e')
            status_text = "СИСТЕМА АКТИВНА"
            text_color = '#00ff00'
        elif status == "error":
            indicator.config(text="⚠", fg='#ff4444', bg='#1a1a2e')
            status_text = "СИСТЕМНАЯ ОШИБКА"
            text_color = '#ff4444'
        else:  # console
            indicator.config(text="⌨", fg='#00ccff', bg='#1a1a2e')
            status_text = "КОНСОЛЬНЫЙ РЕЖИМ"
            text_color = '#00ccff'
        
        indicator.pack(side='left', padx=(10, 5))
        
        # Текст статуса
        status_label = tk.Label(frame, text=status_text, 
                               font=('Courier New', 10, 'bold'),
                               fg=text_color, bg='#1a1a2e')
        status_label.pack(side='left')
        
        return frame
    
    @staticmethod
    def style_header_frame(frame):
        """Стилизует заголовочный фрейм"""
        frame.configure(bg='#1a1a2e')