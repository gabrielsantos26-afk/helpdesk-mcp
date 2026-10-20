# Requisitos: listar chamados

## Objetivo

Disponibilizar, pela tool MCP `listar_chamados`, a consulta de todos os chamados persistidos no SQLite ou somente dos chamados de um status escolhido. A operação é somente de leitura.

## Status aceitos

O filtro `status` aceita exclusivamente estes valores, escritos exatamente assim:

- `aberto`
- `em_andamento`
- `fechado`

A comparação é sensível a maiúsculas/minúsculas e não deve normalizar nem aceitar valores alternativos. Se o parâmetro for omitido ou `null`, a consulta não filtra por status. Uma string vazia ou qualquer outro valor é inválido e deve levantar `ToolError` do `fastmcp`, com uma mensagem que liste os status aceitos. Esse erro não deve ser convertido em um retorno normal como `{"erro": ...}` nem executar uma consulta como se o filtro tivesse sido omitido.

## Entradas

- `status` (opcional): um dos status aceitos. Quando ausente ou `null`, lista chamados de todos os status.
- A tool não recebe SQL, nome de tabela, caminho de banco nem outros parâmetros.

## Saídas e comportamento

- Retorna uma lista de chamados, com cada item contendo `id`, `cliente_id`, `cliente_nome`, `descricao`, `status`, `criado_em` e `atualizado_em`, conforme o modelo definido em `pilha-tecnologia.md`.
- Sem filtro, inclui todos os registros existentes. Com filtro válido, inclui somente registros cujo status corresponda exatamente ao filtro.
- Ordena o resultado de forma determinística por `criado_em` crescente e, em caso de empate, por `id` crescente.
- Quando não houver chamados (com ou sem filtro), retorna uma lista vazia (`[]`), não `null`, não uma mensagem textual e não um erro.
- Para status inválido, levanta `ToolError` do `fastmcp`, com mensagem que indique os valores permitidos. Não modifica o banco e não retorna um objeto de erro como resultado normal.
- A tool não cria, atualiza ou exclui chamados.

## Inicialização do banco e dados fictícios

- Na inicialização do servidor, criar o arquivo do banco, se necessário, e garantir que a tabela `chamados` exista com as colunas e restrições do modelo de dados da Constituição.
- Inserir registros fictícios somente se a tabela `chamados` estiver vazia após a criação/verificação do esquema. Isso cobre tanto um banco recém-criado quanto um banco existente sem registros.
- Se já houver ao menos um registro, não inserir dados fictícios nem apagar ou alterar registros existentes.
- A regra depende do estado atual da tabela: se todos os chamados forem apagados, a próxima inicialização do servidor encontrará a tabela vazia e recriará os dados fictícios. A consulta não dispara semeadura; enquanto a tabela estiver vazia, retorna `[]`.
- Os exemplos devem ser inteiramente fictícios, incluir os três status permitidos e permitir testar listagem geral e filtrada. Não usar dados pessoais ou segredos reais.
- A inicialização e as tools não devem escrever mensagens comuns em `stdout`, reservado ao transporte MCP stdio.

## Casos relevantes

- Listar sem parâmetro e receber chamados de todos os status.
- Listar com cada status permitido e receber somente correspondências.
- Listar com status válido sem correspondências e receber `[]`.
- Listar quando a tabela está vazia e receber `[]`; após apagar todos os chamados e reinicializar o servidor, confirmar que os dados fictícios são recriados.
- Rejeitar status desconhecido, com capitalização diferente ou string vazia por meio de `ToolError` do `fastmcp`, com mensagem que lista os status aceitos.
- Inicializar banco novo e criar esquema e exemplos fictícios.
- Inicializar banco já preenchido e preservar exatamente seus registros, sem semear exemplos.
- Chamar a tool e confirmar que nenhum dado foi alterado.
