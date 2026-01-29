"""
Тема для ассистента Вазилина - современный яркий стиль
"""

import tkinter as tk
from tkinter import ttk

class VazelinaTheme:
    """Современная тема с яркими цветами"""
    
    @staticmethod
    def apply_theme(root):
        """Применяет современную тему к окну"""
        # Яркие современные цвета
        colors = {
            'bg_dark': '#2d1b3d',
            'bg_medium': '#4a2b5f',
            'bg_light': '#673ab7',
            'accent_pink': '#e91e63',
            'accent_purple': '#9c27b0',
            'text_primary': '#ffffff',
            'text_secondary': '#f8bbd9',
            'success': '#4caf50',
            'warning': '#ff9800',
            'error': '#f44336'
        }
        
        root.configure(bg=colors['bg_dark'])
        
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('TFrame', background=colors['bg_medium'])
        style.configure('TLabelFrame', background=colors['bg_medium'], foreground=colors['accent_pink'])
        style.configure('TLabelFrame.Label', background=colors['bg_medium'], foreground=colors['accent_pink'])
        
        style.configure('TButton', 
                       background=colors['bg_light'],
                       foreground=colors['text_primary'],
                       borderwidth=1,
                       focusthickness=3,
                       focuscolor='none')
        style.map('TButton',
                 background=[('active', colors['accent_pink'])],
                 foreground=[('active', colors['bg_dark'])])
    
    @staticmethod
    def create_button(parent, text, command, **kwargs):
        """Создает современную кнопку"""
        btn = tk.Button(parent, text=text, command=command,
                       bg='#9c27b0', fg='white',
                       activebackground='#e91e63',
                       activeforeground='white',
                       font=('Arial', 10, 'bold'),
                       relief='flat',
                       borderwidth=0,
                       cursor='hand2',
                       **kwargs)
        return btn
    
    @staticmethod
    def create_status_indicator(parent, status="active"):
        """Создает индикатор статуса в современном стиле"""
        frame = tk.Frame(parent, bg='#4a2b5f')
        
        if status == "active":
            indicator = tk.Label(frame, text="💃", font=('Arial', 16),
                                fg='#e91e63', bg='#4a2b5f')
            status_text = "СИСТЕМА АКТИВНА"
            text_color = '#e91e63'
        elif status == "error":
            indicator = tk.Label(frame, text="❌", font=('Arial', 16),
                                fg='#f44336', bg='#4a2b5f')
            status_text = "СИСТЕМНАЯ ОШИБКА"
            text_color = '#f44336'
        else:  # console
            indicator = tk.Label(frame, text="💻", font=('Arial', 16),
                                fg='#9c27b0', bg='#4a2b5f')
            status_text = "КОНСОЛЬНЫЙ РЕЖИМ"
            text_color = '#9c27b0'
        
        indicator.pack(side='left', padx=(10, 5))
        
        status_label = tk.Label(frame, text=status_text, 
                               font=('Courier New', 10, 'bold'),
                               fg=text_color, bg='#4a2b5f')
        status_label.pack(side='left')
        
        return frame
    
    @staticmethod
    def style_header_frame(frame):
        """Стилизует заголовочный фрейм"""
        frame.configure(bg='#4a2b5f')