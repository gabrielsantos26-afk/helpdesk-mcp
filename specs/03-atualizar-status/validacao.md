# Validação: atualizar status

A Fase 3 está concluída quando os critérios abaixo forem verificados. Automatizar os comportamentos com `pytest`, incluindo regressão das Fases 1 e 2; usar integração MCP para descoberta, chamadas, persistência e erros.

## Contrato da tool

- [ ] O cliente MCP lista a tool com o nome exato `atualizar_status`.
- [ ] A chamada com `chamado_id` inteiro existente e `novo_status` permitido atualiza o registro e retorna os sete campos `id`, `cliente_id`, `cliente_nome`, `descricao`, `status`, `criado_em` e `atualizado_em`.
- [ ] São aceitos somente os status exatos `aberto`, `em_andamento` e `fechado`.
- [ ] O novo status é persistido e permanece visível em consulta posterior.
- [ ] O snapshot antes/depois confirma que somente `status` e `atualizado_em` mudaram; `id`, `cliente_id`, `cliente_nome`, `descricao` e `criado_em` permanecem iguais.
- [ ] `atualizado_em` contém timestamp UTC em formato ISO 8601 com fuso horário.
- [ ] Status inválido ou ausente, `chamado_id` inválido ou chamado inexistente levanta `ToolError` claro; não retorna objeto de erro como resposta normal e não altera o banco.

## Testes automatizados e integração MCP

- [ ] `pytest` cobre os três status permitidos e valida conteúdo completo da resposta.
- [ ] Testes verificam persistência por nova leitura e preservação dos outros campos.
- [ ] Testes verificam parsing do timestamp e fuso UTC.
- [ ] Testes cobrem status ausente/inválido, ID inválido e chamado inexistente, confirmando `ToolError` e ausência de mutação.
- [ ] Integração MCP confirma descoberta e execução da tool, resposta de sucesso e erros de validação/entidade.
- [ ] Todas as verificações das Fases 1 e 2 continuam passando.

## Validação manual no Copilot Chat

- [ ] Solicitar a atualização de um chamado existente para outro status permitido. Conferir a chamada real de `atualizar_status`, os argumentos enviados e o registro retornado com o novo status.
- [ ] Consultar novamente o mesmo chamado por `listar_chamados` e/ou `buscar_historico_cliente`; confirmar que o status persistiu e os demais campos não mudaram.
- [ ] Solicitar atualização de um chamado inexistente e atualização com status que não existe. Conferir que a tool foi chamada, cada tentativa mostra `ToolError` e nenhum sucesso ou dado é inventado.
- [ ] Confirmar explicitamente a chamada MCP no cliente em cada cenário.

## Regressão e evidências

- Rodar `python -m pytest` a partir da raiz e confirmar que toda a suíte passa.
- Confirmar regressão automatizada das tools `listar_chamados` e `buscar_historico_cliente`.
- Realizar os cenários manuais desta seção e conferir chamada real e persistência visível nas tools de consulta.
