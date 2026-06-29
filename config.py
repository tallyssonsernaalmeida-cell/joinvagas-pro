"""
╔══════════════════════════════════════════════════════════════╗
║   CONFIGURAÇÕES CENTRAIS - CAÇADOR DE VAGAS                 ║
║   Edite este arquivo UMA VEZ                                ║
╚══════════════════════════════════════════════════════════════╝
"""

import os

# ══════════════════════════════════════════════════════════════
# PASTA RAIZ
PASTA_RAIZ = os.path.dirname(os.path.abspath(__file__))

# ══════════════════════════════════════════════════════════════
# DADOS DO CANDIDATO - EDITE AQUI
NOME = "Tallysson Serna Almeida"
EMAIL_REMETENTE = "tallyssonsernaalmeida@gmail.com"
SENHA_EMAIL = "clag vmir gbee uums"  # Gere em: https://myaccount.google.com/apppasswords
TELEFONE = "(65) 99333-0420"

# ══════════════════════════════════════════════════════════════
# LOCALIZAÇÃO E ÁREA
CIDADE = "Joinville"
UF = "SC"
AREA_BUSCA = "Administrativo"
ESCOLARIDADE = "Ensino Médio Completo"

# ══════════════════════════════════════════════════════════════
# ARQUIVOS
ARQUIVO_CURRICULO = "Curriculo_Tallysson_Almeida_2026.pdf"
ARQUIVO_PDF = "Curriculo_Tallysson_Almeida_2026.pdf"

# ══════════════════════════════════════════════════════════════
# LINK DO CURRÍCULO NO GOOGLE DRIVE
LINK_CURRICULO_DRIVE = "https://drive.google.com/file/d/1kHqYmzgit2JEEKba2CafFLoIgra3BXM8/view?usp=drive_link"

# ══════════════════════════════════════════════════════════════
# CONFIGURAÇÕES DE ENVIO
MAX_EMAILS_POR_HORA = 50
PAUSA_ENTRE_ENVIOS = 15      # segundos entre emails
PAUSA_WHATSAPP = 20           # segundos entre WhatsApp
MODO_TESTE = False            # True = simula, não envia

# ══════════════════════════════════════════════════════════════
# MODELOS DE MENSAGEM
ASSUNTO_PADRAO = "Currículo - Vaga Administrativa - Joinville/SC"

MODELO_EMAIL = """{saudacao}

Meu nome é {nome} e estou encaminhando meu currículo para oportunidades na área administrativa em {cidade}/{uf}.

📋 PERFIL PROFISSIONAL:
• Escolaridade: {escolaridade}
• Cidade: {cidade}/{uf}
• Disponibilidade: Imediata

💼 EXPERIÊNCIA PROFISSIONAL:
• Rotinas administrativas e escritório
• Atendimento ao cliente e recepção
• Emissão de notas fiscais
• Controle de planilhas e relatórios
• Pacote Office (Word, Excel, PowerPoint)
• Sistemas ERP

📄 Currículo em anexo para análise.
Estou à disposição para entrevista e início imediato.

Agradeço desde já pela atenção!

Atenciosamente,
{nome}
{telefone}
{email}"""

MODELO_WHATSAPP = """{saudacao}

Meu nome é {nome} e tenho interesse na vaga de {vaga}{na_empresa}.

📍 Perfil:
• {escolaridade}
• {cidade}/{uf}
• Disponível para início imediato

💼 Experiência em rotinas administrativas, atendimento, emissão de notas fiscais, Pacote Office e sistemas ERP.

📄 Meu currículo completo:
https://drive.google.com/file/d/1kHqYmzgit2JEEKba2CafFLoIgra3BXM8/view

Atenciosamente,
{nome}
{telefone}"""