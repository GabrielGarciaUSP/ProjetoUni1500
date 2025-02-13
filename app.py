from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="pt-BR" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ChatBot Dark</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            darkMode: 'class',
            theme: {
                extend: {
                    colors: {
                        darkPrimary: '#1a1b26',
                        darkSecondary: '#24283b',
                        darkAccent: '#7aa2f7'
                    }
                }
            }
        }
    </script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body class="bg-darkPrimary text-gray-100">
    <div class="flex h-screen">
        <!-- Sidebar -->
        <div class="w-80 bg-darkSecondary border-r border-gray-700">
            <div class="p-4 border-b border-gray-700">
                <button onclick="newConversation()" 
                    class="w-full bg-darkAccent text-white px-4 py-3 rounded-lg hover:bg-blue-600 transition-colors duration-200 flex items-center justify-center gap-2">
                    <i class="fas fa-plus"></i>
                    Nova Conversa
                </button>
            </div>
            <div id="conversationsList" class="overflow-y-auto">
                <!-- Conversas serão inseridas aqui -->
            </div>
        </div>

        <!-- Chat principal -->
        <div class="flex-1 flex flex-col bg-darkPrimary">
            <!-- Cabeçalho -->
            <div class="p-4 border-b border-gray-700 bg-darkSecondary">
                <h1 class="text-xl font-bold text-gray-100" id="currentConversationTitle">
                    <i class="fas fa-comments mr-2"></i>
                    Selecione ou inicie uma conversa
                </h1>
            </div>

            <!-- Área de mensagens -->
            <div id="chatArea" class="flex-1 overflow-y-auto p-6 space-y-4">
                <!-- Mensagens aparecerão aqui -->
            </div>

            <!-- Área de input -->
            <div class="p-4 bg-darkSecondary border-t border-gray-700">
                <div class="flex gap-3">
                    <input type="text" id="messageInput" 
                        class="flex-1 p-3 rounded-lg bg-darkPrimary border border-gray-700 text-gray-100 focus:outline-none focus:border-darkAccent"
                        placeholder="Digite sua mensagem..."
                        disabled>
                    <button onclick="sendMessage()" 
                        class="bg-darkAccent text-white px-6 py-3 rounded-lg hover:bg-blue-600 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                        id="sendButton" disabled>
                        <i class="fas fa-paper-plane"></i>
                    </button>
                </div>
            </div>
        </div>
    </div>

    <script>
        let conversations = [];
        let currentConversationId = null;

        function createConversationElement(conversation) {
            const div = document.createElement('div');
            div.className = `p-4 border-b border-gray-700 hover:bg-gray-700/50 cursor-pointer transition-colors duration-200 ${
                conversation.id === currentConversationId ? 'bg-gray-700' : ''
            }`;
            div.onclick = () => loadConversation(conversation.id);
            
            const title = document.createElement('div');
            title.className = 'font-medium flex items-center gap-2';
            title.innerHTML = `<i class="fas fa-message"></i> Conversa ${conversation.id}`;
            
            const preview = document.createElement('div');
            preview.className = 'text-sm text-gray-400 truncate mt-1 ml-6';
            const lastMessage = conversation.messages[conversation.messages.length - 1];
            preview.textContent = lastMessage ? lastMessage.text : 'Nova conversa';
            
            div.appendChild(title);
            div.appendChild(preview);
            return div;
        }

        function updateConversationsList() {
            const list = document.getElementById('conversationsList');
            list.innerHTML = '';
            conversations.forEach(conv => {
                list.appendChild(createConversationElement(conv));
            });
        }

        function addMessageToChat(text, isUser) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `flex ${isUser ? 'justify-end' : 'justify-start'}`;
            
            const messageContent = document.createElement('div');
            messageContent.className = `max-w-[70%] p-4 rounded-2xl ${
                isUser ? 'bg-darkAccent text-white' : 'bg-darkSecondary text-gray-100'
            } shadow-lg`;
            
            const innerDiv = document.createElement('div');
            innerDiv.className = 'flex items-center gap-2';
            
            const icon = document.createElement('i');
            icon.className = isUser ? 'fas fa-user' : 'fas fa-robot';
            icon.style.fontSize = '0.8em';
            
            const textSpan = document.createElement('span');
            textSpan.textContent = text;
            
            innerDiv.appendChild(icon);
            innerDiv.appendChild(textSpan);
            messageContent.appendChild(innerDiv);
            messageDiv.appendChild(messageContent);
            
            chatArea.appendChild(messageDiv);
            chatArea.scrollTop = chatArea.scrollHeight;
        }

        function loadConversation(id) {
            currentConversationId = id;
            const conversation = conversations.find(c => c.id === id);
            
            document.getElementById('currentConversationTitle').innerHTML = 
                `<i class="fas fa-comments mr-2"></i> Conversa ${id}`;
            
            const chatArea = document.getElementById('chatArea');
            chatArea.innerHTML = '';
            conversation.messages.forEach(msg => {
                addMessageToChat(msg.text, msg.isUser);
            });
            
            document.getElementById('messageInput').disabled = false;
            document.getElementById('sendButton').disabled = false;
            
            updateConversationsList();
        }

        function newConversation() {
            const id = conversations.length + 1;
            conversations.push({
                id,
                messages: []
            });
            loadConversation(id);
        }

        async function sendMessage() {
            const messageInput = document.getElementById('messageInput');
            const message = messageInput.value.trim();
            if (!message || !currentConversationId) return;

            addMessageToChat(message, true);
            
            const conversation = conversations.find(c => c.id === currentConversationId);
            conversation.messages.push({
                text: message,
                isUser: true
            });
            
            messageInput.value = '';
            updateConversationsList();

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        mensagem: message
                    }),
                });

                const data = await response.json();
                const botResponse = data.resposta;
                
                addMessageToChat(botResponse, false);
                conversation.messages.push({
                    text: botResponse,
                    isUser: false
                });
                
                updateConversationsList();
            } catch (error) {
                addMessageToChat('Erro ao comunicar com o servidor', false);
            }
        }

        document.getElementById('messageInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });

        // Mensagem de boas-vindas
        newConversation();
        addMessageToChat("Olá! Sou seu assistente virtual. Como posso ajudar?", false);
    </script>
</body>
</html>
'''

respostas = {
    "oi": [
        "Olá! Como posso ajudar?",
        "Oi! Tudo bem?",
        "Olá! Em que posso ser útil hoje?"
    ],
    "bom dia": [
        "Bom dia! Como posso ajudar?",
        "Bom dia! Espero que esteja tendo um ótimo dia!",
        "Bom dia! Em que posso ser útil?"
    ],
    "como vai": [
        "Estou bem, obrigado! E você?",
        "Tudo ótimo! Como você está?",
        "Muito bem! E com você?"
    ],
    "tchau": [
        "Até logo! Tenha um ótimo dia!",
        "Tchau! Foi bom conversar com você!",
        "Até a próxima! Se precisar, estarei aqui!"
    ]
}

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    mensagem = data['mensagem'].lower()
    
    for palavra_chave in respostas:
        if palavra_chave in mensagem:
            return jsonify({
                "resposta": random.choice(respostas[palavra_chave])
            })
    
    return jsonify({
        "resposta": "Desculpe, não entendi. Pode reformular?"
    })

if __name__ == '__main__':
    app.run(debug=True)