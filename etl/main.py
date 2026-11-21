import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from etl.extracao import extrair_tudo
from etl.transformacao import transformar_tudo
from etl.carga import carregar_tudo

def main():
    extrair_tudo()                                  # API + CSV -> brutos/
    produtos, clientes, pedidos = transformar_tudo()  # brutos/ -> dados tratados
    carregar_tudo(produtos, clientes, pedidos)      # dados tratados -> PostgreSQL

if __name__ == '__main__':
    try:
        main()
    except RuntimeError as erro:
        print(f'erro: {erro}')
        sys.exit(1)