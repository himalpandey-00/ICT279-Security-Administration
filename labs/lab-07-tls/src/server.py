import ssl
import socket
import datetime
import time

ipAddress = "127.0.0.1"
port = 4444

# Create TLS context
context = ssl.SSLContext(ssl.PROTOCOL_TLS)

# Load our self-signed certificate as a trusted certificate
context.load_verify_locations("cert.pem")

# Load the server certificate and private key
context.load_cert_chain(
    certfile="cert.pem",
    keyfile="clearkey.pem"
)

# Create normal TCP server socket
serverSocket = socket.socket()
serverSocket.bind((ipAddress, port))
serverSocket.listen()

print("TLS server listening on %s:%d" % (ipAddress, port))

while True:
    # Accept normal TCP connection
    (clientConnection, clientAddress) = serverSocket.accept()
    print("Incoming connection from:%s:%d" % clientAddress)

    # Wrap the accepted connection with TLS
    tlsConnection = context.wrap_socket(
        clientConnection,
        server_side=True
    )

    # Receive encrypted communication through TLS
    msgReceived = tlsConnection.recv(1024)
    print("Received from client:%s" % msgReceived.decode())

    # Send response through TLS
    msgSend = "Hello from TLS Lab 7 secure server"
    tlsConnection.send(msgSend.encode())
    print("Send to client:%s" % msgSend)

    tlsConnection.close()
