import http.server
import json
import socketserver

PORT = 8000

node_a_freq = "1420.0"
node_b_freq = "1420.0"

node_a_packet = {
    "text": "Awaiting transmission...",
    "freq": "1420.0",
    "raw_size": "0 KB",
    "compressed_size": "0 Bytes",
    "savings": "0%",
}
latest_base_reply = {"text": "Awaiting base instructions...", "freq": "1420.0"}


class CustomHandler(http.server.SimpleHTTPRequestHandler):

  def do_GET(self):
    if self.path == "/" or self.path == "/home":
      self.path = "/index.html"
    elif self.path == "/node_a" or self.path == "/node_a.html":
      self.path = "/node_a.html"
    elif self.path == "/command" or self.path == "/node_b.html":
      self.path = "/node_b.html"

    if self.path == "/api/poll-field":
      self.send_response(200)
      self.send_header("Content-type", "application/json")
      self.end_headers()
      if (
          node_a_packet["text"] != "Awaiting transmission..."
          and float(node_b_freq) == float(node_a_packet["freq"])
      ):
        response_data = node_a_packet
      else:
        response_data = {
            "text": "Awaiting secure signal...",
            "status": "out_of_tune",
        }
      self.wfile.write(json.dumps(response_data).encode("utf-8"))
      return

    elif self.path == "/api/poll-base":
      self.send_response(200)
      self.send_header("Content-type", "application/json")
      self.end_headers()
      if (
          latest_base_reply["text"] != "Awaiting base instructions..."
          and float(node_a_freq) == float(latest_base_reply["freq"])
      ):
        response_data = latest_base_reply
      else:
        response_data = {
            "text": "Awaiting base instructions...",
            "status": "out_of_tune",
        }
      self.wfile.write(json.dumps(response_data).encode("utf-8"))
      return

    elif self.path == "/api/get-freq-a":
      self.send_response(200)
      self.send_header("Content-type", "application/json")
      self.end_headers()
      self.wfile.write(json.dumps({"frequency": node_a_freq}).encode("utf-8"))
      return
    elif self.path == "/api/get-freq-b":
      self.send_response(200)
      self.send_header("Content-type", "application/json")
      self.end_headers()
      self.wfile.write(json.dumps({"frequency": node_b_freq}).encode("utf-8"))
      return

    return super().do_GET()

  def do_POST(self):
    global node_a_freq, node_b_freq
    content_length = int(self.headers.get("Content-Length", 0))
    post_data = self.rfile.read(content_length) if content_length > 0 else b""
    data = json.loads(post_data.decode("utf-8")) if post_data else {}

    response = {"status": "success"}

    if self.path == "/api/transmit":
      text = data.get("text", "")
      freq = data.get("freq", node_a_freq)
      node_a_packet["text"] = text
      node_a_packet["freq"] = freq
      node_a_packet["raw_size"] = "52.4 KB"
      node_a_packet["compressed_size"] = (
          f"{len(text.encode('utf-8'))} Bytes"
      )
      node_a_packet["savings"] = "99.8%"
      response.update(node_a_packet)

    elif self.path == "/api/reply":
      text = data.get("text", "")
      freq = data.get("freq", node_b_freq)
      latest_base_reply["text"] = text
      latest_base_reply["freq"] = freq
      response["payload"] = text
      response["freq"] = freq

    elif self.path == "/api/set-freq-a":
      node_a_freq = data.get("frequency", "1420.0")
      response["frequency"] = node_a_freq

    elif self.path == "/api/set-freq-b":
      node_b_freq = data.get("frequency", "1420.0")
      response["frequency"] = node_b_freq

    self.send_response(200)
    self.send_header("Content-type", "application/json")
    self.end_headers()
    self.wfile.write(json.dumps(response).encode("utf-8"))


with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
  print(f"iTantra Server live! Open browser at: http://localhost:{PORT}")
  httpd.serve_forever()