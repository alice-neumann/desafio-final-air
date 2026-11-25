from decimal import Decimal
from etl.carga import conectar
from etl.transformacao import (
    carregar_brutos,
    tratar_pedidos_repetidos,
    tratar_valor_total_pedido,
    tratar_valor_total_divergente,
)

# funcao auxiliar para não repetir codigo
def obter_totais():
    # dados da origem
    unicos, _ = tratar_pedidos_repetidos(carregar_brutos('pedidos'))
    pedidos = [tratar_valor_total_divergente(tratar_valor_total_pedido(p)) for p in unicos]
    soma_origem = sum((p['valor_itens'] for p in pedidos), Decimal('0.00')).quantize(Decimal('0.01'))

    # dados do banco (busca contagem e soma juntas)
    with conectar() as conn, conn.cursor() as cur:
        cur.execute('SELECT COUNT(*), COALESCE(SUM(valor_itens), 0) FROM pedidos')
        qtd_banco, soma_banco = cur.fetchone()

    return {
        'qtd_origem': len(unicos),
        'qtd_banco': qtd_banco,
        'soma_origem': soma_origem,
        'soma_banco': soma_banco,
    }

def test_reconciliacao_contagem_pedidos():
    totais = obter_totais()
    assert totais['qtd_banco'] == totais['qtd_origem']

def test_reconciliacao_soma_valores():
    totais = obter_totais()
    diferenca = abs(totais['soma_origem'] - totais['soma_banco'])
    assert diferenca <= Decimal('0.01')