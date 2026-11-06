import os
from flask import Flask, render_template_string, request, jsonify
from duckduckgo_search import DDGS
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

app = Flask(__name__)

print("🚀 Loading Suhail AI Model... (Pehli baar chalane mein thoda waqt lag sakta hai)")
model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)
pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, max_new_tokens=256)
print("✅ AI Model Loaded Successfully!")

def web_search(query):
    try:
        with DDGS() as ddgs:
            results = [r['body'] for r in ddgs.text(query, max_results=2)]
            return " ".join(results)
    except:
        return "No internet info found."

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Suhail AI - Open World Assistant</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body { background-color: #0f172a; color: #f8fafc; display: flex; flex-direction: column; height: 100vh; }
        header { background: #1e293b; padding: 20px; text-align: center; border-bottom: 1px solid #334155; font-size: 20px; font-weight: bold; color: #38bdf8; }
        .chat-container { flex: 1; padding: 20px; overflow-y: auto; display: flex; flex-direction: column; gap: 15px; max-width: 800px; width: 100%; margin: 0 auto; }
        .message { padding: 12px 18px; border-radius: 12px; max-width: 75%; line-height: 1.5; font-size: 15px; word-wrap: break-word; }
        .user-msg { background: #2563eb; color: #fff; align-self: flex-end; border-bottom-right-radius: 2px; }
        .ai-msg { background: #1e293b; color: #e2e8f0; align-self: flex-start; border-bottom-left-radius: 2px; border: 1px solid #334155; }
        .input-area { background: #1e293b; padding: 20px; display: flex; justify-content: center; border-top: 1px solid #334155; }
        .input-box { max-width: 800px; width: 100%; display: flex; gap: 10px; }
        input[type="text"] { flex: 1; padding: 12px 16px; background: #0f172a; border: 1px solid #475569; border-radius: 8px; color: #fff; font-size: 15px; outline: none; }
        button { background: #38bdf8; color: #0f172a; border: none; padding: 0 24px; border-radius: 8px; font-weight: bold; cursor: pointer; transition: 0.3s; }
        button:hover { background: #0ea5e9; }
    </style>
</head>
<body>

    <header>🧠 Suhail AI - Mera Apna Open-World Assistant</header>

    <div class="chat-container" id="chatContainer">
        <div class="message ai-msg">Namaste Suhail! Main aapka apna AI hoon, mujhe Suhail Mustafai ne banaya hai. Bataiye, aaj kya janna chahte hain?</div>
    </div>

    <div class="input-area">
        <div class="input-box">
            <input type="text" id="userInput" placeholder="Yahan apna sawaal likhein..." onkeypress="handleKey(event)">
            <button onclick="sendMessage()">Bhejo</button>
        </div>
    </div>

<script>
    async function sendMessage() {
        const inputField = document.getElementById('userInput');
        const chatContainer = document.getElementById('chatContainer');
        const text = inputField.value.trim();
        
        if (!text) return;

        chatContainer.innerHTML += `<div class="message user-msg">${text}</div>`;
        inputField.value = '';
        chatContainer.scrollTop = chatContainer.scrollHeight;

        const loadingId = 'loading-' + Date.now();
        chatContainer.innerHTML += `<div class="message ai-msg" id="${loadingId}">Soch raha hoon aur internet se khoj raha hoon... 🔍</div>`;
        chatContainer.scrollTop = chatContainer.scrollHeight;

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt: text })
            });

            const data = await response.json();
            document.getElementById(loadingId).innerText = data.reply;
        } catch (error) {
            document.getElementById(loadingId).innerText = "Error: Server connection fail ho gaya.";
        }
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    function handleKey(event) {
        if (event.key === 'Enter') sendMessage();
    }
</script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/chat', methods=['POST'])
def chat():
    user_data = request.json
    user_query = user_data.get('prompt', '')
    
    context = web_search(user_query)
    
    prompt = f"""<|system|>
You are Suhail AI, an open-world personal assistant created and programmed exclusively by Suhail Mustafai. Whenever anyone asks who created you, who made you, or about your developer, you must proudly answer that you were created by Suhail Mustafai. Use this live search info: {context}
</s>
<|user|>
{user_query}
</s>
<|assistant|>"""

    response = pipe(prompt, do_sample=True, temperature=0.7)[0]['generated_text']
    answer = response.split("<|assistant|>")[-1].strip()
    
    return jsonify({"reply": answer})

if __name__ == '__main__':
    print("🔥 Suhail AI Server is running live at http://localhost:5000")
    app.run(port=5000, debug=False)
  
