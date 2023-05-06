import sys
import time
import tkinter as tk
from threading import Thread

from tkinter import *

from tcp.monopoly_client import MonopolyClient

client: MonopolyClient = None


class GUI:
    master: Tk
    up_frame: Frame
    below_frame: Frame
    scroll_bar: Scrollbar
    list_box: Listbox
    entry: Entry
    client_connected = False
    port = 0

    def __init__(self, master):
        self.master = master
        self.update_window()

    def handle_start(self, port):
        self.port = port
        # TODO: This variable should be thread safe
        global client
        client = MonopolyClient(port)
        self.list_box.insert("end", "Client is connected to server.")
        self.client_connected = True
        t = Thread(target=self.add_new_log)
        t.start()

    def show_entry_fields(self):
        i = self.entry.get()
        if not self.client_connected:
            args = i.split(",")
            if args[0] == "connect":
                self.handle_start(int(args[1]))
                self.entry.delete(0, END)
        else:
            self.entry.delete(0, END)
            client.send_command(i)

    def handle_enter(self, event):
        self.show_entry_fields()

    def update_window(self):
        self.up_frame = Frame(self.master, background="red")

        self.up_frame.pack(expand=True, fill=BOTH)

        self.scroll_bar = tk.Scrollbar(self.up_frame, orient="vertical")
        self.list_box = tk.Listbox(self.up_frame, width=50, height=20, background="gray31",
                                   yscrollcommand=self.scroll_bar.set, fg='#fff')
        self.scroll_bar.config(command=self.list_box.yview)
        self.list_box.insert("end", "Welcome to Monopoly Client GUI.")
        self.scroll_bar.pack(side="right", fill="y")
        self.list_box.pack(side="left", fill="both", expand=True)

        self.below_frame = Frame(self.master, background="black")
        tk.Label(self.below_frame, text="command: ", background="black", fg='#fff').grid(row=0, column=0)
        self.entry = tk.Entry(self.below_frame, background="black", fg='#fff')
        self.entry.grid(row=0, column=1)
        self.entry.bind('<Return>', self.handle_enter)
        tk.Button(self.below_frame, text='send', background="black", command=self.show_entry_fields, fg='#fff').grid(row=0,
                                                                                                          column=2,
                                                                                                          stick=tk.W,
                                                                                                          pady=3)
        self.below_frame.pack(expand=False, fill=X)

    def add_new_log(self):
        i = 0
        self.list_box.insert("end", f"Client is listening localhost:{self.port}")
        while True:
            client.c.acquire()
            client.c.wait()
            print("Condition variable is notified! New log is arrived from server.")
            for log in client.logs:
                print(log)
                self.list_box.insert("end", log)
            client.logs = []
            i += 1
            client.c.release()


if __name__ == "__main__":
    root = Tk()
    window = GUI(root)
    root.mainloop()
