# Validação: buscar histórico de cliente

A Fase 2 está concluída quando os critérios abaixo forem verificados. Automatizar os casos de comportamento com `pytest`, incluindo testes de regressão da Fase 1; usar integração MCP para confirmar descoberta, argumentos, resultados e erros da tool.

## Contrato da tool

- [ ] O cliente MCP lista a tool com o nome exato `buscar_historico_cliente`.
- [ ] Entradas inválidas: `cliente_id` ausente, `null`, booleano, número fracionário ou texto, inclusive texto numérico como `"2"`; todos esses casos levantam `ToolError` do `fastmcp` com mensagem clara.
- [ ] Decisão sobre coerção: não aceitar conversão automática do `fastmcp`; validar estritamente o valor original na tool, de modo que `"2"` continue sendo texto e gere `ToolError`.
- [ ] Uma chamada válida retorna uma lista de chamados contendo exatamente os campos `id`, `cliente_id`, `cliente_nome`, `descricao`, `status`, `criado_em` e `atualizado_em`.
- [ ] Todos os itens retornados têm `cliente_id` igual ao valor solicitado; chamados de outros clientes não aparecem.
- [ ] Resultados são ordenados por `criado_em` crescente e depois `id` crescente.
- [ ] `cliente_id` inteiro negativo ou zero é válido e retorna exatamente `[]`, sem erro; como não há tabela separada de clientes, qualquer outro `cliente_id` sem chamados, inclusive inexistente, também retorna exatamente `[]`, sem erro.
- [ ] A consulta não altera, cria nem exclui registros.

## Testes automatizados e integração MCP

- [ ] `pytest` cobre cliente com vários chamados e confirma que todos e somente os chamados daquele cliente são retornados.
- [ ] Os testes cobrem campos de saída e ordenação determinística, inclusive empate em `criado_em`.
- [ ] `pytest` inclui um teste explícito em que o texto numérico `"2"` levanta `ToolError`.
- [ ] `pytest` inclui testes para `cliente_id` inteiro negativo e zero, confirmando que são válidos e retornam `[]` sem erro.
- [ ] `cliente_id` inteiro negativo ou zero é válido e retorna exatamente `[]`, sem erro; como não há tabela separada de clientes, qualquer outro `cliente_id` sem chamados, inclusive inexistente, também retorna exatamente `[]`, sem erro.
- [ ] Os testes cobrem cada categoria de entrada inválida especificada e confirmam `ToolError`.
- [ ] Os testes comparam os registros antes e depois da consulta para confirmar ausência de mutações.
- [ ] Um teste de integração MCP confirma a descoberta da tool e chamadas válidas, vazias e inválidas pelo cliente.
- [ ] Todos os testes de regressão da Fase 1 continuam passando.

## Validação manual no Copilot Chat

- [ ] Preparar ou identificar um cliente com vários chamados. Pedir no Copilot Chat: **"Mostre o histórico do cliente <cliente_id>"**. Conferir que `buscar_historico_cliente` foi realmente chamada com o `cliente_id` esperado e que o resultado corresponde aos registros desse cliente no SQLite, sem chamados de outros clientes.
- [ ] Pedir no Copilot Chat o histórico de um `cliente_id` sem chamados (incluindo um identificador inexistente). Conferir que `buscar_historico_cliente` foi realmente chamada com o identificador solicitado e retorna `[]`, sem erro ou chamados inventados.
- [ ] Em ambos os cenários, conferir a visualização/registro da chamada MCP; uma resposta textual sem chamada da tool não satisfaz a validação.

## Regressão e evidências

- Rodar `python -m pytest` a partir da raiz e confirmar que toda a suíte passa.
- Confirmar que os testes da Fase 1 continuam cobrindo listagem, filtros, validação, inicialização e preservação dos registros.
- Confirmar manualmente no Copilot Chat os dois cenários desta especificação e a chamada real da tool em cada um.
