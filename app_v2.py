# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════╗
║   JoinVagas PRO - Plataforma Multi-Usuário (Render Ready)   ║
║   Hospedagem: Render.com 24/7 Online                        ║
║   Admin: admin@vagasbot.com / admin123                      ║
╚══════════════════════════════════════════════════════════════╝

FUNCIONALIDADES:
  ✅ Sistema de login/registro multi-usuário
  ✅ Painel individual por usuário
  ✅ Busca de vagas do Telegram (via ler_grupos.py)
  ✅ Envio automático de currículos após busca
  ✅ Dados personalizados por usuário
  ✅ Log em tempo real (SSE)
  ✅ Upload de currículo PDF
  ✅ Configurações pessoais
  ✅ Painel Admin para gerenciar usuários
  ✅ Página de planos
  ✅ Pronto para deploy no Render.com
"""

from flask import Flask, render_template, redirect, url_for, request, jsonify, Response
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os, json, uuid, threading, queue, sys, subprocess, shutil
from datetime import datetime
from flask_cors import CORS
CORS(app)

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
        except:
            pass
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
        except:
            pass
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
        except:
            pass
    logs.append(entrada)
    if len(logs) > 500:
        logs = logs[-500:]
    with open(log_path, 'w', encoding='utf-8') as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)
    if user_id not in user_log_queues:
        user_log_queues[user_id] = queue.Queue(maxsize=500)
    try:
        user_log_queues[user_id].put_nowait(entrada)
    except queue.Full:
        pass

@login_manager.user_loader
def load_user(user_id):
    usuarios = carregar_usuarios()
    if user_id in usuarios:
        u = usuarios[user_id]
        return User(user_id, u['username'], u['email'], u.get('plano', 'gratuito'))
    return None

# ════════════════ EXECUÇÃO DE SCRIPTS ════════════════
PERIODO_PARA_OPCAO = {'7': '6', '30': '2', '60': '3', '90': '4', 'mes': '5'}

def executar_script_com_stdin(script_name, stdin_input, user_id, timeout=600):
    script = os.path.join(BASE_DIR, script_name)
    if not os.path.exists(script):
        add_log_user(user_id, f'Script {script_name} nao encontrado!', 'error')
        return False
    try:
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        env['PYTHONUTF8'] = '1'
        proc = subprocess.Popen(
            [sys.executable, '-X', 'utf8', script],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, cwd=BASE_DIR, env=env
        )
        stdout, _ = proc.communicate(input=stdin_input.encode('utf-8'), timeout=timeout)
        output = stdout.decode('utf-8', errors='ignore')
        for linha in output.splitlines():
            linha = linha.strip()
            if not linha or any(c in linha for c in ['===', '══']):
                continue
            if 'OK' in linha or '✅' in linha:
                tipo = 'success'
            elif 'ERRO' in linha or '❌' in linha:
                tipo = 'error'
            elif 'AVISO' in linha or '⚠' in linha:
                tipo = 'warning'
            else:
                tipo = 'info'
            add_log_user(user_id, linha[:200], tipo)
        return True
    except subprocess.TimeoutExpired:
        proc.kill()
        add_log_user(user_id, f'Timeout: {script_name}', 'error')
        return False
    except Exception as e:
        add_log_user(user_id, f'Erro: {str(e)}', 'error')
        return False

def atualizar_config_py(user_id):
    """Atualiza o config.py com os dados do usuário logado"""
    config = get_user_config(user_id)
    config_path = os.path.join(BASE_DIR, 'config.py')
    if not os.path.exists(config_path):
        return
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
        if not replaced:
            new_lines.append(line)
    with open(config_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    add_log_user(user_id, '✅ Dados atualizados para envio!', 'success')

# ════════════════ ROTAS DE AUTENTICAÇÃO ════════════════
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
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
                    add_log_user(uid, '✅ Login realizado com sucesso!', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    erro = 'Senha incorreta'
                break
        else:
            erro = 'Email nao encontrado'
    return render_template('login.html', erro=erro)

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    erro = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        senha = request.form.get('senha', '')
        if not username or not email or not senha:
            erro = 'Todos os campos sao obrigatorios'
        elif len(senha) < 6:
            erro = 'Senha deve ter pelo menos 6 caracteres'
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
                add_log_user(user_id, '🎉 Conta criada com sucesso! Bem-vindo ao JoinVagas PRO!', 'success')
                return redirect(url_for('dashboard'))
    return render_template('registro.html', erro=erro)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# ════════════════ ROTAS PRINCIPAIS ════════════════
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

# ════════════════ API - STATUS ════════════════
@app.route('/api/status')
@login_required
def api_status():
    estado = get_user_estado(current_user.id)
    vagas_path = os.path.join(BASE_DIR, 'vagas_encontradas.json')
    if os.path.exists(vagas_path):
        try:
            with open(vagas_path, 'r', encoding='utf-8') as f:
                dados = json.load(f)
                estado['vagas_encontradas'] = dados.get('total', 0)
                estado['ultima_busca'] = dados.get('data', '')
        except:
            pass
    return jsonify({
        'buscando': estado['buscando'],
        'enviando': estado['enviando'],
        'vagas_encontradas': estado.get('vagas_encontradas', 0),
        'enviados_email': estado['enviados_email'],
        'enviados_wpp': estado['enviados_wpp'],
        'ultima_busca': estado['ultima_busca'],
        'ultimo_envio': estado['ultimo_envio'],
        'contatos_pendentes': 0,
        'user': {
            'username': current_user.username,
            'email': current_user.email,
            'plano': current_user.plano,
            'is_premium': current_user.is_premium()
        }
    })

# ════════════════ API - LOG SSE ════════════════
@app.route('/api/stream-log')
@login_required
def stream_log():
    user_id = current_user.id
    if user_id not in user_log_queues:
        user_log_queues[user_id] = queue.Queue(maxsize=500)
    
    def gerar():
        log_path = os.path.join(get_user_dir(user_id), 'log.json')
        if os.path.exists(log_path):
            try:
                with open(log_path, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
                    for entrada in logs[-50:]:
                        yield f"data: {json.dumps(entrada, ensure_ascii=False)}\n\n"
            except:
                pass
        log_queue = user_log_queues[user_id]
        while True:
            try:
                entrada = log_queue.get(timeout=25)
                yield f"data: {json.dumps(entrada, ensure_ascii=False)}\n\n"
            except queue.Empty:
                yield 'data: {"heartbeat":true}\n\n'
    
    return Response(gerar(), mimetype='text/event-stream', headers={
        'Cache-Control': 'no-cache', 'Connection': 'keep-alive'
    })

# ════════════════ API - BUSCAR VAGAS (COM ENVIO AUTOMÁTICO) ════════════════
@app.route('/api/buscar-vagas', methods=['POST'])
@login_required
def buscar_vagas():
    user_id = current_user.id
    estado = get_user_estado(user_id)
    
    if estado['buscando']:
        return jsonify({'status': 'erro', 'message': 'Busca ja em andamento'})
    
    data = request.json or {}
    periodo = str(data.get('periodo', '7'))
    
    add_log_user(user_id, f'🔍 Iniciando busca - Periodo: {periodo} dias...', 'info')
    
    estado['buscando'] = True
    estado_path = os.path.join(get_user_dir(user_id), 'estado.json')
    with open(estado_path, 'w') as f:
        json.dump(estado, f)
    
    def executar_busca():
        # 1. Atualizar config.py com dados do usuario
        atualizar_config_py(user_id)
        
        # 2. Buscar vagas no Telegram
        opcao = PERIODO_PARA_OPCAO.get(periodo, '6')
        stdin_input = f"{opcao}\n\n0\n"
        sucesso = executar_script_com_stdin('ler_grupos.py', stdin_input, user_id, timeout=600)
        
        if sucesso:
            csvs = sorted([f for f in os.listdir(BASE_DIR) if f.startswith('VAGAS_ADMIN') and f.endswith('.csv')])
            if csvs:
                estado['csv_atual'] = csvs[-1]
                add_log_user(user_id, '✅ Busca concluida! Vagas encontradas!', 'success')
                
                # 3. ENVIO AUTOMATICO
                add_log_user(user_id, '📧 Iniciando envio automatico...', 'info')
                stdin_envio = '1\nENVIAR\n\n0\n'
                executar_script_com_stdin('rodar_tudo.py', stdin_envio, user_id, timeout=1800)
                add_log_user(user_id, '✅ Envio automatico concluido!', 'success')
        
        estado['buscando'] = False
        with open(estado_path, 'w') as f:
            json.dump(estado, f)
    
    threading.Thread(target=executar_busca, daemon=True).start()
    return jsonify({'status': 'ok', 'message': 'Busca iniciada com sucesso!'})

# ════════════════ API - VAGAS ════════════════
@app.route('/api/vagas')
@login_required
def api_vagas():
    path = os.path.join(BASE_DIR, 'vagas_encontradas.json')
    if not os.path.exists(path):
        return jsonify({'total': 0, 'vagas': [], 'data': '', 'categorias': {}})
    try:
        with open(path, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        vagas = dados.get('vagas', [])
        simplificadas = [{
            'cargo': v.get('cargo', ''),
            'empresa': v.get('empresa', ''),
            'bairro': v.get('bairro', ''),
            'salario': v.get('salario', ''),
            'contrato': v.get('contrato', ''),
            'escolaridade': v.get('escolaridade', ''),
            'email': v.get('email', ''),
            'whatsapp': v.get('whatsapp', ''),
            'periodo': v.get('periodo', ''),
            'data': v.get('data', ''),
            'hora': v.get('hora', ''),
            'categoria': v.get('categoria', 'Geral'),
            'beneficios': v.get('beneficios', '')[:200],
            'requisitos': v.get('requisitos', '')[:200],
            'atividades': v.get('atividades', '')[:200],
            'experiencia': v.get('experiencia', '')[:150],
            'horario': v.get('horario', ''),
            'link_vaga': v.get('link_vaga', ''),
            'link_mensagem': v.get('link_mensagem', ''),
            'descricao': (v.get('descricao', '') or '')[:500]
        } for v in vagas[:1000]]
        return jsonify({
            'total': len(vagas),
            'vagas': simplificadas,
            'data': dados.get('data', ''),
            'categorias': dados.get('categorias', {})
        })
    except Exception as e:
        return jsonify({'total': 0, 'vagas': [], 'erro': str(e)})

# ════════════════ API - CONTATOS ════════════════
@app.route('/api/contatos')
@login_required
def api_contatos():
    path = os.path.join(BASE_DIR, 'contatos_vagas.json')
    if not os.path.exists(path):
        return jsonify({'total': 0, 'contatos': []})
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    except:
        return jsonify({'total': 0, 'contatos': []})

# ════════════════ API - ENVIAR CURRÍCULOS (MANUAL) ════════════════
@app.route('/api/enviar-curriculos', methods=['POST'])
@login_required
def enviar_curriculos():
    user_id = current_user.id
    add_log_user(user_id, '📧 Iniciando envio manual...', 'info')
    
    def executar():
        atualizar_config_py(user_id)
        stdin_envio = '1\nENVIAR\n\n0\n'
        executar_script_com_stdin('rodar_tudo.py', stdin_envio, user_id, timeout=1800)
        add_log_user(user_id, '✅ Envio concluido!', 'success')
    
    threading.Thread(target=executar, daemon=True).start()
    return jsonify({'status': 'ok', 'message': 'Envio iniciado!'})

# ════════════════ API - LOG DE ENVIOS ════════════════
@app.route('/api/log-envios')
@login_required
def api_log_envios():
    path = os.path.join(BASE_DIR, 'log_envios.json')
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return jsonify(json.load(f))
        except:
            pass
    return jsonify({'enviados_email': 0, 'enviados_wpp': 0, 'detalhes': []})

# ════════════════ API - CONFIGURAÇÃO ════════════════
@app.route('/api/configurar', methods=['POST'])
@login_required
def configurar():
    data = request.json or {}
    user_id = current_user.id
    config = get_user_config(user_id)
    
    campos = ['nome', 'email', 'telefone', 'cidade', 'uf', 'escolaridade', 'link_curriculo']
    for campo in campos:
        if campo in data:
            config[campo] = data[campo]
    
    config_path = os.path.join(get_user_dir(user_id), 'config.json')
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    if 'email' in data:
        usuarios = carregar_usuarios()
        if user_id in usuarios:
            usuarios[user_id]['email'] = data['email']
            salvar_usuarios(usuarios)
    
    add_log_user(user_id, '✅ Configuracao salva com sucesso!', 'success')
    return jsonify({'status': 'ok', 'message': 'Configuracao salva!'})

@app.route('/api/upload-curriculo', methods=['POST'])
@login_required
def upload_curriculo():
    if 'curriculo' not in request.files:
        return jsonify({'status': 'erro', 'message': 'Nenhum arquivo enviado'})
    
    file = request.files['curriculo']
    if not file.filename or not file.filename.lower().endswith('.pdf'):
        return jsonify({'status': 'erro', 'message': 'Apenas arquivos PDF sao aceitos'})
    
    user_id = current_user.id
    config = get_user_config(user_id)
    nome_safe = (config.get('nome') or current_user.username).replace(' ', '_')
    filename = f"Curriculo_{nome_safe}.pdf"
    
    filepath = os.path.join(BASE_DIR, 'uploads', filename)
    file.save(filepath)
    
    config['curriculo_path'] = filepath
    config_path = os.path.join(get_user_dir(user_id), 'config.json')
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    add_log_user(user_id, f'📎 Curriculo salvo: {filename}', 'success')
    return jsonify({'status': 'ok', 'message': f'Curriculo salvo! ({filename})'})

# ════════════════ API - UTILITÁRIOS ════════════════
@app.route('/api/limpar-log', methods=['POST'])
@login_required
def limpar_log():
    user_id = current_user.id
    log_path = os.path.join(get_user_dir(user_id), 'log.json')
    if os.path.exists(log_path):
        os.remove(log_path)
    log_envios = os.path.join(BASE_DIR, 'log_envios.json')
    if os.path.exists(log_envios):
        os.remove(log_envios)
    add_log_user(user_id, '🗑️ Log limpo!', 'info')
    return jsonify({'status': 'ok'})

@app.route('/api/reset-contadores', methods=['POST'])
@login_required
def reset_contadores():
    user_id = current_user.id
    estado = get_user_estado(user_id)
    estado['enviados_email'] = 0
    estado['enviados_wpp'] = 0
    estado_path = os.path.join(get_user_dir(user_id), 'estado.json')
    with open(estado_path, 'w') as f:
        json.dump(estado, f)
    add_log_user(user_id, '🔄 Contadores zerados!', 'info')
    return jsonify({'status': 'ok'})

@app.route('/api/upgrade', methods=['POST'])
@login_required
def upgrade_plano():
    return jsonify({'status': 'ok', 'message': 'Redirecionando para pagamento...', 'payment_url': '#'})

# ════════════════ ADMIN ════════════════
@app.route('/admin/usuarios')
@login_required
def admin_usuarios():
    if current_user.plano != 'admin' and current_user.email != 'admin@vagasbot.com':
        return redirect(url_for('dashboard'))
    usuarios = carregar_usuarios()
    lista = [{
        'id': uid[:8], 'username': u['username'], 'email': u['email'],
        'plano': u.get('plano', 'gratuito'), 'ativo': u.get('ativo', True),
        'data_criacao': u.get('data_criacao', '')[:10],
        'ultimo_login': u.get('ultimo_login', '')[:16]
    } for uid, u in usuarios.items()]
    return render_template('admin_usuarios.html', usuarios=lista)

@app.route('/api/admin/toggle-plano', methods=['POST'])
@login_required
def toggle_plano():
    if current_user.plano != 'admin' and current_user.email != 'admin@vagasbot.com':
        return jsonify({'status': 'erro', 'message': 'Acesso negado'})
    data = request.json or {}
    user_id_prefix = data.get('user_id', '')
    novo_plano = data.get('plano', 'gratuito')
    usuarios = carregar_usuarios()
    for uid in usuarios:
        if uid.startswith(user_id_prefix):
            usuarios[uid]['plano'] = novo_plano
            salvar_usuarios(usuarios)
            return jsonify({'status': 'ok', 'message': f'Plano alterado para {novo_plano}!'})
    return jsonify({'status': 'erro', 'message': 'Usuario nao encontrado'})

@app.route('/api/admin/delete-user', methods=['POST'])
@login_required
def delete_user():
    if current_user.plano != 'admin' and current_user.email != 'admin@vagasbot.com':
        return jsonify({'status': 'erro', 'message': 'Acesso negado'})
    data = request.json or {}
    user_id_prefix = data.get('user_id', '')
    usuarios = carregar_usuarios()
    for uid in list(usuarios.keys()):
        if uid.startswith(user_id_prefix) and usuarios[uid].get('plano') != 'admin':
            del usuarios[uid]
            salvar_usuarios(usuarios)
            user_dir = get_user_dir(uid)
            if os.path.exists(user_dir):
                shutil.rmtree(user_dir, ignore_errors=True)
            return jsonify({'status': 'ok', 'message': 'Usuario removido!'})
    return jsonify({'status': 'erro', 'message': 'Usuario nao encontrado ou e admin'})

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
        print('\n' + '='*60)
        print('👤 ADMIN CRIADO')
        print('   Email: admin@vagasbot.com')
        print('   Senha: admin123')
        print('='*60 + '\n')
    
    print('='*60)
    print('🚀 JoinVagas PRO - Plataforma Multi-Usuário')
    print('   http://127.0.0.1:5000')
    print('   Admin: http://127.0.0.1:5000/admin/usuarios')
    print('='*60 + '\n')
    
    # Compatível com Render (usa porta do ambiente)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)