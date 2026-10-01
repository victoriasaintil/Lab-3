import socket
import json
import os

HOST = "0.0.0.0"
PORT = 53533
DB_FILE = "dns_records.json"


def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {}


def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f)


def parse_message(text):
    """Turn 'TYPE=A\nNAME=x VALUE=y TTL=10' into a dict."""
    fields = {}
    for token in text.split():
        if "=" in token:
            key, value = token.split("=", 1)
            fields[key.strip().upper()] = value.strip()
    return fields


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST, PORT))
    print(f"AS listening on UDP {PORT}", flush=True)

    while True:
        data, addr = sock.recvfrom(4096)
        msg = parse_message(data.decode())
        db = load_db()

        # Registration: has VALUE (and TTL)
        if "VALUE" in msg and "NAME" in msg:
            db[msg["NAME"]] = {
                "type": msg.get("TYPE", "A"),
                "value": msg["VALUE"],
                "ttl": msg.get("TTL", "10"),
            }
            save_db(db)
            print(f"Registered {msg['NAME']} -> {msg['VALUE']}", flush=True)

        # DNS query: only NAME and TYPE
        elif "NAME" in msg and "TYPE" in msg:
            record = db.get(msg["NAME"])
            if record:
                reply = (
                    f"TYPE={record['type']}\n"
                    f"NAME={msg['NAME']} VALUE={record['value']} TTL={record['ttl']}\n"
                )
                sock.sendto(reply.encode(), addr)
            else:
                sock.sendto(b"", addr)  # not found


if __name__ == "__main__":
    main()