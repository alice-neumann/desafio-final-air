import json
from pathlib import Path
from datetime import datetime
from decimal import Decimal

RAIZ_PROJETO = Path(__file__).resolve().parent.parent

# Função para carregador os dados brutos
def carregar_brutos(nome):
    caminho = RAIZ_PROJETO / 'brutos' / f'{nome}.json'
    with caminho.open(encoding='utf-8') as arquivo:
        return json.load(arquivo)

# A1
def tratar_email_cliente(cliente):
    cliente_tratado = cliente.copy()
    email = cliente_tratado.get('email')

    if isinstance(email, str):
        email = email.strip()

    cliente_tratado['email'] = email or None
    return cliente_tratado

# A2
def tratar_sigla_estados(cliente):
    cliente_tratado = cliente.copy()
    estado = cliente_tratado.get('estado')

    if isinstance(estado, str):
        estado = estado.strip().upper()

    cliente_tratado['estado'] = estado or None
    return cliente_tratado

# A3
def tratar_data_pedido(pedido):
    pedido_tratado = pedido.copy()
    data = pedido_tratado['data_pedido'].strip()
    
    formato = '%d/%m/%Y' if '/' in data else '%Y-%m-%d'
    pedido_tratado['data_pedido'] = datetime.strptime(data, formato).date()

    return pedido_tratado

# A4
def tratar_valor_total_pedido(pedido):
    pedido_tratado = pedido.copy()
    valor = pedido_tratado['valor_total']

    if isinstance(valor, str):
        valor = valor.strip().replace(',', '.')

    pedido_tratado['valor_total'] = Decimal(str(valor)).quantize(Decimal('0.01'))

    return pedido_tratado

# A5
def tratar_pedidos_repetidos(pedidos):
    ids_vistos = set()
    unicos = []

    for pedido in pedidos:
        if pedido['id'] not in ids_vistos:
            ids_vistos.add(pedido['id'])
            unicos.append(pedido)

    return unicos, len(pedidos) - len(unicos)

# A6
def tratar_valor_total_divergente(pedido):
    pedido_tratado = pedido.copy()

    valor_itens = sum(
        Decimal(str(item['quantidade'])) * Decimal(str(item['preco_unitario']))
        for item in pedido_tratado['itens']
    ).quantize(Decimal('0.01'))

    valor_total = pedido_tratado['valor_total']
    if not isinstance(valor_total, Decimal):
        valor_total = tratar_valor_total_pedido(pedido_tratado)['valor_total']

    pedido_tratado['valor_itens'] = valor_itens
    pedido_tratado['divergente'] = abs(valor_total - valor_itens) > Decimal('0.01')

    return pedido_tratado

# Contadores
clientes = carregar_brutos('clientes')
pedidos = carregar_brutos('pedidos')
pedidos_unicos, repetidos_descartados = tratar_pedidos_repetidos(pedidos)

clientes_tratados = [tratar_sigla_estados(tratar_email_cliente(c)) for c in clientes]
pedidos_tratados = [
    tratar_valor_total_divergente(tratar_valor_total_pedido(tratar_data_pedido(p)))
    for p in pedidos_unicos
]

print(f"emails_nulos={sum(c['email'] is None for c in clientes_tratados)}")                  
print(f"estados_corrigidos={sum(a['estado'] != b['estado'] for a, b in zip(clientes, clientes_tratados))}")  
print(f"datas_convertidas={sum('/' in p['data_pedido'] for p in pedidos_unicos)}")           
print(f"valores_convertidos={sum(isinstance(p['valor_total'], str) for p in pedidos_unicos)}")  
print(f"repetidos_descartados={repetidos_descartados}")                                       
print(f"divergentes={sum(p['divergente'] for p in pedidos_tratados)}")                        