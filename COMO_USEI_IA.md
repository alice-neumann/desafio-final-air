# Como usei IA

## Sugestões aceitas

1. **Separar a requisição da paginação em duas funções**: a IA sugeriu dividir a lógica de consumo da API em `buscar_pagina` (que consulta uma única página e trata erros HTTP e de conexão) e `buscar_todas_as_paginas` (que percorre todas as páginas até `total_pages`). Aceitei porque isso deixa o código mais legível e facilita o tratamento de erros em um único ponto, validei chamando a API com diferentes tamanhos de página e confirmando que o total de registros não mudava.

2. **Usar `datetime.strptime` para datas e `Decimal` para valores monetários**: a IA sugeriu essas abordagens para as armadilhas A3 e A4. Aceitei porque `strptime` já resolve os dois formatos de data com apenas uma condição (`'/' in data`), e `Decimal` evita erros de arredondamento de ponto flutuante em valores financeiros. Validei com os testes do pytest, comparando entradas conhecidas com as saídas esperadas.

3. **Separar os testes de reconciliação em duas funções com uma função auxiliar `obter_totais()`**: a IA sugeriu inicialmente colocar os dois asserts (contagem de pedidos e soma de valores) em uma única função de teste. Questionei essa abordagem porque se o primeiro assert falhasse, o segundo nunca seria executado, e não saberia se a soma financeira estaria correta. A IA então propôs três alternativas: função única, fixture do pytest e função auxiliar simples. Aceitei a terceira opção que carrega os dados uma vez e devolve um dicionário, porque mantém o nível de iniciante sem introduzir conceitos avançados, e permite visualizar os dois resultados de forma independente no relatório do pytest.

4. **Orquestração local com Docker Compose para o Stretch**: pedi à IA para estruturar o `docker-compose.yml` e os Dockerfiles dos serviços (PostgreSQL, API e ETL). Aceitei a estrutura de *healthchecks* com `depends_on: condition: service_healthy`, garantindo que o ETL só inicie após o banco estar pronto e a API responder no `/saude`. Validei executando `docker compose up --build` e confirmando que a carga ocorreu automaticamente.

## Sugestões rejeitadas

1. **Criar a pasta `brutos/` manualmente antes de executar**: a IA sugeriu criar a pasta antes de rodar o script, rejeitei porque a pasta deve ser criada pelo próprio código (com `mkdir(parents=True, exist_ok=True)`), garantindo que o ETL funcione sem depender de preparação manual do ambiente.

2. **Usar `estado or None` na armadilha A2 (padronização de estados)**: a IA repetiu o mesmo padrão da armadilha A1 (e-mails), sugerindo `cliente_tratado['estado'] = estado or None`. Rejeitei porque a coluna `estado` é `NOT NULL` no `schema.sql` e no contrato de dados. Se chegasse um estado vazio, converter para `None` quebraria a carga no banco, a armadilha A2 pede apenas padronização para maiúsculas, então simplifiquei para `cliente['estado'].strip().upper()`, que é coerente com o esquema do banco.

3. **Expor senhas no `docker-compose.yml` e arquivos Docker soltos na raiz**: a IA inicialmente propôs uma alternativa com a senha explícita no compose e comandos de `docker run` no README contendo senhas abertas, além de deixar os Dockerfiles soltos na raiz do projeto. Rejeitei essa exposição por violar a regra de segurança de nunca versionar credenciais e criei o `.env.example`, mantendo a leitura restrita ao `.env`. Também adicionei os arquivos do contêiner dentro da pasta  `docker/` para melhor organização.

## Falhas e retrabalho

1. **Caminho incorreto para a pasta `brutos/`**: a IA gerou o código criando a pasta `brutos/` dentro de `etl/`, em vez de na raiz do projeto. Identifiquei o problema ao perceber que os arquivos JSON estavam sendo salvos no local errado. Corrigi usando `Path(__file__).resolve().parent.parent` para localizar a raiz do projeto automaticamente e criar a pasta no local correto.

2. **Import do módulo `etl` nos testes**: ao criar os arquivos de teste seguindo a sugestão da IA (`from etl.transformacao import ...`), o pytest não encontrava o módulo `etl` e disparava `ModuleNotFoundError`. A IA sugeriu criar um arquivo `pytest.ini` com `pythonpath = .`, mas isso sozinho não resolveu. A solução foi criar o arquivo `etl/__init__.py` e rodar os testes com `python -m pytest -v`, que adiciona o diretório atual ao `sys.path` automaticamente.

3. **Erro de conexão da API no contêiner Docker (`Connection refused [Errno 111]`)**: ao rodar o `docker compose up`, o serviço `verdejar-etl` falhou ao tentar conectar na API em `http://api:8000`. Identifiquei que a API em `insumos/api_verdejar.py` estava configurada para escutar exclusivamente em `127.0.0.1`, rejeitando conexões da rede interna do Docker. Corrigi alterando a interface de escuta da API para `0.0.0.0` e parametrizando a `BASE_URL` no `extracao.py` via variável de ambiente `API_BASE_URL`.