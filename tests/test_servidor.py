import asyncio
import os
import sqlite3
import sys
from pathlib import Path

import pytest
from fastmcp import Client
from fastmcp.client.transports import StdioTransport
from fastmcp.exceptions import ToolError

import servidor


def configurar_banco_temporario(monkeypatch, tmp_path):
    db_path = tmp_path / "helpdesk-test.db"
    monkeypatch.setenv(servidor.VARIAVEL_BANCO, str(db_path))
    return db_path


def ler_todos_os_registros(db_path):
    with sqlite3.connect(db_path) as conexao:
        return conexao.execute(
            """
            SELECT id, cliente_id, cliente_nome, descricao, status, criado_em, atualizado_em
            FROM chamados ORDER BY id
            """
        ).fetchall()


def test_inicializacao_cria_banco_e_semeia_tres_status(tmp_path):
    db_path = tmp_path / "novo" / "helpdesk.db"

    servidor.inicializar_banco(db_path)

    registros = ler_todos_os_registros(db_path)
    assert len(registros) == 3
    assert {registro[4] for registro in registros} == set(servidor.STATUS_PERMITIDOS)


def test_inicializacao_semeia_tabela_existente_vazia(tmp_path):
    db_path = tmp_path / "vazio.db"
    with sqlite3.connect(db_path) as conexao:
        conexao.execute(
            """
            CREATE TABLE chamados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id INTEGER NOT NULL,
                cliente_nome TEXT NOT NULL,
                descricao TEXT NOT NULL,
                status TEXT NOT NULL,
                criado_em TEXT NOT NULL,
                atualizado_em TEXT NOT NULL
            )
            """
        )

    servidor.inicializar_banco(db_path)

    assert len(ler_todos_os_registros(db_path)) == 3


def test_inicializacao_preserva_registros_existentes(tmp_path):
    db_path = tmp_path / "preenchido.db"
    servidor.inicializar_banco(db_path)
    with sqlite3.connect(db_path) as conexao:
        conexao.execute(
            "UPDATE chamados SET descricao = ? WHERE id = 1",
            ("Alteracao que deve ser preservada",),
        )
    antes = ler_todos_os_registros(db_path)

    servidor.inicializar_banco(db_path)

    assert ler_todos_os_registros(db_path) == antes


def test_inicializacao_resemeia_depois_que_todos_sao_apagados(tmp_path):
    db_path = tmp_path / "apagados.db"
    servidor.inicializar_banco(db_path)
    with sqlite3.connect(db_path) as conexao:
        conexao.execute("DELETE FROM chamados")

    servidor.inicializar_banco(db_path)

    assert len(ler_todos_os_registros(db_path)) == 3


@pytest.mark.parametrize("status", servidor.STATUS_PERMITIDOS)
def test_consulta_filtra_por_cada_status(monkeypatch, tmp_path, status):
    configurar_banco_temporario(monkeypatch, tmp_path)
    servidor.inicializar_banco()

    chamados = servidor.consultar_chamados(status)

    assert chamados
    assert {chamado["status"] for chamado in chamados} == {status}


def test_consulta_sem_filtro_retorna_todos_em_ordem(monkeypatch, tmp_path):
    db_path = configurar_banco_temporario(monkeypatch, tmp_path)
    servidor.inicializar_banco()
    antes = ler_todos_os_registros(db_path)

    chamados = servidor.listar_chamados()

    assert len(chamados) == 3
    assert {chamado["status"] for chamado in chamados} == set(servidor.STATUS_PERMITIDOS)
    assert [(chamado["criado_em"], chamado["id"]) for chamado in chamados] == sorted(
        (chamado["criado_em"], chamado["id"]) for chamado in chamados
    )
    assert ler_todos_os_registros(db_path) == antes


def test_consulta_sem_correspondencias_retorna_lista_vazia(monkeypatch, tmp_path):
    configurar_banco_temporario(monkeypatch, tmp_path)
    servidor.inicializar_banco()
    with sqlite3.connect(servidor.caminho_banco()) as conexao:
        conexao.execute("DELETE FROM chamados")

    assert servidor.listar_chamados() == []
    assert servidor.listar_chamados("aberto") == []


@pytest.mark.parametrize("status", ["inexistente", "ABERTO", ""])
def test_status_invalido_levanta_tool_error(monkeypatch, tmp_path, status):
    db_path = configurar_banco_temporario(monkeypatch, tmp_path)
    servidor.inicializar_banco()
    antes = ler_todos_os_registros(db_path)

    with pytest.raises(ToolError) as erro:
        servidor.listar_chamados(status)

    assert all(status_permitido in str(erro.value) for status_permitido in servidor.STATUS_PERMITIDOS)
    assert ler_todos_os_registros(db_path) == antes


def test_cliente_mcp_descobre_e_chama_tool(monkeypatch, tmp_path):
    db_path = tmp_path / "mcp-stdio.db"
    variaveis_ambiente = os.environ.copy()
    variaveis_ambiente[servidor.VARIAVEL_BANCO] = str(db_path)
    transporte = StdioTransport(
        command=sys.executable,
        args=[str(Path(servidor.__file__).resolve())],
        env=variaveis_ambiente,
        cwd=str(Path(servidor.__file__).resolve().parent),
    )

    async def verificar_cliente():
        async with Client(transporte) as cliente:
            tools = await cliente.list_tools()
            assert any(tool.name == "listar_chamados" for tool in tools)
            resultado = await cliente.call_tool("listar_chamados", {})
            assert len(resultado.data) == 3
            erro = await cliente.call_tool(
                "listar_chamados", {"status": "inexistente"}, raise_on_error=False
            )
            assert erro.is_error
            assert all(
                status in str(erro.content)
                for status in servidor.STATUS_PERMITIDOS
            )

    asyncio.run(verificar_cliente())