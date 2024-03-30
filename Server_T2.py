import socket
import threading
import tkinter
import tkinter.scrolledtext
from tkinter import simpledialog

class ServerApp:
    def __init__(self, host, port):
        self.HOST = host
        self.PORT = port

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.HOST, self.PORT))
        self.server.listen()

        self.clients = []
        self.nicknames = []
        self.conversations = {}  

        
        self.server_thread = threading.Thread(target=self.accept_clients)
        self.gui_thread = threading.Thread(target=self.gui_loop)

        self.server_thread.start()
        self.gui_thread.start()

    def accept_clients(self):
        while True:
            client, address = self.server.accept()
            print(f"connected with {str(address)}")

            client.send("NICK".encode('utf-8'))
            nickname = client.recv(4096).decode('utf-8')  

            self.nicknames.append(nickname)
            self.clients.append(client)

            self.update_chat_list()

            print(f"Nickname of the client is {nickname}")
            client.send("connected to server".encode('utf-8'))
            thread = threading.Thread(target=self.handle, args=(client,))
            thread.start()

    def handle(self, client):
        while True:
            try:
                message = ''
                while True:
                    chunk = client.recv(4096).decode('utf-8')
                    message += chunk
                    if '\n\nEND\n\n' in chunk:
                        message=message[:-6]
                        break
                
                if message:
                    sender_index = self.clients.index(client)
                    sender_nickname = self.nicknames[sender_index]
                    print(f"{sender_nickname}: {message}")
                    self.conversations.setdefault(sender_nickname, []).append(f"{sender_nickname}: {message}")
                    if self.selected_client_nickname.get() == sender_nickname:
                        self.update_conversation_text(sender_nickname)
            except:
                index = self.clients.index(client)
                nickname = self.nicknames[index]
                self.clients.remove(client)
                self.nicknames.remove(nickname)
                if nickname in self.conversations:
                    del self.conversations[nickname]
                client.close()
                break

    def on_key(self,event):
        if event.keycode == 13:  
            self.send_message()
            
    def gui_loop(self):
        self.window = tkinter.Tk()
        self.window.resizable(width=False, height=False)
        self.window.title("Server App")
        self.window.config(bg="black")

        self.selected_client_nickname = tkinter.StringVar()
        self.selected_client_nickname.set("")  # Initialize with empty string

        self.window.rowconfigure(0, weight=1)
        self.window.columnconfigure(0, weight=1)
        self.window.columnconfigure(1, weight=3)

        chat_frame = tkinter.Frame(self.window, bg="gray")
        chat_frame.grid(row=0, column=0, sticky="nsew")

        self.chat_list = tkinter.Listbox(chat_frame, bg="white")
        self.chat_list.bind("<<ListboxSelect>>", self.select_client)  # Bind the select event
        self.chat_list.grid(row=0, column=0, sticky="nsew")

        conversation_frame = tkinter.Frame(self.window, bg="lightgray")
        conversation_frame.grid(row=0, column=1, sticky="nsew")
        # conversation_frame.config(bg='black')

        self.conversation_text = tkinter.scrolledtext.ScrolledText(conversation_frame, bg="white", state='disabled', font=("consolas",12))
        self.conversation_text.grid(row=0, column=0, sticky="nsew")
        self.conversation_text.config(bg='black',fg='white')

        self.message_entry = tkinter.Entry(conversation_frame, width=50, font="consolas")
        self.message_entry.grid(row=1, column=0, sticky="ew", padx=5)
        self.message_entry.config(bg='black',fg='white')
        
        
        send_button = tkinter.Button(conversation_frame, text="Send", command=self.send_message, width=10)
        send_button.grid(row=1, column=1, sticky="ew", pady=5)

        self.message_entry.bind('<Key>',self.on_key)
        # Bind window close event
        self.window.protocol("WM_DELETE_WINDOW", self.stop)

        self.window.mainloop()

    def select_client(self, event):
        selected_index = self.chat_list.curselection()
        if selected_index:
            nickname = self.chat_list.get(selected_index)
            self.selected_client_nickname.set(nickname)
            self.update_conversation_text(nickname)

    def send_message(self):
        message = self.message_entry.get()
        selected_client_nickname = self.selected_client_nickname.get()
        if selected_client_nickname:
            selected_index = self.nicknames.index(selected_client_nickname)
            selected_client = self.clients[selected_index]
            selected_client.send(message.encode('utf-8'))
            self.conversation_text.config(state='normal')
            self.conversation_text.insert(tkinter.END, f" {message}\n")
            self.conversation_text.config(state='disabled')
            self.message_entry.delete(0, tkinter.END)

    def update_chat_list(self):
        self.chat_list.delete(0, tkinter.END)
        for name in self.nicknames:
           
            self.chat_list.insert(tkinter.END, name)

    def update_conversation_text(self, nickname):
        self.conversation_text.config(state='normal')
        self.conversation_text.delete('1.0', tkinter.END)
        conversation_history = self.conversations.get(nickname, [])
        for message in conversation_history:
            self.conversation_text.insert(tkinter.END, f"{message}\n")
        self.conversation_text.config(state='disabled')

    def stop(self):
        self.server.close()

        for client in self.clients:
            client.close()

        self.window.quit()

if __name__ == "__main__":
    HOST = '127.0.0.1'
    PORT = 9090
    server_app = ServerApp(HOST, PORT)
