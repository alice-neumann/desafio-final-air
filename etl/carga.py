import os
from pathlib import Path
from decimal import Decimal
import psycopg

RAIZ_PROJETO = Path(__file__).resolve().parent.parent

def ler_env():
    env = {}
    caminho_env = RAIZ_PROJETO / '.env'
    if caminho_env.exists():
        for linha in caminho_env.read_text().splitlines():
            if '=' in linha and not linha.startswith('#'):
                chave, valor = linha.split('=', 1)
                env[chave.strip()] = valor.strip()
    return env

def conectar():
    env = ler_env()
    host = os.getenv('POSTGRES_HOST', env.get('POSTGRES_HOST', 'localhost'))
    port = int(os.getenv('POSTGRES_PORT', env.get('POSTGRES_PORT', 5433)))
    dbname = os.getenv('POSTGRES_DB', env.get('POSTGRES_DB'))
    user = os.getenv('POSTGRES_USER', env.get('POSTGRES_USER'))
    password = os.getenv('POSTGRES_PASSWORD', env.get('POSTGRES_PASSWORD'))

    return psycopg.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password
    )

def limpar_tabelas(cursor):
    cursor.execute('TRUNCATE itens_pedido, pedidos, clientes, produtos')

def carregar_produtos(cursor, produtos):
    cursor.executemany(
        'INSERT INTO produtos (produto_id, nome, categoria, preco_base) VALUES (%s, %s, %s, %s)',
        [(p['produto_id'], p['nome'], p['categoria'], p['preco_base']) for p in produtos],
    )

def carregar_clientes(cursor, clientes):
    cursor.executemany(
        'INSERT INTO clientes (id, nome, email, cidade, estado, cadastro_em) VALUES (%s, %s, %s, %s, %s, %s)',
        [(c['id'], c['nome'], c['email'], c['cidade'], c['estado'], c['cadastro_em']) for c in clientes],
    )

def carregar_pedidos(cursor, pedidos):
    cursor.executemany(
        'INSERT INTO pedidos (id, cliente_id, data_pedido, status, valor_total, valor_itens, divergente) VALUES (%s, %s, %s, %s, %s, %s, %s)',
        [(p['id'], p['cliente_id'], p['data_pedido'], p['status'], p['valor_total'], p['valor_itens'], p['divergente']) for p in pedidos],
    )

def carregar_itens_pedido(cursor, pedidos):
    linhas = [
        (p['id'], item['linha'], item['produto_id'], item['quantidade'], item['preco_unitario'])
        for p in pedidos
        for item in p['itens']
    ]
    cursor.executemany(
        'INSERT INTO itens_pedido (pedido_id, linha, produto_id, quantidade, preco_unitario) VALUES (%s, %s, %s, %s, %s)',
        linhas,
    )

def contar_tabelas(cursor, pedidos):
    contagens = {}
    for tabela in ('produtos', 'clientes', 'pedidos', 'itens_pedido'):
        cursor.execute(f'SELECT COUNT(*) FROM {tabela}')
        contagens[tabela] = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM pedidos WHERE divergente')
    divergentes = cursor.fetchone()[0]

    cursor.execute('SELECT COALESCE(SUM(valor_itens), 0) FROM pedidos')
    soma_destino = cursor.fetchone()[0]

    soma_origem = sum(
        (pedido['valor_itens'] for pedido in pedidos),
        Decimal('0.00'),
    ).quantize(Decimal('0.01'))

    print(
        f"carga: clientes={contagens['clientes']} produtos={contagens['produtos']} "
        f"pedidos={contagens['pedidos']} itens={contagens['itens_pedido']}"
    )
    print(
        f'reconciliacao: soma_valor_itens_origem={soma_origem:.2f} '
        f'soma_valor_itens_destino={soma_destino:.2f} '
        f'diferenca={abs(soma_origem - soma_destino):.2f}'
    )
    print(f'divergentes: {divergentes} pedidos com valor_total diferente da soma dos itens')

def carregar_tudo(produtos, clientes, pedidos):
    with conectar() as conn:                 
        with conn.cursor() as cursor:
            limpar_tabelas(cursor)
            carregar_produtos(cursor, produtos)
            carregar_clientes(cursor, clientes)
            carregar_pedidos(cursor, pedidos)
            carregar_itens_pedido(cursor, pedidos)
            contar_tabelas(cursor, pedidos)