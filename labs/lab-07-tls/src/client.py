import socket
import ssl
import os
import time

serverIP = "127.0.0.1"
serverPort = 4444

# Expected Common Name in the server certificate
expectedCommonName = "www.test.org"

# Create TLS context
context = ssl.SSLContext(ssl.PROTOCOL_TLS)

# Require the server to provide a trusted certificate
context.verify_mode = ssl.CERT_REQUIRED

# Trust our self-signed certificate
context.load_verify_locations("cert.pem")

# Create normal TCP socket
clientSocket = socket.socket()

# Wrap the TCP socket with TLS
tlsSocket = context.wrap_socket(clientSocket)

# Connect to server
tlsSocket.connect((serverIP, serverPort))

print("TLS connection established")

# Obtain the server certificate
server_cert = tlsSocket.getpeercert()

print("\nServer certificate:")
print(server_cert)

# Extract Common Name
commonName = dict(item[0] for item in server_cert["subject"])["commonName"]

print("\nCertificate Common Name:", commonName)

# Check Common Name
if commonName != expectedCommonName:
    print("ERROR: Certificate Common Name does not match expected server name")
    tlsSocket.close()
    exit()

print("Common Name check: PASSED")

# Extract certificate validity timestamps
notAfterTimestamp = ssl.cert_time_to_seconds(server_cert["notAfter"])
notBeforeTimestamp = ssl.cert_time_to_seconds(server_cert["notBefore"])

currentTimestamp = time.time()

# Check certificate validity
if currentTimestamp < notBeforeTimestamp:
    print("ERROR: Certificate is not yet valid")
    tlsSocket.close()
    exit()

if currentTimestamp > notAfterTimestamp:
    print("ERROR: Certificate has expired")
    tlsSocket.close()
    exit()

print("Certificate validity check: PASSED")

# Send message
msgSend = "Hello from TLS Lab 7 secure client"
tlsSocket.send(msgSend.encode())
print("\nSend to server:%s" % msgSend)

# Receive response
msgReceived = tlsSocket.recv(1024)
print("Received from server:%s" % msgReceived.decode())

# Display negotiated TLS information
print("\nTLS version:", tlsSocket.version())
print("Cipher suite:", tlsSocket.cipher())

# Close TLS connection
tlsSocket.close()
