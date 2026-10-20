# Pilha tecnológica

## Decisões obrigatórias
- **Python 3.11+**, com ambiente virtual (`.venv`) e dependências em `requirements.txt`.
- **fastmcp** para implementar o servidor e expor as tools.
- **SQLite** (módulo `sqlite3` da biblioteca padrão) para persistir os chamados.
- Na inicialização, criar a tabela `chamados` conforme o modelo abaixo somente se ela não existir. Bancos preexistentes com esquema diferente não são validados nem migrados.
- Semear **registros fictícios** na inicialização somente quando a tabela `chamados` estiver vazia. Não apagar nem sobrescrever registros existentes; se todos forem apagados, a próxima inicialização semeia novamente.
- Execução local, com transporte MCP **stdio**.
- O caminho do banco é configurado pela variável de ambiente `HELPDESK_DB_PATH`; sem ela, usar `helpdesk.db` na raiz do projeto.
- Os status permitidos são exatamente `aberto`, `em_andamento` e `fechado`, sensíveis a maiúsculas e minúsculas.
- Erros de validação e de entidade inexistente que sejam definidos como falha de uma tool devem ser levantados como `ToolError` do FastMCP, com mensagem clara; não retornar objeto de erro como resultado normal. Consultas sem resultados retornam `[]` quando especificado no contrato da tool.

## Modelo de dados
Tabela `chamados`:

| Campo | Tipo | Observação |
|-------|------|------------|
| `id` | INTEGER PK AUTOINCREMENT | Identifica o chamado |
| `cliente_id` | INTEGER NOT NULL | Identifica o cliente |
| `cliente_nome` | TEXT NOT NULL | Nome do cliente |
| `descricao` | TEXT NOT NULL | Descrição do problema |
| `status` | TEXT NOT NULL | Um dos status permitidos: `aberto`, `em_andamento`, `fechado` |
| `criado_em` | TEXT NOT NULL | Data/hora ISO 8601 com fuso horário |
| `atualizado_em` | TEXT NOT NULL | Data/hora ISO 8601 com fuso horário |

Os status são valores exatos, sem normalização de maiúsculas/minúsculas. A tabela criada pela aplicação restringe `status` a esses valores. Essa restrição não é aplicada retroativamente a uma tabela preexistente.

O histórico de um cliente é obtido consultando `chamados` por `cliente_id`,
ordenado por `criado_em` crescente e, em caso de empate, por `id` crescente.
Timestamps gerados pela aplicação usam UTC e formato ISO 8601 com fuso horário.

Não existe tabela separada de clientes neste exemplo. A busca de histórico usa
os `cliente_id` registrados em `chamados`; para um `cliente_id` inexistente ou
sem chamados, retorna uma lista vazia (`[]`), sem erro.

A atualização de status altera somente `status` e `atualizado_em`. Os campos
`id`, `cliente_id`, `cliente_nome`, `descricao` e `criado_em` são preservados.
Este exemplo não mantém histórico ou auditoria das mudanças de status.
Na tool de atualização, status inválido ou chamado inexistente levanta `ToolError`
do FastMCP, com mensagem clara; nesses casos, o registro permanece inalterado.

## Restrições
- Evitar `print()` em stdout no servidor (stdout é usado pelo protocolo stdio).
- Testes automatizados com `pytest`.
- Sem chaves de API ou dados sensíveis no repositório.
