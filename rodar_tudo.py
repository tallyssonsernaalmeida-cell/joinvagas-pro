# -*- coding: utf-8 -*-
"""
JoinVagas PRO - Pipeline Completo
Telegram >> CSV >> Contatos >> Envio Automático
Execute: python rodar_tudo.py
"""

import os, sys, json, csv, time, re, smtplib, webbrowser, io
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from urllib.parse import quote
import subprocess

# Forçar UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ════════════════ CONFIGURAÇÕES ════════════════
try:
    from config import *
except ImportError:
    PASTA_RAIZ = os.path.dirname(os.path.abspath(__file__))
    NOME = "Tallysson Serna Almeida"
    EMAIL = "tallyssonsernaalmeida@gmail.com"
    SENHA_APP = "clag vmir gbee uums"
    TELEFONE = "(65) 99333-0420"
    CIDADE = "Joinville"
    UF = "SC"
    ESCOLARIDADE = "Ensino Médio Completo"
    CURRICULO_PDF = "meu_curriculo.pdf"
    LINK_CURRICULO = "https://drive.google.com/file/d/1kHqYmzgit2JEEKba2CafFLoIgra3BXM8/view"
    PAUSA_EMAIL = 15
    PAUSA_WPP = 20
    MODO_TESTE = False

# Corrigir variáveis do config.py
if 'EMAIL_REMETENTE' in dir(): 
    EMAIL = EMAIL_REMETENTE
if 'SENHA_EMAIL' in dir(): 
    SENHA_APP = SENHA_EMAIL
if 'LINK_CURRICULO_DRIVE' in dir(): 
    LINK_CURRICULO = LINK_CURRICULO_DRIVE
if 'ARQUIVO_CURRICULO' in dir(): 
    CURRICULO_PDF = ARQUIVO_CURRICULO
if 'ARQUIVO_PDF' in dir(): 
    CURRICULO_PDF = ARQUIVO_PDF

# Garantir que PAUSA_WPP existe
if 'PAUSA_WHATSAPP' in dir():
    PAUSA_WPP = PAUSA_WHATSAPP

os.chdir(PASTA_RAIZ)

# ════════════════ FUNÇÕES ════════════════

def titulo(texto):
    print(f"\n{'='*60}")
    print(f"  {texto}")
    print(f"{'='*60}")

def saudacao():
    h = datetime.now().hour
    if 5 <= h < 12: 
        return "Bom dia! Tudo bem?"
    elif 12 <= h < 18: 
        return "Boa tarde! Tudo bem?"
    else: 
        return "Boa noite! Tudo bem?"

def buscar_telegram():
    """Passo 1: Buscar vagas do Telegram"""
    titulo("[TG] PASSO 1: Buscando vagas do Telegram")
    script = "ler_grupos.py"
    if not os.path.exists(script):
        print("[ERRO] ler_grupos.py nao encontrado!")
        return None
    print("Buscando vagas...")
    try:
        resultado = subprocess.run(
            [sys.executable, script],
            cwd=PASTA_RAIZ, capture_output=True, text=True, timeout=600,
            env={**os.environ, 'PYTHONIOENCODING': 'utf-8'}
        )
        if resultado.stdout:
            for linha in resultado.stdout.strip().split("\n")[-10:]:
                print(f"   {linha}")
        arquivos = [f for f in os.listdir() if f.startswith('VAGAS_ADMIN') and f.endswith('.csv')]
        if arquivos:
            arquivo = sorted(arquivos)[-1]
            print(f"\n[OK] Planilha: {arquivo}")
            return arquivo
        print("[ERRO] Nenhum CSV gerado!")
        return None
    except Exception as e:
        print(f"[ERRO] {e}")
        return None

def extrair_contatos(arquivo_csv):
    """Passo 2: Extrair contatos do CSV"""
    titulo("[DATA] PASSO 2: Extraindo contatos")
    if not arquivo_csv or not os.path.exists(arquivo_csv):
        print("[ERRO] Arquivo nao encontrado!")
        return []
    
    enviados = set()
    if os.path.exists("log_envios.json"):
        with open("log_envios.json", "r", encoding="utf-8") as f:
            try:
                for item in json.load(f).get('detalhes', []):
                    if item.get('destino'): 
                        enviados.add(item['destino'])
            except: 
                pass
    
    print(f"   Ja enviados: {len(enviados)}")
    
    with open(arquivo_csv, 'r', encoding='utf-8-sig') as f:
        linhas = f.readlines()
    
    contatos = []
    cabecalho = False
    colunas = []
    
    for linha in linhas:
        if not linha.strip(): 
            continue
        if any(linha.startswith(x) for x in ['RELATORIO', 'Periodo:', 'Gerado em:', 'Total de', '===', 'RESUMO', 'TOP']): 
            continue
        
        if not cabecalho and ('Periodo' in linha or 'Cargo' in linha):
            colunas = [c.strip() for c in linha.split(';')]
            cabecalho = True
            continue
        
        if cabecalho:
            vals = [c.strip() for c in linha.split(';')]
            if len(vals) < 5: 
                continue
            
            row = {}
            for j, col in enumerate(colunas):
                row[col] = vals[j] if j < len(vals) else ''
            
            wpp = (row.get('WhatsApp', '') or row.get('Whatsapp', '') or row.get('Telefone', '') or '').strip()
            email = (row.get('Email', '') or row.get('email', '') or '').strip()
            
            if (wpp and len(''.join(filter(str.isdigit, wpp))) >= 8) or (email and '@' in email):
                contatos.append({
                    'whatsapp': wpp if wpp and len(''.join(filter(str.isdigit, wpp))) >= 8 else '',
                    'email': email if email and '@' in email else '',
                    'cargo': row.get('Cargo', 'Area Administrativa').strip(),
                    'empresa': row.get('Empresa', '').strip(),
                    'periodo': row.get('Periodo', '').strip(),
                })
    
    # Remover duplicados
    unicos = []
    vistos = set()
    for c in contatos:
        chave = c['whatsapp'] or c['email']
        if chave and chave not in vistos and chave not in enviados:
            vistos.add(chave)
            unicos.append(c)
    
    # Priorizar recentes
    recentes = [c for c in unicos if any(p in c.get('periodo', '') for p in ['ULTIMOS 7', 'ULTIMOS 15', 'ULTIMOS 30', 'ESTA SEMANA', 'HOJE'])]
    ordenados = recentes + [c for c in unicos if c not in recentes]
    
    print(f"   [OK] {len(ordenados)} NOVOS contatos")
    print(f"   [WPP] WhatsApp: {len([c for c in ordenados if c['whatsapp']])}")
    print(f"   [@] Email: {len([c for c in ordenados if c['email']])}")
    
    with open("contatos_vagas.json", "w", encoding="utf-8") as f:
        json.dump({"total": len(ordenados), "contatos": ordenados}, f, ensure_ascii=False, indent=2)
    
    return ordenados

def gerar_mensagens(contatos):
    """Passo 3: Gerar mensagens personalizadas"""
    titulo("[...] PASSO 3: Gerando mensagens")
    s = saudacao()
    print(f"   Saudacao: {s}")
    
    mensagens = []
    for i, c in enumerate(contatos, 1):
        cargo = c.get('cargo', 'Area Administrativa')
        empresa = c.get('empresa', '')
        
        corpo_email = f"""{s}

Meu nome é {NOME} e estou encaminhando meu currículo para oportunidades na área administrativa em {CIDADE}/{UF}.

📋 PERFIL PROFISSIONAL:
• Escolaridade: {ESCOLARIDADE}
• Cidade: {CIDADE}/{UF}
• Disponibilidade: Imediata

💼 EXPERIÊNCIA:
• Rotinas administrativas e escritório
• Atendimento ao cliente
• Emissão de notas fiscais
• Pacote Office
• Sistemas ERP

📄 Currículo em anexo.
Estou à disposição para entrevista.

Atenciosamente,
{NOME}
{TELEFONE}
{EMAIL}"""

        corpo_wpp = f"""{s}

Meu nome é {NOME} e tenho interesse na vaga de {cargo}{' na ' + empresa if empresa else ''}.

📍 Perfil:
• {ESCOLARIDADE}
• {CIDADE}/{UF}
• Disponível para início imediato

💼 Experiência em rotinas administrativas, atendimento, emissão de notas fiscais, Pacote Office e sistemas ERP.

📄 Meu currículo: {LINK_CURRICULO}

Atenciosamente,
{NOME}
{TELEFONE}"""

        mensagens.append({
            'id': i,
            'cargo': cargo,
            'empresa': empresa,
            'email': c.get('email', ''),
            'whatsapp': c.get('whatsapp', ''),
            'assunto': f"Currículo - {NOME} - {cargo}",
            'corpo_email': corpo_email,
            'corpo_wpp': corpo_wpp,
        })
    
    with open("mensagens_geradas.json", "w", encoding="utf-8") as f:
        json.dump(mensagens, f, ensure_ascii=False, indent=2)
    
    print(f"   [OK] {len(mensagens)} mensagens geradas")
    return mensagens

def enviar(mensagens):
    """Passo 4: Enviar mensagens"""
    titulo("[@] PASSO 4: Enviando")
    
    if MODO_TESTE:
        print("[AVISO] MODO TESTE - Nada enviado!")
        return
    
    total = len(mensagens)
    print(f"   [DATA] {total} mensagens para enviar")
    
    srv = None
    com_email = [m for m in mensagens if m['email']]
    
    if com_email:
        print("\n[@] Conectando Gmail...")
        try:
            srv = smtplib.SMTP("smtp.gmail.com", 587, timeout=30)
            srv.ehlo()
            srv.starttls()
            srv.ehlo()
            srv.login(EMAIL, SENHA_APP.replace(" ", ""))
            print("[OK] Conectado ao Gmail!")
        except Exception as e:
            print(f"[ERRO] Gmail: {e}")
    
    log = []
    env_email = 0
    env_wpp = 0
    
    for i, msg in enumerate(mensagens, 1):
        print(f"\n[{i}/{total}] {msg['cargo'][:50]}")
        
        # Enviar Email
        if msg['email'] and srv:
            print(f"   [@] {msg['email']}...", end=" ")
            try:
                mime = MIMEMultipart()
                mime['From'] = EMAIL
                mime['To'] = msg['email']
                mime['Subject'] = msg['assunto']
                mime.attach(MIMEText(msg['corpo_email'], 'plain', 'utf-8'))
                
                # Anexar currículo se existir
                curriculo_path = CURRICULO_PDF
                if not os.path.exists(curriculo_path):
                    # Procurar na pasta uploads
                    for f in os.listdir('uploads'):
                        if f.endswith('.pdf'):
                            curriculo_path = os.path.join('uploads', f)
                            break
                
                if os.path.exists(curriculo_path):
                    with open(curriculo_path, 'rb') as f:
                        anexo = MIMEBase('application', 'octet-stream')
                        anexo.set_payload(f.read())
                        encoders.encode_base64(anexo)
                        anexo.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(curriculo_path)}"')
                        mime.attach(anexo)
                
                srv.sendmail(EMAIL, msg['email'], mime.as_string())
                print("[OK]")
                env_email += 1
                log.append({'hora': datetime.now().strftime('%H:%M:%S'), 'canal': 'email', 'destino': msg['email'], 'status': 'enviado'})
            except Exception as e:
                print(f"[ERRO] {str(e)[:50]}")
                log.append({'hora': datetime.now().strftime('%H:%M:%S'), 'canal': 'email', 'destino': msg['email'], 'status': f'erro: {str(e)[:50]}'})
            
            time.sleep(PAUSA_EMAIL)
        
        # Enviar WhatsApp
        if msg['whatsapp']:
            print(f"   [WPP] {msg['whatsapp']}...", end=" ")
            try:
                num = ''.join(filter(str.isdigit, msg['whatsapp']))
                if not num.startswith('55'):
                    num = '55' + num
                
                url_wpp = f"https://web.whatsapp.com/send?phone={num}&text={quote(msg['corpo_wpp'])}"
                webbrowser.open(url_wpp)
                time.sleep(8)
                
                try:
                    import pyautogui
                    pyautogui.press('enter')
                    print("[OK]")
                except:
                    print("[AVISO] Confirme o envio manualmente!")
                
                env_wpp += 1
                log.append({'hora': datetime.now().strftime('%H:%M:%S'), 'canal': 'whatsapp', 'destino': msg['whatsapp'], 'status': 'enviado'})
            except Exception as e:
                print(f"[ERRO] {str(e)[:50]}")
                log.append({'hora': datetime.now().strftime('%H:%M:%S'), 'canal': 'whatsapp', 'destino': msg['whatsapp'], 'status': f'erro: {str(e)[:50]}'})
            
            time.sleep(PAUSA_WPP)
    
    # Fechar conexão
    if srv:
        try:
            srv.quit()
        except:
            pass
    
    # Salvar log
    with open("log_envios.json", "w", encoding="utf-8") as f:
        json.dump({
            'data': datetime.now().strftime('%d/%m/%Y %H:%M'),
            'enviados_email': env_email,
            'enviados_wpp': env_wpp,
            'detalhes': log
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n[OK] Emails: {env_email} | [WPP] WhatsApp: {env_wpp}")

def pipeline():
    """Executa a pipeline completa"""
    inicio = time.time()
    print(f"\n>> PIPELINE - {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    
    csv_file = buscar_telegram()
    if not csv_file:
        print("[ERRO] Sem vagas!")
        return
    
    contatos = extrair_contatos(csv_file)
    if not contatos:
        print("[ERRO] Sem contatos novos!")
        return
    
    mensagens = gerar_mensagens(contatos)
    enviar(mensagens)
    
    print(f"\n⏱️ Tempo total: {time.time() - inicio:.0f}s")

def menu():
    print(f"\n{'='*60}")
    print(f"  >> JoinVagas PRO - {CIDADE}/{UF}")
    print(f"{'='*60}")
    print(f"  {NOME}")
    print(f"  {EMAIL}")
    print(f"  {saudacao()}")
    print(f"\n  [1] PIPELINE COMPLETO (Buscar + Enviar)")
    print(f"  [2] Só BUSCAR vagas")
    print(f"  [3] Só ENVIAR (já tenho CSV)")
    print(f"  [4] Ver LOG de envios")
    print(f"  [5] MODO TESTE (simular)")
    print(f"  [6] Limpar LOG")
    print(f"  [0] Sair")
    return input("\n  Escolha: ").strip()

def main():
    global MODO_TESTE
    
    while True:
        opcao = menu()
        
        if opcao == '0':
            print("\n👋 Até logo!")
            break
        
        elif opcao == '1':
            MODO_TESTE = False
            pipeline()
        
        elif opcao == '2':
            buscar_telegram()
        
        elif opcao == '3':
            arquivos = [f for f in os.listdir() if f.startswith('VAGAS_ADMIN') and f.endswith('.csv')]
            if arquivos:
                contatos = extrair_contatos(sorted(arquivos)[-1])
                if contatos:
                    mensagens = gerar_mensagens(contatos)
                    enviar(mensagens)
            else:
                print("[ERRO] Sem CSV!")
        
        elif opcao == '4':
            if os.path.exists("log_envios.json"):
                with open("log_envios.json", "r") as f:
                    log = json.load(f)
                print(f"\n📊 LOG: {log.get('data')}")
                print(f"   Emails: {log.get('enviados_email', 0)}")
                print(f"   WhatsApp: {log.get('enviados_wpp', 0)}")
            else:
                print("[ERRO] Sem log!")
        
        elif opcao == '5':
            MODO_TESTE = True
            print("\n[AVISO] MODO TESTE ATIVADO!")
            pipeline()
            MODO_TESTE = False
        
        elif opcao == '6':
            if os.path.exists("log_envios.json"):
                os.remove("log_envios.json")
                print("\n[OK] Log limpo!")
            else:
                print("[ERRO] Sem log!")
        
        else:
            print("[ERRO] Opção inválida!")
        
        input("\n  Pressione ENTER para continuar...")

if __name__ == "__main__":
    main()