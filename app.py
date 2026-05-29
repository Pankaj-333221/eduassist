from flask import Flask, request, jsonify, send_file, Response, session, redirect
import requests, os

app = Flask(__name__)
app.secret_key = "eduassist_secret_2024"
KEY = os.environ.get("GROQ_API_KEY", "")

USERS = {
    "professor": "vit2024",
    "admin": "eduassist123"
}

LOGIN_PAGE = """
<!DOCTYPE html>
<html>
<head>
<title>EduAssist AI — Login</title>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:wght@400;500&family=DM+Sans:wght@400;500&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'DM Sans',sans-serif;background:#f7f5f0;display:flex;align-items:center;justify-content:center;min-height:100vh}
.box{background:#fff;border-radius:16px;padding:2.5rem;max-width:400px;width:92%;border:1px solid rgba(60,50,30,0.12);box-shadow:0 8px 40px rgba(0,0,0,0.08)}
.logo{font-family:'Fraunces',serif;font-size:1.4rem;color:#1b4332;margin-bottom:4px}
.sub{font-size:13px;color:#6b6558;margin-bottom:24px}
label{font-size:11px;font-weight:500;letter-spacing:0.06em;text-transform:uppercase;color:#a09a8e;display:block;margin-bottom:6px}
input{width:100%;padding:11px 14px;border:1.5px solid #d0cdc6;border-radius:8px;font-size:14px;outline:none;margin-bottom:16px;font-family:'DM Sans',sans-serif}
input:focus{border-color:#2d6a4f}
button{width:100%;padding:12px;background:#1b4332;color:#fff;border:none;border-radius:8px;font-size:14px;font-weight:500;cursor:pointer;font-family:'DM Sans',sans-serif}
button:hover{background:#2d6a4f}
.error{color:#c0392b;font-size:12.5px;margin-bottom:12px}
</style>
</head>
<body>
<div class="box">
  <div class="logo">📚 EduAssist AI</div>
  <div class="sub">VIT Faculty Edition — Please login</div>
  {error}
  <form method="POST" action="/login">
  <label>Username</label>
  <input type="text" name="username" placeholder="Enter username" required>
  <label>Password</label>
  <input type="password" name="password" placeholder="Enter password" required>
  <button type="submit">Login →</button>
  </form>
</div>
</body>
</html>
"""

@app.route('/')
def home():
    if not session.get('logged_in'):
        return redirect('/login')
    return send_file('index.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        u = request.form.get('username','')
        p = request.form.get('password','')
        if USERS.get(u) == p:
            session['logged_in'] = True
            session['username'] = u
            return redirect('/')
        return LOGIN_PAGE.replace('{error}', '<div class="error">❌ Wrong username or password</div>')
    return LOGIN_PAGE.replace('{error}', '')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/api/chat', methods=['POST','OPTIONS'])
def chat():
    if request.method == 'OPTIONS':
        r = jsonify({})
        r.headers['Access-Control-Allow-Origin'] = '*'
        r.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return r
    if not session.get('logged_in'):
        return jsonify({'error':'Unauthorized'}), 401
    body = request.json
    msgs = []
    if 'systemInstruction' in body:
        msgs.append({'role':'system','content':body['systemInstruction']['parts'][0]['text']})
    for m in body.get('contents',[]):
        role = 'assistant' if m['role']=='model' else 'user'
        msgs.append({'role':role,'content':m['parts'][0].get('text','')})
    resp = requests.post(
        'https://api.groq.com/openai/v1/chat/completions',
        headers={'Authorization':'Bearer '+KEY,'Content-Type':'application/json'},
        json={'model':'llama-3.1-8b-instant','messages':msgs,'max_tokens':1000}
    )
    d = resp.json()
    if resp.status_code != 200:
        return jsonify({'error': d}), 500
    text = d['choices'][0]['message']['content']
    r = jsonify({'candidates':[{'content':{'parts':[{'text':text}]}}]})
    r.headers['Access-Control-Allow-Origin'] = '*'
    return r

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
