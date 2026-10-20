# Requisitos: atualizar status

## Objetivo

Disponibilizar a tool MCP `atualizar_status` para alterar o status de um chamado existente no SQLite. Esta é a única operação de escrita desta fase.

## Entradas

- `chamado_id` (obrigatório): identificador inteiro do chamado.
- `novo_status` (obrigatório): um destes valores exatos, sensíveis a maiúsculas/minúsculas: `aberto`, `em_andamento` ou `fechado`.
- Não aceitar argumentos adicionais nem receber SQL ou caminho do banco pela tool.

## Saída e comportamento

- Para um chamado existente e um status válido, persiste o novo status e atualiza `atualizado_em` para o horário corrente em UTC, no formato ISO 8601 com fuso horário.
- Retorna o chamado atualizado com os mesmos campos das tools de consulta: `id`, `cliente_id`, `cliente_nome`, `descricao`, `status`, `criado_em` e `atualizado_em`.
- Altera exclusivamente `status` e `atualizado_em`. Preserva `id`, `cliente_id`, `cliente_nome`, `descricao` e `criado_em`.
- Não cria, remove nem mantém histórico/auditoria de mudanças de status.
- `chamado_id` inválido e `novo_status` ausente, nulo ou inválido levantam `ToolError` do `fastmcp`, com mensagem clara. Chamado inexistente também levanta `ToolError`. Não retornar objeto de erro como resultado normal.
- Em qualquer erro, não alterar o registro.

## Dependências e limites

- Reutiliza o esquema e o caminho de banco SQLite definidos na Constituição.
- Não altera cliente ou descrição e não adiciona tabela ou coluna.
- Preserva as tools `listar_chamados` e `buscar_historico_cliente`.

## Casos relevantes

- Atualizar chamado existente para cada status permitido e receber o registro atualizado.
- Confirmar persistência em consulta subsequente.
- Confirmar que apenas `status` e `atualizado_em` mudaram, e que o timestamp está em UTC/ISO 8601 com fuso.
- Rejeitar status inválido, incluindo capitalização diferente, com `ToolError` e sem mutação.
- Rejeitar chamado inexistente com `ToolError` e sem mutação.
- Rejeitar `chamado_id` inválido com `ToolError` e sem mutação.
