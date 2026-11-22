# Contrato de dados: ETL Verdejar

Destino: PostgreSQL, conforme `insumos/schema.sql`. 
Origem: API (`/clientes`, `/pedidos`) e `insumos/dados/produtos.csv`.

## Clientes
| Campo | Tipo | Nulo? | Regra de transformação |
|---|---|---|---|
| id | INTEGER | Não | Copiar como chave primária |
| nome | TEXT | Não | Copiar sem alteração |
| email | TEXT | Sim | Ausente, nulo ou vazio vira nulo; espaços nas pontas removidos; o cliente nunca é descartado (A1) |
| cidade | TEXT | Não | Copiar sem alteração |
| estado | CHAR(2) | Não | Espaços nas pontas removidos e sempre em letras maiúsculas (A2) |
| cadastro_em | DATE | Não | Já vem em AAAA-MM-DD; copiado sem alteração no Python e convertido para DATE pelo PostgreSQL na carga |

## Produtos
| Campo | Tipo | Nulo? | Regra de transformação |
|---|---|---|---|
| produto_id | INTEGER | Não | Converter o texto do CSV para inteiro; chave primária |
| nome | TEXT | Não | Copiar sem alteração |
| categoria | TEXT | Não | Copiar sem alteração |
| preco_base | NUMERIC(10,2) | Não | Converter o texto do CSV (por exemplo, `3.5`) para decimal com duas casas |

## Pedidos
| Campo | Tipo | Nulo? | Regra de transformação |
|---|---|---|---|
| id | INTEGER | Não | Copiar como chave primária; pedidos repetidos são removidos, mantendo a primeira ocorrência (A5) |
| cliente_id | INTEGER | Não | Referenciar um registro existente em clientes (chave estrangeira) |
| data_pedido | DATE | Não | Converter AAAA-MM-DD ou DD/MM/AAAA para DATE (A3) |
| status | TEXT | Não | Copiar sem alteração (os pedidos cancelados também são carregados) |
| valor_total | NUMERIC(12,2) | Não | Se vier como texto, trocar a vírgula por ponto; converter para decimal com duas casas (A4) |
| valor_itens | NUMERIC(12,2) | Não | Soma de quantidade x preco_unitario de cada item, com duas casas (A6). Não existe na origem |
| divergente | BOOLEAN | Não | Verdadeiro se \|valor_total − valor_itens\| > 0,01 (A6). Não existe na origem |

## itens_pedido
| Campo | Tipo | Nulo? | Regra de transformação |
|---|---|---|---|
| pedido_id | INTEGER | Não | Referenciar um registro existente em pedidos (chave estrangeira) |
| linha | INTEGER | Não | Gerar a posição do item no pedido, iniciada em 1. Não existe na origem |
| produto_id | INTEGER | Não | Referenciar um registro existente em produtos |
| quantidade | INTEGER | Não | Copiar como inteiro |
| preco_unitario | NUMERIC(10,2) | Não | Converter para decimal com duas casas |
