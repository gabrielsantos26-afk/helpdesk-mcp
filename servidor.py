"""Servidor MCP local para consulta de chamados ficticios do helpdesk."""

from __future__ import annotations

import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

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


@mcp.tool
def listar_chamados(status: str | None = None) -> list[dict[str, Any]]:
    """Lista todos os chamados ou filtra por um dos status permitidos."""
    if status is not None and status not in STATUS_PERMITIDOS:
        status_texto = ", ".join(STATUS_PERMITIDOS)
        raise ToolError(f"Status invalido. Status aceitos: {status_texto}.")
    return consultar_chamados(status)


def main() -> None:
    inicializar_banco()
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()