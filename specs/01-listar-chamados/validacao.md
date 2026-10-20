# Validação: listar chamados

A Fase 1 está concluída quando todos os critérios abaixo forem verificados. Automatizar os casos de comportamento com `pytest`; usar um teste de integração MCP para comprovar a descoberta e a chamada da tool.

## Contrato da tool

- [ ] O cliente MCP lista a tool com o nome exato `listar_chamados`.
- [ ] A chamada sem filtro retorna uma lista com todos os chamados do SQLite e os campos `id`, `cliente_id`, `cliente_nome`, `descricao`, `status`, `criado_em` e `atualizado_em`.
- [ ] A chamada com `aberto`, `em_andamento` ou `fechado` retorna exclusivamente chamados com o status correspondente.
- [ ] Resultados são ordenados por `criado_em` crescente e depois `id` crescente.
- [ ] Um status desconhecido, com capitalização diferente ou vazio levanta `ToolError` do `fastmcp`, com erro de validação claro que informa os status aceitos; não retorna um objeto normal como `{"erro": ...}`.
- [ ] Uma consulta sem correspondências retorna exatamente uma lista vazia (`[]`), sem erro.
- [ ] Uma consulta não altera, cria nem exclui registros.

## Inicialização e persistência

- [ ] Com banco inexistente, a inicialização cria o banco e a tabela `chamados`, e semeia exemplos fictícios que cobrem os três status.
- [ ] Com banco existente e tabela vazia, a inicialização semeia os exemplos fictícios.
- [ ] Com banco já preenchido, a inicialização preserva os registros existentes e não acrescenta exemplos.
- [ ] Executar a inicialização repetidamente não duplica registros nem apaga alterações existentes.
- [ ] Se todos os chamados forem apagados, a tool retorna `[]` até o servidor ser reinicializado; na próxima inicialização, a tabela vazia é semeada novamente com dados fictícios.
- [ ] O servidor não envia mensagens comuns para `stdout`, mantendo-o disponível para o protocolo MCP stdio.

## Validação manual no Copilot Chat

- [ ] No Copilot Chat, pedir: **"Liste todos os chamados"**. Conferir que a interface mostra a chamada à tool `listar_chamados` e que o resultado corresponde aos registros existentes no banco.
- [ ] No Copilot Chat, pedir: **"Quais chamados estão abertos?"**. Conferir que a tool `listar_chamados` foi chamada com `status` igual a `aberto` e que o resultado contém somente chamados abertos.
- [ ] No Copilot Chat, pedir: **"Liste os chamados com um status que não existe"**. Conferir que a tool `listar_chamados` foi realmente chamada, que exibe o erro de validação com os status aceitos e que o cliente não apresenta uma lista ou resposta inventada como se a consulta tivesse funcionado.
- [ ] Em todos os cenários, verificar explicitamente o registro/visualização da chamada à tool; uma resposta textual do modelo sem chamada MCP não satisfaz a validação.

## Comandos e evidências

- Rodar `pytest` e confirmar que todos os testes da Fase 1 passam.
- Iniciar o servidor pelo transporte stdio em um teste de integração e confirmar descoberta e chamada da tool, sem texto estranho no canal de protocolo.
- Executar os três cenários da seção **Validação manual no Copilot Chat**, confirmando que a tool foi chamada em cada cenário.
- Verificar que os testes de inicialização usam bancos temporários isolados e que o teste de preservação compara os registros antes e depois da inicialização.
