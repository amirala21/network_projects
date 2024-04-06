import socket
import threading
import tkinter
import tkinter.scrolledtext
from tkinter import simpledialog
import os


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

        self.CHUNK_SIZE = 4096
        self.receiving_file=False
        self.sending_file=False
        self.des_path=""
        self.src_path=""
        
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
            message=b''
            while True:
                
                chunk = client.recv(self.CHUNK_SIZE)
                message += chunk
                if chunk == b'EOF':
                    break
            if self.receiving_file is True:
                print('receiving...')
                print(self.des_path)
                full_path = os.path.join(self.des_path)
                try:
                    if True:
                        try:
                            with open(full_path, 'wb') as file:
                                print ("saving file...")
                                    
                                file.write(message)
                                self.conversation_text.config(state='normal')
                                self.conversation_text.insert(tkinter.END, f"File received and saved to {self.des_path}\n")
                                self.conversation_text.config(state='disabled')
                        except Exception as e:
                            print(f"Error receiving file: {e}")
                except Exception as e:
                    print(f"error : {e}")
                self.receiving_file=False
                
            else:
                try:                    
                    if message:
                        message=message.decode('utf-8')
                        message=message[:-3]
                        sender_index = self.clients.index(client)
                        sender_nickname = self.nicknames[sender_index]
                        print(f"{sender_nickname}: {message}")
                        self.conversations.setdefault(sender_nickname, []).append(f" >>> {message}")
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
        self.selected_client_nickname.set("")  

        self.window.rowconfigure(0, weight=1)
        self.window.columnconfigure(0, weight=1)
        self.window.columnconfigure(1, weight=3)

        chat_frame = tkinter.Frame(self.window, bg="gray")
        chat_frame.grid(row=0, column=0, sticky="nsew")

        self.chat_list = tkinter.Listbox(chat_frame, bg="white")
        self.chat_list.bind("<<ListboxSelect>>", self.select_client)  # Bind the select event
        self.chat_list.grid(row=0, column=0, sticky="nsew")

        disconnect_button = tkinter.Button(chat_frame, text="Disconnect", command=self.disconnect_selected_client)
        disconnect_button.grid(row=1, column=0, sticky="ew", pady=5)

        change_name_button = tkinter.Button(chat_frame, text="Change Name", command=self.change_client_name)
        change_name_button.grid(row=2, column=0, sticky="ew", pady=5)

        move_up_button = tkinter.Button(chat_frame, text="Move Up", command=self.move_up)
        move_up_button.grid(row=3, column=0, sticky="ew", pady=5)

        move_down_button = tkinter.Button(chat_frame, text="Move Down", command=self.move_down)
        move_down_button.grid(row=4, column=0, sticky="ew", pady=5)

        Broadcast_button=tkinter.Button(chat_frame,text="Broadcast",command=self.broadcast)
        Broadcast_button.grid(row=5, column=0, sticky="ew", pady=5)
        
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
   
    def handle_command(self,command):
        
        parts=command.split(' ')
        if parts[0]=="DOWNLOAD":
            self.receiving_file=True
            self.des_path=parts[2]
            print("downloading >>> ",self.des_path)
        elif parts[0]=='UPLOAD':
            self.sending_file=True
            self.src_path=parts[1]
            print("uploading >>> ",self.src_path)
        return command
        
    # def send_file(self, client, file_path):
    
    #     try:
    #         with open(file_path, 'rb') as file:
    #             while chunk:
    #                 chunk = file.read(self.CHUNK_SIZE)
                    
    #                 client.sendall(chunk)
    #             self.conversation_text.config(state='normal')
    #             self.conversation_text.insert(tkinter.END, f"File {os.path.basename(file_path)} sent\n")
    #             self.conversation_text.config(state='disabled')
    #     except Exception as e:
    #         print(f"Error sending file: {e}")
    #     return
    def send_file(self):
        if self.sending_file is True:
            try:
                chunk=b''
                with open(self.src_path, 'rb') as file:
                    print(f"file {self.src_path} is reading...")
                    with open(self.src_path, 'rb') as file:
                        chunk = file.read()
                        # self.client.sendall(chunk)
                        # self.client.send(b'EOF')
                    selected_client_nickname = self.selected_client_nickname.get()
                    if selected_client_nickname:
                        selected_index = self.nicknames.index(selected_client_nickname)
                        selected_client = self.clients[selected_index]
                    selected_client.sendall(chunk)
                    selected_client.send(b'EOF')
                    self.conversation_text.config(state='normal')
                    self.conversation_text.insert(tkinter.END, f"File {os.path.basename(self.src_path)} sent\n")
                    self.conversation_text.config(state='disabled')
            except Exception as e:
                print(f"Error sending file: {e}")
            self.sending_file=False
    
    def broadcast(self):
        message=simpledialog.askstring("Command", f"please enter command:")
        for nick in self.nicknames:
            selected_client_nickname = nick
            if selected_client_nickname:
                selected_index = self.nicknames.index(selected_client_nickname)
                selected_client = self.clients[selected_index]
                selected_client.send(message.encode('utf-8'))
                self.conversation_text.config(state='normal')
                self.conversation_text.insert(tkinter.END, f" {message}\n")
                self.conversation_text.config(state='disabled')
                self.message_entry.delete(0, tkinter.END)
    
    def select_client(self, event):
        selected_index = self.chat_list.curselection()
        if selected_index:
            nickname = self.chat_list.get(selected_index)
            self.selected_client_nickname.set(nickname)
            self.update_conversation_text(nickname)

    def send_message(self):
        
        message = self.message_entry.get()
        # if message.startswith("DOWNLOAD"):
        #     self.receiving_file=True
        selected_client_nickname = self.selected_client_nickname.get()
        if selected_client_nickname:
            selected_index = self.nicknames.index(selected_client_nickname)
            selected_client = self.clients[selected_index]
            selected_client.send(self.handle_command(message).encode('utf-8'))
            # selected_client.send(b'EOF')
            self.conversation_text.config(state='normal')
            self.conversation_text.insert(tkinter.END, f" {message}\n")
            self.conversation_text.config(state='disabled')
            self.message_entry.delete(0, tkinter.END)
        if self.sending_file is True:
            self.send_file()

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

    def disconnect_selected_client(self):
        selected_index = self.chat_list.curselection()
        if selected_index:
            nickname = self.chat_list.get(selected_index)
            self.selected_client_nickname.set("")
            self.update_conversation_text("")
            self.update_chat_list()

    def change_client_name(self):
        selected_index = self.chat_list.curselection()
        if selected_index:
            old_nickname = self.chat_list.get(selected_index)
            new_nickname = simpledialog.askstring("Change Name", f"Change name of {old_nickname} to:")
            if new_nickname and new_nickname != old_nickname:
                index = self.nicknames.index(old_nickname)
                self.nicknames[index] = new_nickname
                self.update_chat_list()
                self.chat_list.selection_clear(0, tkinter.END)
                self.chat_list.select_set(selected_index)
                self.selected_client_nickname.set(new_nickname)
                self.update_conversation_text(new_nickname)

    def move_up(self):
        selected_index = self.chat_list.curselection()
        if selected_index and selected_index[0] > 0:
            nickname = self.chat_list.get(selected_index)
            index = selected_index[0]
            self.nicknames[index], self.nicknames[index - 1] = self.nicknames[index - 1], self.nicknames[index]
            self.update_chat_list()
            self.chat_list.selection_set(index - 1)

    def move_down(self):
        selected_index = self.chat_list.curselection()
        if selected_index and selected_index[0] < len(self.nicknames) - 1:
            nickname = self.chat_list.get(selected_index)
            index = selected_index[0]
            self.nicknames[index], self.nicknames[index + 1] = self.nicknames[index + 1], self.nicknames[index]
            self.update_chat_list()
            self.chat_list.selection_set(index + 1)

    def stop(self):
        self.server.close()

        for client in self.clients:
            client.close()

        self.window.quit()

HOST = '127.0.0.1'
PORT = 9090
server_app = ServerApp(HOST, PORT)
