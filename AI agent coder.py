import os
from flask import Flask, request, render_template_string, jsonify
from groq import Groq
from dotenv import load_dotenv

# --- CONFIGURATION ---
load_dotenv()
# [IMPORTANT] ENTER YOUR GROQ API KEY HERE
os.environ["GROQ_API_KEY"] = "GROQ_API_KEY_HERE"

# ==========================================
# CONFIGURATION
# ==========================================
MODEL_ID = "llama-3.3-70b-versatile"

app = Flask(__name__)

# ==========================================
# ADVANCED FRONTEND (Colorful & Functional)
# ==========================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Aurora AI App Builder</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- FontAwesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <!-- CodeMirror for better editing -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/codemirror.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/theme/dracula.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/codemirror.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/mode/xml/xml.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/mode/javascript/javascript.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/mode/css/css.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/mode/htmlmixed/htmlmixed.min.js"></script>

    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;700&display=swap');
        
        body { 
            font-family: 'Plus Jakarta Sans', sans-serif; 
            overflow: hidden;
        }

        /* Animated Background */
        .aurora-bg {
            background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
            background-size: 400% 400%;
            animation: gradient 15s ease infinite;
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            z-index: -1;
        }
        @keyframes gradient {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        /* Glassmorphism */
        .glass-panel {
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.3);
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        }

        .glass-sidebar {
            background: rgba(20, 20, 30, 0.6);
            backdrop-filter: blur(20px);
            border-right: 1px solid rgba(255, 255, 255, 0.1);
        }

        /* Custom Scrollbar */
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.3); border-radius: 3px; }
        ::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.5); }

        /* CodeMirror Overrides */
        .CodeMirror { height: 100%; font-size: 14px; background: transparent !important; }
        .cm-s-dracula.CodeMirror { background: rgba(40, 42, 54, 0.8) !important; }

        .loader-dot {
            animation: bounce 1.4s infinite ease-in-out both;
        }
        .loader-dot:nth-child(1) { animation-delay: -0.32s; }
        .loader-dot:nth-child(2) { animation-delay: -0.16s; }
        @keyframes bounce { 0%, 80%, 100% { transform: scale(0); } 40% { transform: scale(1); } }
    </style>
</head>
<body class="h-screen flex text-white">

    <div class="aurora-bg"></div>

    <!-- SIDEBAR -->
    <div class="w-[420px] glass-sidebar flex flex-col z-10 shadow-2xl">
        
        <!-- Header -->
        <div class="p-6 border-b border-white/10 flex justify-between items-center">
            <div>
                <h1 class="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-blue-200">
                    Aurora Builder
                </h1>
                <p class="text-xs text-blue-200/70 font-medium tracking-wide mt-1">ADVANCED AI CODING AGENT</p>
            </div>
            <button onclick="toggleSettings()" class="w-8 h-8 rounded-full bg-white/10 hover:bg-white/20 flex items-center justify-center transition">
                <i class="fa-solid fa-gear text-sm"></i>
            </button>
        </div>

        <!-- Settings (Hidden) -->
        <div id="settingsPanel" class="hidden bg-black/40 p-4 border-b border-white/10 backdrop-blur-md">
            <label class="block text-xs font-bold text-blue-200 mb-2 uppercase">Groq API Key</label>
            <input type="password" id="apiKey" placeholder="gsk_..." 
                   class="w-full bg-white/5 border border-white/10 rounded px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-400 transition">
        </div>

        <!-- Content -->
        <div class="flex-1 flex flex-col p-6 gap-4 overflow-hidden">
            
            <!-- Prompt Area -->
            <div class="flex flex-col gap-2 flex-1">
                <label class="text-sm font-semibold text-white/90">What are we building?</label>
                <div class="relative flex-1 shadow-inner rounded-xl overflow-hidden border border-white/10 group">
                    <textarea id="prompt" placeholder="Example: A futuristic dashboard with a sales chart and a todo list using React..." 
                              class="w-full h-full bg-black/20 p-4 text-sm text-white placeholder-white/30 focus:outline-none focus:bg-black/30 resize-none transition"></textarea>
                    
                    <!-- Generate Button -->
                    <button id="generateBtn" onclick="generateCode()" 
                            class="absolute bottom-4 right-4 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-400 hover:to-purple-500 text-white px-6 py-2 rounded-lg shadow-lg transform transition hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed font-semibold flex items-center gap-2">
                        <span>Generate</span>
                        <i class="fa-solid fa-wand-magic-sparkles"></i>
                    </button>
                </div>
            </div>

            <!-- Enhancers -->
            <div>
                <label class="text-xs font-bold text-blue-200 uppercase tracking-wider mb-3 block">Enhancers</label>
                <div class="flex flex-wrap gap-2">
                    <button onclick="appendPrompt('Use React and Tailwind.')" class="px-3 py-1.5 rounded-full bg-white/5 hover:bg-white/15 border border-white/10 text-xs transition border-l-4 border-l-blue-500">
                        <i class="fa-brands fa-react mr-1"></i> React
                    </button>
                    <button onclick="appendPrompt('Make it fully mobile responsive.')" class="px-3 py-1.5 rounded-full bg-white/5 hover:bg-white/15 border border-white/10 text-xs transition border-l-4 border-l-green-500">
                        <i class="fa-solid fa-mobile-screen mr-1"></i> Mobile
                    </button>
                    <button onclick="appendPrompt('Use Framer Motion for animations.')" class="px-3 py-1.5 rounded-full bg-white/5 hover:bg-white/15 border border-white/10 text-xs transition border-l-4 border-l-pink-500">
                        <i class="fa-solid fa-film mr-1"></i> Animate
                    </button>
                    <button onclick="appendPrompt('Add a dark/light mode toggle.')" class="px-3 py-1.5 rounded-full bg-white/5 hover:bg-white/15 border border-white/10 text-xs transition border-l-4 border-l-yellow-500">
                        <i class="fa-solid fa-circle-half-stroke mr-1"></i> Dark Mode
                    </button>
                </div>
            </div>

            <!-- Status -->
            <div id="statusMsg" class="h-6 text-xs text-center text-white/70 font-mono flex justify-center gap-1 items-center hidden">
                <div class="loader-dot w-2 h-2 bg-white rounded-full"></div>
                <div class="loader-dot w-2 h-2 bg-white rounded-full"></div>
                <div class="loader-dot w-2 h-2 bg-white rounded-full"></div>
            </div>

        </div>
    </div>

    <!-- MAIN WORKSPACE -->
    <div class="flex-1 flex flex-col relative z-0">
        
        <!-- Toolbar -->
        <div class="h-16 glass-panel m-4 mb-0 rounded-t-2xl flex items-center justify-between px-6">
            <!-- Tabs -->
            <div class="flex bg-black/20 rounded-lg p-1">
                <button onclick="switchTab('preview')" id="tab-preview" class="px-6 py-2 rounded-md text-sm font-semibold transition bg-white/20 text-white shadow-sm ring-1 ring-white/10">
                    <i class="fa-solid fa-eye mr-2"></i>Live Preview
                </button>
                <button onclick="switchTab('code')" id="tab-code" class="px-6 py-2 rounded-md text-sm font-semibold text-white/50 hover:text-white transition">
                    <i class="fa-solid fa-code mr-2"></i>Editor
                </button>
            </div>

            <!-- Actions -->
            <div class="flex gap-3">
                <button onclick="runManualCode()" id="runBtn" class="hidden bg-green-500/20 hover:bg-green-500/40 text-green-300 border border-green-500/30 px-4 py-2 rounded-lg text-sm font-bold transition">
                    <i class="fa-solid fa-play mr-2"></i>Run Changes
                </button>
                <button onclick="copyCode()" class="bg-white/5 hover:bg-white/10 border border-white/10 px-4 py-2 rounded-lg text-sm font-medium transition">
                    <i class="fa-regular fa-copy mr-2"></i>Copy
                </button>
            </div>
        </div>

        <!-- Viewport -->
        <div class="flex-1 mx-4 mb-4 glass-panel rounded-b-2xl border-t-0 relative overflow-hidden shadow-2xl">
            
            <!-- PREVIEW -->
            <div id="view-preview" class="absolute inset-0 w-full h-full bg-white/90 backdrop-blur-sm rounded-b-xl overflow-hidden">
                <iframe id="previewFrame" class="w-full h-full border-none" sandbox="allow-scripts allow-modals allow-forms allow-popups allow-same-origin"></iframe>
                
                <!-- Placeholder -->
                <div id="previewPlaceholder" class="absolute inset-0 flex flex-col items-center justify-center bg-slate-900 z-10">
                    <div class="w-20 h-20 bg-gradient-to-tr from-blue-500 to-purple-500 rounded-2xl flex items-center justify-center shadow-lg shadow-purple-500/30 mb-6 animate-pulse">
                        <i class="fa-solid fa-cube text-3xl text-white"></i>
                    </div>
                    <h2 class="text-2xl font-bold text-white mb-2">Ready to Build</h2>
                    <p class="text-white/50 text-sm">Enter a prompt to generate a React or HTML app.</p>
                </div>
            </div>

            <!-- CODE EDITOR -->
            <div id="view-code" class="absolute inset-0 w-full h-full hidden">
                <textarea id="codeEditor"></textarea>
            </div>

        </div>
    </div>

    <!-- JAVASCRIPT LOGIC -->
    <script>
        // --- Initialization ---
        let editor; // CodeMirror instance
        
        window.onload = function() {
            // Restore API Key
            const savedKey = localStorage.getItem("groq_api_key");
            if (savedKey) document.getElementById("apiKey").value = savedKey;

            // Init CodeMirror
            editor = CodeMirror.fromTextArea(document.getElementById("codeEditor"), {
                mode: "htmlmixed",
                theme: "dracula",
                lineNumbers: true,
                lineWrapping: true,
                scrollbarStyle: "native"
            });
            
            // Auto-update editor on tab switch
            editor.on("change", function() {
                // Optional: Auto-run? No, better manual for safety
            });
        };

        // --- UI Functions ---
        function toggleSettings() {
            document.getElementById("settingsPanel").classList.toggle("hidden");
        }

        function appendPrompt(text) {
            const textarea = document.getElementById('prompt');
            textarea.value = textarea.value + " " + text;
            textarea.focus();
        }

        function switchTab(tab) {
            const previewView = document.getElementById('view-preview');
            const codeView = document.getElementById('view-code');
            const tabPreview = document.getElementById('tab-preview');
            const tabCode = document.getElementById('tab-code');
            const runBtn = document.getElementById('runBtn');

            if (tab === 'preview') {
                previewView.classList.remove('hidden');
                codeView.classList.add('hidden');
                runBtn.classList.add('hidden');
                
                // Update styles
                tabPreview.classList.add('bg-white/20', 'text-white', 'shadow-sm', 'ring-1', 'ring-white/10');
                tabPreview.classList.remove('text-white/50');
                tabCode.classList.remove('bg-white/20', 'text-white', 'shadow-sm', 'ring-1', 'ring-white/10');
                tabCode.classList.add('text-white/50');
            } else {
                previewView.classList.add('hidden');
                codeView.classList.remove('hidden');
                runBtn.classList.remove('hidden');
                
                // Refresh editor layout
                setTimeout(() => editor.refresh(), 10);

                // Update styles
                tabCode.classList.add('bg-white/20', 'text-white', 'shadow-sm', 'ring-1', 'ring-white/10');
                tabCode.classList.remove('text-white/50');
                tabPreview.classList.remove('bg-white/20', 'text-white', 'shadow-sm', 'ring-1', 'ring-white/10');
                tabPreview.classList.add('text-white/50');
            }
        }

        // --- Core Logic ---
        async function generateCode() {
            const prompt = document.getElementById('prompt').value;
            const apiKey = document.getElementById('apiKey').value;
            const loading = document.getElementById('statusMsg');
            const btn = document.getElementById('generateBtn');

            if (!apiKey) {
                toggleSettings();
                alert("Please enter your Groq API Key in settings.");
                return;
            }
            if (!prompt) return;

            localStorage.setItem("groq_api_key", apiKey);
            
            // UI Loading State
            loading.classList.remove('hidden');
            btn.disabled = true;
            btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i>`;

            try {
                const response = await fetch('/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ prompt: prompt, api_key: apiKey })
                });

                const data = await response.json();

                if (data.error) {
                    alert("Error: " + data.error);
                } else {
                    const code = data.code;
                    
                    // Set code to editor
                    editor.setValue(code);
                    
                    // Update preview
                    updatePreview(code);
                    
                    // Switch to preview tab
                    switchTab('preview');
                    document.getElementById('previewPlaceholder').classList.add('hidden');
                }

            } catch (err) {
                alert("Network Error: " + err.message);
            } finally {
                loading.classList.add('hidden');
                btn.disabled = false;
                btn.innerHTML = `<span>Generate</span><i class="fa-solid fa-wand-magic-sparkles"></i>`;
            }
        }

        function updatePreview(code) {
            const iframe = document.getElementById('previewFrame');
            const doc = iframe.contentWindow.document;
            doc.open();
            doc.write(code);
            doc.close();
        }

        function runManualCode() {
            const code = editor.getValue();
            updatePreview(code);
            switchTab('preview');
        }

        function copyCode() {
            const code = editor.getValue();
            if(!code) return;
            navigator.clipboard.writeText(code).then(() => {
                alert("Code copied to clipboard!");
            });
        }
    </script>
</body>
</html>
"""

# ==========================================
# BACKEND LOGIC
# ==========================================

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    user_prompt = data.get('prompt')
    user_api_key = data.get('api_key')

    if not user_api_key or not user_prompt:
        return jsonify({"error": "Missing Credentials"}), 400

    try:
        client = Groq(api_key=user_api_key)
        
        # --- ADVANCED SYSTEM PROMPT ---
        # This is the secret sauce for "Advanced Apps"
        system_prompt = (
            "You are an elite Frontend AI Architect. "
            "Your goal is to generate HIGH-QUALITY, MODERN, SINGLE-FILE web applications. "
            "You must output a single valid HTML file containing all CSS, JS, and Layout.\n\n"
            
            "CRITICAL TECH STACK RULES:\n"
            "1. USE REACT: Use React 18 and ReactDOM 18 via CDN (unpkg). "
            "   Include Babel standalone to compile JSX in the browser (<script type='text/babel'>).\n"
            "2. USE TAILWIND CSS: Use the Tailwind CSS CDN script for styling.\n"
            "3. USE FONT AWESOME: Include FontAwesome CDN for icons.\n"
            "4. NO EXTERNAL CSS/JS FILES: All logic must be inside <script> tags and styles in <style> (if not using Tailwind).\n\n"
            
            "DESIGN GUIDELINES:\n"
            "- Make it look expensive and professional (shadows, rounded corners, gradients).\n"
            "- Use modern layouts (Flexbox/Grid).\n"
            "- Ensure mobile responsiveness.\n"
            "- If the user asks for complex logic (Game, Calculator, Dashboard), implement FULL functionality in React state.\n\n"
            
            "OUTPUT FORMAT:\n"
            "- Return ONLY the raw HTML code. Do not wrap in markdown (```html). Do not add conversational text."
        )

        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            model=MODEL_ID,
            temperature=0.1, # Low temp for code precision
            max_tokens=8000,
            top_p=1,
            stream=False,
        )

        generated_code = chat_completion.choices[0].message.content
        
        # Sanitization: Remove markdown fences if the model disobeys
        generated_code = generated_code.replace("```html", "").replace("```", "")

        return jsonify({"code": generated_code})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print(f"Starting Aurora AI Builder on [http://127.0.0.1:5000](http://127.0.0.1:5000)")
    app.run(debug=True, port=5000)