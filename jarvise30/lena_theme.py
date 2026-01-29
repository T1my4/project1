"""
Тема для ассистента Лена - мягкий приятный стиль
"""

import tkinter as tk
from tkinter import ttk

class LenaTheme:
    """Мягкая тема с пастельными цветами"""
    
    @staticmethod
    def apply_theme(root):
        """Применяет мягкую тему к окну"""
        # Пастельные цвета
        colors = {
            'bg_dark': '#4a235a',
            'bg_medium': '#6c3483',
            'bg_light': '#8e44ad',
            'accent_purple': '#d7bde2',
            'accent_lavender': '#e8daef',
            'text_primary': '#ffffff',
            'text_secondary': '#f4ecf7',
            'success': '#a3e4d7',
            'warning': '#f9e79f',
            'error': '#f5b7b1'
        }
        
        root.configure(bg=colors['bg_dark'])
        
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('TFrame', background=colors['bg_medium'])
        style.configure('TLabelFrame', background=colors['bg_medium'], foreground=colors['accent_lavender'])
        style.configure('TLabelFrame.Label', background=colors['bg_medium'], foreground=colors['accent_lavender'])
        
        style.configure('TButton', 
                       background=colors['bg_light'],
                       foreground=colors['text_primary'],
                       borderwidth=1,
                       focusthickness=3,
                       focuscolor='none')
        style.map('TButton',
                 background=[('active', colors['accent_purple'])],
                 foreground=[('active', colors['bg_dark'])])
    
    @staticmethod
    def create_button(parent, text, command, **kwargs):
        """Создает мягкую кнопку"""
        btn = tk.Button(parent, text=text, command=command,
                       bg='#8e44ad', fg='white',
                       activebackground='#d7bde2',
                       activeforeground='#4a235a',
                       font=('Arial', 10, 'bold'),
                       relief='ridge',
                       borderwidth=2,
                       cursor='hand2',
                       **kwargs)
        return btn
    
    @staticmethod
    def create_status_indicator(parent, status="active"):
        """Создает индикатор статуса в мягком стиле"""
        frame = tk.Frame(parent, bg='#6c3483')
        
        if status == "active":
            indicator = tk.Label(frame, text="🌸", font=('Arial', 16),
                                fg='#d7bde2', bg='#6c3483')
            status_text = "СИСТЕМА АКТИВНА"
            text_color = '#d7bde2'
        elif status == "error":
            indicator = tk.Label(frame, text="🍂", font=('Arial', 16),
                                fg='#f5b7b1', bg='#6c3483')
            status_text = "СИСТЕМНАЯ ОШИБКА"
            text_color = '#f5b7b1'
        else:  # console
            indicator = tk.Label(frame, text="📝", font=('Arial', 16),
                                fg='#e8daef', bg='#6c3483')
            status_text = "КОНСОЛЬНЫЙ РЕЖИМ"
            text_color = '#e8daef'
        
        indicator.pack(side='left', padx=(10, 5))
        
        status_label = tk.Label(frame, text=status_text, 
                               font=('Courier New', 10, 'bold'),
                               fg=text_color, bg='#6c3483')
        status_label.pack(side='left')
        
        return frame
    
    @staticmethod
    def style_header_frame(frame):
        """Стилизует заголовочный фрейм"""
        frame.configure(bg='#6c3483')