# Como usei IA

## Sugestões aceitas

1. **Separar a requisição da paginação em duas funções**: a IA sugeriu dividir a lógica de consumo da API em `buscar_pagina` (que consulta uma única página e trata erros HTTP e de conexão) e `buscar_todas_as_paginas` (que percorre todas as páginas até `total_pages`). Aceitei porque isso deixa o código mais legível e facilita o tratamento de erros em um único ponto. Validei chamando a API com diferentes tamanhos de página e confirmando que o total de registros não mudava.

2. **Usar `datetime.strptime` para datas e `Decimal` para valores monetários**: a IA sugeriu essas abordagens para as armadilhas A3 e A4. Aceitei porque `strptime` já resolve os dois formatos de data com uma condicional simples (`'/' in data`), e `Decimal` evita erros de arredondamento de ponto flutuante em valores financeiros (por exemplo, `0.1 + 0.2 != 0.3` em float, mas funciona corretamente com `Decimal`). Validei com os testes do pytest, comparando entradas conhecidas com as saídas esperadas.

3. **Separar os testes de reconciliação em duas funções com uma função auxiliar `obter_totais()`**: a IA sugeriu inicialmente colocar os dois asserts (contagem de pedidos e soma de valores) em uma única função de teste. Questionei essa abordagem porque, se o primeiro assert falhasse, o segundo nunca seria executado, e eu não saberia se a soma financeira estava correta. A IA então propôs três alternativas: função única, fixture do pytest e função auxiliar simples. Aceitei a terceira opção (função auxiliar `obter_totais()` que carrega os dados uma vez e devolve um dicionário, chamada por dois testes separados) porque mantém o nível de iniciante sem introduzir conceitos avançados como decorators e fixtures, e permite visualizar os dois resultados de forma independente no relatório do pytest.

## Sugestões rejeitadas

1. **Criar a pasta `brutos/` manualmente antes de executar**: a IA sugeriu criar a pasta antes de rodar o script. Rejeitei porque a pasta deve ser criada pelo próprio código (com `mkdir(parents=True, exist_ok=True)`), garantindo que o ETL funcione sem depender de preparação manual do ambiente.

2. **Usar `estado or None` na armadilha A2 (padronização de estados)**: a IA repetiu o mesmo padrão da armadilha A1 (e-mails), sugerindo `cliente_tratado['estado'] = estado or None`. Rejeitei porque a coluna `estado` é `NOT NULL` no `schema.sql` e no contrato de dados. Se chegasse um estado vazio, converter para `None` quebraria a carga no banco com `NotNullViolation`. A armadilha A2 pede apenas padronização para maiúsculas, então simplifiquei para `cliente['estado'].strip().upper()`, que é coerente com o esquema do banco.

## Falhas e retrabalho

1. **Caminho incorreto para a pasta `brutos/`**: a IA gerou o código criando a pasta `brutos/` dentro de `etl/`, em vez de na raiz do projeto. Identifiquei o problema ao perceber que os arquivos JSON estavam sendo salvos no local errado. Corrigi usando `Path(__file__).resolve().parent.parent` para localizar a raiz do projeto automaticamente e criar a pasta no local correto.

2. **Import do módulo `etl` nos testes**: ao criar os arquivos de teste seguindo a sugestão da IA (`from etl.transformacao import ...`), o pytest não encontrava o módulo `etl` e disparava `ModuleNotFoundError`. A IA sugeriu criar um arquivo `pytest.ini` com `pythonpath = .`, mas isso sozinho não resolveu. A solução foi criar o arquivo `etl/__init__.py` (transformando a pasta em um pacote Python) e rodar os testes com `python -m pytest -v`, que adiciona o diretório atual ao `sys.path` automaticamente.