import socket
import threading
from helper import read_exactly, send_message, receive_message
import tkinter as tk
from tkinter import scrolledtext, messagebox
import queue

# Global variables
sock = None
message_queue = queue.Queue()


def receive_messages():
    """Receive messages from the server."""
    try:
        while True:
            message = receive_message(sock)
            message_queue.put(message)
    except:
        message_queue.put("Connection lost")


def connect_to_server():
    """Connect to the server and switch to chat interface."""
    global sock
    ip = ip_entry.get()
    port = int(port_entry.get())
    username = username_entry.get()
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, port))
        send_message(sock, username)

        # Hide login, show chat
        for widget in login_frame.winfo_children():
            widget.pack_forget()
        chat_frame.pack()

        # Start receiving thread
        threading.Thread(target=receive_messages, daemon=True).start()
    except Exception as e:
        messagebox.showerror("Connection Error", str(e))


def send_message_to_server():
    """Send the message from the input field."""
    message = message_entry.get()
    if message and sock:
        send_message(sock, message)
        message_entry.delete(0, tk.END)


def update_chat():
    """Update the chat display from the queue."""
    while not message_queue.empty():
        message = message_queue.get()
        if "Connection lost" in message:
            messagebox.showerror("Error", "Connection to server lost")
            root.quit()
        else:
            chat_text.config(state=tk.NORMAL)
            chat_text.insert(tk.END, f"{message}\n")
            chat_text.config(state=tk.DISABLED)
            chat_text.see(tk.END)
    root.after(100, update_chat)


# GUI setup
root = tk.Tk()
root.geometry("800x800")
root.title("Chills Spot")

tk.Label(root, text="Welcome to Chilling Spot",width=50,bg="lightblue",pady=7,font=("Arial", 16)).pack(pady=10)

# Login frame
login_frame = tk.Frame(root,bg="lightblue",width=1000,height=500, )
login_frame.pack(padx=50,pady=50,fill="both",expand=True)

tk.Label(login_frame, text="Server IP:",width=50,bg="lightblue",pady=7,font=("Arial", 16)).pack(pady=10)
ip_entry = tk.Entry(login_frame,width=35,font=("Arial", 16))
ip_entry.insert(0, "localhost")
ip_entry.pack(pady=10)

tk.Label(login_frame, text="Port:",width=50,bg="lightblue",pady=7,font=("Arial", 16)).pack(pady=10)
port_entry = tk.Entry(login_frame,width=35,font=("Arial", 16))
port_entry.insert(0, "12345")
port_entry.pack(pady=10)

tk.Label(login_frame, text="Username:",width=50,bg="lightblue",pady=7,font=("Arial", 16)).pack(pady=10)
username_entry = tk.Entry(login_frame,width=35,font=("Arial", 16))
username_entry.pack(pady=10)

def on_enter(e):
    e.widget['background'] = 'lightblue'

def on_leave(e):
    e.widget['background'] = 'skyblue'  # default color for buttons

btn=tk.Button(login_frame, bg="skyblue",font=("Arial", 25),text="Connect", command=connect_to_server,width=25,pady=10)
btn.pack(pady=50)
btn.bind("<Enter>", on_enter)
btn.bind("<Leave>", on_leave)

# Chat frame (hidden initially)
chat_frame = tk.Frame(root)

chat_text = scrolledtext.ScrolledText(chat_frame, width=50, height=20, state=tk.DISABLED)
chat_text.pack()

message_entry = tk.Entry(chat_frame, width=40)
message_entry.pack(side=tk.LEFT)

tk.Button(chat_frame, text="Send", command=send_message_to_server).pack(side=tk.LEFT)

# Start chat updates
root.after(100, update_chat)
root.mainloop()