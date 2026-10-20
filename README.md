# helpdesk-mcp

Servidor MCP local para consultar e atualizar chamados ficticios de helpdesk.
As Fases 1, 2 e 3 disponibilizam `listar_chamados`,
`buscar_historico_cliente` e `atualizar_status`.

> Projeto didático da disciplina GAC126 (PASIA, UFLA), desenvolvido com
> Spec-Driven Development (SDD).

## Requisitos

- Python 3.11 ou superior.
- `venv` e `pip`.

## Instalar

Na raiz do projeto, crie o ambiente e instale as dependencias:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Executar

Inicie o servidor pelo transporte MCP stdio:

```bash
source .venv/bin/activate
python servidor.py
```

O servidor cria o banco SQLite local em `helpdesk.db` e semeia dados ficticios
se a tabela `chamados` estiver vazia. Registros ja existentes sao preservados.
Se todos os chamados forem apagados, a proxima inicializacao semeia os exemplos
novamente.

`listar_chamados` lista todos os registros ou filtra por status. Para consultar
o historico de um cliente, use `buscar_historico_cliente` com `cliente_id`
inteiro; clientes sem chamados recebem uma lista vazia. Para alterar um chamado,
use `atualizar_status` com `chamado_id` e `novo_status` (`aberto`,
`em_andamento` ou `fechado`). A resposta contém o chamado atualizado; erros de
status ou de chamado inexistente sao informados sem alterar o registro.

Para escolher outro arquivo de banco, defina `HELPDESK_DB_PATH` antes de iniciar:

```bash
HELPDESK_DB_PATH=/caminho/para/helpdesk.db python servidor.py
```

## Registrar no VS Code

O arquivo `.vscode/mcp.json` registra o servidor usando o Python de `.venv`.
Abra o workspace no VS Code, permita a inicializacao do servidor MCP quando
solicitado e confira que `listar_chamados` aparece entre as tools disponiveis.
No Windows, ajuste o campo `command` em `.vscode/mcp.json` para
`${workspaceFolder}/.venv/Scripts/python.exe`.

## Testes

Os testes automatizados ficam em `tests/` e usam bancos temporarios, sem alterar
o banco local. Execute a partir da raiz do projeto:

```bash
source .venv/bin/activate
python -m pytest
```

No Windows PowerShell, ative o ambiente com
`.venv\Scripts\Activate.ps1` e execute `python -m pytest`.

## Especificacoes

- [`specs/missao.md`](specs/missao.md): objetivo e limites do projeto.
- [`specs/pilha-tecnologia.md`](specs/pilha-tecnologia.md): decisoes tecnicas.
- [`specs/01-listar-chamados/`](specs/01-listar-chamados/): requisitos, planejamento e validacao da Fase 1.
- [`specs/02-historico-cliente/`](specs/02-historico-cliente/): requisitos, planejamento e validacao da Fase 2.
- [`specs/03-atualizar-status/`](specs/03-atualizar-status/): requisitos, planejamento e validacao da Fase 3.
