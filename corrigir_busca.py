with open('app_v2.py', 'r', encoding='utf-8') as f:
    codigo = f.read()

# Encontrar a posicao da funcao
idx = codigo.find('def executar_busca():')
print(f'Funcao encontrada na posicao: {idx}')

# Encontrar o fim da funcao (proxima funcao ou rota)
fim = codigo.find('\n    threading.Thread', idx)
print(f'Fim da funcao: {fim}')

# Extrair a funcao atual
funcao_atual = codigo[idx:fim]
print('\n=== FUNCAO ATUAL ===')
print(funcao_atual[:200])

# Criar a nova funcao
funcao_nova = '''    def executar_busca():
        # Atualizar config.py com dados do usuario logado
        config_user = get_user_config(user_id)
        config_path = os.path.join(BASE_DIR, 'config.py')
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            subs = {
                'NOME = ': 'NOME = "' + config_user.get('nome', 'Tallysson Serna Almeida') + '"\\n',
                'EMAIL_REMETENTE = ': 'EMAIL_REMETENTE = "' + config_user.get('email', 'tallyssonsernaalmeida@gmail.com') + '"\\n',
                'TELEFONE = ': 'TELEFONE = "' + config_user.get('telefone', '(65) 99333-0420') + '"\\n',
                'CIDADE = ': 'CIDADE = "' + config_user.get('cidade', 'Joinville') + '"\\n',
                'UF = ': 'UF = "' + config_user.get('uf', 'SC') + '"\\n',
                'ESCOLARIDADE = ': 'ESCOLARIDADE = "' + config_user.get('escolaridade', 'Ensino Medio Completo') + '"\\n',
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
                executar_script_com_stdin('rodar_tudo.py', '1\\nENVIAR\\n\\n0\\n', user_id, timeout=1800)
                add_log_user(user_id, 'Envio automatico concluido!', 'success')
        estado['buscando'] = False
        with open(estado_path, 'w') as f: json.dump(estado, f)'''

# Substituir
codigo = codigo[:idx] + funcao_nova + codigo[fim:]

with open('app_v2.py', 'w', encoding='utf-8') as f:
    f.write(codigo)

print('✅ executar_busca atualizada com dados do usuario!')