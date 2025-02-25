from flask import Flask, request, jsonify, session, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from datetime import timedelta

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:zikinha1575@localhost/ChatBotVendas'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'sua_chave_secreta'

# Define o tempo de expiração da sessão para 30 minutos (opcional)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Modelos
class Usuario(db.Model):
    id_usuario = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)
    conversas = db.relationship('Conversa', backref='usuario', lazy=True)

class Conversa(db.Model):
    id_conversa = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(50), default='aberta')
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'), nullable=False)
    mensagens = db.relationship('Mensagem', backref='conversa', lazy=True)

class Mensagem(db.Model):
    id_mensagem = db.Column(db.Integer, primary_key=True)
    conteudo = db.Column(db.Text, nullable=False)
    data_envio = db.Column(db.DateTime, server_default=db.func.now())
    remetente = db.Column(db.String(50), nullable=False)
    conversa_id = db.Column(db.Integer, db.ForeignKey('conversa.id_conversa'), nullable=False)

# Criar banco de dados
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    if 'usuario_id' not in session:
        print("Usuário não logado, redirecionando para login.")  # Para depuração
        return redirect(url_for('login'))  # Redireciona para login se não estiver logado
    print(f"Usuário logado, id: {session['usuario_id']}")  # Para depuração
    return render_template('chatbot.html')  # Página do chatbot só será acessada se o usuário estiver logado

# Rota de cadastro
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data.get('nome') or not data.get('email') or not data.get('senha'):
        return jsonify({'message': 'Todos os campos são obrigatórios'}), 400
    
    if Usuario.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email já cadastrado'}), 400
    
    senha_hash = bcrypt.generate_password_hash(data['senha']).decode('utf-8')
    novo_usuario = Usuario(nome=data['nome'], email=data['email'], senha=senha_hash)
    db.session.add(novo_usuario)
    db.session.commit()
    return jsonify({'message': 'Usuário cadastrado com sucesso'})

# Rota de login
@app.route('/login', methods=['POST'])
def login():
    data = request.form
    usuario = Usuario.query.filter_by(email=data.get('email')).first()
    if usuario and bcrypt.check_password_hash(usuario.senha, data.get('senha')):
        session['usuario_id'] = usuario.id_usuario
        # Não definimos session.permanent para não manter a sessão após o fechamento do navegador
        print(f"Usuário logado: {usuario.id_usuario}")  # Para depuração
        return redirect(url_for('home'))  # Redireciona para a página principal do chatbot após o login
    print("Credenciais inválidas.")  # Verifique se chegou aqui
    return jsonify({'message': 'Credenciais inválidas'}), 401

# Rota de logout
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('usuario_id', None)  # Remove a sessão manualmente
    print("Usuário deslogado.")  # Para depuração
    return redirect(url_for('home'))  # Redireciona para a tela inicial

# Rota para criar uma nova conversa
@app.route('/conversas', methods=['POST'])
def criar_conversa():
    if 'usuario_id' not in session:
        return jsonify({'message': 'Não autorizado'}), 401
    data = request.get_json()
    nova_conversa = Conversa(titulo=data['titulo'], id_usuario=session['usuario_id'])
    db.session.add(nova_conversa)
    db.session.commit()
    return jsonify({'message': 'Conversa criada com sucesso', 'id_conversa': nova_conversa.id_conversa})

# Rota para enviar mensagem
@app.route('/mensagens', methods=['POST'])
def enviar_mensagem():
    if 'usuario_id' not in session:
        return jsonify({'message': 'Não autorizado'}), 401
    data = request.get_json()
    nova_mensagem = Mensagem(
        conteudo=data['conteudo'],
        remetente='usuario',
        conversa_id=data['conversa_id']
    )
    db.session.add(nova_mensagem)
    db.session.commit()
    return jsonify({'message': 'Mensagem enviada'})

if __name__ == '__main__':
    app.run(debug=True)
