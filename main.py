import os 
import time

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





