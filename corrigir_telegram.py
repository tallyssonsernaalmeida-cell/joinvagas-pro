with open('ler_grupos.py', 'r', encoding='utf-8') as f:
    codigo = f.read()

# Substituir a função conectar
antigo = 'async def conectar(self):\n        await self.client.start(PHONE)\n        print("✅ Conectado ao Telegram!")'

novo = '''async def conectar(self):
        try:
            await self.client.start(phone=PHONE)
            print("✅ Conectado ao Telegram!")
        except Exception as e:
            print(f"⚠️ Erro na conexao: {e}")
            print("⚠️ Usando sessao existente...")'''

if antigo in codigo:
    codigo = codigo.replace(antigo, novo)
    with open('ler_grupos.py', 'w', encoding='utf-8') as f:
        f.write(codigo)
    print('✅ ler_grupos.py corrigido!')
else:
    print('❌ Trecho nao encontrado. Procurando...')
    idx = codigo.find('async def conectar')
    if idx > 0:
        print(codigo[idx:idx+200])