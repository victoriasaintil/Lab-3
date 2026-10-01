import socket
import requests
from flask import Flask, request

app = Flask(__name__)


def dns_lookup(hostname, as_ip, as_port):
    """Ask the AS for the IP of hostname. Returns the IP or None."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(3)
    try:
        query = f"TYPE=A\nNAME={hostname}\n"
        sock.sendto(query.encode(), (as_ip, int(as_port)))
        data, _ = sock.recvfrom(4096)
    except (socket.timeout, OSError):
        return None
    finally:
        sock.close()

    for token in data.decode().split():
        if token.startswith("VALUE="):
            return token.split("=", 1)[1]
    return None


@app.route("/fibonacci", methods=["GET"])
def fibonacci():
    hostname = request.args.get("hostname")
    fs_port = request.args.get("fs_port")
    number = request.args.get("number")
    as_ip = request.args.get("as_ip")
    as_port = request.args.get("as_port")

    if not all([hostname, fs_port, number, as_ip, as_port]):
        return "Missing parameters", 400

    fs_ip = dns_lookup(hostname, as_ip, as_port)
    if not fs_ip:
        return "Hostname not found", 404

    try:
        resp = requests.get(
            f"http://{fs_ip}:{fs_port}/fibonacci",
            params={"number": number},
            timeout=5,
        )
    except requests.RequestException:
        return "Could not reach Fibonacci server", 500

    return resp.text, resp.status_code


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)