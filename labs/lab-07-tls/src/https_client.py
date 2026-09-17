import socket
import ssl

hostname = "www.murdoch.edu.au"
port = 443

# Create TLS client context
context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)

# Load trusted system CA certificates
context.load_verify_locations("/etc/ssl/certs/ca-certificates.crt")

# Require a valid trusted server certificate
context.verify_mode = ssl.CERT_REQUIRED
context.check_hostname = True

# Create TCP socket
clientSocket = socket.socket()

# Wrap TCP socket with TLS
tlsSocket = context.wrap_socket(
    clientSocket,
    server_hostname=hostname
)

# Connect to Murdoch University HTTPS server
tlsSocket.connect((hostname, port))

print("TLS connection established")
print("TLS version:", tlsSocket.version())
print("Cipher suite:", tlsSocket.cipher())

# Send HTTP GET request
request = (
    "GET / HTTP/1.1\r\n"
    "Host: www.murdoch.edu.au\r\n"
    "Connection: close\r\n"
    "\r\n"
)

tlsSocket.sendall(request.encode())

print("\nHTTP request sent")

# Receive complete response
response = b""

while True:
    data = tlsSocket.recv(4096)

    if not data:
        break

    response += data

tlsSocket.close()

print("\nReceived HTTPS response:\n")
print(response.decode(errors="replace"))
