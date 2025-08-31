import socket
import threading
import json

class NetworkManager:
    def __init__(self):
        self.is_server = False
        self.clients = []
        self.server_socket = None
        self.client_socket = None
        self.connected = False
        self.message_handlers = {}
        
    def start_server(self, port=12345):
        self.is_server = True
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('', port))
        self.server_socket.listen(5)
        print(f"Server started on port {port}")
        
        # Accept clients in separate thread
        thread = threading.Thread(target=self._accept_clients)
        thread.daemon = True
        thread.start()
        
    def connect_to_server(self, address, port=12345):
        self.is_server = False
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect((address, port))
            self.connected = True
            print(f"Connected to server {address}:{port}")
            
            # Start receiving messages
            thread = threading.Thread(target=self._receive_messages)
            thread.daemon = True
            thread.start()
            return True
        except:
            print("Failed to connect to server")
            return False
            
    def send_message(self, message_type, data):
        message = {
            'type': message_type,
            'data': data
        }
        json_message = json.dumps(message)
        
        if self.is_server:
            for client in self.clients:
                try:
                    client.send(json_message.encode())
                except:
                    pass
        elif self.connected:
            self.client_socket.send(json_message.encode())
            
    def register_handler(self, message_type, handler):
        self.message_handlers[message_type] = handler
        
    def _accept_clients(self):
        while True:
            client, addr = self.server_socket.accept()
            self.clients.append(client)
            print(f"Client connected: {addr}")
            
            # Start receiving from this client
            thread = threading.Thread(target=self._receive_from_client, args=(client,))
            thread.daemon = True
            thread.start()
            
    def _receive_from_client(self, client):
        while True:
            try:
                data = client.recv(1024)
                if data:
                    self._process_message(data.decode(), client)
            except:
                self.clients.remove(client)
                break
                
    def _receive_messages(self):
        while self.connected:
            try:
                data = self.client_socket.recv(1024)
                if data:
                    self._process_message(data.decode(), None)
            except:
                self.connected = False
                break
                
    def _process_message(self, message, client):
        try:
            message_obj = json.loads(message)
            handler = self.message_handlers.get(message_obj['type'])
            if handler:
                handler(message_obj['data'], client)
        except:
            pass