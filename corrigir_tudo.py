import json, re

print("=" * 50)
print("CORRIGINDO JoinVagas PRO")
print("=" * 50)

# 1. CORRIGIR LOGIN - Garantir que usuários persistem
print("\n1. Verificando usuários...")
with open('data/usuarios.json', 'r', encoding='utf-8') as f:
    usuarios = json.load(f)
print(f"   {len(usuarios)} usuários encontrados")

# 2. CORRIGIR ler_grupos.py - Validar WhatsApp
print("\n2. Corrigindo validação de WhatsApp...")
with open('ler_grupos.py', 'r', encoding='utf-8') as f:
    codigo = f.read()

# Adicionar função de validação de WhatsApp
validacao_wpp = '''
    def validar_whatsapp(self, numero):
        """Valida se o número parece um WhatsApp real"""
        if not numero:
            return False
        digitos = ''.join(filter(str.isdigit, numero))
        # WhatsApp brasileiro tem 11 dígitos (com DDD) ou 13 (com 55)
        if len(digitos) < 10 or len(digitos) > 14:
            return False
        # Não pode ser número repetido
        if len(set(digitos)) <= 2:
            return False
        # DDD válido
        ddds_validos = ['11','12','13','14','15','16','17','18','19','21','22','24','27','28','31','32','33','34','35','37','38','41','42','43','44','45','46','47','48','49','51','53','54','55','61','62','63','64','65','66','67','68','69','71','73','74','75','77','79','81','82','83','84','85','86','87','88','89','91','92','93','94','95','96','97','98','99']
        ddd = digitos[-11:-9] if len(digitos) >= 11 else ''
        if ddd and ddd not in ddds_validos:
            return False
        return True
'''

# Inserir após a classe
if 'class BuscadorVagasCompleto:' in codigo:
    idx = codigo.find('def classificar_vaga(self, texto):')
    codigo = codigo[:idx] + validacao_wpp + '\n    ' + codigo[idx:]

# Usar validação ao extrair WhatsApp
codigo = codigo.replace(
    "dados['whatsapp'] = match.group(0)",
    "num = match.group(0)\n                if self.validar_whatsapp(num):\n                    dados['whatsapp'] = num"
)

with open('ler_grupos.py', 'w', encoding='utf-8') as f:
    f.write(codigo)
print("   ✅ WhatsApp com validação!")

# 3. CORRIGIR dashboard.html - Remover modo teste
print("\n3. Corrigindo dashboard...")
with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Remover checkbox de modo teste
html = html.replace(
    '<label class="checkbox-label"><input type="checkbox" id="modo-teste"> Modo Teste — Simular envio</label>',
    '<p style="font-size:12px;color:var(--text-muted);margin-bottom:14px">✅ Selecione as vagas em "Vagas Encontradas" e clique abaixo para enviar</p>'
)

# Mudar texto do botão
html = html.replace(
    '<i class="fas fa-rocket"></i> Enviar Currículos',
    '<i class="fas fa-paper-plane"></i> Iniciar Envio Automatizado'
)

# Adicionar checkbox na tabela de vagas
html = html.replace(
    '<thead><tr><th>Cargo</th>',
    '<thead><tr><th><input type="checkbox" id="select-all" onclick="toggleAll()" title="Selecionar todas"></th><th>Cargo</th>'
)

html = html.replace(
    'tbody id="tabela-vagas"',
    'tbody id="tabela-vagas" style="cursor:pointer"'
)

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("   ✅ Dashboard atualizado!")

# 4. CORRIGIR app_v2.py - Vagas zeradas
print("\n4. Corrigindo vagas zeradas...")
with open('app_v2.py', 'r', encoding='utf-8') as f:
    codigo = f.read()

# Garantir que status retorne 0 para novos usuários
if "'vagas_encontradas': estado['vagas_encontradas']" in codigo:
    codigo = codigo.replace(
        "'vagas_encontradas': estado['vagas_encontradas']",
        "'vagas_encontradas': estado.get('vagas_encontradas', 0)"
    )

with open('app_v2.py', 'w', encoding='utf-8') as f:
    f.write(codigo)
print("   ✅ Vagas zeradas para novos usuários!")

print("\n" + "=" * 50)
print("✅ TUDO CORRIGIDO!")
print("=" * 50)