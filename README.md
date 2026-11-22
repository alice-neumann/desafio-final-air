# Desafio Final — ETL da Verdejar

Desafio Final do Bootcamp **Fellowship AI-Driven Data Engineering** (Fase 1 · Sprint 2).

A Verdejar é uma loja virtual fictícia de hortifrúti. Este projeto implementa um pipeline ETL em Python que extrai dados de clientes e pedidos de uma API HTTP local paginada e um catálogo de produtos em CSV, trata seis armadilhas de qualidade declaradas nos dados (A1 a A6), carrega tudo em um banco PostgreSQL e prova que a carga está completa e correta por meio de reconciliação, testes automatizados e consultas SQL de validação.

Todos os dados são 100% sintéticos, gerados com seed fixa (2026).

---

## Estrutura do projeto

```
desafio-final-air/
├── docker/                         # Arquivos Docker
│   ├── Dockerfile.api              # Imagem da API Verdejar
│   └── Dockerfile.etl              # Imagem do pipeline ETL
│
├── insumos/                        # Dados e scripts fornecidos pelo desafio
│   ├── dados/
│   │   ├── clientes.json           
│   │   ├── pedidos.json            
│   │   └── produtos.csv            
│   ├── api_verdejar.py             # API local (rotas /clientes, /pedidos, /saude)
│   ├── gerar_dados.py              # Script gerador dos dados sintéticos (seed 2026)
│   ├── README_insumos.md           # Documentação dos insumos fornecidos
│   └── schema.sql                  # Esquema de destino no PostgreSQL (4 tabelas)
│
├── etl/                            # Módulo principal do pipeline ETL
│   ├── __init__.py                 
│   ├── extracao.py                 
│   ├── transformacao.py            
│   ├── carga.py                    
│   └── main.py                     
│
├── tests/                          # Testes automatizados com pytest
│   ├── test_transformacao.py       # 11 testes unitários das armadilhas A1–A6
│   └── test_reconciliacao.py       # 2 testes de reconciliação (contagem e soma vs banco)
│
├── brutos/                         # Dados brutos extraídos da API (não versionado)
│   ├── clientes.json
│   ├── pedidos.json
│   └── produtos.json
│
├── .env                            # Credenciais do banco (não versionado)
├── .env.example                    # Modelo de variáveis de ambiente
├── .gitignore                      
├── docker-compose.yml              # Stretch: orquestração completa (db, api, etl)
├── requirements.txt                # Dependências do projeto (psycopg, pytest)
├── COMO_USEI_IA.md                 # Registro de uso da IA como par
├── CONTRATO_DE_DADOS.md            # Contrato de dados: campos, tipos e regras por tabela
├── consultas_validacao.sql         # 3 consultas SQL de validação + teste de consulta
└── README.md                       
```

---

## Como rodar

Você pode executar o projeto de duas formas:
- **Opção 1** (Orquestração com Docker Compose): sobe banco, API e executa o ETL com um único comando, sem necessidade de configurar ambiente Python local.
- **Opção 2** (Manual): ideal para rodar cada serviço individualmente no terminal ou rodar a bateria de testes automatizados com o pytest.

---

### 1. Pré-requisitos gerais

- Docker Desktop instalado e em execução
- Python 3.10 ou superior
- Git

---

### 2. Preparação do repositório e variáveis de ambiente

Clone o repositório:

```bash
git clone https://github.com/alice-neumann/desafio-final-air.git
cd desafio-final-air
```

Copie o arquivo de exemplo `.env.example` para `.env` (este arquivo já está no `.gitignore` para nunca expor senhas no versionamento):

```bash
# Windows (PowerShell)
Copy-Item .env.example .env

# Linux / macOS
cp .env.example .env
```

Abra o arquivo `.env` gerado e defina a sua senha em `POSTGRES_PASSWORD`:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=defina_sua_senha_aqui
POSTGRES_DB=verdejar
```

---

### Opção 1: Execução com um único comando (Docker Compose)

Com o Docker Desktop rodando e o arquivo `.env` configurado, basta executar na raiz do projeto:

```bash
docker compose up --build
```

O Docker Compose irá automaticamente:
1. Ler as credenciais do arquivo `.env`;
2. Subir o PostgreSQL na porta `5433` e aplicar o `insumos/schema.sql`;
3. Construir e iniciar a API local em `http://127.0.0.1:8000`;
4. Aguardar o *healthcheck* de ambos os serviços responderem com sucesso;
5. Construir e executar o contêiner do ETL (`etl/main.py`), exibindo todas as mensagens e contadores diretamente no terminal. Os dados brutos ficam disponíveis em `./brutos` no seu computador (volume `./brutos:/app/brutos`).

Para testar a **idempotência** (executar o ETL uma segunda vez com os serviços já ligados):

```bash
docker compose run --rm etl
```

Para encerrar os serviços quando terminar:

```bash
docker compose down
```

---

### Opção 2: Execução manual (Passo a passo com venv)

#### 1. Criar e ativar o ambiente virtual

```bash
python -m venv .venv

# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Linux / macOS
source .venv/bin/activate
```


#### 2. Instalar as dependências

```bash
pip install -r requirements.txt
```

#### 3. Subir o banco de dados via Docker Compose

Inicie apenas o serviço do banco de dados em segundo plano (o Compose utiliza as variáveis do seu `.env` de forma protegida e aplica o `schema.sql` automaticamente):

```bash
docker compose up -d db
```

#### 4. Subir a API local

Em um terminal separado (com o `.venv` ativo), dentro da pasta `insumos/`:

```bash
cd insumos
python api_verdejar.py
```

Confirme que a API está no ar:

```bash
curl http://127.0.0.1:8000/saude
```

Resposta esperada: `{"status": "ok"}`

#### 5. Executar o ETL

No terminal principal, na raiz do projeto:

```bash
cd etl
python main.py
```

#### 6. Rodar os testes automatizados

Volte para a raiz do projeto (`cd ..`). Os testes de reconciliação comparam a origem com o banco e leem a pasta `brutos/`, então rode o ETL (passo 5) **antes**, com o banco ativo:

```bash
python -m pytest -v
```

Para rodar só os testes unitários de transformação (sem banco e sem ETL prévio):

```bash
python -m pytest tests/test_transformacao.py -v
```

---

## Caminho do banco e biblioteca de conexão

| Item | Escolha |
|---|---|
| Caminho do banco | B - PostgreSQL em contêiner Docker |
| Imagem | `postgres:16` |
| Porta (host → contêiner) | 5433 → 5432 |
| Biblioteca Python | `psycopg` v3 (`psycopg[binary]`) |

---

## Ver as tabelas no pgAdmin (opcional)

Com o banco no ar (`docker compose up -d db` ou `docker compose up --build`), é possível conferir as tabelas no pgAdmin instalado no computador:

1. No pgAdmin, clique com o botão direito em **Servers** e escolha **Register → Server...**.
2. Aba **General**: em *Name*, escreva um nome qualquer (por exemplo, `verdejar`).
3. Aba **Connection**, preenchendo com os valores do seu `.env`:
   | Campo no pgAdmin | Valor |
   |---|---|
   | Host name/address | `localhost` |
   | Port | `5433` |
   | Maintenance database | valor de `POSTGRES_DB` (`verdejar`) |
   | Username | valor de `POSTGRES_USER` (`postgres`) |
   | Password | valor de `POSTGRES_PASSWORD` |

4. Clique em **Save**.
5. As tabelas ficam em **Servers → verdejar → Databases → verdejar → Schemas → public → Tables**: `clientes`, `itens_pedido`, `pedidos` e `produtos`.

Observações:
- A porta é `5433` (a do Compose), e não a `5432`, que pode estar em uso por um PostgreSQL instalado localmente.
- As tabelas existem assim que o banco sobe (o `schema.sql` é aplicado na criação), mas só terão linhas depois de executar o ETL.

## Armadilhas tratadas (A1 a A6)

As seis armadilhas declaradas nos dados são tratadas em funções puras no módulo `etl/transformacao.py`. Cada função recebe um registro e devolve um registro tratado, o que permite testá-las isoladamente com o pytest.

| Código | Problema | Tratamento aplicado |
|---|---|---|
| A1 | E-mails ausentes em parte dos clientes | Cliente mantido, e-mail gravado como nulo (`None`) |
| A2 | Sigla do estado em caixa mista (`rs` e `RS`) | Padronizado para maiúsculas com `.strip().upper()` |
| A3 | Data do pedido em dois formatos (`AAAA-MM-DD` e `DD/MM/AAAA`) | Convertido para `date` com `datetime.strptime` |
| A4 | Valor total ora número, ora texto com vírgula decimal | Convertido para `Decimal` com duas casas decimais |
| A5 | Pedidos repetidos (mesmo id) entre páginas da API | Mantida apenas a primeira ocorrência via `set()` de ids |
| A6 | Valor total divergente da soma dos itens | Calculado `valor_itens` e marcado `divergente = True` se diferença > 0,01 |

---

## Estratégia de idempotência

A estratégia escolhida foi limpar todas as tabelas antes de cada carga (`TRUNCATE`), respeitando a ordem inversa das chaves estrangeiras:

```sql
TRUNCATE itens_pedido, pedidos, clientes, produtos
```

Isso garante que executar o ETL duas vezes seguidas produz exatamente as mesmas contagens no banco, sem duplicar dados e sem erros de chave primária.

### Evidência: saída de duas execuções seguidas

#### Primeira execução
```
extracao: clientes paginas=20 registros=1000
extracao: pedidos paginas=102 registros_brutos=5100
transformacao: pedidos_unicos=5000 repetidos_descartados=100
transformacao: emails_nulos=81 estados_padronizados=151 datas_convertidas=1037 valores_convertidos=1255
carga: clientes=1000 produtos=12 pedidos=5000 itens=12455
reconciliacao: soma_valor_itens_origem=311228.75 soma_valor_itens_destino=311228.75 diferenca=0.00
divergentes: 238 pedidos com valor_total diferente da soma dos itens
```

#### Segunda execução
```
extracao: clientes paginas=20 registros=1000
extracao: pedidos paginas=102 registros_brutos=5100
transformacao: pedidos_unicos=5000 repetidos_descartados=100
transformacao: emails_nulos=81 estados_padronizados=151 datas_convertidas=1037 valores_convertidos=1255
carga: clientes=1000 produtos=12 pedidos=5000 itens=12455
reconciliacao: soma_valor_itens_origem=311228.75 soma_valor_itens_destino=311228.75 diferenca=0.00
divergentes: 238 pedidos com valor_total diferente da soma dos itens
```

---

## Testes automatizados (pytest)

Os testes estão organizados em dois arquivos na pasta `tests/`:

### `test_transformacao.py` — 11 testes unitários

Testa cada armadilha (A1 a A6) com entradas conhecidas e saídas esperadas, sem depender do banco de dados:

| Teste | Armadilha | O que valida |
|---|---|---|
| `test_a1_email_valido_permanece` | A1 | E-mail válido não é alterado |
| `test_a1_email_vazio_ou_nulo_vira_none` | A1 | E-mail vazio, só espaços ou `None` vira `None` |
| `test_a2_estado_minusculo_vira_maiusculo` | A2 | `'rs'` e `' sp '` viram `'RS'` e `'SP'` |
| `test_a2_estado_maiusculo_permanece` | A2 | `'SC'` continua `'SC'` |
| `test_a3_data_formato_barra` | A3 | `'15/03/2026'` vira `date(2026, 3, 15)` |
| `test_a3_data_formato_iso` | A3 | `'2026-03-15'` vira `date(2026, 3, 15)` |
| `test_a4_valor_texto_com_virgula` | A4 | `'125,84'` vira `Decimal('125.84')` |
| `test_a4_valor_numerico_float` | A4 | `94.34` (float) vira `Decimal('94.34')` |
| `test_a5_pedidos` | A5 | Remove duplicados mantendo a primeira ocorrência e contando os descartados |
| `test_a6_pedido_sem_divergencia` | A6 | Pedido com soma correta marca `divergente = False` |
| `test_a6_pedido_com_divergencia` | A6 | Pedido com soma diferente marca `divergente = True` |

### `test_reconciliacao.py` — 2 testes de reconciliação

Compara os dados da origem (arquivos brutos tratados) com os dados gravados no PostgreSQL:

| Teste | O que valida |
|---|---|
| `test_reconciliacao_contagem_pedidos` | Quantidade de pedidos únicos da origem = `COUNT(*)` na tabela `pedidos` |
| `test_reconciliacao_soma_valores` | Soma de `valor_itens` da origem = `SUM(valor_itens)` no banco (tolerância de 0,01) |

### Saída do pytest

```
tests/test_reconciliacao.py::test_reconciliacao_contagem_pedidos PASSED                                     [  7%]
tests/test_reconciliacao.py::test_reconciliacao_soma_valores PASSED                                         [ 15%]
tests/test_transformacao.py::test_a1_email_valido_permanece PASSED                                          [ 23%]
tests/test_transformacao.py::test_a1_email_vazio_ou_nulo_vira_none PASSED                                   [ 30%]
tests/test_transformacao.py::test_a2_estado_minusculo_vira_maiusculo PASSED                                 [ 38%]
tests/test_transformacao.py::test_a2_estado_maiusculo_permanece PASSED                                      [ 46%]
tests/test_transformacao.py::test_a3_data_formato_barra PASSED                                              [ 53%]
tests/test_transformacao.py::test_a3_data_formato_iso PASSED                                                [ 61%]
tests/test_transformacao.py::test_a4_valor_texto_com_virgula PASSED                                         [ 69%]
tests/test_transformacao.py::test_a4_valor_numerico_float PASSED                                            [ 76%]
tests/test_transformacao.py::test_a5_pedidos PASSED                                                         [ 84%]
tests/test_transformacao.py::test_a6_pedido_sem_divergencia PASSED                                          [ 92%]
tests/test_transformacao.py::test_a6_pedido_com_divergencia PASSED                                          [100%]

============================================ 13 passed in 0.32s ==================================================
```

---

## Consultas SQL de validação

As três consultas obrigatórias estão no arquivo `consultas_validacao.sql`.

Decisões de definição:
- "Vendas" exclui pedidos cancelados (`status NOT ILIKE 'cancelado'`). Os cancelados continuam carregados no banco, o filtro fica só na consulta.
- O total soma `valor_itens` (a soma dos itens do pedido), e não `valor_total`. Nos pedidos divergentes os dois diferem.
- As consultas (b) e (c) não filtram por status: contam todos os pedidos (5000) e todos os divergentes (238), para bater com os contadores do ETL.

### (a) Total de vendas por mês

```
    mes	     qtd_vendas	 valor_total
"2026-01-01"	380	  24251.65
"2026-02-01"	429	  26798.74
"2026-03-01"	372	  23421.23
"2026-04-01"	415	  24706.39
"2026-05-01"	418	  24838.16
"2026-06-01"	413	  24897.33
"2026-07-01"	413	  26088.25
"2026-08-01"	374	  24271.32
"2026-09-01"	395	  24251.68
"2026-10-01"	375	  23937.57
```

### Teste de consulta: soma dos meses = soma geral

```
soma_dos_meses   soma_geral   bate
   247462.32	  247462.32   true
```

### Teste adicional: vendas + cancelados = soma geral de toda a tabela

O teste acima usa o mesmo filtro nos dois lados. Este fecha com a tabela inteira: a soma das vendas (sem cancelados) mais a soma dos cancelados deve ser igual à soma de `valor_itens` de todos os pedidos, que é o mesmo valor da reconciliação do ETL.

```
vendas        cancelados   soma_geral    bate
247462.32     63766.43     311228.75     true
```

### (b) Quantidade de pedidos por estado

```
estado    qtd_pedidos
 "RS"	      1543
 "SC"	      1127
 "PR"	       974
 "SP"	       880
 "MG"	       476
```

### (c) Pedidos divergentes

```
 id   cliente_id     data_pedido	 status	      valor_total    valor_itens    divergente	 diferenca
  1	 303	    "2026-02-19"        "entregue"	 125.84	       130.84	       true	    5.00
 51	  23	    "2026-04-27"       "cancelado"	  26.58	        23.58	       true	   -3.00
 71	 962	    "2026-05-27"       "cancelado"	 144.35	        34.35	       true	  -10.00
 81	 198	    "2026-09-05"        "entregue"	  -1.84	         3.16	       true	    5.00
106	 973	    "2026-05-02"   "em_transporte"        47.78	        44.78	       true	   -3.00

Total rows: 238
```

---

## Observações sobre os dados e os insumos

- **Pedido com valor_total negativo:** o pedido 81 tem `valor_total = -1.84` (a soma dos itens é 3.16). É o único caso nos dados e não é uma das armadilhas declaradas. O ETL não descarta o pedido, ele é carregado como veio e marcado como divergente.
- **Insumo alterado:** em `insumos/api_verdejar.py`, a API passou a escutar em `0.0.0.0` (antes `127.0.0.1`), para aceitar conexões da rede interna do Docker no Compose. Na execução manual isso também a expõe na rede local; os dados são sintéticos. O restante dos insumos (`schema.sql`, dados) não foi alterado.

---

## Stretch: Orquestração local com Docker Compose

Item de Stretch escolhido: **orquestração local com Docker**. O `docker-compose.yml` sobe o PostgreSQL, a API e o ETL com um único comando (`docker compose up --build`, descrito na Opção 1).

- `db`: PostgreSQL 16 na porta 5433; aplica o `insumos/schema.sql` na criação e tem *healthcheck* (`pg_isready`).
- `api`: imagem de `docker/Dockerfile.api`, porta 8000, com *healthcheck* em `/saude`.
- `etl`: imagem de `docker/Dockerfile.etl`; `depends_on` com `service_healthy` faz o ETL iniciar só com banco e API prontos, e os brutos são gravados em `./brutos`.

Idempotência pelo Compose: `docker compose run --rm etl` repete a carga e mantém as mesmas contagens.