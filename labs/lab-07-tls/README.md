\# Lab 07 – Transport Layer Security (TLS)



\## Overview



This lab explored how Transport Layer Security (TLS) can protect communication between a client and server. A simple Python client and server were first implemented using normal TCP sockets to demonstrate that application data can be observed in plaintext.



The same client-server communication was then secured using TLS and a self-signed X.509 certificate. Wireshark was used to compare the unencrypted and encrypted traffic and inspect the TLS handshake and negotiated cipher suite.



Finally, the TLS client was modified to connect to the Murdoch University website over HTTPS using trusted system CA certificates.



\## Environment



\- Ubuntu 20.04 VM

\- Python 3.8.10

\- Wireshark 3.2.3

\- OpenSSL

\- Python `socket` and `ssl` modules

\- Loopback interface (`127.0.0.1`)

\- Local test port: `4444`



\---



\## Task 1 – Simple TCP Client and Server



A basic Python client and server were created using TCP sockets.



The server listened on:



```text

127.0.0.1:4444

