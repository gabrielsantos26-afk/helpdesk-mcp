# Planejamento: buscar histórico de cliente

Executar as tarefas na ordem abaixo. O escopo limita-se à Fase 2; não implementar `atualizar_status` nem outras operações de escrita.

1. **Preparar o teste e a persistência de referência**
   - Reutilizar o banco SQLite e a variável de ambiente `HELPDESK_DB_PATH` da Fase 1.
   - Preparar fixtures com banco temporário e chamados de mais de um cliente, incluindo vários chamados para um mesmo cliente e timestamps empatados.
   - Não criar tabela de clientes.

2. **Definir e validar a entrada**
   - Implementar a tool `buscar_historico_cliente` com `cliente_id` obrigatório e inteiro.
   - Entradas inválidas: `cliente_id` ausente, `null`, booleano, número fracionário ou texto, inclusive texto numérico como `"2"`; todos esses casos levantam `ToolError` do `fastmcp` com mensagem clara.
   - Decisão sobre coerção: não aceitar conversão automática do `fastmcp`; validar estritamente o valor original na tool, de modo que `"2"` continue sendo texto e gere `ToolError`.
   - Cobrir com teste explícito o texto numérico `"2"` e testar os inteiros negativo e zero.
   - `cliente_id` inteiro negativo ou zero é válido e retorna exatamente `[]`, sem erro; como não há tabela separada de clientes, qualquer outro `cliente_id` sem chamados, inclusive inexistente, também retorna exatamente `[]`, sem erro.

3. **Implementar a consulta somente de leitura**
   - Consultar `chamados` por `cliente_id` usando parâmetro SQL vinculado.
   - Retornar os mesmos sete campos definidos para `listar_chamados`.
   - Ordenar por `criado_em` crescente e `id` crescente para desempatar.
   - Não alterar dados nem semear registros durante a consulta.

4. **Registrar e integrar a tool MCP**
   - Registrar `buscar_historico_cliente` no servidor stdio existente.
   - Conferir descoberta e chamadas via cliente MCP para cliente com resultados, sem resultados e entrada inválida.
   - Preservar integralmente a tool e os contratos da Fase 1.

5. **Adicionar testes automatizados**
   - Testar cliente com vários chamados, exclusão de chamados de outros clientes, campos e ordenação determinística.
   - Automatizar o caso único de ausência de chamados definido na Tarefa 2, incluindo inteiros negativo, zero e cliente inexistente.
   - Testar todos os casos inválidos definidos na Tarefa 2, incluindo explicitamente o texto numérico `"2"`.
   - Testar confirmação de ausência de mutações.
   - Testar descoberta e chamadas da nova tool por integração MCP.
   - Rodar também todos os testes de regressão da Fase 1, sem enfraquecer ou remover cobertura existente.

6. **Atualizar documentação e validação**
   - Atualizar README e configuração MCP somente se forem necessários para a nova tool; manter o transporte stdio e os comandos já estabelecidos.
   - Executar `pytest` para a suíte completa e corrigir falhas relacionadas à Fase 2.
   - Realizar os cenários manuais definidos em `validacao.md` e conferir no cliente que a tool foi efetivamente chamada.
