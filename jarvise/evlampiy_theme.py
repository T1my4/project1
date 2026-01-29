"""
Тема для ассистента Евлампий - классический академический стиль
"""

import tkinter as tk
from tkinter import ttk

class EvlampiyTheme:
    """Классическая тема в академическом стиле"""
    
    @staticmethod
    def apply_theme(root):
        """Применяет классическую тему к окну"""
        # Цвета академического стиля
        colors = {
            'bg_dark': '#1e3d2e',
            'bg_medium': '#2d5a3d',
            'bg_light': '#3c774c',
            'accent_green': '#4caf50',
            'accent_gold': '#ffd700',
            'text_primary': '#ffffff',
            'text_secondary': '#e8f5e9',
            'success': '#81c784',
            'warning': '#ffb74d',
            'error': '#e57373'
        }
        
        root.configure(bg=colors['bg_dark'])
        
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('TFrame', background=colors['bg_medium'])
        style.configure('TLabelFrame', background=colors['bg_medium'], foreground=colors['accent_gold'])
        style.configure('TLabelFrame.Label', background=colors['bg_medium'], foreground=colors['accent_gold'])
        
        style.configure('TButton', 
                       background=colors['bg_light'],
                       foreground=colors['text_primary'],
                       borderwidth=1,
                       focusthickness=3,
                       focuscolor='none')
        style.map('TButton',
                 background=[('active', colors['accent_green'])],
                 foreground=[('active', colors['bg_dark'])])
    
    @staticmethod
    def create_button(parent, text, command, **kwargs):
        """Создает классическую кнопку"""
        btn = tk.Button(parent, text=text, command=command,
                       bg='#2e7d32', fg='white',
                       activebackground='#4caf50',
                       activeforeground='white',
                       font=('Arial', 10, 'bold'),
                       relief='groove',
                       borderwidth=2,
                       cursor='hand2',
                       **kwargs)
        return btn
    
    @staticmethod
    def create_status_indicator(parent, status="active"):
        """Создает индикатор статуса в классическом стиле"""
        frame = tk.Frame(parent, bg='#2d5a3d')
        
        if status == "active":
            indicator = tk.Label(frame, text="✓", font=('Arial', 16),
                                fg='#81c784', bg='#2d5a3d')
            status_text = "СИСТЕМА АКТИВНА"
            text_color = '#81c784'
        elif status == "error":
            indicator = tk.Label(frame, text="✗", font=('Arial', 16),
                                fg='#e57373', bg='#2d5a3d')
            status_text = "СИСТЕМНАЯ ОШИБКА"
            text_color = '#e57373'
        else:  # console
            indicator = tk.Label(frame, text="📚", font=('Arial', 16),
                                fg='#ffd700', bg='#2d5a3d')
            status_text = "КОНСОЛЬНЫЙ РЕЖИМ"
            text_color = '#ffd700'
        
        indicator.pack(side='left', padx=(10, 5))
        
        status_label = tk.Label(frame, text=status_text, 
                               font=('Courier New', 10, 'bold'),
                               fg=text_color, bg='#2d5a3d')
        status_label.pack(side='left')
        
        return frame
    
    @staticmethod
    def style_header_frame(frame):
        """Стилизует заголовочный фрейм"""
        frame.configure(bg='#2d5a3d')