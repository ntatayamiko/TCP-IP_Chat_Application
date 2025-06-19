import socket
import threading
from helper import read_exactly, send_message, receive_message
import tkinter as tk
from tkinter import scrolledtext
import queue

# Global variables
clients = {}  # {socket: username}
clients_lock = threading.Lock()
log_queue = queue.Queue()


def broadcast_message(sender_sock, message):
    """Broadcast a message to all clients except the sender."""
    formatted_msg = f"{clients[sender_sock]}: {message}"
    with clients_lock:
        other_sockets = [sock for sock in clients if sock != sender_sock]
    for sock in other_sockets:
        try:
            send_message(sock, formatted_msg)
        except:
            pass  # Handle in client thread


def handle_client(client_sock, addr):
    """Handle a single client connection."""
    try:
        # Receive username
        username = receive_message(client_sock)
        with clients_lock:
            clients[client_sock] = username
        log_queue.put(f"{username} connected from {addr}")

        # Receive and broadcast messages
        while True:
            message = receive_message(client_sock)
            broadcast_message(client_sock, message)
    except:
        # Client disconnected
        with clients_lock:
            if client_sock in clients:
                username = clients[client_sock]
                del clients[client_sock]
        client_sock.close()
        log_queue.put(f"{username} disconnected")


def accept_connections(server_sock):
    """Accept incoming client connections."""
    while True:
        client_sock, addr = server_sock.accept()
        threading.Thread(target=handle_client, args=(client_sock, addr), daemon=True).start()


def start_server():
    """Start the server when the button is clicked."""
    port = int(port_entry.get())
    ip_add=socket.gethostbyname("localhost")
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind((ip_add, port))
    server_sock.listen()
    log_queue.put(f" !! Server started on port {port} address {ip_add}")
    start_button.config(state=tk.DISABLED)
    threading.Thread(target=accept_connections, args=(server_sock,), daemon=True).start()


def update_logs():
    """Update the GUI log from the queue."""
    while not log_queue.empty():
        message = log_queue.get()
        log_text.config(state=tk.NORMAL)
        log_text.insert(tk.END, f"{message}\n")
        log_text.config(state=tk.DISABLED)
        log_text.see(tk.END)
    root.after(100, update_logs)


# GUI setup
root = tk.Tk()
root.title("Chat Server")
root.geometry("600x600")
root.config(bg="lightblue")

frame1=tk.Frame(root,bg="lightblue",width=800,height=50)
frame1.pack(pady=30)

tk.Label(root,text="Port:",width=50,bg="lightblue",pady=7,font=("Arial", 16)).pack()
port_entry = tk.Entry(root, width=22,bg="white",font=("Arial", 16))
port_entry.insert(0, "12345")
port_entry.pack(pady=10)


def on_enter(e):
    e.widget['background'] = 'lightblue'

def on_leave(e):
    e.widget['background'] = 'skyblue'  # default color for buttons

start_button = tk.Button(root,bg="skyblue",font=("Arial", 25),width=20,pady=10, text="Start Server", command=start_server)
start_button.pack(pady=20)
start_button.bind("<Enter>", on_enter)
start_button.bind("<Leave>", on_leave)

log_text = scrolledtext.ScrolledText(root, font=(20), fg="white",bg="black",width=70, height=13, state=tk.DISABLED)
log_text.pack()

# Start log updates
root.after(100, update_logs)
root.mainloop()