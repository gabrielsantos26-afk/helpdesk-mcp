# helpdesk-mcp

Servidor **MCP (Model Context Protocol)** em Python para um sistema de helpdesk.
Ele expõe *tools* que permitem a um agente de IA (ou a uma aplicação cliente de MCP)
consultar e atualizar chamados de suporte técnico armazenados em SQLite.

> Projeto didático da disciplina GAC126 (PASIA, UFLA), desenvolvido com
> Spec-Driven Development (SDD).

## Tools planejadas

| Tool | Descrição |
|------|-----------|
| `listar_chamados` | Lista chamados, com filtro opcional por status |
| `buscar_historico_cliente` | Retorna os chamados de um cliente |
| `atualizar_status` | Altera o status de um chamado existente |

## Documentação do projeto (Constituição)

- [`specs/missao.md`](specs/missao.md): propósito, usuários, escopo e limites
- [`specs/pilha-tecnologia.md`](specs/pilha-tecnologia.md): decisões técnicas
- [`specs/roadmap.md`](specs/roadmap.md): fases de entrega

## Status

Fase de **Constituição** concluída. Nenhuma tool implementada ainda.
Instruções de instalação e execução serão adicionadas na implementação.
