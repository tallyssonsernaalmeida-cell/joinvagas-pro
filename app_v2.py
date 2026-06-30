# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════╗
║   EMPREGAAI - Plataforma Multi-Usuário (Render Ready)       ║
║   Worker automático a cada 30 minutos                        ║
║   API aberta para o App + Controle de Versão                ║
║   Admin: admin@vagasbot.com / admin123                      ║
╚══════════════════════════════════════════════════════════════╝
"""

from flask import Flask, render_template, redirect, url_for, request, jsonify, Response
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os, json, uuid, threading, queue, sys, subprocess, shutil, time
from datetime import datetime

# ════════════════ CONFIGURAÇÃO ════════════════
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24).hex())
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.makedirs('uploads', exist_ok=True)
os.makedirs('data', exist_ok=True)
os.makedirs('user_data', exist_ok=True)

user_log_queues = {}

# ════════════════ VARIÁVEIS GLOBAIS ════════════════
ultima_busca = None
busca_em_andamento = False
VERSAO_APP = "1.0.1"  # Versão atual do App
FORCE_UPDATE = False   # True = força atualização

# ════════════════ MODELO DE USUÁRIO ════════════════
class User(UserMixin):
    def __init__(self, user_id, username, email, plano='gratuito'):
        self.id = user_id
        self.username = username
        self.email = email
        self.plano = plano
    
    def is_premium(self):
        return self.plano in ['premium', 'vitalicio', 'admin']

# ════════════════ FUNÇÕES AUXILIARES ════════════════
def carregar_usuarios():
    path = os.path.join(BASE_DIR, 'data', 'usuarios.json')
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def salvar_usuarios(usuarios):
    path = os.path.join(BASE_DIR, 'data', 'usuarios.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(usuarios, f, ensure_ascii=False, indent=2)

def get_user_dir(user_id):
    user_dir = os.path.join(BASE_DIR, 'user_data', user_id)
    os.makedirs(user_dir, exist_ok=True)
    return user_dir

def get_user_config(user_id):
    config_path = os.path.join(get_user_dir(user_id), 'config.json')
    config_padrao = {
        'nome': '', 'email': '', 'telefone': '', 'cidade': '', 'uf': '',
        'escolaridade': 'Ensino Médio Completo', 'curriculo_path': '', 'link_curriculo': ''
    }
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_padrao.update(json.load(f))
        except: pass
    return config_padrao

def get_user_estado(user_id):
    estado_path = os.path.join(get_user_dir(user_id), 'estado.json')
    estado_padrao = {
        'buscando': False, 'enviando': False, 'vagas_encontradas': 0,
        'enviados_email': 0, 'enviados_wpp': 0,
        'ultima_busca': '', 'ultimo_envio': '', 'csv_atual': ''
    }
    if os.path.exists(estado_path):
        try:
            with open(estado_path, 'r', encoding='utf-8') as f:
                estado_padrao.update(json.load(f))
        except: pass
    return estado_padrao

def add_log_user(user_id, msg, tipo='info'):
    hora = datetime.now().strftime('%H:%M:%S')
    entrada = {'hora': hora, 'msg': msg, 'tipo': tipo}
    log_path = os.path.join(get_user_dir(user_id), 'log.json')
    logs = []
    if os.path.exists(log_path):
        try:
            with open(log_path, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        except: pass
    logs.append(entrada)
    if len(logs) > 500: logs = logs[-500:]
    with open(log_path, 'w', encoding='utf-8') as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)
    if user_id not in user_log_queues:
        user_log_queues[user_id] = queue.Queue(maxsize=500)
    try: user_log_queues[user_id].put_nowait(entrada)
    except queue.Full: pass

@login_manager.user_loader
def load_user(user_id):
    usuarios = carregar_usuarios()
    if user_id in usuarios:
        u = usuarios[user_id]
        return User(user_id, u['username'], u['email'], u.get('plano', 'gratuito'))
    return None

# ════════════════ WORKER AUTOMÁTICO ════════════════
def worker_busca_automatica():
    global busca_em_andamento, ultima_busca
    time.sleep(10)
    print("🔄 Worker automático iniciado (busca a cada 30 min)")
    while True:
        try:
            agora = datetime.now()
            precisa_buscar = False
            if ultima_busca is None: precisa_buscar = True
            elif (agora - ultima_busca).total_seconds() > 1800: precisa_buscar = True
            if precisa_buscar and not busca_em_andamento:
                busca_em_andamento = True
                print(f"\n🔍 [AUTO] Buscando vagas - {agora.strftime('%H:%M:%S')}")
                try:
                    stdin_input = "6\n\n0\n"
                    env = os.environ.copy()
                    env['PYTHONIOENCODING'] = 'utf-8'
                    env['PYTHONUTF8'] = '1'
                    proc = subprocess.Popen([sys.executable, '-X', 'utf8', os.path.join(BASE_DIR, 'ler_grupos.py')],
                        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=BASE_DIR, env=env)
                    proc.communicate(input=stdin_input.encode('utf-8'), timeout=300)
                    csvs = sorted([f for f in os.listdir(BASE_DIR) if f.startswith('VAGAS_ADMIN') and f.endswith('.csv')])
                    if csvs:
                        total = 0
                        vagas_path = os.path.join(BASE_DIR, 'vagas_encontradas.json')
                        if os.path.exists(vagas_path):
                            with open(vagas_path, 'r', encoding='utf-8') as f:
                                total = json.load(f).get('total', 0)
                        print(f"✅ [AUTO] Busca concluída! {total} vagas. Arquivo: {csvs[-1]}")
                    ultima_busca = datetime.now()
                except subprocess.TimeoutExpired:
                    proc.kill()
                    print("⏱️ [AUTO] Timeout")
                except Exception as e:
                    print(f"❌ [AUTO] Erro: {e}")
                busca_em_andamento = False
            time.sleep(60)
        except Exception as e:
            print(f"❌ [AUTO] Erro crítico: {e}")
            time.sleep(60)

def executar_busca_telegram():
    global ultima_busca
    try:
        stdin_input = "6\n\n0\n"
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        env['PYTHONUTF8'] = '1'
        proc = subprocess.Popen([sys.executable, '-X', 'utf8', os.path.join(BASE_DIR, 'ler_grupos.py')],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=BASE_DIR, env=env)
        proc.communicate(input=stdin_input.encode('utf-8'), timeout=300)
        ultima_busca = datetime.now()
        return True
    except: return False

def atualizar_config_py(user_id):
    config = get_user_config(user_id)
    config_path = os.path.join(BASE_DIR, 'config.py')
    if not os.path.exists(config_path): return
    with open(config_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    subs = {
        'NOME = ': f'NOME = "{config.get("nome", "Tallysson Serna Almeida")}"\n',
        'EMAIL_REMETENTE = ': f'EMAIL_REMETENTE = "{config.get("email", "tallyssonsernaalmeida@gmail.com")}"\n',
        'TELEFONE = ': f'TELEFONE = "{config.get("telefone", "(65) 99333-0420")}"\n',
        'CIDADE = ': f'CIDADE = "{config.get("cidade", "Joinville")}"\n',
        'UF = ': f'UF = "{config.get("uf", "SC")}"\n',
        'ESCOLARIDADE = ': f'ESCOLARIDADE = "{config.get("escolaridade", "Ensino Medio Completo")}"\n',
    }
    new_lines = []
    for line in lines:
        replaced = False
        for k, v in subs.items():
            if line.strip().startswith(k):
                new_lines.append(v)
                replaced = True
                break
        if not replaced: new_lines.append(line)
    with open(config_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

# ════════════════ ROTAS DE AUTENTICAÇÃO ════════════════
@app.route('/')
def index():
    if current_user.is_authenticated: return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated: return redirect(url_for('dashboard'))
    erro = None
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        senha = request.form.get('senha', '')
        usuarios = carregar_usuarios()
        for uid, u in usuarios.items():
            if u.get('email', '').lower() == email:
                if check_password_hash(u['senha'], senha):
                    usuarios[uid]['ultimo_login'] = datetime.now().isoformat()
                    salvar_usuarios(usuarios)
                    user = User(uid, u['username'], u['email'], u.get('plano', 'gratuito'))
                    login_user(user, remember=True)
                    return redirect(url_for('dashboard'))
                else: erro = 'Senha incorreta'
                break
        else: erro = 'Email nao encontrado'
    return render_template('login.html', erro=erro)

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if current_user.is_authenticated: return redirect(url_for('dashboard'))
    erro = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        senha = request.form.get('senha', '')
        if not username or not email or not senha: erro = 'Todos os campos sao obrigatorios'
        elif len(senha) < 6: erro = 'Senha deve ter pelo menos 6 caracteres'
        else:
            usuarios = carregar_usuarios()
            if any(u.get('email', '').lower() == email for u in usuarios.values()):
                erro = 'Email ja cadastrado'
            else:
                user_id = str(uuid.uuid4())
                usuarios[user_id] = {
                    'username': username, 'email': email,
                    'senha': generate_password_hash(senha), 'plano': 'gratuito',
                    'data_criacao': datetime.now().isoformat(),
                    'ultimo_login': datetime.now().isoformat(), 'ativo': True
                }
                salvar_usuarios(usuarios)
                get_user_dir(user_id)
                user = User(user_id, username, email, 'gratuito')
                login_user(user, remember=True)
                return redirect(url_for('dashboard'))
    return render_template('registro.html', erro=erro)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    config = get_user_config(current_user.id)
    estado = get_user_estado(current_user.id)
    return render_template('dashboard.html', estado=estado, config=config, user=current_user)

@app.route('/planos')
@login_required
def planos():
    return render_template('planos.html', user=current_user)

# ════════════════ API - VERSÃO DO APP ════════════════
@app.route('/api/versao')
def api_versao():
    """API que o App consulta para saber se precisa atualizar"""
    return jsonify({
        'versao': VERSAO_APP,
        'force_update': FORCE_UPDATE,
        'download_url': 'https://joinvagas-pro.onrender.com/app/latest',
        'atualizado_em': datetime.now().strftime('%d/%m/%Y %H:%M')
    })

# ════════════════ API PÚBLICA - VAGAS ════════════════
@app.route('/api/vagas')
def api_vagas():
    path = os.path.join(BASE_DIR, 'vagas_encontradas.json')
    if not os.path.exists(path):
        return jsonify({'total': 0, 'vagas': [], 'data': '', 'categorias': {}})
    try:
        with open(path, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        vagas = dados.get('vagas', [])
        simplificadas = [{
            'cargo': v.get('cargo', ''), 'empresa': v.get('empresa', ''),
            'bairro': v.get('bairro', ''), 'salario': v.get('salario', ''),
            'contrato': v.get('contrato', ''), 'escolaridade': v.get('escolaridade', ''),
            'email': v.get('email', ''), 'whatsapp': v.get('whatsapp', ''),
            'periodo': v.get('periodo', ''), 'data': v.get('data', ''),
            'hora': v.get('hora', ''), 'categoria': v.get('categoria', 'Geral'),
            'descricao': (v.get('descricao', '') or '')[:500]
        } for v in vagas[:1000]]
        return jsonify({
            'total': len(vagas), 'vagas': simplificadas,
            'data': dados.get('data', ''), 'categorias': dados.get('categorias', {}),
            'ultima_busca': ultima_busca.strftime('%d/%m/%Y %H:%M') if ultima_busca else 'Nunca'
        })
    except Exception as e:
        return jsonify({'total': 0, 'vagas': [], 'erro': str(e)})

@app.route('/api/status')
def api_status():
    vagas_path = os.path.join(BASE_DIR, 'vagas_encontradas.json')
    total = 0
    if os.path.exists(vagas_path):
        try:
            with open(vagas_path, 'r', encoding='utf-8') as f:
                total = json.load(f).get('total', 0)
        except: pass
    return jsonify({
        'online': True, 'vagas_encontradas': total,
        'ultima_busca': ultima_busca.strftime('%d/%m/%Y %H:%M') if ultima_busca else 'Nunca',
        'buscando_agora': busca_em_andamento
    })

@app.route('/api/buscar-vagas', methods=['POST'])
def buscar_vagas():
    global busca_em_andamento
    if busca_em_andamento:
        return jsonify({'status': 'ok', 'message': 'Busca já em andamento.', 'buscando': True})
    def executar():
        global busca_em_andamento
        busca_em_andamento = True
        executar_busca_telegram()
        busca_em_andamento = False
    threading.Thread(target=executar, daemon=True).start()
    return jsonify({'status': 'ok', 'message': 'Busca iniciada!'})

@app.route('/api/contatos')
def api_contatos():
    path = os.path.join(BASE_DIR, 'contatos_vagas.json')
    if not os.path.exists(path): return jsonify({'total': 0, 'contatos': []})
    try:
        with open(path, 'r', encoding='utf-8') as f: return jsonify(json.load(f))
    except: return jsonify({'total': 0, 'contatos': []})

@app.route('/api/log-envios')
def api_log_envios():
    path = os.path.join(BASE_DIR, 'log_envios.json')
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f: return jsonify(json.load(f))
        except: pass
    return jsonify({'enviados_email': 0, 'enviados_wpp': 0, 'detalhes': []})

# ════════════════ ROTAS PROTEGIDAS ════════════════
@app.route('/api/stream-log')
@login_required
def stream_log():
    user_id = current_user.id
    if user_id not in user_log_queues: user_log_queues[user_id] = queue.Queue(maxsize=500)
    def gerar():
        log_queue = user_log_queues[user_id]
        while True:
            try:
                entrada = log_queue.get(timeout=25)
                yield f"data: {json.dumps(entrada, ensure_ascii=False)}\n\n"
            except queue.Empty:
                yield 'data: {"heartbeat":true}\n\n'
    return Response(gerar(), mimetype='text/event-stream', headers={'Cache-Control': 'no-cache', 'Connection': 'keep-alive'})

@app.route('/api/enviar-curriculos', methods=['POST'])
@login_required
def enviar_curriculos():
    user_id = current_user.id
    def executar():
        atualizar_config_py(user_id)
        try:
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            proc = subprocess.Popen([sys.executable, os.path.join(BASE_DIR, 'rodar_tudo.py')],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=BASE_DIR, env=env)
            proc.communicate(input=b'1\nENVIAR\n\n0\n', timeout=1800)
        except: pass
    threading.Thread(target=executar, daemon=True).start()
    return jsonify({'status': 'ok'})

@app.route('/api/configurar', methods=['POST'])
@login_required
def configurar():
    data = request.json or {}
    user_id = current_user.id
    config = get_user_config(user_id)
    for campo in ['nome', 'email', 'telefone', 'cidade', 'uf', 'escolaridade', 'link_curriculo']:
        if campo in data: config[campo] = data[campo]
    with open(os.path.join(get_user_dir(user_id), 'config.json'), 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    return jsonify({'status': 'ok'})

@app.route('/api/upload-curriculo', methods=['POST'])
@login_required
def upload_curriculo():
    if 'curriculo' not in request.files: return jsonify({'status': 'erro'})
    file = request.files['curriculo']
    if not file.filename or not file.filename.lower().endswith('.pdf'): return jsonify({'status': 'erro'})
    file.save(os.path.join(BASE_DIR, 'uploads', f"Curriculo_{current_user.username}.pdf"))
    return jsonify({'status': 'ok'})

@app.route('/api/limpar-log', methods=['POST'])
@login_required
def limpar_log(): return jsonify({'status': 'ok'})

@app.route('/api/reset-contadores', methods=['POST'])
@login_required
def reset_contadores(): return jsonify({'status': 'ok'})

@app.route('/api/upgrade', methods=['POST'])
def upgrade_plano(): return jsonify({'status': 'ok', 'message': 'Pagamento em desenvolvimento...'})

# ════════════════ ADMIN ════════════════
@app.route('/admin/usuarios')
@login_required
def admin_usuarios():
    if current_user.plano != 'admin' and current_user.email != 'admin@vagasbot.com':
        return redirect(url_for('dashboard'))
    usuarios = carregar_usuarios()
    lista = [{'id': uid[:8], 'username': u['username'], 'email': u['email'], 'plano': u.get('plano', 'gratuito')} for uid, u in usuarios.items()]
    return render_template('admin_usuarios.html', usuarios=lista)

@app.route('/api/admin/toggle-plano', methods=['POST'])
@login_required
def toggle_plano():
    if current_user.plano != 'admin': return jsonify({'status': 'erro'})
    return jsonify({'status': 'ok'})

@app.route('/api/admin/delete-user', methods=['POST'])
@login_required
def delete_user():
    if current_user.plano != 'admin': return jsonify({'status': 'erro'})
    return jsonify({'status': 'ok'})

# ════════════════ INICIALIZAÇÃO ════════════════
if __name__ == '__main__':
    usuarios = carregar_usuarios()
    if not any(u.get('email') == 'admin@vagasbot.com' for u in usuarios.values()):
        admin_id = str(uuid.uuid4())
        usuarios[admin_id] = {
            'username': 'Admin', 'email': 'admin@vagasbot.com',
            'senha': generate_password_hash('admin123'), 'plano': 'admin',
            'data_criacao': datetime.now().isoformat(),
            'ultimo_login': datetime.now().isoformat(), 'ativo': True
        }
        salvar_usuarios(usuarios)
        print('\n👤 ADMIN: admin@vagasbot.com / admin123\n')
    
    print('='*60)
    print('🚀 EMPREGAAI - API Online com Worker Automático')
    print(f'   App Versão: {VERSAO_APP}')
    print('   Worker: busca a cada 30 minutos')
    print('='*60 + '\n')
    
    worker_thread = threading.Thread(target=worker_busca_automatica, daemon=True)
    worker_thread.start()
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)