import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont
from tkinter import Canvas
import math
import ctypes
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

# 定义颜色方案 - 绿色主题
COLORS = {
    'bg_dark': '#1e2b1e',        # 深绿色背景
    'bg_light': '#2d3f2d',       # 浅绿色背景
    'accent': '#4CAF50',         # 主题绿色
    'accent_hover': '#66BB6A',   # 悬停时的绿色
    'text': '#E8F5E9',          # 文字颜色
    'text_secondary': '#C8E6C9', # 次要文字颜色
    'border': '#2d3f2d',        # 边框颜色
    'title_bg': '#388E3C',      # 标题栏背景色
}

# 定义字体设置
FONTS = {
    'title': ('Microsoft YaHei UI', 14, 'bold'),    # 标题字体
    'normal': ('Microsoft YaHei UI', 10),           # 普通文本字体
    'button': ('Microsoft YaHei UI', 10),           # 按钮字体
    'lyrics': ('Microsoft YaHei UI', 12),           # 歌词字体
    'lyrics_highlight': ('Microsoft YaHei UI', 14, 'bold')  # 高亮歌词字体
}

def create_custom_button(parent, text, command, width=None):
    """创建自义样式的按钮，带有悬停效果"""
    btn = tk.Button(parent, text=text, command=command,
                    bg=COLORS['accent'],
                    fg=COLORS['text'],
                    activebackground=COLORS['accent_hover'],
                    activeforeground=COLORS['text'],
                    relief=tk.FLAT,
                    font=('Helvetica', 10),
                    padx=15, pady=5,
                    width=width if width else None,
                    cursor='hand2')
    
    btn.bind('<Enter>', lambda e: btn.config(bg=COLORS['accent_hover']))
    btn.bind('<Leave>', lambda e: btn.config(bg=COLORS['accent']))
    
    return btn

def create_round_rectangle(canvas, x1, y1, x2, y2, radius=25, **kwargs):
    """创建圆角矩形"""
    points = [x1+radius, y1,
             x1+radius, y1,
             x2-radius, y1,
             x2-radius, y1,
             x2, y1,
             x2, y1+radius,
             x2, y1+radius,
             x2, y2-radius,
             x2, y2-radius,
             x2, y2,
             x2-radius, y2,
             x2-radius, y2,
             x1+radius, y2,
             x1+radius, y2,
             x1, y2,
             x1, y2-radius,
             x1, y2-radius,
             x1, y1+radius,
             x1, y1+radius,
             x1, y1]

    return canvas.create_polygon(points, **kwargs, smooth=True)

def create_playing_animation(canvas, x, y, color):
    """创建播放动画效果"""
    bars = []
    for i in range(3):
        bar = canvas.create_rectangle(x + i*6, y, x + i*6 + 2, y + 10,
                                    fill=color, width=0)
        bars.append(bar)
    return bars

def animate_playing(canvas, bars, step=0):
    """更新播放动画"""
    heights = [6, 10, 4]  # 默认高度
    new_heights = heights[step:] + heights[:step]  # 循环移动高度
    
    for bar, height in zip(bars, new_heights):
        x1, _, x2, _ = canvas.coords(bar)
        canvas.coords(bar, x1, 15-height/2, x2, 15+height/2)
    
    canvas.after(200, lambda: animate_playing(canvas, bars, (step+1)%3))

def create_wave_effect(canvas, width, height):
    """创建音频波形效果"""
    points = []
    for x in range(0, width, 2):
        y = height/2 + math.sin(x/10) * (height/4)  # 调整波形幅度
        points.extend([x, y])
    
    wave = canvas.create_line(points,
                            fill=COLORS['accent'],    # 使用主题色
                            width=2,                  # 增加线条宽度
                            smooth=True)              # 平滑曲线
    return wave

def update_wave(canvas, wave, offset):
    """更新波形动画"""
    points = []
    width = canvas.winfo_width()
    height = canvas.winfo_height()
    
    for x in range(0, width, 2):
        y = height/2 + math.sin((x+offset)/10) * (height/4)  # 调整波形幅度
        points.extend([x, y])
    
    canvas.coords(wave, *points)
    canvas.after(50, lambda: update_wave(canvas, wave, offset+1))

def setup_ui(app):
    """设置主窗口UI组件"""
    # 设置DPI缩放
    app.root.tk.call('tk', 'scaling', 1.5)  # 调整DPI缩放比例
    
    # 创建背景画布
    canvas = Canvas(app.root, 
                   bg=COLORS['bg_dark'],
                   highlightthickness=0,
                   width=app.root.winfo_width(),
                   height=app.root.winfo_height())
    canvas.place(x=0, y=0, relwidth=1, relheight=1)
    
    # 创建圆角矩形背景
    create_round_rectangle(canvas, 2, 2, 
                          app.root.winfo_width()-2,
                          app.root.winfo_height()-2,
                          radius=15,
                          fill=COLORS['bg_dark'],
                          outline=COLORS['border'],
                          width=2)

    # 创建标题栏 - 只修改背景色
    title_bar = tk.Frame(app.root, bg=COLORS['title_bg'])
    title_bar.pack(fill=tk.X, pady=5)

    # 窗口标题 - 更新标题文本
    title_label = tk.Label(title_bar, text="个人音乐电台",
                          bg=COLORS['title_bg'],
                          fg=COLORS['text'],
                          font=FONTS['title'])
    title_label.pack(side=tk.LEFT, padx=10)

    # 添加标题栏拖动功能
    def start_move(event):
        app.root.x = event.x_root - app.root.winfo_x()
        app.root.y = event.y_root - app.root.winfo_y()

    def do_move(event):
        x = event.x_root - app.root.x
        y = event.y_root - app.root.y
        app.root.geometry(f'+{x}+{y}')

    # 只绑定标题栏和标题文本的拖动事件
    title_bar.bind('<Button-1>', start_move)
    title_bar.bind('<B1-Motion>', do_move)
    title_label.bind('<Button-1>', start_move)
    title_label.bind('<B1-Motion>', do_move)

    # 控制按钮框架 - 更新背景色
    control_buttons = tk.Frame(title_bar, bg=COLORS['title_bg'])
    control_buttons.pack(side=tk.RIGHT, padx=5)

    # 最小化按钮 - 更新背景色
    def minimize_window():
        app.root.update_idletasks()
        app.root.overrideredirect(False)  # 临时恢复窗口边框
        app.root.iconify()  # 最小化窗口
        
        def check_state():
            if app.root.state() == 'normal':  # 当窗口恢复时
                app.root.overrideredirect(True)  # 重新移除边框
            else:
                app.root.after(100, check_state)
        
        check_state()

    minimize_button = tk.Button(control_buttons, text="—",
                              bg=COLORS['title_bg'],
                              fg=COLORS['text'],
                              font=FONTS['button'],
                              bd=0,
                              padx=10,
                              cursor='hand2',
                              command=minimize_window)
    minimize_button.pack(side=tk.LEFT, padx=2)
    
    # 更新最小化按钮悬停效果
    def on_minimize_enter(e):
        minimize_button.config(bg=COLORS['accent'])
    def on_minimize_leave(e):
        minimize_button.config(bg=COLORS['title_bg'])
    
    minimize_button.bind('<Enter>', on_minimize_enter)
    minimize_button.bind('<Leave>', on_minimize_leave)

    # 关闭按钮 - 更新背景色
    close_button = tk.Button(control_buttons, text="×",
                            bg=COLORS['title_bg'],
                            fg=COLORS['text'],
                            font=('Arial', 16, 'bold'),
                            bd=0,
                            padx=10,
                            cursor='hand2',
                            command=lambda: app.root.destroy())
    close_button.pack(side=tk.LEFT, padx=2)
    
    # 更新关闭按钮悬停效果
    def on_close_enter(e):
        close_button.config(bg=COLORS['accent'])
    def on_close_leave(e):
        close_button.config(bg=COLORS['title_bg'])
    
    close_button.bind('<Enter>', on_close_enter)
    close_button.bind('<Leave>', on_close_leave)

    # 设置窗口背景色和样式
    app.root.configure(bg=COLORS['bg_dark'])
    app.root.option_add('*Font', 'Helvetica 10')
    
    # 创建主框架
    main_frame = tk.Frame(app.root, bg=COLORS['bg_dark'])
    main_frame.pack(padx=20, pady=(0, 20), fill=tk.BOTH, expand=True)

    # 顶部控制区域
    top_frame = tk.Frame(main_frame, bg=COLORS['bg_dark'])
    top_frame.pack(fill=tk.X, pady=(0, 10))

    # 电台切换区域
    radio_label = tk.Label(top_frame, text="电台:",
                          bg=COLORS['bg_dark'],
                          fg=COLORS['text'],
                          font=('Helvetica', 10, 'bold'))
    radio_label.pack(side=tk.LEFT, padx=(0, 5))

    # 自定义 Combobox 样式
    style = ttk.Style()
    
    # 完全覆盖 Combobox 的所有状态样式
    style.map('Custom.TCombobox',
              fieldbackground=[('readonly', COLORS['bg_dark']),
                             ('disabled', COLORS['bg_dark']),
                             ('active', COLORS['bg_dark'])],
              selectbackground=[('readonly', COLORS['accent']),
                              ('disabled', COLORS['accent']),
                              ('active', COLORS['accent'])],
              selectforeground=[('readonly', COLORS['text']),
                              ('disabled', COLORS['text']),
                              ('active', COLORS['text'])],
              background=[('readonly', COLORS['bg_dark']),
                         ('disabled', COLORS['bg_dark']),
                         ('active', COLORS['bg_dark'])])
    
    style.configure('Custom.TCombobox',
                   fieldbackground=COLORS['bg_dark'],     # 输入框背景色
                   background=COLORS['bg_dark'],          # 整体背景色
                   foreground=COLORS['text'],             # 文字颜色
                   arrowcolor=COLORS['accent'],           # 下拉箭头颜色
                   selectbackground=COLORS['accent'],     # 选中项背景色
                   selectforeground=COLORS['text'],       # 选中项文字颜色
                   borderwidth=0,                         # 无边框
                   padding=5)                             # 内边距
    
    # 设置下拉列表样式
    app.root.option_add('*TCombobox*Listbox.background', COLORS['bg_dark'])
    app.root.option_add('*TCombobox*Listbox.foreground', COLORS['text'])
    app.root.option_add('*TCombobox*Listbox.selectBackground', COLORS['accent'])
    app.root.option_add('*TCombobox*Listbox.selectForeground', COLORS['text'])
    app.root.option_add('*TCombobox*Listbox.font', FONTS['normal'])
    app.root.option_add('*TCombobox*Listbox.borderWidth', '0')
    
    # 创建电台选择框
    app.radio_combobox = ttk.Combobox(top_frame,
                                     state="readonly",
                                     width=30,
                                     style='Custom.TCombobox',
                                     font=FONTS['normal'])
    app.radio_combobox.pack(side=tk.LEFT, padx=5)
    app.radio_combobox.bind("<<ComboboxSelected>>", app.switch_playlist)
    app.radio_combobox['values'] = list(app.playlists.keys())

    app.playlist_button = create_custom_button(top_frame, "播放列表", app.toggle_playlist)
    app.playlist_button.pack(side=tk.LEFT, padx=5)

    # 播放列表框
    playlist_frame = tk.Frame(main_frame, bg=COLORS['bg_dark'])
    playlist_frame.pack(fill=tk.BOTH, expand=True, pady=10)

    # 播放模式按钮框架
    play_mode_frame = tk.Frame(playlist_frame, bg=COLORS['bg_dark'])
    play_mode_frame.pack(side=tk.RIGHT, padx=10)

    # 单曲循环按钮
    single_loop_button = create_custom_button(play_mode_frame, "单曲循环",
                                            command=lambda: app.set_play_mode("single_loop"))
    single_loop_button.pack(fill=tk.X, pady=2)

    # 列表循环按钮
    list_loop_button = create_custom_button(play_mode_frame, "列表循环",
                                          command=lambda: app.set_play_mode("list_loop"))
    list_loop_button.pack(fill=tk.X, pady=2)

    # 随机播放按钮
    random_play_button = create_custom_button(play_mode_frame, "随机播放",
                                            command=lambda: app.set_play_mode("random"))
    random_play_button.pack(fill=tk.X, pady=2)

    # 自定义滚动条样式
    style.configure("Custom.Vertical.TScrollbar",
                   background=COLORS['accent'],
                   troughcolor=COLORS['bg_light'],
                   width=10,
                   arrowsize=13)

    # 创建播放列表和滚动条
    scrollbar = ttk.Scrollbar(playlist_frame, style="Custom.Vertical.TScrollbar")
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    app.listbox = tk.Listbox(playlist_frame,
                            bg=COLORS['bg_light'],
                            fg=COLORS['text'],
                            selectbackground=COLORS['accent'],
                            selectforeground=COLORS['text'],
                            font=('Helvetica', 10),
                            height=15,
                            activestyle='none',
                            bd=0,
                            highlightthickness=0,
                            yscrollcommand=scrollbar.set)
    app.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.config(command=app.listbox.yview)
    app.listbox.grid_remove()  # 初始隐藏

    # 进度条样式
    style.configure("Custom.Horizontal.TProgressbar",
                   background=COLORS['accent'],
                   troughcolor=COLORS['bg_light'],
                   thickness=8)

    # 创建波形效果画布 - 放在进度条上方
    wave_canvas = tk.Canvas(main_frame,
                          height=60,               # 设置画布高度
                          bg=COLORS['bg_dark'],    # 设置背景色
                          highlightthickness=0)    # 移除边框
    wave_canvas.pack(fill=tk.X, pady=(10, 5))     # 放在合适的位置

    # 创建并启动波形效果
    def start_wave_animation():
        # 等待画布完全创建
        wave_canvas.update()
        # 创建波形
        wave = create_wave_effect(wave_canvas,
                                wave_canvas.winfo_width(),
                                wave_canvas.winfo_height())
        # 启动动画
        update_wave(wave_canvas, wave, 0)

    # 确保画布创建完成后再启动动画
    app.root.after(100, start_wave_animation)

    # 进度条
    app.progress = ttk.Progressbar(main_frame,
                                 style="Custom.Horizontal.TProgressbar",
                                 orient="horizontal",
                                 mode="determinate")
    app.progress.pack(fill=tk.X, pady=5)
    app.progress.bind("<Button-1>", app.on_progress_click)
    app.progress.bind("<B1-Motion>", app.on_progress_drag)
    app.progress.bind("<ButtonRelease-1>", app.on_progress_release)

    # 控制按钮区域 - 重新布局
    control_frame = tk.Frame(main_frame, bg=COLORS['bg_dark'])
    control_frame.pack(fill=tk.X, pady=10)

    # 创建左侧播放控制按钮框架
    play_control_frame = tk.Frame(control_frame, bg=COLORS['bg_dark'])
    play_control_frame.pack(side=tk.LEFT, padx=20)

    # 播放控制按钮 - 统一大小和间距
    button_width = 8  # 统一按钮宽度
    play_button = create_custom_button(play_control_frame, "播放", app.play_music, width=button_width)
    play_button.pack(side=tk.LEFT, padx=5)

    pause_button = create_custom_button(play_control_frame, "暂停", app.pause_music, width=button_width)
    pause_button.pack(side=tk.LEFT, padx=5)

    next_button = create_custom_button(play_control_frame, "下一首", app.next_song, width=button_width)
    next_button.pack(side=tk.LEFT, padx=5)

    stop_button = create_custom_button(play_control_frame, "停止", app.stop_music, width=button_width)
    stop_button.pack(side=tk.LEFT, padx=5)

    # 音量控制 - 右对齐
    volume_frame = tk.Frame(control_frame, bg=COLORS['bg_dark'])
    volume_frame.pack(side=tk.RIGHT, padx=20)

    volume_label = tk.Label(volume_frame, text="音量:", bg=COLORS['bg_dark'], fg=COLORS['text'])
    volume_label.pack(side=tk.LEFT, padx=(0, 5))

    app.volume_slider = tk.Scale(volume_frame,
                               from_=0, to=100,
                               orient="horizontal",
                               command=app.set_volume,
                               length=150,
                               bg=COLORS['bg_dark'],
                               fg=COLORS['text'],
                               activebackground=COLORS['accent_hover'],
                               background=COLORS['accent'],
                               troughcolor=COLORS['bg_light'],
                               sliderrelief='flat',
                               sliderlength=15,
                               width=8,
                               showvalue=0,
                               highlightthickness=0)
    app.volume_slider.set(50)
    app.volume_slider.pack(side=tk.LEFT)

    # 播放列表管理按钮 - 重新布局
    playlist_control_frame = tk.Frame(main_frame, bg=COLORS['bg_dark'])
    playlist_control_frame.pack(fill=tk.X, pady=15)

    # 创建左侧和右侧按钮框架
    left_buttons = tk.Frame(playlist_control_frame, bg=COLORS['bg_dark'])
    left_buttons.pack(side=tk.LEFT, padx=20)

    right_buttons = tk.Frame(playlist_control_frame, bg=COLORS['bg_dark'])
    right_buttons.pack(side=tk.RIGHT, padx=20)

    # 音乐管理按钮
    add_button = create_custom_button(left_buttons, "添加音乐", app.add_music, width=10)
    add_button.pack(side=tk.LEFT, padx=5)

    remove_button = create_custom_button(left_buttons, "删除音乐", app.remove_music, width=10)
    remove_button.pack(side=tk.LEFT, padx=5)

    # 电台管理按钮
    add_radio_button = create_custom_button(right_buttons, "添加电台", app.add_radio, width=10)
    add_radio_button.pack(side=tk.LEFT, padx=5)

    remove_radio_button = create_custom_button(right_buttons, "删除电台", app.remove_radio, width=10)
    remove_radio_button.pack(side=tk.LEFT, padx=5)

    # 时间标签
    app.time_label = tk.Label(main_frame,
                             text="00:00 / 00:00",
                             bg=COLORS['bg_dark'],
                             fg=COLORS['text'])
    app.time_label.pack(pady=5)

    # 创建歌词显示区域的标题
    lyrics_label = tk.Label(main_frame,
                          text="歌词显示",
                          bg=COLORS['bg_dark'],
                          fg=COLORS['text'],
                          font=FONTS['title'])
    lyrics_label.pack(pady=(20, 5))

    # 歌词显示框 - 显著增大尺寸
    app.lyrics_text = tk.Text(main_frame,
                            wrap=tk.WORD,          # 自动换行
                            height=25,             # 增加显示行数
                            width=80,              # 增加显示宽度
                            font=FONTS['normal'],  # 正常字体
                            bg=COLORS['bg_light'], # 背景色
                            fg=COLORS['text'],     # 文字颜色
                            relief=tk.FLAT,        # 扁平效果
                            padx=30,               # 增加水平内边距
                            pady=20)               # 增加垂直内边距
    app.lyrics_text.pack(fill=tk.BOTH, expand=True, padx=100, pady=20)  # 增加外边距
    
    # 配置歌词显示样式
    app.lyrics_text.tag_configure("center", justify='center')
    app.lyrics_text.tag_configure("highlight",
                                foreground=COLORS['accent'],      # 使用主题色高亮
                                font=FONTS['lyrics_highlight'],   # 使用高亮字体
                                justify='center')                 # 居中对齐

    # 更新播放列表
    if app.current_playlist_name:
        app.current_playlist = app.playlists[app.current_playlist_name]
        app.update_listbox()

    # 设置窗口最小尺寸
    app.root.update()
    app.root.minsize(app.root.winfo_width(), app.root.winfo_height())