with open('ler_grupos.py', 'r', encoding='utf-8') as f:
    codigo = f.read()

# Corrigir a validação do WhatsApp - erro do 'num'
# Remover a validação quebrada e usar só verificação de dígitos
codigo = codigo.replace(
    "num = match.group(0)\n                if self.validar_whatsapp(num):\n                    dados['whatsapp'] = num",
    "dados['whatsapp'] = match.group(0)"
)

# Simplificar a função validar_whatsapp
codigo = codigo.replace(
    '''    def validar_whatsapp(self, numero):
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
        return True''',
    '''    def validar_whatsapp(self, numero):
        """Valida se o número parece um WhatsApp real"""
        if not numero:
            return False
        digitos = ''.join(filter(str.isdigit, numero))
        # Precisa ter pelo menos 10 dígitos
        if len(digitos) < 10:
            return False
        # Não pode ser número repetido
        if len(set(digitos)) <= 2:
            return False
        return True'''
)

with open('ler_grupos.py', 'w', encoding='utf-8') as f:
    f.write(codigo)

print('✅ WhatsApp corrigido!')