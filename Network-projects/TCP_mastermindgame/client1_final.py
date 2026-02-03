from socket import *

server_name = input("Enter server IP: ").strip()
server_port = int(input("Enter server port: "))

client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect((server_name, server_port))


# รับ message จาก server
message = client_socket.recv(1024).decode()
print(message)

while True:
    msg = client_socket.recv(1024).decode()
    if not msg:
        break
    print(msg)

    # ถ้า server บอก "Your turn" ให้ผู้เล่นเดา
    if "Your turn" in msg:
        while True:
            guess = input("Enter your guess unique 6 digits (พิมพ์ติดกันเลย): ").strip()
            if len(guess) == 6 and guess.isdigit() and len(set(guess)) == 6:
                # แปลงเป็น "1 2 3 4 5 6" ก่อนส่งไป server
                guess = " ".join(list(guess))
                client_socket.sendall(guess.encode())
                break
            print("Invalid 1input! Please enter exactly unique 6 digits.")

        # รับผลลัพธ์จาก server
        result_msg = client_socket.recv(1024).decode()
        print(result_msg)
