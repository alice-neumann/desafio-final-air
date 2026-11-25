-- (a) Total de vendas por mês
SELECT 
	DATE_TRUNC('month', data_pedido)::DATE AS mes, 
	COUNT(*) AS qtd_vendas,
	SUM(valor_itens) AS valor_total
FROM pedidos
WHERE status NOT ILIKE 'cancelado'
GROUP BY mes
ORDER BY mes;

-- (a) Teste da consulta: a soma dos meses deve bater com a soma geral da tabela
WITH por_mes AS (
    SELECT 
		DATE_TRUNC('month', data_pedido)::DATE AS mes,
        SUM(valor_itens) AS total_mes
    FROM pedidos
    WHERE status NOT ILIKE 'cancelado'
    GROUP BY mes
)
SELECT (SELECT SUM(total_mes) FROM por_mes) AS soma_dos_meses,
       (SELECT SUM(valor_itens) FROM pedidos WHERE status NOT ILIKE 'cancelado') AS soma_geral,
       (SELECT SUM(total_mes) FROM por_mes) =
       (SELECT SUM(valor_itens) FROM pedidos WHERE status NOT ILIKE 'cancelado') AS bate;

-- (b) Quantidade de pedidos por estado
SELECT 
	c.estado, COUNT(*) AS qtd_pedidos
FROM clientes AS c
JOIN pedidos AS p ON c.id = p.cliente_id
GROUP BY c.estado
ORDER BY qtd_pedidos DESC;

-- (c) Pedidos divergentes
SELECT *, (valor_itens - valor_total) AS diferenca
FROM pedidos 
WHERE divergente = TRUE
ORDER BY id;














