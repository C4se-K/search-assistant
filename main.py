import os 
import time
import socket




def check_net_connection(host = "8.8.8.8", port = 53, timeout = 3):
    
    # host 8.8.8.8 is one of google's pubilic DNS server on port 53    

    try:
        socket.setdefaulttimeout(timeout)
        with socket.create_connection((host, port)):
            return True
    except OSError:
        return False




delim = "::"

try:
    while True:
        u_input = input()
        
        if not u_input:
            #print("no input")
            continue

        a = u_input.split(delim)

        for i, b in enumerate(a):
            print(f" {i +1}: {b}")


except KeyboardInterrupt:
    print("\n system end...")
finally:
    ...





