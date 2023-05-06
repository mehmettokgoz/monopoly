import time
import tkinter as tk
from threading import Thread

from tkinter import *

from tcp.monopoly_client import MonopolyClient

port = 1543
client = MonopolyClient(port)


class Window:
    logs = []

    def update_window(self):
        self.subframe = Frame(self.master, background="blue")
        self.subject = Label(self.subframe, text="Subject")
        self.subject.place(relx=0.5, rely=0.5, anchor=CENTER)
        self.subframe.pack(expand=True, fill=BOTH)

        self.scrollbar = tk.Scrollbar(self.subframe, orient="vertical")
        self.lb = tk.Listbox(self.subframe, width=50, height=10, yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.lb.yview)

        self.scrollbar.pack(side="right", fill="y")
        self.lb.pack(side="left", fill="both", expand=True)

        for i in self.logs:
            self.lb.insert("end", i)

        self.subframe2 = Frame(self.master, background="gray")

        def show_entry_fields():
            self.lb.insert("First Name: %s\nLast Name:" % (e1.get()))

        tk.Label(self.subframe2, text="command: ").grid(row=0)
        e1 = tk.Entry(self.subframe2)
        e1.grid(row=0, column=1)
        tk.Button(self.subframe2, text='send', command=show_entry_fields).grid(row=0, column=2, sticky=tk.W, pady=4)
        self.subframe2.pack(expand=True, fill=BOTH)

    def __init__(self, master):
        self.master = master
        self.update_window()
        t = Thread(target=self.add_new_log)
        t.start()

    def add_new_log(self):
        i = 0
        client.c.acquire()
        while True:
            self.lb.insert("end", "starting to wait for client c")
            # Wait for new log to arrive - client.c is notified inside the MonopolyClient
            client.c.wait()
            self.lb.insert("end",f"new log item {i}")
            i += 1


if __name__ == "__main__":
    root = Tk()
    window = Window(root)
    root.mainloop()
