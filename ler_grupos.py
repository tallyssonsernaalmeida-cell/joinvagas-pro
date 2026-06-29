# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════╗
║   JoinVagas PRO - Caçador de Vagas Completo v10             ║
║   Todas as categorias: Admin, Operacional, Técnico          ║
║   Execute: python ler_grupos.py                              ║
╚══════════════════════════════════════════════════════════════╝
"""

import os, json, re, csv
from datetime import datetime, timedelta
from telethon import TelegramClient
import asyncio
import sys, io

# Forçar UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# ════════════════ CONFIGURAÇÕES ════════════════
API_ID = 33280233
API_HASH = '886a811ca3712904a2656ba7d1a78d9a'
PHONE = '+5565993330420'

GRUPOS_IDS = [-1001191506085]  # Empregos Joinville e Região

# ════════════════ LISTAS DE CARGOS ════════════════

VAGAS_ADMINISTRATIVAS = [
    'auxiliar administrativo', 'assistente administrativo',
    'analista administrativo', 'auxiliar de escritório',
    'assistente de escritório', 'secretária', 'secretario',
    'recepcionista', 'office boy', 'office girl',
    'auxiliar financeiro', 'assistente financeiro',
    'analista financeiro', 'auxiliar de rh',
    'assistente de rh', 'analista de rh',
    'auxiliar de dp', 'assistente de dp', 'analista de dp',
    'auxiliar fiscal', 'assistente fiscal', 'analista fiscal',
    'auxiliar de compras', 'assistente de compras', 'comprador',
    'auxiliar de logística', 'assistente de logística',
    'analista de logística', 'auxiliar de cobrança',
    'assistente de cobrança', 'auxiliar de faturamento',
    'assistente de faturamento', 'auxiliar de contas',
    'assistente de contas', 'departamento pessoal',
    'recursos humanos', 'jovem aprendiz administrativo',
    'estágio administrativo', 'aprendiz administrativo',
    'trainee administrativo', 'auxiliar contábil',
    'assistente contábil', 'analista contábil',
    'contas a pagar', 'contas a receber', 'faturamento',
    'tesouraria', 'controladoria', 'gestão de parcerias',
    'analista de crm', 'assistente de sac',
    'auxiliar geral de escritório', 'coordenador administrativo',
    'supervisor administrativo', 'gerente administrativo',
    'assistente de marketing', 'analista de marketing',
    'assistente comercial', 'analista comercial',
    'assistente de vendas', 'backoffice', 'front office',
    'analista de importação', 'advogado', 'consultor',
]

VAGAS_OPERACIONAIS = [
    'auxiliar de produção', 'operador de produção',
    'auxiliar de serviços gerais', 'serviços gerais',
    'ajudante', 'auxiliar de limpeza', 'faxineira', 'faxineiro',
    'zelador', 'porteiro', 'vigia', 'segurança',
    'auxiliar de cozinha', 'cozinheiro', 'cozinheira',
    'atendente', 'balconista', 'vendedor', 'vendedora',
    'operador de caixa', 'caixa', 'repositor', 'estoquista',
    'auxiliar de estoque', 'conferente', 'separador',
    'embalador', 'auxiliar de carga e descarga',
    'auxiliar de depósito', 'almoxarife', 'auxiliar de almoxarifado',
    'motorista', 'entregador', 'motoboy', 'motofretista',
    'ajudante de motorista', 'auxiliar de entregas',
    'operador de empilhadeira', 'operador de máquinas',
    'auxiliar de manutenção', 'eletricista', 'mecânico',
    'soldador', 'pintor', 'pedreiro', 'carpinteiro',
    'auxiliar de obras', 'servente', 'jardineiro',
    'auxiliar de jardinagem', 'lixeiro', 'coletor',
    'auxiliar de lavanderia', 'camareira', 'garçom', 'garçonete',
    'copeiro', 'copeira', 'auxiliar de padaria', 'padeiro',
    'açougueiro', 'auxiliar de açougue', 'operador de loja',
    'fiscal de loja', 'fiscal de prevenção', 'promotor de vendas',
    'demonstrador', 'degustador', 'repositor de mercadorias',
    'auxiliar de supermercado', 'operador de telemarketing',
    'atendente de call center', 'auxiliar de atendimento',
    'jovem aprendiz', 'menor aprendiz', 'estagiário',
    'auxiliar geral', 'ajudante geral', 'braçal',
    'servente hospitalar', 'cuidadora de idosos', 'cuidador de idosos',
    'passadeira', 'costureira', 'costureiro',
    'lavador de', 'polidor', 'armador de ferros',
    'auxiliar de expedição', 'ajudante de carga',
    'operador de fundição', 'trabalhador no cultivo',
    'latoeiro', 'encanador', 'auxiliar de encanador',
]

VAGAS_TECNICAS = [
    'técnico em', 'tecnico em', 'técnico de', 'tecnico de',
    'analista de sistemas', 'desenvolvedor', 'programador',
    'analista de ti', 'suporte técnico', 'técnico de informática',
    'técnico em eletrônica', 'técnico em eletrotécnica',
    'técnico em mecânica', 'técnico em mecatrônica',
    'técnico em automação', 'técnico em refrigeração',
    'técnico em climatização', 'técnico em segurança do trabalho',
    'técnico em enfermagem', 'técnico em radiologia',
    'técnico em farmácia', 'técnico em química',
    'técnico em alimentos', 'técnico em qualidade',
    'técnico em logística', 'técnico em produção',
    'técnico em processos', 'técnico em planejamento',
    'técnico em manutenção', 'técnico em edificações',
    'técnico em contabilidade', 'técnico em administração',
    'técnico em recursos humanos', 'técnico em marketing',
    'técnico em vendas', 'técnico em design',
    'técnico em comunicação', 'engenheiro', 'supervisor técnico',
    'coordenador técnico', 'líder técnico', 'especialista',
    'analista de dados', 'analista de suporte',
    'analista de infraestrutura', 'analista de redes',
    'analista de segurança', 'desenvolvedor web',
    'desenvolvedor mobile', 'desenvolvedor full stack',
    'devops', 'scrum master', 'product owner',
    'ux designer', 'ui designer', 'designer gráfico',
    'web designer', 'social media', 'gestor de tráfego',
    'editor de vídeo', 'fotógrafo', 'cinegrafista',
    'laboratorista', 'engenheiro ambiental',
]

# ════════════════ PALAVRAS PARA IGNORAR ════════════════
IGNORAR_PALAVRAS = [
    'vaga encerrada', 'vaga fechada', 'vaga cancelada',
    'vaga preenchida', 'vaga suspensa', 'não estamos contratando',
    'compartilhe', 'compartilhar', 'divulgue', 'grupo de vagas',
    'regras do grupo', 'seja bem vindo', 'bem-vindo',
    'anúncio', 'promoção', 'sorteio', 'curso gratuito',
    'vendo', 'compro', 'troco', 'alugo', 'aluga-se',
    'vende-se', 'procuro emprego', 'procuro vaga',
    'estou procurando', 'busco oportunidade', 'disponível para',
    'currículo', 'curriculo', 'encaminho meu',
]

# ════════════════ BAIRROS DE JOINVILLE ════════════════
BAIRROS_JOINVILLE = [
    'Adhemar Garcia', 'América', 'Anita Garibaldi', 'Atiradores',
    'Aventureiro', 'Boa Vista', 'Boehmerwald', 'Bom Retiro',
    'Bucarein', 'Centro', 'Comasa', 'Costa e Silva', 'Distrito Industrial',
    'Espinheiros', 'Fátima', 'Floresta', 'Glória', 'Guanabara',
    'Iririú', 'Itaum', 'Itinga', 'Jardim Iririú', 'Jardim Paraíso',
    'Jardim Sofia', 'João Costa', 'Jarivatuba', 'Moro do Amaral',
    'Nova Brasília', 'Paranaguamirim', 'Petrópolis', 'Pirabeiraba',
    'Profipo', 'Saguaçu', 'Santa Catarina', 'Santo Antônio',
    'São Marcos', 'Vila Cubatão', 'Vila Nova', 'Zona Industrial Norte',
    'Zona Industrial Tupy', 'Zona Sul', 'Zona Leste', 'Zona Norte',
]

# ════════════════ LISTA DE EMPRESAS CONHECIDAS ════════════════
EMPRESAS_CONHECIDAS = [
    'Sodexo', 'Whirlpool', 'Tupy', 'BM Vagas', 'Employer RH',
    'RH Gruppe', 'Grupo Barigui', 'Coco Bambu', 'Britânia',
    'Zanotti', 'Agricopel', 'Panificadora Delary', 'Hotel Palugi',
    'Lumi Logistics', 'Hoffmann RH', 'WB Soluções RH',
    'Core People Consultoria', 'Sapore', 'SEDNA Group',
    'CIA Plastic', 'Diklatex', 'JS Auto Center', 'JD Unit',
    'CSI Cargo', 'Amparus', 'Park Perini',
]


# ═══════════════════════════════════════════════════════════
# CLASSE PRINCIPAL
# ═══════════════════════════════════════════════════════════

class BuscadorVagasCompleto:
    def __init__(self, data_inicio, data_fim, nome_periodo):
        self.client = TelegramClient('sessao_busca', API_ID, API_HASH)
        self.data_inicio = data_inicio
        self.data_fim = data_fim
        self.nome_periodo = nome_periodo
        
    async def conectar(self):
        await self.client.start(PHONE)
        print("✅ Conectado ao Telegram!")
    
    # ════════════════ CLASSIFICAÇÃO ════════════════
    
    def classificar_vaga(self, texto):
        """Classifica a vaga por categoria"""
        t = texto.lower()
        
        for termo in VAGAS_TECNICAS:
            if termo in t:
                return 'Técnico'
        
        for termo in VAGAS_ADMINISTRATIVAS:
            if termo in t:
                return 'Administrativo'
        
        for termo in VAGAS_OPERACIONAIS:
            if termo in t:
                return 'Operacional'
        
        return 'Geral'
    
    def deve_ignorar(self, texto):
        """Verifica se a mensagem deve ser ignorada"""
        t = texto.lower()
        for palavra in IGNORAR_PALAVRAS:
            if palavra in t:
                return True
        return False
    
    # ════════════════ EXTRAÇÃO DE DADOS ════════════════
    
    def extrair_cargo(self, texto):
        """Extrai o cargo da vaga - VERSÃO ROBUSTA"""
        texto_lower = texto.lower()
        
        # Juntar todas as listas e ordenar por tamanho (mais específico primeiro)
        todas_listas = VAGAS_TECNICAS + VAGAS_ADMINISTRATIVAS + VAGAS_OPERACIONAIS
        todas_listas.sort(key=len, reverse=True)
        
        # Procurar cargo nas listas
        for termo in todas_listas:
            if termo in texto_lower:
                return termo.title()
        
        # Padrões regex para extrair cargo
        padroes = [
            r'(?:vaga|oportunidade|posição)\s+(?:de|para|aberta\s+(?:de|para))\s+([A-Za-zÀ-ÿ\s]{4,50}?)(?:\.|,|\n|$|\.)',
            r'(?:precisa-se|necessita-se|contrata-se)\s+(?:de\s+)?(?:um|uma\s+)?([A-Za-zÀ-ÿ\s]{4,50}?)(?:\.|,|\n|$)',
            r'(?:estamos\s+contratando|está\s+contratando)\s+(?:um|uma\s+)?([A-Za-zÀ-ÿ\s]{4,50}?)(?:\.|,|\n|$)',
            r'(?:temos\s+vaga\s+(?:de|para))\s+([A-Za-zÀ-ÿ\s]{4,50}?)(?:\.|,|\n|$)',
        ]
        
        for padrao in padroes:
            match = re.search(padrao, texto, re.IGNORECASE)
            if match:
                cargo = match.group(1).strip().title()
                if 4 < len(cargo) < 60:
                    return cargo
        
        # Procurar na primeira linha se parece um cargo
        linhas = texto.strip().split('\n')
        for linha in linhas[:2]:
            linha = linha.strip().lower()
            if len(linha) > 80:
                continue
            palavras_chave = ['auxiliar', 'assistente', 'analista', 'operador', 'técnico',
                            'tecnico', 'vendedor', 'motorista', 'ajudante', 'supervisor',
                            'coordenador', 'gerente', 'estágio', 'estagio', 'aprendiz',
                            'recepcionista', 'secretária', 'secretaria', 'servente',
                            'pedreiro', 'carpinteiro', 'eletricista', 'mecânico',
                            'soldador', 'pintor', 'cozinheiro', 'cozinheira',
                            'garçom', 'garcom', 'camareira', 'fiscal', 'comprador']
            if any(p in linha for p in palavras_chave):
                return linha.title()[:60]
        
        return ''
    
    def validar_empresa(self, nome):
        """Valida se o texto é realmente um nome de empresa"""
        if not nome or len(nome) < 3:
            return False
        
        nome_lower = nome.lower().strip()
        
        # Se está na lista de empresas conhecidas, validar
        for emp in EMPRESAS_CONHECIDAS:
            if emp.lower() in nome_lower:
                return True
        
        palavras_proibidas = [
            'vaga', 'vagas', 'joinville', 'sc', 'região', 'bairro',
            'salário', 'salario', 'horário', 'horario', 'benefício', 'beneficio',
            'requisito', 'requisitos', 'whatsapp', 'whats', 'telegram',
            'grupo', 'canal', 'estamos', 'contratando', 'contrata',
            'oportunidade', 'oportunidades', 'curriculo', 'currículo',
            'enviar', 'interessados', 'candidatos', 'seleção', 'selecao',
            'processo', 'seletivo', 'vaga aberta', 'vaga disponível',
            'auxiliar', 'assistente', 'analista', 'operador', 'técnico',
            'tecnico', 'estágio', 'estagio', 'aprendiz', 'trainee',
            'pretendida', 'pretendido', 'disponível', 'disponivel',
            'imediato', 'imediata', 'início', 'inicio', 'aberta',
            'urgente', 'imperdivel', 'imperdível', 'nova', 'novo',
            'confidencial', 'sigiloso', 'entrar em contato',
            'tipo de', 'não exigida', 'escolaridade', 'registro em carteira',
            'com registro', 'fornecida pela empresa', 'seguro de vida',
            'convênio', 'convenio', 'vaga noturna', 'vaga de emprego',
            'oportunidade de', 'temos vagas', 'localizada no',
            'localizada na', 'contratação', 'contratacao',
            'pré-requisitos', 'pre-requisitos', 'atividades',
            'atribuições', 'atribuicoes', 'funções', 'funcoes',
            'responsabilidades', 'carga horária', 'carga horaria',
            'remuneração', 'remuneracao', 'salário a combinar',
            'ensino médio', 'ensino medio', 'ensino fundamental',
            'ensino superior', 'experiência', 'experiencia',
        ]
        
        # Verificar se o nome contém palavras proibidas
        palavras_nome = nome_lower.split()
        for palavra in palavras_nome:
            if palavra in palavras_proibidas:
                return False
        
        # Se mais da metade das palavras são proibidas, rejeitar
        proibidas_count = sum(1 for p in palavras_nome if p in palavras_proibidas)
        if proibidas_count >= len(palavras_nome) / 2:
            return False
        
        return True
    
    def extrair_empresa(self, texto_original):
        """Extrai nome da empresa com alta precisão"""
        texto = texto_original
        
        # Primeiro verificar empresas conhecidas
        for emp in EMPRESAS_CONHECIDAS:
            if emp.lower() in texto.lower():
                # Encontrar o nome completo
                match = re.search(r'\b' + re.escape(emp) + r'\b', texto, re.IGNORECASE)
                if match:
                    inicio = max(0, match.start() - 5)
                    fim = min(len(texto), match.end() + 20)
                    contexto = texto[inicio:fim]
                    # Tentar pegar nome completo
                    nome_match = re.search(r'([A-Z][A-Za-zÀ-ÿ&\s\-\.]{2,40})', contexto)
                    if nome_match:
                        nome = nome_match.group(1).strip()
                        if self.validar_empresa(nome):
                            return nome
        
        # Padrões de nome de empresa
        padroes = [
            r'(?:^|\n)([A-Z][A-Za-zÀ-ÿ&\s\-\.]{3,40})\s+(?:contrata|está\s+contratando|estamos\s+contratando)',
            r'(?:venha\s+para|trabalhe\s+na|faça\s+parte\s+da|junte-se\s+à|se\s+junte\s+a)\s+([A-Z][A-Za-zÀ-ÿ&\s\-\.]{3,40})',
            r'\*\*([A-Z][A-Za-zÀ-ÿ&\s\-\.]{3,50})\*\*',
            r'(?:empresa|consultoria|grupo|companhia)[:\s]+([A-Z][A-Za-zÀ-ÿ&\s\-\.]{3,50}?)(?:\.|,|\n|$)',
            r'(?:^|\n)([A-Z][A-Z\s\-\.&]{5,40})(?:\n|$)',
            r'contrata-se\s+(?:para|na)\s+([A-Z][A-Za-zÀ-ÿ&\s\-\.]{3,40})',
            r'processo\s+seletivo\s+(?:da\s+)?([A-Z][A-Za-zÀ-ÿ&\s\-\.]{3,40})',
            r'#([A-Z][A-Za-zÀ-ÿ]{3,30})',
            r'([A-Z][A-Za-zÀ-ÿ&\s\-\.]{3,40})\s+(?:está\s+com|tem|possui)\s+(?:vagas|oportunidades)',
        ]
        
        for padrao in padroes:
            match = re.search(padrao, texto, re.IGNORECASE)
            if match:
                nome = match.group(1).strip()
                nome = re.sub(r'[,\s\-\.]+$', '', nome)
                if self.validar_empresa(nome):
                    return nome
        
        return ''
    
    def limpar_texto(self, texto):
        """Limpa o texto mantendo caracteres especiais"""
        texto = re.sub(r'[^\x20-\x7E\xA0-\xFF\u0100-\u017F\u0180-\u024F\u1E00-\u1EFF\u2000-\u206F]', '', texto)
        texto = re.sub(r'\s+', ' ', texto)
        return texto.strip()
    
    def extrair(self, texto_original):
        """Extrai todos os dados de uma vaga"""
        texto = self.limpar_texto(texto_original)
        
        dados = {
            'cargo': '',
            'empresa': '',
            'salario': '',
            'cidade': 'Joinville/SC',
            'bairro': '',
            'horario': '',
            'contrato': '',
            'email': '',
            'whatsapp': '',
            'telefone': '',
            'beneficios': '',
            'requisitos': '',
            'atividades': '',
            'escolaridade': '',
            'experiencia': '',
            'link_vaga': '',
            'fonte': '',
            'categoria': '',
            'descricao': texto[:1000],
        }
        
        # 1. Classificar categoria
        dados['categoria'] = self.classificar_vaga(texto)
        
        # 2. Extrair cargo (ANTES da empresa para evitar confusão)
        dados['cargo'] = self.extrair_cargo(texto)
        
        # 3. Extrair empresa
        dados['empresa'] = self.extrair_empresa(texto_original)
        
        # 4. Salário
        match = re.search(r'R\$\s?[\d\.,]+(?:\s?(?:mil|hora|mês|mes|dia|semana))?', texto, re.IGNORECASE)
        if match:
            dados['salario'] = match.group(0).strip()
        
        # 5. Bairro
        for b in BAIRROS_JOINVILLE:
            if b.lower() in texto.lower():
                dados['bairro'] = b
                break
        
        # 6. Contrato
        tipos_contrato = ['CLT', 'PJ', 'Estágio', 'Estagio', 'Temporário', 'Temporario',
                         'Jovem Aprendiz', 'Menor Aprendiz', 'Trainee',
                         'Autônomo', 'Autonomo', 'Freelancer', 'MEI',
                         'Efetivo', 'Contrato', 'Tempo parcial', 'Integral']
        for t in tipos_contrato:
            if t.lower() in texto.lower():
                dados['contrato'] = t
                break
        
        # 7. Email
        match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', texto)
        if match:
            dados['email'] = match.group(0).lower()
        
        # 8. WhatsApp
        wpp_padroes = [
            r'(?:whatsapp|whats|wpp|zap|contato|fone|tel|telefone|celular|cel)[:\s]*\(?(\d{2})\)?\s?(\d{4,5}[-\s]?\d{4})',
            r'\(?(\d{2})\)?\s?9?\d{4}[-\s]?\d{4}',
        ]
        for padrao in wpp_padroes:
            match = re.search(padrao, texto, re.IGNORECASE)
            if match:
                if len(match.groups()) >= 2:
                    dados['whatsapp'] = f"({match.group(1)}) {match.group(2)}"
                else:
                    dados['whatsapp'] = match.group(0)
                break
        
        # 9. Escolaridade
        escolaridades = {
            'ensino fundamental incompleto': 'Fundamental Incompleto',
            'ensino fundamental completo': 'Fundamental Completo',
            'ensino fundamental': 'Fundamental',
            'ensino médio incompleto': 'Médio Incompleto',
            'ensino medio incompleto': 'Médio Incompleto',
            'ensino médio completo': 'Médio Completo',
            'ensino medio completo': 'Médio Completo',
            'ensino médio': 'Médio',
            'ensino medio': 'Médio',
            'superior incompleto': 'Superior Incompleto',
            'superior completo': 'Superior Completo',
            'ensino superior': 'Superior',
            'graduação': 'Superior',
            'graduacao': 'Superior',
            'tecnólogo': 'Tecnólogo',
            'tecnologo': 'Tecnólogo',
            'pós-graduação': 'Pós-Graduação',
            'pos-graduação': 'Pós-Graduação',
            'mestrado': 'Mestrado',
            'doutorado': 'Doutorado',
        }
        for termo, valor in escolaridades.items():
            if termo in texto.lower():
                dados['escolaridade'] = valor
                break
        
        # 10. Benefícios
        match = re.search(r'benefícios?[:\s]+(.+?)(?:\n\n|\n[A-ZÀ-Ý]|\n\*|\Z)', texto, re.IGNORECASE | re.DOTALL)
        if match:
            dados['beneficios'] = self.limpar_texto(match.group(1))[:300]
        
        # 11. Requisitos
        match = re.search(r'(?:requisitos|pré-requisitos|pré requisitos|o que precisa|necessário|necessario|buscamos alguém|buscamos alguem)[:\s]+(.+?)(?:\n\n|\n[A-ZÀ-Ý]|\n\*|\Z)', texto, re.IGNORECASE | re.DOTALL)
        if match:
            dados['requisitos'] = self.limpar_texto(match.group(1))[:300]
        
        # 12. Atividades
        match = re.search(r'(?:atividades|atribuições|atribuicoes|funções|funcoes|responsabilidades|o que faz|atuação|atuacao|atividades\*)[:\s]+(.+?)(?:\n\n|\n[A-ZÀ-Ý]|\n\*|\Z)', texto, re.IGNORECASE | re.DOTALL)
        if match:
            dados['atividades'] = self.limpar_texto(match.group(1))[:400]
        
        # 13. Experiência
        match = re.search(r'experiência[:\s]+(.+?)(?:\n\n|\n[A-ZÀ-Ý]|\Z)', texto, re.IGNORECASE | re.DOTALL)
        if match:
            dados['experiencia'] = self.limpar_texto(match.group(1))[:200]
        
        # 14. Horário
        match = re.search(r'(?:horário|horario|jornada|turno|expediente)[:\s]+([\d\w\s:,\-às]{10,80}?)(?:\.|\n|$)', texto, re.IGNORECASE)
        if match:
            dados['horario'] = match.group(1).strip()[:60]
        
        # 15. Link da vaga
        match = re.search(r'(?:link|acesse|saiba mais|inscrição|cadastro|formulário)[:\s]+(https?://[^\s]+)', texto, re.IGNORECASE)
        if match:
            dados['link_vaga'] = match.group(1)
        
        # Se não encontrou cargo mas encontrou empresa, tentar extrair cargo do início
        if not dados['cargo'] and dados['empresa']:
            linhas = texto.strip().split('\n')
            for linha in linhas[:3]:
                linha = linha.strip()
                if dados['empresa'].lower() not in linha.lower() and len(linha) > 5 and len(linha) < 80:
                    dados['cargo'] = linha[:60]
                    break
        
        return dados
    
    # ════════════════ BUSCA NO TELEGRAM ════════════════
    
    async def buscar_grupo(self, grupo_id, nome_grupo):
        print(f"\n🔍 {nome_grupo}")
        print(f"   Período: {self.data_inicio.strftime('%d/%m/%Y')} até {self.data_fim.strftime('%d/%m/%Y')}")
        
        try:
            entity = await self.client.get_entity(grupo_id)
            
            vagas = []
            total_processadas = 0
            total_encontradas = 0
            
            async for message in self.client.iter_messages(
                entity, limit=10000, offset_date=self.data_fim
            ):
                data_msg = message.date.replace(tzinfo=None) if message.date.tzinfo else message.date
                
                if data_msg < self.data_inicio:
                    continue
                
                texto = ""
                try:
                    texto = message.text or message.message or ""
                except:
                    pass
                
                if not texto or len(texto) < 50:
                    continue
                
                total_processadas += 1
                
                if total_processadas % 500 == 0:
                    print(f"   📊 {total_processadas} mensagens ({total_encontradas} vagas)...")
                
                if self.deve_ignorar(texto):
                    continue
                
                palavras_vaga = [
                    'vaga', 'contrata', 'contratando', 'oportunidade',
                    'processo seletivo', 'seleção', 'recrutamento',
                    'estamos com', 'temos vaga', 'precisa-se',
                    'necessita-se', 'contrata-se', 'venha trabalhar',
                    'faça parte', 'junte-se', 'trabalhe conosco',
                ]
                
                if not any(p in texto.lower() for p in palavras_vaga):
                    continue
                
                total_encontradas += 1
                dados = self.extrair(texto)
                
                # Classificar período
                dias_atras = (datetime.now() - data_msg).days
                
                if dias_atras <= 7:
                    sub_periodo = 'ÚLTIMOS 7 DIAS'
                elif dias_atras <= 15:
                    sub_periodo = 'ÚLTIMOS 15 DIAS'
                elif dias_atras <= 30:
                    sub_periodo = 'ÚLTIMOS 30 DIAS'
                elif dias_atras <= 60:
                    sub_periodo = '30 A 60 DIAS'
                else:
                    sub_periodo = '60 A 90 DIAS'
                
                link_mensagem = f"https://t.me/c/{str(grupo_id)[4:]}/{message.id}"
                
                vagas.append({
                    'periodo': sub_periodo,
                    'mes_referencia': data_msg.strftime('%B/%Y').upper(),
                    'dias_atras': dias_atras,
                    'data': data_msg.strftime('%d/%m/%Y'),
                    'hora': data_msg.strftime('%H:%M'),
                    'cargo': dados['cargo'],
                    'empresa': dados['empresa'],
                    'cidade': dados['cidade'],
                    'bairro': dados['bairro'],
                    'salario': dados['salario'],
                    'horario': dados['horario'],
                    'contrato': dados['contrato'],
                    'escolaridade': dados['escolaridade'],
                    'email': dados['email'],
                    'whatsapp': dados['whatsapp'],
                    'telefone': dados['telefone'],
                    'beneficios': dados['beneficios'],
                    'requisitos': dados['requisitos'],
                    'atividades': dados['atividades'],
                    'experiencia': dados['experiencia'],
                    'categoria': dados['categoria'],
                    'link_vaga': dados['link_vaga'],
                    'link_mensagem': link_mensagem,
                    'descricao': dados['descricao'],
                    'fonte': nome_grupo,
                    'id_mensagem': message.id,
                })
            
            print(f"   ✅ {total_encontradas} vagas encontradas")
            return vagas
            
        except Exception as e:
            print(f"   ❌ Erro: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    # ════════════════ GERAR ARQUIVOS ════════════════
    
    def gerar_excel(self, vagas):
        """Gera arquivo CSV organizado"""
        vagas.sort(key=lambda x: f"{x['data']} {x['hora']}", reverse=True)
        
        data_hoje = datetime.now().strftime('%Y%m%d_%H%M')
        arquivo = f'VAGAS_ADMIN_{self.nome_periodo}_{data_hoje}.csv'
        
        periodos = {
            'ÚLTIMOS 7 DIAS': [], 'ÚLTIMOS 15 DIAS': [],
            'ÚLTIMOS 30 DIAS': [], '30 A 60 DIAS': [], '60 A 90 DIAS': [],
        }
        
        for v in vagas:
            if v['periodo'] in periodos:
                periodos[v['periodo']].append(v)
        
        with open(arquivo, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f, delimiter=';')
            
            writer.writerow(['RELATÓRIO DE VAGAS - JOINVILLE/SC'])
            writer.writerow([f'Período: {self.data_inicio.strftime("%d/%m/%Y")} a {self.data_fim.strftime("%d/%m/%Y")}'])
            writer.writerow([f'Gerado em: {datetime.now().strftime("%d/%m/%Y %H:%M")}'])
            writer.writerow([f'Total de vagas: {len(vagas)}'])
            writer.writerow([])
            
            colunas = [
                'Período', 'Categoria', 'Mês Ref.', 'Data', 'Hora',
                'Cargo', 'Empresa', 'Cidade', 'Bairro', 'Salário',
                'Horário', 'Contrato', 'Escolaridade',
                'Email', 'WhatsApp', 'Telefone',
                'Benefícios', 'Requisitos', 'Atividades', 'Experiência',
                'Link Vaga', 'Link Mensagem', 'Fonte', 'Descrição'
            ]
            
            emojis = {
                'ÚLTIMOS 7 DIAS': '🔴', 'ÚLTIMOS 15 DIAS': '🟠',
                'ÚLTIMOS 30 DIAS': '🟡', '30 A 60 DIAS': '🟢', '60 A 90 DIAS': '🔵',
            }
            
            for nome_periodo, lista in periodos.items():
                if not lista:
                    continue
                
                writer.writerow([])
                writer.writerow([f'{emojis.get(nome_periodo, "")} {nome_periodo} - {len(lista)} vagas'])
                writer.writerow([])
                writer.writerow(colunas)
                
                for v in lista:
                    writer.writerow([
                        v['periodo'], v['categoria'], v['mes_referencia'],
                        v['data'], v['hora'], v['cargo'], v['empresa'],
                        v['cidade'], v['bairro'], v['salario'],
                        v['horario'], v['contrato'], v['escolaridade'],
                        v['email'], v['whatsapp'], v['telefone'],
                        v['beneficios'], v['requisitos'], v['atividades'],
                        v['experiencia'], v['link_vaga'], v['link_mensagem'],
                        v['fonte'], v['descricao']
                    ])
            
            writer.writerow([])
            writer.writerow(['=' * 30 + ' RESUMO ' + '=' * 30])
            writer.writerow(['Total de vagas:', len(vagas)])
            for nome_periodo, lista in periodos.items():
                if lista:
                    writer.writerow([f'{nome_periodo}:', len(lista)])
            writer.writerow([])
            writer.writerow(['POR CATEGORIA:'])
            for cat in ['Administrativo', 'Operacional', 'Técnico', 'Geral']:
                qtd = len([v for v in vagas if v['categoria'] == cat])
                if qtd > 0:
                    writer.writerow([f'{cat}:', qtd])
        
        print(f"\n📊 Arquivo gerado: {arquivo}")
        return arquivo
    
    # ════════════════ EXECUTAR ════════════════
    
    async def executar(self):
        print("\n" + "="*60)
        print(f"  🔍 JoinVagas PRO - Buscando vagas")
        print(f"  {self.data_inicio.strftime('%d/%m/%Y')} até {self.data_fim.strftime('%d/%m/%Y')}")
        print("="*60)
        
        await self.conectar()
        
        todas = []
        for gid in GRUPOS_IDS:
            vagas = await self.buscar_grupo(gid, "Empregos Joinville e Região")
            todas.extend(vagas)
        
        if not todas:
            print("\n❌ Nenhuma vaga encontrada!")
            await self.client.disconnect()
            return
        
        arquivo = self.gerar_excel(todas)
        
        with open('vagas_encontradas.json', 'w', encoding='utf-8') as f:
            json.dump({
                'data': datetime.now().strftime('%d/%m/%Y %H:%M'),
                'periodo': self.nome_periodo,
                'total': len(todas),
                'vagas': todas,
                'categorias': {
                    'Administrativo': len([v for v in todas if v['categoria'] == 'Administrativo']),
                    'Operacional': len([v for v in todas if v['categoria'] == 'Operacional']),
                    'Técnico': len([v for v in todas if v['categoria'] == 'Técnico']),
                    'Geral': len([v for v in todas if v['categoria'] == 'Geral']),
                }
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ {len(todas)} vagas salvas!")
        print(f"📁 {arquivo}")
        print(f"📁 vagas_encontradas.json")
        
        await self.client.disconnect()


# ════════════════ MENU ════════════════

def menu():
    print("\n" + "=" * 60)
    print("  🔍 JoinVagas PRO - Caçador de Vagas")
    print("  Joinville/SC - Todas as categorias")
    print("=" * 60)
    print(f"  📅 Hoje: {datetime.now().strftime('%d/%m/%Y')}")
    print()
    print("  [1] 📅 Desde 01/06/2026 até HOJE")
    print("  [2] 📆 Últimos 30 dias")
    print("  [3] 📆 Últimos 60 dias")
    print("  [4] 📆 Últimos 90 dias")
    print("  [5] 🗓️  Mês atual")
    print("  [6] 🔙 Últimos 7 dias")
    print("  [0] Sair")
    print()
    return input("  Escolha: ").strip()


async def main():
    while True:
        opcao = menu()
        
        if opcao == '0':
            print("\n👋 Até logo!")
            break
        
        hoje = datetime.now()
        
        periodos = {
            '1': (datetime(2026, 6, 1), hoje, "DESDE_01JUNHO2026"),
            '2': (hoje - timedelta(days=30), hoje, "30DIAS"),
            '3': (hoje - timedelta(days=60), hoje, "60DIAS"),
            '4': (hoje - timedelta(days=90), hoje, "90DIAS"),
            '5': (datetime(hoje.year, hoje.month, 1), hoje, f"MES_{hoje.strftime('%B%Y').upper()}"),
            '6': (hoje - timedelta(days=7), hoje, "7DIAS"),
        }
        
        if opcao in periodos:
            inicio, fim, nome = periodos[opcao]
            print(f"\n⏳ Buscando de {inicio.strftime('%d/%m/%Y')} até {fim.strftime('%d/%m/%Y')}...")
            
            bot = BuscadorVagasCompleto(inicio, fim, nome)
            await bot.executar()
            
            input("\n  Pressione ENTER para continuar...")
        else:
            print("❌ Opção inválida!")


if __name__ == '__main__':
    print("""
╔══════════════════════════════════════════════════╗
║   JoinVagas PRO - Caçador de Vagas v10           ║
║   Todas as categorias | Joinville/SC             ║
╚══════════════════════════════════════════════════╝
    """)
    asyncio.run(main())