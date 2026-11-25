from datetime import date
from decimal import Decimal

from etl.transformacao import (
    tratar_email_cliente,
    tratar_sigla_estados,
    tratar_data_pedido,
    tratar_valor_total_pedido,
    tratar_pedidos_repetidos,
    tratar_valor_total_divergente,
)

# A1: e-mails ausentes
def test_a1_email_valido_permanece():
    cliente = {'id': 1, 'email': 'ana.silva@exemplo.com'}
    resultado = tratar_email_cliente(cliente)
    assert resultado['email'] == 'ana.silva@exemplo.com'

def test_a1_email_vazio_ou_nulo_vira_none():
    assert tratar_email_cliente({'id': 1, 'email': ''})['email'] is None
    assert tratar_email_cliente({'id': 2, 'email': '   '})['email'] is None
    assert tratar_email_cliente({'id': 3, 'email': None})['email'] is None

# A2: sigla do estado em caixa mista
def test_a2_estado_minusculo_vira_maiusculo():
    assert tratar_sigla_estados({'id': 1, 'estado': 'rs'})['estado'] == 'RS'
    assert tratar_sigla_estados({'id': 2, 'estado': ' sp '})['estado'] == 'SP'

def test_a2_estado_maiusculo_permanece():
    assert tratar_sigla_estados({'id': 1, 'estado': 'SC'})['estado'] == 'SC'

# A3: datas em dois formatos 
def test_a3_data_formato_barra():
    pedido = {'id': 1, 'data_pedido': '15/03/2026'}
    resultado = tratar_data_pedido(pedido)
    assert resultado['data_pedido'] == date(2026, 3, 15)

def test_a3_data_formato_iso():
    pedido = {'id': 1, 'data_pedido': '2026-03-15'}
    resultado = tratar_data_pedido(pedido)
    assert resultado['data_pedido'] == date(2026, 3, 15)

# A4: valor total em formato numérico e texto com vírgula
def test_a4_valor_texto_com_virgula():
    pedido = {'id': 1, 'valor_total': '125,84'}
    resultado = tratar_valor_total_pedido(pedido)
    assert resultado['valor_total'] == Decimal('125.84')

def test_a4_valor_numerico_float():
    pedido = {'id': 1, 'valor_total': 94.34}
    resultado = tratar_valor_total_pedido(pedido)
    assert resultado['valor_total'] == Decimal('94.34')

# A5: pedidos repetidos entre páginas (mantém o primeiro e descarta duplicados)
def test_a5_pedidos():
    pedidos_brutos = [
        {'id': 101, 'cliente_id': 1},
        {'id': 102, 'cliente_id': 2},
        {'id': 101, 'cliente_id': 1},  # duplicado
        {'id': 103, 'cliente_id': 3},
        {'id': 102, 'cliente_id': 2},  # duplicado
    ]
    unicos, descartados = tratar_pedidos_repetidos(pedidos_brutos)
    
    assert len(unicos) == 3
    assert descartados == 2
    assert [p['id'] for p in unicos] == [101, 102, 103]

# A6: valor total divergente da soma dos itens
def test_a6_pedido_sem_divergencia():
    pedido = {
        'id': 1,
        'valor_total': Decimal('25.00'),
        'itens': [
            {'quantidade': 2, 'preco_unitario': Decimal('10.00')},
            {'quantidade': 1, 'preco_unitario': Decimal('5.00')},
        ],
    }
    resultado = tratar_valor_total_divergente(pedido)
    assert resultado['valor_itens'] == Decimal('25.00')
    assert resultado['divergente'] is False

def test_a6_pedido_com_divergencia():
    pedido = {
        'id': 2,
        'valor_total': Decimal('30.00'),  # diferente da soma dos itens (25.00)
        'itens': [
            {'quantidade': 2, 'preco_unitario': Decimal('10.00')},
            {'quantidade': 1, 'preco_unitario': Decimal('5.00')},
        ],
    }
    resultado = tratar_valor_total_divergente(pedido)
    assert resultado['valor_itens'] == Decimal('25.00')
    assert resultado['divergente'] is True