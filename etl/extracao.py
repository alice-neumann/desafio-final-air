import csv
import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import urlopen
from pathlib import Path

BASE_URL = os.getenv('API_BASE_URL', 'http://127.0.0.1:8000')

def buscar_pagina(rota, pagina, tamanho=50):
    url = f'{BASE_URL}/{rota}?page={pagina}&page_size={tamanho}'

    try:
        with urlopen(url, timeout=10) as resposta:
            if resposta.status != 200:
                raise RuntimeError(f'API respondeu com HTTP {resposta.status}')
            return json.load(resposta)

    except HTTPError as erro:
        if erro.code == 404:
            raise RuntimeError(
                f'A página {pagina} da rota /{rota} não foi encontrada.'
            ) from erro
        raise RuntimeError(f'A API respondeu com HTTP {erro.code}.') from erro

    except URLError as erro:
        raise RuntimeError(
            f'Não foi possível conectar à API em {BASE_URL}: {erro.reason}'
        ) from erro

def buscar_todas_as_paginas(rota, tamanho=50):
    primeira_pagina = buscar_pagina(rota, pagina=1, tamanho=tamanho)
    registros = primeira_pagina['items']
    total_paginas = primeira_pagina['total_pages']

    for pagina in range(2, total_paginas + 1):
        resposta = buscar_pagina(rota, pagina=pagina, tamanho=tamanho)
        registros.extend(resposta['items'])

    return registros, total_paginas

def extrair_tudo():
    clientes, paginas_clientes = buscar_todas_as_paginas('clientes', tamanho=50)
    pedidos, paginas_pedidos = buscar_todas_as_paginas('pedidos', tamanho=50)

    raiz_projeto = Path(__file__).resolve().parent.parent
    arquivo_produtos = raiz_projeto / 'insumos' / 'dados' / 'produtos.csv'
    with arquivo_produtos.open('r', encoding='utf-8', newline='') as arquivo:
        produtos = list(csv.DictReader(arquivo))

    print(f'extracao: clientes paginas={paginas_clientes} registros={len(clientes)}')
    print(f'extracao: pedidos paginas={paginas_pedidos} registros_brutos={len(pedidos)}')

    pasta_brutos = raiz_projeto / 'brutos'
    pasta_brutos.mkdir(parents=True, exist_ok=True)

    for nome, registros in (
        ('clientes', clientes),
        ('pedidos', pedidos),
        ('produtos', produtos),
    ):
        destino = pasta_brutos / f'{nome}.json'
        with destino.open('w', encoding='utf-8') as arquivo:
            json.dump(registros, arquivo, ensure_ascii=False, indent=2)