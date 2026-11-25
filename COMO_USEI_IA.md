# Como usei IA

## Ferramentas

- **GitHub Copilot**
- **Claude**

## Sugestões aceitas

1. **Separar a requisição da paginação em duas funções**: a IA sugeriu dividir a lógica de consumo da API em `buscar_pagina` (que consulta uma única página e trata erros HTTP e de conexão) e `buscar_todas_as_paginas` (que percorre todas as páginas até `total_pages`). Aceitei porque isso deixa o código mais legível e facilita o tratamento de erros -em um único ponto. Como validei: chamei a API com diferentes tamanhos de página e confirmei que o total de registros não mudava.

2. **Usar `datetime.strptime` para datas e `Decimal` para valores monetários**: a IA sugeriu essas abordagens para as armadilhas A3 e A4. Aceitei porque `strptime` resolve os dois formatos de data com uma condicional simples (`'/' in data`), e `Decimal` evita erros de arredondamento de ponto flutuante em valores financeiros (por exemplo, `0.1 + 0.2 != 0.3` em float). Como validei: testes do pytest com entradas conhecidas (`'125,84'` vira `Decimal('125.84')`, `'15/03/2026'` vira `date(2026, 3, 15)`).

3. **Separar os testes de reconciliação em duas funções com uma função auxiliar `obter_totais()`**: a IA sugeriu inicialmente colocar os dois asserts (contagem de pedidos e soma de valores) em uma única função de teste. Questionei essa abordagem porque, se o primeiro assert falhasse, o segundo nunca seria executado, e eu não saberia se a soma financeira estava correta. A IA propôs três alternativas: função única, fixture do pytest e função auxiliar simples. Aceitei a terceira, porque carrega os dados uma vez e permite ver os dois resultados de forma independente no relatório do pytest, sem introduzir fixtures. Como validei: rodei o pytest com o banco carregado e os dois testes aparecem separados e passando.

6. **Orquestração local com Docker Compose para o Stretch**: pedi à IA para estruturar o `docker-compose.yml` e os Dockerfiles dos serviços (PostgreSQL, API e ETL). Aceitei a estrutura de healthchecks com `depends_on: condition: service_healthy`, garantindo que o ETL só inicie após o banco estar pronto e a API responder no `/saude`. Como validei: executei `docker compose up --build` e confirmei que a carga ocorreu automaticamente.

## Sugestões rejeitadas

1. **Criar a pasta `brutos/` manualmente antes de executar**: a IA sugeriu criar a pasta antes de rodar o script. Rejeitei porque a pasta deve ser criada pelo próprio código (`mkdir(parents=True, exist_ok=True)`), para o ETL funcionar sem preparação manual. Como validei: `brutos/` está no `.gitignore`, então não existe em um clone novo, rodei o ETL em uma cópia nova do repositório e o código criou a pasta sozinho.

2. **Usar estado or None na armadilha A2 (padronização de estados)**: a IA repetiu o mesmo padrão da armadilha A1 (e-mails), sugerindo cliente_tratado['estado'] = estado or None. Rejeitei porque a coluna estado é NOT NULL no schema.sql e no contrato de dados. Se chegasse um estado vazio, converter para None quebraria a carga no banco, a armadilha A2 pede apenas padronização para maiúsculas, então simplifiquei para cliente['estado'].strip().upper(), que é coerente com o esquema do banco.

3. **Colocar a senha do banco no `docker-compose.yml` e em comandos `docker run` no README**: a IA inicialmente propôs uma alternativa com a senha explícita. Rejeitei por violar a regra de nunca versionar credenciais, criei o `.env.example` e mantive a leitura restrita ao `.env`, que está no `.gitignore`. Também organizei os arquivos de contêiner na pasta `docker/`. Como validei: `git ls-files` não lista o `.env` e a busca da senha em todo o histórico (`git log --all -p -S"<senha>"`) não retorna nada.

4. **Converter `cadastro_em` para `date` em Python com uma função própria**: a IA propôs uma função pura com `date.fromisoformat` para esse campo. Não implementei porque os 1000 cadastros já vêm em AAAA-MM-DD, não há armadilha de formato nessa coluna, e o PostgreSQL converte o texto para `DATE` na carga. Registrei a decisão no `CONTRATO_DE_DADOS.md`. Como validei: a carga de 1000 clientes ocorreu sem erro e a coluna é `DATE` no `schema.sql`.

## Falhas e retrabalho

1. **Caminho incorreto para a pasta `brutos/`**: a IA gerou o código criando a pasta `brutos/` dentro de `etl/`, em vez de na raiz do projeto. Identifiquei o problema ao perceber que os arquivos JSON estavam sendo salvos no local errado. Corrigi usando `Path(__file__).resolve().parent.parent` para localizar a raiz do projeto automaticamente e criar a pasta no local correto.

2. **Import do módulo `etl` nos testes**: ao criar os arquivos de teste seguindo a sugestão da IA (`from etl.transformacao import ...`), o pytest não encontrava o módulo `etl` e disparava `ModuleNotFoundError`. A IA sugeriu criar um arquivo `pytest.ini` com `pythonpath = .`, mas isso sozinho não resolveu. A solução foi criar o arquivo `etl/__init__.py` (transformando a pasta em um pacote Python) e rodar os testes com `python -m pytest -v`, que adiciona o diretório atual ao `sys.path`.

3. **Erro de conexão da API no contêiner Docker (`Connection refused [Errno 111]`)**: ao rodar o `docker compose up`, o serviço `verdejar-etl` falhou ao tentar conectar na API em `http://api:8000`. Identifiquei que a API em `insumos/api_verdejar.py` estava configurada para escutar exclusivamente em `127.0.0.1`, rejeitando conexões da rede interna do Docker. Corrigi alterando a interface de escuta da API para `0.0.0.0` e parametrizando a `BASE_URL` no `extracao.py` via variável de ambiente `API_BASE_URL`.

5. **Comando de carga do schema incompatível com o PowerShell**: a IA me passou `docker exec -i verdejar-pg psql ... < schema.sql`, que só funciona no Git Bash. No PowerShell apareceu `Operador '<' reservado para uso futuro` e as tabelas não foram criadas (`Did not find any relations`). Retrabalho: usei `Get-Content insumos\schema.sql | docker exec -i verdejar-pg psql -U postgres -d verdejar`, e confirmei as tabelas com `\dt`.

6. **Pasta `brutos/` não aparecia no meu computador ao rodar pelo Docker Compose**: o `docker-compose.yml` proposto não montava nenhuma pasta no serviço do ETL, então a pasta era criada só dentro do contêiner e sumia ao terminar. Percebi ao testar o repositório em uma pasta nova. Retrabalho: acrescentei o volume `./brutos:/app/brutos` no serviço `etl`, e a pasta passou a aparecer na raiz do projeto.

## Tutoria nas consultas SQL (Sprint 1)

Usei o Claude como tutor durante o curso banco de dados da sprint 1. Pedi explicações de conceitos (`CASE WHEN`, `COALESCE`, leads, receita, conversão, ticket médio) e a conferência das minhas respostas dos projetos 1 e 2 do curso de SQL. Nas consultas de validação desse desafio, a revisão levantou que "vendas" era ambíguo quanto aos pedidos cancelados. Decidi excluir os cancelados e somar `valor_itens`, e acrescentei um segundo teste da (a) (vendas + cancelados = soma geral da tabela). Como validei: executei as consultas no banco e conferi cada resultado com a contagem do ETL (5000 pedidos, 238 divergentes).