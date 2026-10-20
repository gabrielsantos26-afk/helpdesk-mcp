# Roadmap

Cada fase é desenvolvida em uma branch própria (`feature/NN-...`), com
requisitos, planejamento e validação em `specs/NN-.../`.

## Fase 1: Listar chamados
- **Tool:** `listar_chamados`, com filtro opcional por status.
- **Objetivo:** permitir consultar todos os chamados ou apenas os de um status.
- **Conclusão:** a tool aparece no cliente MCP, retorna os dados corretos do
  SQLite, trata status inválido e ausência de resultados, e os testes passam.
- **Status:** pendente

## Fase 2: Buscar histórico de cliente
- **Tool:** `buscar_historico_cliente`.
- **Objetivo:** consultar todos os chamados de um cliente.
- **Conclusão:** retorna o histórico correto para clientes com vários chamados,
  trata cliente inexistente, preserva a Fase 1, e os testes passam.
- **Status:** pendente

## Fase 3: Atualizar status
- **Tool:** `atualizar_status`.
- **Objetivo:** alterar o status de um chamado existente.
- **Conclusão:** valida status e chamado inexistente, persiste a mudança no
  SQLite, preserva as Fases 1 e 2, e os testes passam.
- **Status:** pendente
