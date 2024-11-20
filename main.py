import tkinter as tk
import pygame
from src.player import MusicPlayer
from src.ui import setup_ui, COLORS
import time
import os
import sys

def resource_path(relative_path):
    """获取资源的绝对路径"""
    try:
        # PyInstaller创建临时文件夹,将路径存储在_MEIPASS中
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

class SplashScreen:
    def __init__(self, parent):
        self.parent = parent
        self.splash = tk.Toplevel(parent)
        self.splash.overrideredirect(True)
        
        # 设置启动窗口图标
        try:
            icon_path = resource_path('icon.ico')
            self.splash.iconbitmap(default=icon_path)
        except:
            print("无法加载启动窗口图标")
        
        # 获取屏幕尺寸
        screen_width = parent.winfo_screenwidth()
        screen_height = parent.winfo_screenheight()
        
        # 设置启动窗口尺寸和位置
        width = 400
        height = 300
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.splash.geometry(f'{width}x{height}+{x}+{y}')
        
        # 设置透明度
        self.splash.attributes('-alpha', 0.0)
        
        # 创建圆角背景
        self.canvas = tk.Canvas(self.splash, width=width, height=height,
                              highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # 创建渐变背景
        self.create_gradient_background(width, height)
        
        # 创建标题
        self.canvas.create_text(width//2, height//3,
                              text="个人音乐电台",
                              font=('Helvetica', 24, 'bold'),
                              fill=COLORS['text'])
        
        # 创建加载进度条背景
        self.progress_bg = self.canvas.create_rectangle(50, height//2,
                                                      width-50, height//2+10,
                                                      fill=COLORS['bg_light'],
                                                      outline="")
        
        # 创建加载进度条
        self.progress = self.canvas.create_rectangle(50, height//2,
                                                   50, height//2+10,
                                                   fill=COLORS['accent'],
                                                   outline="")
        
        # 创建加载文本
        self.loading_text = self.canvas.create_text(width//2, height*2//3,
                                                  text="正在加载...",
                                                  font=('Helvetica', 12),
                                                  fill=COLORS['text'])
        
        self.fade_in()

    def create_gradient_background(self, width, height):
        """创建渐变背景"""
        # 定义渐变色
        gradient_colors = [
            '#1e392a',  # 深绿色
            '#2d5a27',  # 中绿色
            '#3c7a24',  # 浅绿色
        ]
        
        # 计算每个颜色区域的高度
        section_height = height / (len(gradient_colors) - 1)
        
        # 创建渐变效果
        for i in range(len(gradient_colors) - 1):
            # 获取当前颜色对
            color1 = gradient_colors[i]
            color2 = gradient_colors[i + 1]
            
            # 创建多个渐变矩形
            steps = 50  # 渐变步数
            for j in range(steps):
                # 计算当前位置
                y1 = i * section_height + (j * section_height / steps)
                y2 = y1 + (section_height / steps)
                
                # 计算当前颜色
                ratio = j / steps
                r1, g1, b1 = [int(color1[i:i+2], 16) for i in (1, 3, 5)]
                r2, g2, b2 = [int(color2[i:i+2], 16) for i in (1, 3, 5)]
                r = int(r1 + (r2 - r1) * ratio)
                g = int(g1 + (g2 - g1) * ratio)
                b = int(b1 + (b2 - b1) * ratio)
                color = f'#{r:02x}{g:02x}{b:02x}'
                
                # 创建矩形
                self.canvas.create_rectangle(0, y1, width, y2,
                                          fill=color, outline="")

    def fade_in(self):
        """实现渐入效果"""
        alpha = self.splash.attributes('-alpha')
        if alpha < 1.0:
            alpha += 0.1
            self.splash.attributes('-alpha', alpha)
            self.splash.after(50, self.fade_in)
        else:
            self.simulate_loading()

    def update_progress(self, value):
        """更新进度条"""
        width = self.canvas.winfo_width()
        progress_width = width - 100
        x = 50 + (progress_width * value)
        self.canvas.coords(self.progress, 50, self.canvas.winfo_height()//2,
                         x, self.canvas.winfo_height()//2+10)
        self.canvas.update()

    def simulate_loading(self):
        """模拟加载过程"""
        for i in range(11):
            self.update_progress(i/10)
            time.sleep(0.1)
        self.fade_out()

    def fade_out(self):
        """实现渐出效果"""
        alpha = self.splash.attributes('-alpha')
        if alpha > 0.0:
            alpha -= 0.1
            self.splash.attributes('-alpha', alpha)
            self.splash.after(50, self.fade_out)
        else:
            self.splash.destroy()
            self.show_main_window()

    def show_main_window(self):
        """显示主窗口"""
        self.parent.deiconify()  # 显示主窗口
        setup_main_window(self.parent)

def setup_main_window(root):
    """设置主窗口"""
    # 初始化 Pygame 混音器
    pygame.mixer.init()
    
    app = MusicPlayer(root)
    setup_ui(app)
    
    def on_closing():
        pygame.mixer.quit()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)

def main():
    root = tk.Tk()
    root.title("个人音乐电台")
    root.geometry("1200x900")
    
    # 设置窗口图标
    try:
        icon_path = resource_path('icon.ico')
        root.iconbitmap(default=icon_path)
    except Exception as e:
        print(f"无法加载窗口图标: {e}")
    
    # 先创建一个标准窗口以确保任务栏显示
    root.update_idletasks()
    root.deiconify()  # 确保窗口可见
    
    # 设置窗口属性
    root.attributes('-alpha', 0.95)
    
    # 先让窗口显示在任务栏
    root.state('normal')
    root.update()
    
    # 然后再设置为无边框
    root.overrideredirect(True)
    
    # 隐藏主窗口
    root.withdraw()
    
    # 显示启动画面
    splash = SplashScreen(root)
    
    root.mainloop()

if __name__ == "__main__":
    main()