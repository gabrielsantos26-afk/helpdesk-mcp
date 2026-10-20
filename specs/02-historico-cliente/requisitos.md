# Requisitos: buscar histórico de cliente

## Objetivo

Disponibilizar a tool MCP `buscar_historico_cliente` para consultar os chamados associados a um cliente, usando a tabela `chamados` existente. Esta operação é somente de leitura.

## Entrada

- `cliente_id` (obrigatório): identificador inteiro do cliente.
- A tool não recebe SQL, nome de tabela, caminho de banco ou outros parâmetros.

## Saída e comportamento

- Retorna uma lista de chamados com os mesmos campos de `listar_chamados`: `id`, `cliente_id`, `cliente_nome`, `descricao`, `status`, `criado_em` e `atualizado_em`.
- Inclui exclusivamente chamados cujo `cliente_id` seja igual ao parâmetro fornecido.
- Ordena de forma determinística por `criado_em` crescente e, em caso de empate, por `id` crescente.
- `cliente_id` inteiro negativo ou zero é válido e retorna exatamente `[]`, sem erro; como não há tabela separada de clientes, qualquer outro `cliente_id` sem chamados, inclusive inexistente, também retorna exatamente `[]`, sem erro.
- Entradas inválidas: `cliente_id` ausente, `null`, booleano, número fracionário ou texto, inclusive texto numérico como `"2"`; todos esses casos levantam `ToolError` do `fastmcp` com mensagem clara.
- Decisão sobre coerção: não aceitar conversão automática do `fastmcp`; validar estritamente o valor original na tool, de modo que `"2"` continue sendo texto e gere `ToolError`.
- A tool não retorna objeto de erro como resultado normal.
- Não altera, cria nem exclui registros.

## Dependências e limites

- Reutiliza a tabela `chamados` e o modelo definidos em `specs/pilha-tecnologia.md`; não cria tabela de clientes nem expande o esquema.
- Não implementa atualização de chamados, que pertence à Fase 3.

## Casos relevantes

- Cliente com vários chamados recebe todos e somente os seus chamados.
- `cliente_id` inteiro negativo ou zero é válido e retorna exatamente `[]`, sem erro; como não há tabela separada de clientes, qualquer outro `cliente_id` sem chamados, inclusive inexistente, também retorna exatamente `[]`, sem erro.
- Prever um teste explícito para o texto numérico `"2"` e um teste para inteiros negativo e zero.
- Empate em `criado_em` é resolvido por `id` crescente.
- A operação não modifica o conteúdo do banco.
