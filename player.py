import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
import os
import random
import pygame
from .data import DataHandler
from .utils import parse_lyrics, format_time
from .ui import COLORS

class MusicPlayer:
    def __init__(self, root):
        self.root = root
        self.is_dragging = False
        self.current_song_length = 0
        self.position_flag = 0
        self.current_playlist_name = None
        self.current_playlist = []
        self.current_song_index = 0
        self.play_mode = "list_loop"
        self.lyrics = []
        self.playlists = {}

        self.data_handler = DataHandler("playlists.json")
        self.load_data()

    def load_data(self):
        """加载播放列表数据"""
        self.playlists = self.data_handler.playlists
        self.current_playlist_name = self.data_handler.current_playlist_name
        if self.current_playlist_name and self.current_playlist_name in self.playlists:
            self.current_playlist = self.playlists[self.current_playlist_name]

    def save_data(self):
        """保存播放列表数据"""
        self.data_handler.save_data(self.playlists, self.current_playlist_name)

    def play_music(self):
        """播放音乐"""
        if not self.current_playlist:
            # 创建自定义警告窗口
            warning_window = tk.Toplevel(self.root)
            warning_window.overrideredirect(True)  # 无边框
            warning_window.configure(bg=COLORS['bg_dark'])
            
            # 设置窗口位置（居中显示）
            window_width = 300
            window_height = 100
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            x = (screen_width - window_width) // 2
            y = (screen_height - window_height) // 2
            warning_window.geometry(f'{window_width}x{window_height}+{x}+{y}')
            
            # 创建警告内容
            warning_frame = tk.Frame(warning_window, bg=COLORS['bg_dark'], padx=20, pady=15)
            warning_frame.pack(fill=tk.BOTH, expand=True)
            
            # 警告文本
            warning_label = tk.Label(warning_frame,
                                   text="播放列表为空",
                                   bg=COLORS['bg_dark'],
                                   fg=COLORS['text'],
                                   font=('Microsoft YaHei UI', 10))
            warning_label.pack(pady=(0, 10))
            
            # 确定按钮
            ok_button = tk.Button(warning_frame,
                                text="确定",
                                bg=COLORS['accent'],
                                fg=COLORS['text'],
                                activebackground=COLORS['accent_hover'],
                                activeforeground=COLORS['text'],
                                relief=tk.FLAT,
                                cursor='hand2',
                                command=warning_window.destroy)
            ok_button.pack()
            
            # 添加按钮悬停效果
            def on_enter(e):
                ok_button.config(bg=COLORS['accent_hover'])
            def on_leave(e):
                ok_button.config(bg=COLORS['accent'])
            
            ok_button.bind('<Enter>', on_enter)
            ok_button.bind('<Leave>', on_leave)
            
            # 自动关闭窗口
            warning_window.after(2000, warning_window.destroy)
            return
        
        self._start_playing()

    def _start_playing(self, start_pos=0):
        """开始播放音乐"""
        if not self.current_playlist:
            return
        song_path = self.current_playlist[self.current_song_index]
        lrc_path = os.path.splitext(song_path)[0] + ".lrc"

        try:
            pygame.mixer.music.load(song_path)
            sound = pygame.mixer.Sound(song_path)
            self.current_song_length = sound.get_length()
        except pygame.error as e:
            messagebox.showerror("错误", f"无法加载音乐文件: {e}")
            return

        if hasattr(self, 'progress'):
            self.progress['maximum'] = self.current_song_length

        self.update_time_label(0, self.current_song_length)

        # 加载歌词文件 - 尝试不同的编码方式
        print(f"尝试加载歌词文件: {lrc_path}")
        if os.path.exists(lrc_path):
            encodings = ['utf-8', 'gbk', 'gb2312', 'ansi']
            for encoding in encodings:
                try:
                    with open(lrc_path, 'r', encoding=encoding) as file:
                        lrc_content = file.read()
                        print(f"使用 {encoding} 编码成功读取歌词")
                        self.lyrics = parse_lyrics(lrc_content)
                        if self.lyrics:  # 如果成功解析到歌词
                            break
                except UnicodeDecodeError:
                    continue
                except Exception as e:
                    print(f"使用 {encoding} 编码读取歌词出错: {e}")
            
            if not self.lyrics:
                print("无法使用任何编码方式正确读取歌词")
        else:
            print(f"歌词文件不存在: {lrc_path}")
            self.lyrics = []

        if hasattr(self, 'lyrics_text'):
            self.lyrics_text.delete(1.0, tk.END)

        pygame.mixer.music.play(start=start_pos)
        self.update_progress()

    def pause_music(self):
        """暂停音乐"""
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()

    def resume_music(self):
        """恢复播放"""
        pygame.mixer.music.unpause()

    def stop_music(self):
        """停止播放"""
        pygame.mixer.music.stop()
        self.update_time_label(0, 0)
        if hasattr(self, 'progress'):
            self.progress['value'] = 0
        if hasattr(self, 'lyrics_text'):
            self.lyrics_text.delete(1.0, tk.END)

    def next_song(self):
        """播放下一首"""
        if not self.current_playlist:
            return

        if self.play_mode == "single_loop":
            pass
        elif self.play_mode == "list_loop":
            self.current_song_index = (self.current_song_index + 1) % len(self.current_playlist)
        elif self.play_mode == "random":
            self.current_song_index = random.randint(0, len(self.current_playlist) - 1)

        if hasattr(self, 'listbox'):
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(self.current_song_index)

        self.update_time_label(0, self.current_song_length)
        if hasattr(self, 'progress'):
            self.progress['value'] = 0
        if hasattr(self, 'lyrics_text'):
            self.lyrics_text.delete(1.0, tk.END)

        self._start_playing()

    def set_volume(self, value):
        """设置音量"""
        volume = float(value) / 100
        pygame.mixer.music.set_volume(volume)

    def set_play_mode(self, mode):
        """设置播放模式"""
        self.play_mode = mode
        
        # 创建自定义样式的消息框
        msg_window = tk.Toplevel(self.root)
        msg_window.overrideredirect(True)  # 无边框
        msg_window.configure(bg=COLORS['bg_dark'])
        
        # 设置窗口位置（居中显示）
        window_width = 300
        window_height = 100
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        msg_window.geometry(f'{window_width}x{window_height}+{x}+{y}')
        
        # 创建消息内容
        msg_frame = tk.Frame(msg_window, bg=COLORS['bg_dark'], padx=20, pady=15)
        msg_frame.pack(fill=tk.BOTH, expand=True)
        
        # 消息文本
        mode_text = {
            "single_loop": "单曲循环",
            "list_loop": "列表循环",
            "random": "随机播放"
        }
        msg_label = tk.Label(msg_frame,
                            text=f"播放模式已设置为: {mode_text.get(mode, mode)}",
                            bg=COLORS['bg_dark'],
                            fg=COLORS['text'],
                            font=('Microsoft YaHei UI', 10))
        msg_label.pack(pady=(0, 10))
        
        # 确定按钮
        ok_button = tk.Button(msg_frame,
                             text="确定",
                             bg=COLORS['accent'],
                             fg=COLORS['text'],
                             activebackground=COLORS['accent_hover'],
                             activeforeground=COLORS['text'],
                             relief=tk.FLAT,
                             cursor='hand2',
                             command=msg_window.destroy)
        ok_button.pack()
        
        # 添加按钮悬停效果
        def on_enter(e):
            ok_button.config(bg=COLORS['accent_hover'])
        def on_leave(e):
            ok_button.config(bg=COLORS['accent'])
        
        ok_button.bind('<Enter>', on_enter)
        ok_button.bind('<Leave>', on_leave)
        
        # 自动关闭窗口
        msg_window.after(2000, msg_window.destroy)

    def switch_playlist(self, event):
        """切换播放列表"""
        selected_radio = self.radio_combobox.get()
        if selected_radio in self.playlists:
            self.current_playlist_name = selected_radio
            self.current_playlist = self.playlists[selected_radio]
            self.update_listbox()

    def toggle_playlist(self):
        """切换播放列表显示状态"""
        if hasattr(self, 'listbox'):
            if self.listbox.winfo_ismapped():
                self.listbox.grid_remove()
            else:
                self.listbox.grid()

    def add_music(self):
        """添加音乐到播放列表"""
        files = filedialog.askopenfilenames(title="选择音乐文件", filetypes=[("音频文件", "*.mp3 *.wav")])
        if files and self.current_playlist_name:
            self.current_playlist.extend(files)
            self.playlists[self.current_playlist_name] = self.current_playlist
            self.update_listbox()
            self.save_data()

    def remove_music(self):
        """从播放列表中移除音乐"""
        selected_indices = self.listbox.curselection()
        if selected_indices:
            for index in reversed(selected_indices):
                del self.current_playlist[index]
                self.listbox.delete(index)
            self.save_data()

    def add_radio(self):
        """添加新电台"""
        # 创建自定义输入对话框
        dialog = tk.Toplevel(self.root)
        dialog.overrideredirect(True)  # 无边框
        dialog.configure(bg=COLORS['bg_dark'])
        
        # 设置窗口位置（居中显示）
        window_width = 300
        window_height = 150
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        dialog.geometry(f'{window_width}x{window_height}+{x}+{y}')
        
        # 创建输入框架
        frame = tk.Frame(dialog, bg=COLORS['bg_dark'], padx=20, pady=15)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题标签
        title_label = tk.Label(frame,
                              text="请输入新的电台名称",
                              bg=COLORS['bg_dark'],
                              fg=COLORS['text'],
                              font=('Microsoft YaHei UI', 12))
        title_label.pack(pady=(0, 15))
        
        # 输入框
        entry = tk.Entry(frame,
                        bg=COLORS['bg_light'],
                        fg=COLORS['text'],
                        insertbackground=COLORS['text'],  # 光标颜色
                        relief=tk.FLAT,
                        font=('Microsoft YaHei UI', 10))
        entry.pack(fill=tk.X, pady=(0, 15))
        
        # 按钮框架
        button_frame = tk.Frame(frame, bg=COLORS['bg_dark'])
        button_frame.pack()
        
        # 确定和取消按钮
        def ok_command():
            name = entry.get().strip()
            if name:
                self.playlists[name] = []
                self.radio_combobox['values'] = list(self.playlists.keys())
                self.save_data()
            dialog.destroy()
        
        def cancel_command():
            dialog.destroy()
        
        # 创建按钮
        ok_button = tk.Button(button_frame,
                             text="确定",
                             bg=COLORS['accent'],
                             fg=COLORS['text'],
                             activebackground=COLORS['accent_hover'],
                             activeforeground=COLORS['text'],
                             relief=tk.FLAT,
                             cursor='hand2',
                             command=ok_command)
        ok_button.pack(side=tk.LEFT, padx=5)
        
        cancel_button = tk.Button(button_frame,
                                 text="取消",
                                 bg=COLORS['accent'],
                                 fg=COLORS['text'],
                                 activebackground=COLORS['accent_hover'],
                                 activeforeground=COLORS['text'],
                                 relief=tk.FLAT,
                                 cursor='hand2',
                                 command=cancel_command)
        cancel_button.pack(side=tk.LEFT, padx=5)
        
        # 添加按钮悬停效果
        def on_enter(e, button):
            button.config(bg=COLORS['accent_hover'])
        def on_leave(e, button):
            button.config(bg=COLORS['accent'])
        
        ok_button.bind('<Enter>', lambda e: on_enter(e, ok_button))
        ok_button.bind('<Leave>', lambda e: on_leave(e, ok_button))
        cancel_button.bind('<Enter>', lambda e: on_enter(e, cancel_button))
        cancel_button.bind('<Leave>', lambda e: on_leave(e, cancel_button))
        
        # 绑定回车键和ESC键
        entry.bind('<Return>', lambda e: ok_command())
        dialog.bind('<Escape>', lambda e: cancel_command())
        
        # 设置焦点到输入框
        entry.focus_set()
        
        # 使对话框模态
        dialog.grab_set()
        dialog.wait_window()

    def remove_radio(self):
        """删除电台"""
        selected_radio = self.radio_combobox.get()
        if selected_radio in self.playlists:
            del self.playlists[selected_radio]
            self.radio_combobox['values'] = list(self.playlists.keys())
            self.save_data()

    def update_listbox(self):
        """更新播放列表显示"""
        if not hasattr(self, 'listbox'):
            return
        self.listbox.delete(0, tk.END)
        for file in self.current_playlist:
            self.listbox.insert(tk.END, os.path.basename(file))

    def on_progress_click(self, event):
        """进度条点击事件"""
        self.is_dragging = True

    def on_progress_drag(self, event):
        """进度条拖动事件"""
        if self.is_dragging and self.current_song_length > 0 and hasattr(self, 'progress'):
            value = event.x * self.current_song_length / self.progress.winfo_width()
            self.progress['value'] = value
            self.update_time_label(value, self.current_song_length)
            self.update_lyrics(value)

    def on_progress_release(self, event):
        """处理进度条释放事件"""
        if self.is_dragging and self.current_song_length > 0:
            value = event.x * self.current_song_length / self.progress.winfo_width()
            self.progress['value'] = value
            self.update_time_label(value, self.current_song_length)
            self.update_lyrics(value)

            try:
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.play(start=value)  # 从新位置开始播放
                else:
                    self._start_playing(start_pos=value)

                # 计算位置偏移
                current_time = pygame.mixer.music.get_pos() / 1000
                self.position_flag = value - current_time

            except pygame.error:
                self._start_playing(start_pos=value)

            self.is_dragging = False

    def update_progress(self):
        """更新进度条和歌词显示"""
        if not self.is_dragging and pygame.mixer.music.get_busy():
            current_time = pygame.mixer.music.get_pos() / 1000
            adjusted_time = current_time + self.position_flag  # 应用位置偏移

            # 确保调整后的时间在有效范围内
            adjusted_time = max(0, min(adjusted_time, self.current_song_length))

            if hasattr(self, 'progress'):
                self.progress['value'] = adjusted_time
            if hasattr(self, 'time_label'):
                self.update_time_label(adjusted_time, self.current_song_length)
            if hasattr(self, 'lyrics_text'):
                self.update_lyrics(adjusted_time)

            # 检查是否需要播放下一首歌
            if adjusted_time >= self.current_song_length - 1:
                self.next_song()
        self.root.after(1000, self.update_progress)

    def update_time_label(self, current_time, total_time):
        """更新时间标签"""
        if not hasattr(self, 'time_label'):
            return
        current_time_str = format_time(current_time)
        total_time_str = format_time(total_time)
        self.time_label.config(text=f"{current_time_str} / {total_time_str}")

    def update_lyrics(self, current_time):
        """更新歌词显示"""
        if self.lyrics and hasattr(self, 'lyrics_text'):
            # 找到当前应该显示的歌词
            current_index = 0
            for i, (time, text) in enumerate(self.lyrics):
                if time > current_time:
                    current_index = i - 1
                    break
            else:
                current_index = len(self.lyrics) - 1

            # 确保索引有效
            current_index = max(0, current_index)

            # 清空当前显示的歌词
            self.lyrics_text.delete(1.0, tk.END)

            # 显示当前歌词及其前后文
            start_index = max(0, current_index - 1)
            end_index = min(len(self.lyrics), current_index + 2)

            for i in range(start_index, end_index):
                time, text = self.lyrics[i]
                # 当前播放的歌词使用高亮样式
                if i == current_index:
                    self.lyrics_text.insert(tk.END, f"{text}\n", "highlight")
                else:
                    self.lyrics_text.insert(tk.END, f"{text}\n", "center")