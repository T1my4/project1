# futuristic_theme.py
"""
Футуристичная тема для голосового ассистента в стиле Тони Старка (Железного Человека)
"""
import tkinter as tk
from tkinter import ttk, scrolledtext
import math

class FuturisticStarkTheme:
    """Футуристичная тема в стиле Тони Старка"""
    
    # Основные цвета Железного Человека
    STARK_COLORS = {
        'primary_red': '#ff003c',      # Ярко-красный Железного Человека
        'primary_gold': '#ffd700',     # Золотой акцент
        'dark_bg': '#0a0a0a',          # Темный фон
        'darker_bg': '#050505',        # Еще темнее фон
        'panel_bg': '#1a1a1a',         # Фон панелей
        'text_primary': '#ffffff',     # Основной текст
        'text_secondary': '#cccccc',   # Вторичный текст
        'text_accent': '#ffd700',      # Акцентный текст
        'text_red': '#ff003c',         # Красный текст
        'border_color': '#333333',     # Цвет границ
        'hover_color': '#2a2a2a',      # Цвет при наведении
        'active_color': '#3a3a3a',     # Цвет активного элемента
        'gradient_start': '#1a1a1a',   # Начало градиента
        'gradient_end': '#0a0a0a',     # Конец градиента
        'glow_color': '#ff003c',       # Цвет свечения
        'blue_accent': '#00a8ff',      # Синий акцент (реактора)
        'success_green': '#00ff88',    # Зеленый успеха
        'warning_orange': '#ffaa00',   # Оранжевый предупреждения
        'error_red': '#ff003c',        # Красный ошибки
        'info_blue': '#00a8ff',        # Синий информации
    }
    
    # Шрифты
    FONTS = {
        'title': ('Arial', 16, 'bold'),
        'subtitle': ('Arial', 12, 'bold'),
        'normal': ('Arial', 10),
        'small': ('Arial', 9),
        'mono': ('Courier New', 9),
        'heading': ('Arial', 14, 'bold'),
        'status': ('Arial', 11, 'bold'),
    }
    
    # Стили для элементов интерфейса
    @classmethod
    def apply_theme(cls, root_widget):
        """Применяет футуристичную тему к корневому виджету"""
        colors = cls.STARK_COLORS
        
        try:
            # Настройка корневого окна
            root_widget.configure(bg=colors['dark_bg'])
            
            # Рекурсивно обновляем все виджеты
            cls._update_widgets(root_widget, colors)
            
        except Exception as e:
            print(f"Ошибка применения темы: {e}")
    
    @classmethod
    def _update_widgets(cls, widget, colors):
        """Рекурсивно обновляет все виджеты"""
        try:
            # Обработка разных типов виджетов
            if isinstance(widget, tk.Frame):
                cls._style_frame(widget, colors)
            elif isinstance(widget, ttk.Frame):
                cls._style_ttk_frame(widget, colors)
            elif isinstance(widget, tk.Label):
                cls._style_label(widget, colors)
            elif isinstance(widget, tk.LabelFrame):
                cls._style_label_frame(widget, colors)
            elif isinstance(widget, ttk.LabelFrame):
                cls._style_ttk_label_frame(widget, colors)
            elif isinstance(widget, tk.Text) or isinstance(widget, scrolledtext.ScrolledText):
                cls._style_text(widget, colors)
            elif isinstance(widget, tk.Canvas):
                cls._style_canvas(widget, colors)
            elif isinstance(widget, ttk.Scrollbar):
                cls._style_scrollbar(widget, colors)
            
            # Рекурсивно обрабатываем дочерние виджеты
            for child in widget.winfo_children():
                cls._update_widgets(child, colors)
                
        except Exception as e:
            # Пропускаем ошибки для специфичных виджетов
            pass
    
    @classmethod
    def _style_frame(cls, widget, colors):
        """Стилизует Frame"""
        try:
            widget.configure(
                bg=colors['panel_bg'],
                highlightbackground=colors['border_color'],
                highlightcolor=colors['glow_color'],
                highlightthickness=1
            )
        except:
            try:
                widget.configure(bg=colors['panel_bg'])
            except:
                pass
    
    @classmethod
    def _style_ttk_frame(cls, widget, colors):
        """Стилизует ttk.Frame"""
        try:
            style = ttk.Style()
            style.configure(
                'Custom.TFrame',
                background=colors['panel_bg'],
                relief='flat',
                borderwidth=1
            )
            widget.configure(style='Custom.TFrame')
        except:
            pass
    
    @classmethod
    def _style_label(cls, widget, colors):
        """Стилизует Label"""
        try:
            # Определяем тип текста для стилизации
            text = widget.cget('text') if widget.cget('text') else ''
            text_lower = text.lower()
            
            # Выбор цвета текста в зависимости от содержимого
            if any(keyword in text_lower for keyword in ['ассистент', 'assistant', 'джарвис', 'jarvis']):
                text_color = colors['text_accent']
                font = cls.FONTS['title']
            elif any(keyword in text_lower for keyword in ['статус', 'status', 'активен', 'active']):
                text_color = colors['success_green']
                font = cls.FONTS['status']
            elif any(keyword in text_lower for keyword in ['ошибка', 'error', '⚠', '❌']):
                text_color = colors['error_red']
                font = cls.FONTS['normal']
            elif any(keyword in text_lower for keyword in ['предупреждение', 'warning', '⚠']):
                text_color = colors['warning_orange']
                font = cls.FONTS['normal']
            elif any(keyword in text_lower for keyword in ['информация', 'info', 'ℹ', '✅']):
                text_color = colors['info_blue']
                font = cls.FONTS['normal']
            elif any(keyword in text_lower for keyword in ['настройки', 'settings', 'управление', 'control']):
                text_color = colors['text_primary']
                font = cls.FONTS['heading']
            else:
                text_color = colors['text_secondary']
                font = cls.FONTS['normal']
            
            widget.configure(
                bg=colors['panel_bg'],
                fg=text_color,
                font=font,
                padx=5,
                pady=2
            )
        except:
            pass
    
    @classmethod
    def _style_label_frame(cls, widget, colors):
        """Стилизует LabelFrame"""
        try:
            widget.configure(
                bg=colors['dark_bg'],
                fg=colors['text_accent'],
                font=cls.FONTS['subtitle'],
                relief='groove',
                borderwidth=2,
                highlightbackground=colors['border_color'],
                highlightcolor=colors['glow_color']
            )
        except:
            pass
    
    @classmethod
    def _style_ttk_label_frame(cls, widget, colors):
        """Стилизует ttk.LabelFrame"""
        try:
            style = ttk.Style()
            style.configure(
                'Custom.TLabelframe',
                background=colors['dark_bg'],
                foreground=colors['text_accent'],
                relief='groove',
                borderwidth=2
            )
            style.configure(
                'Custom.TLabelframe.Label',
                background=colors['dark_bg'],
                foreground=colors['text_accent'],
                font=cls.FONTS['subtitle']
            )
            widget.configure(style='Custom.TLabelframe')
        except:
            pass
    
    @classmethod
    def _style_text(cls, widget, colors):
        """Стилизует Text и ScrolledText"""
        try:
            widget.configure(
                bg=colors['darker_bg'],
                fg=colors['text_primary'],
                insertbackground=colors['primary_red'],
                selectbackground=colors['primary_red'],
                selectforeground=colors['text_primary'],
                font=cls.FONTS['mono'],
                relief='sunken',
                borderwidth=2,
                highlightbackground=colors['border_color'],
                highlightcolor=colors['glow_color'],
                highlightthickness=1
            )
        except:
            pass
    
    @classmethod
    def _style_canvas(cls, widget, colors):
        """Стилизует Canvas"""
        try:
            widget.configure(
                bg=colors['dark_bg'],
                highlightbackground=colors['border_color'],
                highlightcolor=colors['glow_color'],
                highlightthickness=1
            )
        except:
            pass
    
    @classmethod
    def _style_scrollbar(cls, widget, colors):
        """Стилизует Scrollbar"""
        try:
            style = ttk.Style()
            style.configure(
                'Custom.Vertical.TScrollbar',
                background=colors['panel_bg'],
                troughcolor=colors['darker_bg'],
                bordercolor=colors['border_color'],
                arrowcolor=colors['text_secondary'],
                relief='flat'
            )
            style.map(
                'Custom.Vertical.TScrollbar',
                background=[('active', colors['primary_red']),
                          ('pressed', colors['primary_red'])],
                arrowcolor=[('active', colors['text_accent']),
                          ('pressed', colors['text_accent'])]
            )
            widget.configure(style='Custom.Vertical.TScrollbar')
        except:
            pass
    
    @classmethod
    def create_gradient_background(cls, canvas, width, height):
        """Создает градиентный фон на Canvas"""
        colors = cls.STARK_COLORS
        
        # Создаем градиент от темного к черному
        for i in range(height):
            # Рассчитываем цвет для каждой линии
            ratio = i / height
            r = int(10 + ratio * 5)
            g = int(10 + ratio * 5)
            b = int(10 + ratio * 5)
            color = f'#{r:02x}{g:02x}{b:02x}'
            
            canvas.create_line(0, i, width, i, fill=color)
        
        # Добавляем футуристичные линии
        canvas.create_line(0, 0, width, 0, fill=colors['border_color'], width=1)
        canvas.create_line(0, height-1, width, height-1, fill=colors['border_color'], width=1)
        
        # Добавляем акцентные элементы (как в интерфейсе Железного Человека)
        canvas.create_line(width//4, 0, width//4, height, fill=colors['border_color'], width=1, dash=(5, 3))
        canvas.create_line(width//2, 0, width//2, height, fill=colors['border_color'], width=1, dash=(5, 3))
        canvas.create_line(3*width//4, 0, 3*width//4, height, fill=colors['border_color'], width=1, dash=(5, 3))
    
    @classmethod
    def create_stark_logo(cls, canvas, x, y, size=50):
        """Создает логотип в стиле Железного Человека"""
        colors = cls.STARK_COLORS
        
        # Создаем стилизованный реактор дуги
        # Внешний круг
        canvas.create_oval(
            x - size, y - size,
            x + size, y + size,
            outline=colors['primary_red'],
            width=3,
            fill=''
        )
        
        # Внутренний круг
        canvas.create_oval(
            x - size//2, y - size//2,
            x + size//2, y + size//2,
            outline=colors['blue_accent'],
            width=2,
            fill=''
        )
        
        # Центральная точка (реактор)
        canvas.create_oval(
            x - size//4, y - size//4,
            x + size//4, y + size//4,
            outline=colors['primary_gold'],
            fill=colors['primary_red'],
            width=2
        )
        
        # Лучи
        for angle in range(0, 360, 45):
            rad = angle * 3.14159 / 180
            x1 = x + (size//3) * math.cos(rad)
            y1 = y + (size//3) * math.sin(rad)
            x2 = x + (size - 5) * math.cos(rad)
            y2 = y + (size - 5) * math.sin(rad)
            
            canvas.create_line(
                x1, y1, x2, y2,
                fill=colors['primary_gold'],
                width=2
            )
    
    @classmethod
    def create_futuristic_button(cls, parent, text, command=None, **kwargs):
        """Создает футуристичную кнопку"""
        colors = cls.STARK_COLORS
        
        button = tk.Label(
            parent,
            text=text,
            font=cls.FONTS['normal'],
            bg=colors['panel_bg'],
            fg=colors['text_primary'],
            relief='raised',
            borderwidth=2,
            padx=15,
            pady=8,
            cursor='hand2'
        )
        
        if command:
            button.bind("<Button-1>", lambda e: command())
        
        # Эффекты при наведении
        def on_enter(e):
            button.configure(
                bg=colors['primary_red'],
                fg=colors['text_primary']
            )
        
        def on_leave(e):
            button.configure(
                bg=colors['panel_bg'],
                fg=colors['text_primary']
            )
        
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
        
        return button
    
    @classmethod
    def create_status_indicator(cls, parent, status="active"):
        """Создает индикатор статуса в футуристичном стиле"""
        colors = cls.STARK_COLORS
        
        if status == "active":
            color = colors['success_green']
            text = "🟢 АКТИВЕН"
        elif status == "inactive":
            color = colors['warning_orange']
            text = "🟡 НЕАКТИВЕН"
        elif status == "error":
            color = colors['error_red']
            text = "🔴 ОШИБКА"
        else:
            color = colors['text_secondary']
            text = "⚪ СТАТУС"
        
        frame = tk.Frame(parent, bg=colors['panel_bg'], padx=10, pady=5)
        
        # Индикатор (круг)
        indicator = tk.Canvas(frame, width=20, height=20, bg=colors['panel_bg'], 
                            highlightthickness=0)
        indicator.create_oval(2, 2, 18, 18, fill=color, outline=colors['border_color'])
        
        # Текст статуса
        label = tk.Label(frame, text=text, bg=colors['panel_bg'], 
                        fg=colors['text_primary'], font=cls.FONTS['status'])
        
        indicator.pack(side='left', padx=(0, 10))
        label.pack(side='left')
        
        return frame
    
    @classmethod
    def create_futuristic_progress(cls, canvas, x, y, width, height, value, max_value=100):
        """Создает футуристичный индикатор прогресса"""
        colors = cls.STARK_COLORS
        
        # Фон прогресс-бара
        canvas.create_rectangle(
            x, y,
            x + width, y + height,
            fill=colors['darker_bg'],
            outline=colors['border_color'],
            width=1
        )
        
        # Заполненная часть
        fill_width = (value / max_value) * width
        canvas.create_rectangle(
            x, y,
            x + fill_width, y + height,
            fill=colors['primary_red'],
            outline='',
            width=0
        )
        
        # Эффект свечения на конце
        if fill_width > 0:
            canvas.create_rectangle(
                x + fill_width - 5, y,
                x + fill_width, y + height,
                fill=colors['blue_accent'],
                outline='',
                width=0
            )
        
        # Текст значения
        canvas.create_text(
            x + width // 2, y + height // 2,
            text=f"{value}%",
            fill=colors['text_primary'],
            font=cls.FONTS['small']
        )