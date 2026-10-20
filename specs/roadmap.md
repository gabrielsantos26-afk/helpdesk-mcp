# Roadmap

Cada fase é desenvolvida em uma branch própria (`feature/NN-...`), com
requisitos, planejamento e validação em `specs/NN-.../`.

## Fase 1: Listar chamados
- **Tool:** `listar_chamados`, com filtro opcional por status.
- **Objetivo:** permitir consultar todos os chamados ou apenas os de um status.
- **Conclusão:** a tool aparece no cliente MCP; sem filtro retorna todos os
  chamados, e com filtro retorna somente os chamados do status exato. Os itens
  incluem os campos definidos no modelo e são ordenados por `criado_em` e `id`.
  Status inválido levanta `ToolError`; consultas sem resultados retornam `[]`.
  Inicialização, preservação/semeadura e chamadas MCP estão cobertas por testes,
  e os três cenários manuais de `specs/01-listar-chamados/validacao.md` foram
  conferidos.
- **Status:** concluída

## Fase 2: Buscar histórico de cliente
- **Tool:** `buscar_historico_cliente`.
- **Objetivo:** consultar todos os chamados de um cliente.
- **Contrato a implementar:** recebe `cliente_id` obrigatório; retorna uma lista
  dos chamados desse cliente, com os campos do modelo, ordenada por `criado_em`
  crescente e `id` crescente em caso de empate. Cliente inexistente ou sem
  chamados retorna `[]`; não há tabela separada de clientes, e a consulta não
  modifica dados.
- **Conclusão:** a tool é descoberta e chamada via MCP; testes cobrem cliente
  com vários chamados, ordenação, cliente sem histórico (`[]`), campos de saída
  e ausência de mutações. A Fase 1 continua passando, e os três cenários manuais
  de listagem continuam válidos.
- **Status:** concluída

## Fase 3: Atualizar status
- **Tool:** `atualizar_status`.
- **Objetivo:** alterar o status de um chamado existente.
- **Contrato a implementar:** recebe o identificador do chamado e um status
  permitido (`aberto`, `em_andamento` ou `fechado`). Em sucesso, persiste o novo
  status e atualiza `atualizado_em` em UTC no formato ISO 8601 com fuso horário;
  retorna o chamado atualizado. A
  atualização altera somente `status` e `atualizado_em`, preservando `id`,
  `cliente_id`, `cliente_nome`, `descricao` e `criado_em`; não mantém histórico
  de status. Status inválido ou chamado inexistente levanta `ToolError` claro e
  não altera o registro.
- **Conclusão:** testes verificam sucesso, persistência após nova consulta,
  atualização do timestamp, status inválido, chamado inexistente e ausência de
  mutação nos casos de erro. A tool é descoberta/chamada via MCP, as Fases 1 e 2
  continuam passando e os cenários manuais anteriores permanecem válidos.
- **Status:** concluída
