import time
import tkinter as tk
import multiprocessing as mp
from tkinter import ttk
from ttkbootstrap import Style

class PYGUI:
    def __init__(self):
        self.init_parms = None
        self.tor_label = None
        self.dict_par = self._tkinter_init()
        self.combobox = {}

    def _tkinter_init(self):
        # window = tk.Tk()
        style = Style(theme='darkly')
        window = style.master
        window.title('Click Fraud')
        window.geometry('400x620')

        tab_main = ttk.Notebook()  # 創建分頁
        tab_main.place(relx=0.02, rely=0.02, relwidth=0.95, relheight=0.95)
        tab1 = tk.Frame(tab_main)  # 創建第一頁
        tab1.place(x=0, y=0)
        tab_main.add(tab1, text='SEO流量查詢')

        dict_par = {
            "window": window,
            "tab1": tab1,
        }
        return dict_par

    def layer1_loss_ip(self):
        check_frame1 = ttk.Frame(self.dict_par['tab1'])
        check_frame1.pack(fill=tk.X, ipady=5)
        label1_Label = tk.LabelFrame(check_frame1, text='缺失IP爬蟲', borderwidth=1)
        label1_Label.pack(side=tk.LEFT, expand=tk.YES)
        self.layer1_loss_vpn(check_frame1)


    def layer1_loss_vpn(self, check_frame1):
        label2_Label = tk.LabelFrame(check_frame1, text='缺失VPN爬蟲', borderwidth=1)
        label2_Label.pack(side=tk.RIGHT, expand=tk.YES)



    def gui_unity(self):
        self.layer1_loss_ip()
        self.dict_par['window'].mainloop()
        
pygui = PYGUI()
pygui.gui_unity()