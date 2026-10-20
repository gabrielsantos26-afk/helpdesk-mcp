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


def test_inicializacao_semeia_tabela_existente_compativel_vazia(tmp_path):
    db_path = tmp_path / "vazio.db"
    with sqlite3.connect(db_path) as conexao:
        conexao.execute(
            """
            CREATE TABLE chamados (
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


def test_historico_cliente_retorna_todos_e_somente_seus_chamados(monkeypatch, tmp_path):
    db_path = configurar_banco_temporario(monkeypatch, tmp_path)
    servidor.inicializar_banco()
    antes = ler_todos_os_registros(db_path)

    chamados = servidor.buscar_historico_cliente(101)

    assert len(chamados) == 2
    assert {chamado["cliente_id"] for chamado in chamados} == {101}
    assert all(
        set(chamado)
        == {
            "id",
            "cliente_id",
            "cliente_nome",
            "descricao",
            "status",
            "criado_em",
            "atualizado_em",
        }
        for chamado in chamados
    )
    assert ler_todos_os_registros(db_path) == antes


def test_historico_cliente_ordena_empate_por_id(monkeypatch, tmp_path):
    configurar_banco_temporario(monkeypatch, tmp_path)
    servidor.inicializar_banco()
    with sqlite3.connect(servidor.caminho_banco()) as conexao:
        conexao.execute(
            "UPDATE chamados SET criado_em = ? WHERE cliente_id = ?",
            ("2025-02-01T10:00:00+00:00", 101),
        )

    chamados = servidor.buscar_historico_cliente(101)

    assert [chamado["id"] for chamado in chamados] == sorted(
        chamado["id"] for chamado in chamados
    )


def test_historico_cliente_sem_chamados_retorna_lista_vazia(monkeypatch, tmp_path):
    configurar_banco_temporario(monkeypatch, tmp_path)
    servidor.inicializar_banco()

    assert servidor.buscar_historico_cliente(99999) == []
    assert servidor.buscar_historico_cliente(0) == []
    assert servidor.buscar_historico_cliente(-1) == []


@pytest.mark.parametrize("cliente_id", [None, True, 2.5, "cliente", "2"])
def test_cliente_id_invalido_levanta_tool_error_sem_mutacao(
    monkeypatch, tmp_path, cliente_id
):
    db_path = configurar_banco_temporario(monkeypatch, tmp_path)
    servidor.inicializar_banco()
    antes = ler_todos_os_registros(db_path)

    with pytest.raises(ToolError, match="inteiro"):
        servidor.buscar_historico_cliente(cliente_id)

    assert ler_todos_os_registros(db_path) == antes


def test_cliente_id_ausente_levanta_tool_error(monkeypatch, tmp_path):
    configurar_banco_temporario(monkeypatch, tmp_path)
    servidor.inicializar_banco()

    with pytest.raises(ToolError, match="inteiro"):
        servidor.buscar_historico_cliente()


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
    campos_esperados = {
        "id",
        "cliente_id",
        "cliente_nome",
        "descricao",
        "status",
        "criado_em",
        "atualizado_em",
    }
    entradas_invalidas = [
        {},
        {"cliente_id": None},
        {"cliente_id": True},
        {"cliente_id": 2.5},
        {"cliente_id": "2"},
    ]

    async def verificar_cliente():
        async with Client(transporte) as cliente:
            tools = await cliente.list_tools()
            assert any(tool.name == "listar_chamados" for tool in tools)
            resultado = await cliente.call_tool("listar_chamados", {})
            assert len(resultado.data) == 3
            assert all(set(chamado) == campos_esperados for chamado in resultado.data)

            for status in servidor.STATUS_PERMITIDOS:
                filtrados = await cliente.call_tool(
                    "listar_chamados", {"status": status}
                )
                assert filtrados.data
                assert all(
                    set(chamado) == campos_esperados
                    and chamado["status"] == status
                    for chamado in filtrados.data
                )

            historico = await cliente.call_tool(
                "buscar_historico_cliente", {"cliente_id": 101}
            )
            assert len(historico.data) == 2
            assert all(set(chamado) == campos_esperados for chamado in historico.data)
            assert all(chamado["cliente_id"] == 101 for chamado in historico.data)
            assert [(chamado["criado_em"], chamado["id"]) for chamado in historico.data] == sorted(
                (chamado["criado_em"], chamado["id"])
                for chamado in historico.data
            )

            for cliente_id in (99999, 0, -1):
                historico_vazio = await cliente.call_tool(
                    "buscar_historico_cliente", {"cliente_id": cliente_id}
                )
                assert historico_vazio.data == []

            for argumentos in entradas_invalidas:
                erro_historico = await cliente.call_tool(
                    "buscar_historico_cliente",
                    argumentos,
                    raise_on_error=False,
                )
                assert erro_historico.is_error
                assert "inteiro" in str(erro_historico.content)

            with sqlite3.connect(db_path) as conexao:
                conexao.execute("DELETE FROM chamados")
            sem_correspondencias = await cliente.call_tool(
                "listar_chamados", {"status": "aberto"}
            )
            assert sem_correspondencias.data == []

            erro = await cliente.call_tool(
                "listar_chamados", {"status": "inexistente"}, raise_on_error=False
            )
            assert erro.is_error
            assert all(
                status in str(erro.content)
                for status in servidor.STATUS_PERMITIDOS
            )

    asyncio.run(verificar_cliente())