import socket, random, threading

client_id = 1
client_list = []  # เก็บ client_id, connection_socket
lock = threading.Lock()  # เพื่อให้ client รอตามคิว
n_rounds = 12
winner = None  # ตอนเริ่มเกมยังไม่มีผู้ชนะ

# ตั้ง server
server_host = '0.0.0.0'
server_port = 12000
num_players = int(input("Max of players: "))  # ใส่จำนวนplayer เก็บเป็น int

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # สร้าง TCP Welcome socket
server_socket.bind((server_host, server_port))  # ใช้ bind กับ listen เพื่อรอ client เข้ามา
server_socket.listen()
print("Waiting for clients joins...")


# รับ client
while client_id <= num_players:  # num_players จำนวน Player ที่ใส่ไป
    connection_socket, addr = server_socket.accept()
    with lock:
        client_list.append((client_id, connection_socket))
        print(f"Client {client_id} connected from {addr} as Player {client_id}")

        # บอกกับ client ว่าเป็น Player ไหน
        msg = f"You are Player {client_id}\n"
        if client_id < num_players:
            msg += "Wait for others players to join...\n"  # ถ้ายังน้อยกว่า num_players รอจนกว่าจะครบ
        connection_socket.sendall(msg.encode())
        client_id = client_id + 1

# Player ครบตามจำนวน num_players แล้วเริ่มเกม
print("All clients connected")
input("Press ENTER to start the game...")

# server บอกเริ่มเกม
for cid, connection_socket in client_list:
    connection_socket.sendall("Game started!🔥\n".encode())


# ฟังก์ชันสุ่มเลข 6 ตัว ไม่ซ้ำ
def unique_6_digits():
    return random.sample(range(10), 6)  # range 0-9


random_digits = unique_6_digits()
print("Random number 6 digits: ", random_digits)

# เข้าลูปเล่นในแต่ละรอบ
names = [f"Player {cid}" for cid, connection_socket in client_list]  # สร้างลิสต์ผู้เล่น

for round_num in range(1, n_rounds + 1):
    player_idx = (round_num - 1) % len(names)  # index เริ่มจาก 0
    player = names[player_idx]  # Ex. player i[1] = player 2
    current_connection_socket = client_list[player_idx][1]

    # ส่งให้ client คนปัจจุบัน
    current_connection_socket.sendall(f"[Round {round_num}] Your turn! {player}\n".encode())

    # ส่งให้ client ที่ยังไม่ถึงตาเล่น
    i = 0
    for cid, connection_socket in client_list:
        if i != player_idx:
            connection_socket.sendall(f"[Round {round_num}] {player} turn, please wait...\n".encode())
        i = i + 1

    # รอคำตอบจาก Player ปัจจุบัน
    guess = current_connection_socket.recv(1024).decode().strip()
    guess = list(map(int, guess.split()))

    # ตรวจคำตอบ ของ Player
    result_per_pos = []
    i = 0
    for g in guess:  # i → index (ตำแหน่ง 0–5)
        if g == random_digits[i]:
            result_per_pos.append("pos")  # ถูกตำแหน่ง
        elif g in random_digits:
            result_per_pos.append("digit")  # มีเลขแต่ไม่ถูกตำแหน่ง
        else:
            result_per_pos.append("none")
        i = i + 1

    correct_pos = result_per_pos.count("pos")  # นับจำนวนที่มีตัวเลข + ถูกตำแหน่ง
    correct_digit = result_per_pos.count("digit")  # มีตัวเลข แต่ไม่ถูกตำแหน่ง

    # แปลง guess เป็น string เพื่อแสดงผล
    guess_str = ' '.join(map(str, guess))

    # ส่งผลลัพธ์ให้ Player ทุกคน
    result_msg = f"{player} guessed pos: {correct_pos} digit: {correct_digit} | {guess_str}\n"
    for cid, connection_socket in client_list:
        connection_socket.sendall(result_msg.encode())

    # แสดงผลฝั่ง Server ด้วย
    print(f"[Round {round_num}] {player} guessed pos: {correct_pos} digit: {correct_digit} | {guess_str}\n")

    # ตรวจสอบ Player ที่ชนะ
    if guess == random_digits:
        winner = player
        print(f"\n{winner} WINS!🥇")
        break

# สรุปผล
if winner:
    end_msg = f"\n{winner} WINS!🥇 The number was {' '.join(map(str, random_digits))}\n"
else:
    end_msg = f"\nGame over. Number was {' '.join(map(str, random_digits))}\n"

for cid, connection_socket in client_list:
    connection_socket.sendall(end_msg.encode())

server_socket.close()
print("[Server] Game ended.")
