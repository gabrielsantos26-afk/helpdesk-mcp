"""Servidor MCP local para consulta de chamados ficticios do helpdesk."""

from __future__ import annotations

import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from fastmcp.tools import FunctionTool

STATUS_PERMITIDOS = ("aberto", "em_andamento", "fechado")
VARIAVEL_BANCO = "HELPDESK_DB_PATH"
BANCO_PADRAO = Path(__file__).resolve().parent / "helpdesk.db"

mcp = FastMCP("helpdesk-mcp")


def caminho_banco() -> Path:
    """Retorna o caminho configurado para o banco SQLite."""
    valor_configurado = os.environ.get(VARIAVEL_BANCO)
    return Path(valor_configurado).expanduser() if valor_configurado else BANCO_PADRAO


def inicializar_banco(db_path: Path | str | None = None) -> None:
    """Cria o esquema e semeia exemplos somente quando a tabela esta vazia."""
    caminho = Path(db_path).expanduser() if db_path is not None else caminho_banco()
    caminho.parent.mkdir(parents=True, exist_ok=True)

    conexao = sqlite3.connect(caminho)
    try:
        conexao.execute(
            """
            CREATE TABLE IF NOT EXISTS chamados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id INTEGER NOT NULL,
                cliente_nome TEXT NOT NULL,
                descricao TEXT NOT NULL,
                status TEXT NOT NULL CHECK (status IN ('aberto', 'em_andamento', 'fechado')),
                criado_em TEXT NOT NULL,
                atualizado_em TEXT NOT NULL
            )
            """
        )
        total = conexao.execute("SELECT COUNT(*) FROM chamados").fetchone()[0]
        if total == 0:
            agora = datetime.now(timezone.utc).isoformat()
            chamados_exemplo = [
                (
                    101,
                    "Cliente Exemplo A",
                    "Nao consegue acessar o portal de suporte.",
                    "aberto",
                    "2025-01-10T09:00:00+00:00",
                    agora,
                ),
                (
                    102,
                    "Cliente Exemplo B",
                    "Solicita orientacao para configurar o email.",
                    "em_andamento",
                    "2025-01-11T10:30:00+00:00",
                    agora,
                ),
                (
                    101,
                    "Cliente Exemplo A",
                    "Erro de sincronizacao corrigido.",
                    "fechado",
                    "2025-01-12T14:15:00+00:00",
                    agora,
                ),
            ]
            conexao.executemany(
                """
                INSERT INTO chamados (
                    cliente_id, cliente_nome, descricao, status, criado_em, atualizado_em
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                chamados_exemplo,
            )
        conexao.commit()
    finally:
        conexao.close()


def consultar_chamados(status: str | None = None) -> list[dict[str, Any]]:
    """Consulta chamados existentes, sem inicializar nem alterar o banco."""
    caminho = caminho_banco()
    conexao = sqlite3.connect(caminho)
    conexao.row_factory = sqlite3.Row
    try:
        if status is None:
            linhas = conexao.execute(
                """
                SELECT id, cliente_id, cliente_nome, descricao, status, criado_em, atualizado_em
                FROM chamados
                ORDER BY criado_em ASC, id ASC
                """
            ).fetchall()
        else:
            linhas = conexao.execute(
                """
                SELECT id, cliente_id, cliente_nome, descricao, status, criado_em, atualizado_em
                FROM chamados
                WHERE status = ?
                ORDER BY criado_em ASC, id ASC
                """,
                (status,),
            ).fetchall()
        return [dict(linha) for linha in linhas]
    finally:
        conexao.close()


def consultar_historico_cliente(cliente_id: int) -> list[dict[str, Any]]:
    """Consulta o historico de chamados de um cliente, sem alterar dados."""
    conexao = sqlite3.connect(caminho_banco())
    conexao.row_factory = sqlite3.Row
    try:
        linhas = conexao.execute(
            """
            SELECT id, cliente_id, cliente_nome, descricao, status, criado_em, atualizado_em
            FROM chamados
            WHERE cliente_id = ?
            ORDER BY criado_em ASC, id ASC
            """,
            (cliente_id,),
        ).fetchall()
        return [dict(linha) for linha in linhas]
    finally:
        conexao.close()


@mcp.tool
def listar_chamados(status: str | None = None) -> list[dict[str, Any]]:
    """Lista todos os chamados ou filtra por um dos status permitidos."""
    if status is not None and status not in STATUS_PERMITIDOS:
        status_texto = ", ".join(STATUS_PERMITIDOS)
        raise ToolError(f"Status invalido. Status aceitos: {status_texto}.")
    return consultar_chamados(status)


def buscar_historico_cliente(cliente_id: Any = None) -> list[dict[str, Any]]:
    """Retorna os chamados do cliente em ordem cronologica deterministica."""
    if type(cliente_id) is not int:
        raise ToolError("cliente_id e obrigatorio e deve ser um numero inteiro.")
    return consultar_historico_cliente(cliente_id)


ferramenta_historico_cliente = FunctionTool.from_function(buscar_historico_cliente)
ferramenta_historico_cliente.parameters = {
    "type": "object",
    "properties": {"cliente_id": {"type": "integer"}},
    "required": ["cliente_id"],
    "additionalProperties": False,
}
mcp.add_tool(ferramenta_historico_cliente)


def atualizar_status(chamado_id: Any = None, novo_status: Any = None) -> dict[str, Any]:
    """Atualiza o status de um chamado e retorna o registro atualizado."""
    if type(chamado_id) is not int:
        raise ToolError("chamado_id e obrigatorio e deve ser um numero inteiro.")
    if type(novo_status) is not str or novo_status not in STATUS_PERMITIDOS:
        status_texto = ", ".join(STATUS_PERMITIDOS)
        raise ToolError(f"Status invalido. Status aceitos: {status_texto}.")

    atualizado_em = datetime.now(timezone.utc).isoformat()
    conexao = sqlite3.connect(caminho_banco())
    conexao.row_factory = sqlite3.Row
    try:
        cursor = conexao.execute(
            """
            UPDATE chamados
            SET status = ?, atualizado_em = ?
            WHERE id = ?
            """,
            (novo_status, atualizado_em, chamado_id),
        )
        if cursor.rowcount == 0:
            raise ToolError(f"Chamado {chamado_id} nao encontrado.")

        linha = conexao.execute(
            """
            SELECT id, cliente_id, cliente_nome, descricao, status, criado_em, atualizado_em
            FROM chamados
            WHERE id = ?
            """,
            (chamado_id,),
        ).fetchone()
        chamado_atualizado = dict(linha)
        conexao.commit()
        return chamado_atualizado
    except Exception:
        conexao.rollback()
        raise
    finally:
        conexao.close()


ferramenta_atualizar_status = FunctionTool.from_function(atualizar_status)
ferramenta_atualizar_status.parameters = {
    "type": "object",
    "properties": {
        "chamado_id": {"type": "integer"},
        "novo_status": {"type": "string", "enum": list(STATUS_PERMITIDOS)},
    },
    "required": ["chamado_id", "novo_status"],
    "additionalProperties": False,
}
mcp.add_tool(ferramenta_atualizar_status)


def main() -> None:
    inicializar_banco()
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()