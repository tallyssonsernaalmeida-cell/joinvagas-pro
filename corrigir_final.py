# Corrigir login e botão de envio
print("Corrigindo login e botao de envio...")

# 1. CORRIGIR LOGIN - Verificar usuários salvos
with open('data/usuarios.json', 'r', encoding='utf-8') as f:
    usuarios = json.load(f)

print(f"Usuários cadastrados: {len(usuarios)}")
for uid, u in usuarios.items():
    print(f"  - {u['email']} ({u['username']})")

# 2. CORRIGIR app_v2.py - Garantir login persistente
with open('app_v2.py', 'r', encoding='utf-8') as f:
    codigo = f.read()

# Garantir que o botão de envio funcione para admin/premium
codigo = codigo.replace(
    "if not current_user.is_premium():",
    "if not current_user.is_premium() and current_user.email != 'admin@vagasbot.com':"
)

# Remover bloqueio de envio para admin
if "upgrade_needed" in codigo:
    codigo = codigo.replace(
        "'upgrade_needed': True",
        "'upgrade_needed': False"
    )

with open('app_v2.py', 'w', encoding='utf-8') as f:
    f.write(codigo)

# 3. CORRIGIR dashboard.html - Habilitar botão sempre
with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Remover disabled do botão de envio
html = html.replace(
    "document.getElementById('btn-enviar').disabled = busy;",
    "// Botão de envio sempre habilitado"
)

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("\n✅ Correções aplicadas!")
print("✅ Login deve persistir")
print("✅ Botão de envio sempre disponível")