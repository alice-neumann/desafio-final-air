# Como usei IA

## Sugestões aceitas                         

- Separar a requisição da paginação: mantive `buscar_pagina` para consultar uma página e tratar erros HTTP e de conexão, e `buscar_todas_as_paginas` para percorrer até `total_pages`. 
- Usar `datetime.strptime` para interpretar os dois formatos de data e `Decimal` para evitar erros de float em valores monetários.

## Sugestões rejeitadas

- Criar `brutos` manualmente antes de executar: não segui essa orientação porque a pasta deve ser criada pelo próprio script, não dependendo de uma preparação manual.

## Falhas e retrabalho

- Caminho inicial incorreto para `brutos`: a pasta estava sendo criada dentro de `etl`, em vez de na raiz do projeto. Corrigi o caminho para que o script localize a raiz automaticamente e crie a pasta no local esperado.