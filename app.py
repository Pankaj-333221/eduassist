from flask import Flask, request, jsonify, send_file
import requests, os

app = Flask(__name__)
KEY = "GROQ_KEY_HERE"

@app.route('/')
def home():
    return send_file('index.html')

@app.route('/api/chat', methods=['POST','OPTIONS'])
def chat():
    if request.method == 'OPTIONS':
        r = jsonify({})
        r.headers['Access-Control-Allow-Origin'] = '*'
        r.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return r
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

app.run(host='0.0.0.0', port=8080)
