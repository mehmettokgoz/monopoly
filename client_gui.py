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
    button: Button
    label: Label
    entry: Entry
    client_connected = False
    port = 0
    item_num = 0

    def __init__(self, master):
        self.item_num = 0
        self.master = master
        self.update_window()

    def handle_start(self, port):
        self.port = port
        global client
        client = MonopolyClient(port)
        self.listbox_insert("Client is connected to server.")
        self.client_connected = True
        t = Thread(target=self.add_new_log)
        t.start()

    def listbox_insert(self, p):
        self.list_box.insert("end", p)
        self.list_box.select_clear(self.list_box.size() - 2)
        self.list_box.select_set(END)
        self.list_box.yview(END)

        self.item_num += 1

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
        self.up_frame = Frame(self.master, background="gray20")

        self.up_frame.pack(expand=True, fill=BOTH)

        self.scroll_bar = tk.Scrollbar(self.up_frame, orient="vertical")
        self.list_box = tk.Listbox(self.up_frame, width=60, height=20,
                                   yscrollcommand=self.scroll_bar.set, fg='white', bg='black')
        self.scroll_bar.config(command=self.list_box.yview)
        self.list_box.config(yscrollcommand=self.scroll_bar.set)
        self.listbox_insert(
            "Welcome to Monopoly client GUI. Use 'connect,PORT' command to connect the server.")
        self.scroll_bar.pack(side="right", fill="y")
        self.list_box.pack(side="left", fill="both", expand=True)

        self.below_frame = Frame(self.master)

        self.entry = tk.Entry(self.below_frame, background="white", fg='black')
        self.entry.pack(side=LEFT, expand=True, fill=X)
        self.entry.bind('<Return>', self.handle_enter)

        self.button = tk.Button(self.below_frame, text='SEND', command=self.show_entry_fields,
                                bg='white', fg='black', pady=3, padx=3)
        self.button.pack(side=LEFT)
        self.below_frame.pack(expand=False, fill=X, padx=5, pady=5)

    def add_new_log(self):
        i = 0
        self.listbox_insert(f"Client is listening localhost:{self.port}")
        while True:
            client.c.acquire()
            client.c.wait()
            print("Condition variable is notified! New log is arrived from server.")
            for log in client.logs:
                for log_item in log.decode().split("\n"):
                    print("log:", log_item)
                    if log_item != "":
                        self.listbox_insert(log_item.strip("\n").encode())
            client.logs = []
            i += 1
            client.c.release()


if __name__ == "__main__":
    root = Tk()
    window = GUI(root)
    root.mainloop()

