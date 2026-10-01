import socket
from flask import Flask, request, jsonify

app = Flask(__name__)


def fib(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


@app.route("/register", methods=["PUT"])
def register():
    body = request.get_json(silent=True)
    if not body:
        return "Bad request", 400

    hostname = body.get("hostname")
    ip = body.get("ip")
    as_ip = body.get("as_ip")
    as_port = body.get("as_port")

    if not all([hostname, ip, as_ip, as_port]):
        return "Missing fields", 400

    # Send the UDP registration message to the AS
    message = f"TYPE=A\nNAME={hostname} VALUE={ip} TTL=10\n"
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(message.encode(), (as_ip, int(as_port)))
        sock.close()
    except Exception as e:
        return f"Registration failed: {e}", 500

    return "Registered", 201


@app.route("/fibonacci", methods=["GET"])
def fibonacci():
    number = request.args.get("number")
    try:
        n = int(number)
        if n < 0:
            raise ValueError
    except (TypeError, ValueError):
        return "Bad format", 400

    return jsonify(fib(n)), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9090)
