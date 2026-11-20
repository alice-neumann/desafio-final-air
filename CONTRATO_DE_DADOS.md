# Contrato de dados: ETL Verdejar

## Clientes
| Campo | Tipo | Nulo? | Regra de transformação |
|---|---|---|---|
| id | INTEGER | Não | Copiar como chave primária |
| nome | TEXT | Não | Copiar sem alteração |
| email | TEXT | Sim | Ausente ou vazio vira nulo, espaços nas pontas removidos, o cliente nunca é descartado (A1) |
| cidade | TEXT | Não | Copiar sem alteração |
| estado | CHAR(2) | Não |  Espaços nas pontas removidos, sempre em letras maiúsculas (A2) |
| cadastro_em | DATE | Não | Copiar sem alteração |

## Pedidos
Campo | Tipo | Nulo? | Regra de transformação |
|---|---|---|---|
| id | INTEGER | Não | Copiar como chave primária, remover pedidos repetidos (A5) |
| cliente_id | INTEGER | Não | Referenciar um registro existente em clientes (chave estrangeira) |
| data_pedido | DATE | Não | Converter AAAA-MM-DD ou DD/MM/AAAA para DATE (A3) |
| status | TEXT | Não | Copiar sem alteração |
| valor_total | NUMERIC(12,2) | Não | Substituir vírgula por ponto e converter para duas casas decimais (A4) |
| valor_itens | NUMERIC(12,2) | Não | Soma de quantidade x preco_unitario de cada item, com 2 casas (A6). Não existe na origem |
| divergente            | BOOLEAN     | Não    | Verdadeiro se \|valor_total − valor_itens\| > 0,01 (A6). Não existe na origem |

## Produtos
Campo | Tipo | Nulo? | Regra de transformação |
|---|---|---|---|
| produto_id | INTEGER | Não | Copiar como chave primária |
| nome | TEXT | Não | Copiar sem alteração |
| categoria | TEXT | Não | Copiar sem alteração |
| preco_base | NUMERIC(10,2) | Não | Copiar sem alteração |

## itens_pedido
Campo | Tipo | Nulo? | Regra de transformação |
|---|---|---|---|
| pedido_id | INTEGER | Não | Referenciar um registro existente em pedidos (chave estrangeira) |
| linha | INTEGER | Não | Gerar a posição do item no pedido, iniciada em 1 |
| produto_id | INTEGER | Não | Referenciar um registro existente em produtos |
| quantidade | INTEGER | Não | Copiar como inteiro |
| preco_unitario | NUMERIC(10,2) | Não | Converter para decimal com duas casas |
