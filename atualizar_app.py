# Script para atualizar app_v2.py
with open('app_v2.py', 'r', encoding='utf-8') as f:
    codigo = f.read()

# 1. Atualizar executar_busca
trecho_antigo = '''    def executar_busca():
        opcao = PERIODO_PARA_OPCAO.get(periodo, '6')
        stdin_input = f"{opcao}\\n\\n0\\n"
        sucesso = executar_script_com_stdin('ler_grupos.py', stdin_input, user_id, timeout=600)
        if sucesso:
            csvs = sorted([f for f in os.listdir(BASE_DIR) if f.startswith('VAGAS_ADMIN') and f.endswith('.csv')])
            if csvs:
                estado['csv_atual'] = csvs[-1]
                add_log_user(user_id, f'Busca concluida! {estado["vagas_encontradas"]} vagas encontradas!', 'success')
                add_log_user(user_id, 'Iniciando envio automatico...', 'info')
                executar_script_com_stdin('rodar_tudo.py', '1\\nENVIAR\\n\\n0\\n', user_id, timeout=1800)
                add_log_user(user_id, 'Envio automatico concluido!', 'success')
        estado['buscando'] = False
        with open(estado_path, 'w') as f: json.dump(estado, f)'''

trecho_novo = '''    def executar_busca():
        # Atualizar config.py com dados do usuario
        config = get_user_config(user_id)
        config_path = os.path.join(BASE_DIR, 'config.py')
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config_lines = f.readlines()
            substituicoes = {
                'NOME = ': 'NOME = "' + config.get('nome', 'Tallysson Serna Almeida') + '"\\n',
                'EMAIL_REMETENTE = ': 'EMAIL_REMETENTE = "' + config.get('email', 'tallyssonsernaalmeida@gmail.com') + '"\\n',
                'TELEFONE = ': 'TELEFONE = "' + config.get('telefone', '(65) 99333-0420') + '"\\n',
                'CIDADE = ': 'CIDADE = "' + config.get('cidade', 'Joinville') + '"\\n',
                'UF = ': 'UF = "' + config.get('uf', 'SC') + '"\\n',
                'ESCOLARIDADE = ': 'ESCOLARIDADE = "' + config.get('escolaridade', 'Ensino Medio Completo') + '"\\n',
            }
            novas_linhas = []
            for linha in config_lines:
                for chave, valor in substituicoes.items():
                    if linha.strip().startswith(chave):
                        linha = valor
                        break
                novas_linhas.append(linha)
            with open(config_path, 'w', encoding='utf-8') as f:
                f.writelines(novas_linhas)
        add_log_user(user_id, 'Dados atualizados para envio!', 'success')
        
        # Buscar vagas
        opcao = PERIODO_PARA_OPCAO.get(periodo, '6')
        stdin_input = f"{opcao}\\n\\n0\\n"
        sucesso = executar_script_com_stdin('ler_grupos.py', stdin_input, user_id, timeout=600)
        if sucesso:
            csvs = sorted([f for f in os.listdir(BASE_DIR) if f.startswith('VAGAS_ADMIN') and f.endswith('.csv')])
            if csvs:
                estado['csv_atual'] = csvs[-1]
                add_log_user(user_id, 'Busca concluida! Vagas encontradas!', 'success')
                # ENVIO AUTOMATICO
                add_log_user(user_id, 'Iniciando envio automatico...', 'info')
                stdin_envio = '1\\nENVIAR\\n\\n0\\n'
                executar_script_com_stdin('rodar_tudo.py', stdin_envio, user_id, timeout=1800)
                add_log_user(user_id, 'Envio automatico concluido!', 'success')
        estado['buscando'] = False
        with open(estado_path, 'w') as f: json.dump(estado, f)'''

if trecho_antigo in codigo:
    codigo = codigo.replace(trecho_antigo, trecho_novo)
    print('✅ executar_busca atualizada!')
else:
    print('⚠️ Trecho antigo nao encontrado - procure manualmente')

# 2. Atualizar enviar_curriculos
trecho_antigo2 = '''    def executar():
        executar_script_com_stdin('rodar_tudo.py', '1\\nENVIAR\\n\\n0\\n', user_id, timeout=1800)
        add_log_user(user_id, 'Envio concluido!', 'success')'''

trecho_novo2 = '''    def executar():
        # Atualizar config.py com dados do usuario
        config = get_user_config(user_id)
        config_path = os.path.join(BASE_DIR, 'config.py')
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config_lines = f.readlines()
            substituicoes = {
                'NOME = ': 'NOME = "' + config.get('nome', 'Tallysson Serna Almeida') + '"\\n',
                'EMAIL_REMETENTE = ': 'EMAIL_REMETENTE = "' + config.get('email', 'tallyssonsernaalmeida@gmail.com') + '"\\n',
                'TELEFONE = ': 'TELEFONE = "' + config.get('telefone', '(65) 99333-0420') + '"\\n',
                'CIDADE = ': 'CIDADE = "' + config.get('cidade', 'Joinville') + '"\\n',
                'UF = ': 'UF = "' + config.get('uf', 'SC') + '"\\n',
                'ESCOLARIDADE = ': 'ESCOLARIDADE = "' + config.get('escolaridade', 'Ensino Medio Completo') + '"\\n',
            }
            novas_linhas = []
            for linha in config_lines:
                for chave, valor in substituicoes.items():
                    if linha.strip().startswith(chave):
                        linha = valor
                        break
                novas_linhas.append(linha)
            with open(config_path, 'w', encoding='utf-8') as f:
                f.writelines(novas_linhas)
        
        stdin_envio = '1\\nENVIAR\\n\\n0\\n'
        executar_script_com_stdin('rodar_tudo.py', stdin_envio, user_id, timeout=1800)
        add_log_user(user_id, 'Envio concluido!', 'success')'''

if trecho_antigo2 in codigo:
    codigo = codigo.replace(trecho_antigo2, trecho_novo2)
    print('✅ enviar_curriculos atualizada!')
else:
    print('⚠️ Trecho antigo2 nao encontrado')

with open('app_v2.py', 'w', encoding='utf-8') as f:
    f.write(codigo)

print('✅ app_v2.py atualizado com sucesso!')