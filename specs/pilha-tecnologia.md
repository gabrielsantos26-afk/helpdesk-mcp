# Pilha tecnológica

## Decisões obrigatórias
- **Python 3.11+**, com ambiente virtual (`.venv`) e dependências em `requirements.txt`.
- **fastmcp** para implementar o servidor e expor as tools.
- **SQLite** (módulo `sqlite3` da biblioteca padrão) para persistir os chamados.
- Criação automática do banco e de **registros fictícios** na inicialização,
  somente se o banco ainda não existir ou estiver vazio (sem apagar alterações).
- Execução local, com transporte MCP **stdio**.

## Modelo de dados (proposta)
Tabela `chamados`:

| Campo | Tipo | Observação |
|-------|------|------------|
| `id` | INTEGER PK AUTOINCREMENT | Identifica o chamado |
| `cliente_id` | INTEGER NOT NULL | Identifica o cliente |
| `cliente_nome` | TEXT NOT NULL | Nome do cliente |
| `descricao` | TEXT NOT NULL | Descrição do problema |
| `status` | TEXT NOT NULL | Um dos status permitidos |
| `criado_em` | TEXT NOT NULL | Data/hora ISO 8601 |
| `atualizado_em` | TEXT NOT NULL | Data/hora ISO 8601 |

Status permitidos (proposta): `aberto`, `em_andamento`, `fechado`.

O histórico de um cliente é obtido consultando `chamados` por `cliente_id`,
ordenado por `criado_em`.

## Restrições
- Evitar `print()` em stdout no servidor (stdout é usado pelo protocolo stdio).
- Testes automatizados com `pytest`.
- Sem chaves de API ou dados sensíveis no repositório.
