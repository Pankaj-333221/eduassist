import http.server, json, urllib.request

KEY = "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"

class H(http.server.SimpleHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin","*")
        self.send_header("Access-Control-Allow-Headers","Content-Type")
        self.end_headers()
    def do_GET(self):
        if self.path=="/": self.path="/index.html"
        super().do_GET()
    def do_POST(self):
        if self.path=="/api/chat":
            body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            msgs = []
            sys = ""
            if "systemInstruction" in body:
                sys = body["systemInstruction"]["parts"][0]["text"]
            if sys:
                msgs.append({"role":"system","content":sys})
            for m in body.get("contents",[]):
                role = "assistant" if m["role"]=="model" else "user"
                text = m["parts"][0].get("text","")
                msgs.append({"role":role,"content":text})
            payload = json.dumps({"model":"llama3-8b-8192","messages":msgs,"max_tokens":1000}).encode()
            req = urllib.request.Request(
                "https://api.groq.com/openai/v1/chat/completions",
                data=payload,
                headers={"Content-Type":"application/json","Authorization":"Bearer "+KEY}
            )
            try:
                with urllib.request.urlopen(req,timeout=30) as r:
                    d = json.loads(r.read())
                text = d["choices"][0]["message"]["content"]
                out = json.dumps({"candidates":[{"content":{"parts":[{"text":text}]}}]}).encode()
                self.send_response(200)
                self.send_header("Content-Type","application/json")
                self.send_header("Access-Control-Allow-Origin","*")
                self.end_headers()
                self.wfile.write(out)
            except Exception as e:
                self.send_response(500)
                self.send_header("Access-Control-Allow-Origin","*")
                self.end_headers()
                self.wfile.write(json.dumps({"error":str(e)}).encode())
    def log_message(self,*a): pass

print("Server on 8080")
with http.server.HTTPServer(("",8080),H) as s:
    s.serve_forever()
