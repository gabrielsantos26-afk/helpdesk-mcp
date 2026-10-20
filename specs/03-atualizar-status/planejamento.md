# Planejamento: atualizar status

Executar as tarefas na ordem abaixo. O escopo limita-se à Fase 3; não implementar criação/exclusão de chamados, histórico de status ou outras funcionalidades.

1. **Preparar fixtures e estado inicial**
   - Reutilizar SQLite e `HELPDESK_DB_PATH` das fases anteriores.
   - Preparar fixtures em banco temporário com chamado existente e registros para comprovar preservação de campos.
   - Capturar valores originais antes da atualização para comparação.

2. **Validar entradas e localizar o chamado**
   - Implementar `atualizar_status` com `chamado_id` inteiro obrigatório e `novo_status` obrigatório.
   - Aceitar somente `aberto`, `em_andamento` e `fechado`, sem normalização.
   - Levantar `ToolError` claro para ID inválido, status ausente/inválido ou chamado inexistente; não fazer update em nenhum desses casos.

3. **Implementar a atualização transacional**
   - Atualizar somente `status` e `atualizado_em` do registro identificado.
   - Gerar `atualizado_em` em UTC e ISO 8601 com fuso horário.
   - Executar a mudança em transação e verificar existência pelo resultado da atualização.
   - Retornar o registro completo atualizado com os sete campos do modelo; não criar histórico de status.

4. **Registrar e testar a tool MCP**
   - Expor a tool no servidor stdio existente.
   - Adicionar teste MCP para descoberta, chamada bem-sucedida, persistência e erros.
   - Confirmar que as tools das Fases 1 e 2 mantêm seus nomes, argumentos e resultados.

5. **Adicionar testes automatizados**
   - Testar atualização para os três status, resposta completa e persistência após nova consulta.
   - Comparar snapshots para garantir que apenas `status` e `atualizado_em` mudem.
   - Testar que o timestamp retornado é ISO 8601 com fuso UTC.
   - Testar status inválido, ID inválido e chamado inexistente com `ToolError` e sem mutação.
   - Executar integralmente os testes de regressão das Fases 1 e 2.

6. **Atualizar documentação e validar a fase**
   - Atualizar README com a terceira tool e exemplos de uso.
   - Rodar `python -m pytest` e corrigir falhas da fase.
   - Realizar os cenários manuais definidos em `validacao.md` no Copilot Chat e confirmar chamadas reais à tool.
