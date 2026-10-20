"""Chat Streamlit que acessa o servidor helpdesk exclusivamente via MCP."""

from __future__ import annotations

import asyncio
import re
import sys
from pathlib import Path
from typing import Any

import streamlit as st
from fastmcp import Client
from fastmcp.client.transports import StdioTransport

RAIZ_PROJETO = Path(__file__).resolve().parents[1]
CAMINHO_SERVIDOR = RAIZ_PROJETO / "servidor.py"


def interpretar_comando(texto: str) -> tuple[str, dict[str, Any]] | None:
    """Converte um comando aceito em nome de tool e argumentos MCP."""
    comando = texto.strip()
    normalizado = comando.casefold()

    if normalizado == "listar":
        return "listar_chamados", {}
    if normalizado == "listar abertos":
        return "listar_chamados", {"status": "aberto"}

    historico = re.fullmatch(r"hist[oó]rico do cliente\s+([+-]?\d+)", comando, re.IGNORECASE)
    if historico:
        return "buscar_historico_cliente", {"cliente_id": int(historico.group(1))}

    atualizacao = re.fullmatch(
        r"alterar chamado\s+([+-]?\d+)\s+para\s+(\S+)",
        comando,
        re.IGNORECASE,
    )
    if atualizacao:
        return "atualizar_status", {
            "chamado_id": int(atualizacao.group(1)),
            "novo_status": atualizacao.group(2).casefold(),
        }

    return None


async def chamar_tool(nome: str, argumentos: dict[str, Any]) -> Any:
    """Executa uma tool abrindo o servidor local pelo transporte stdio."""
    transporte = StdioTransport(
        command=sys.executable,
        args=[str(CAMINHO_SERVIDOR)],
        cwd=str(RAIZ_PROJETO),
    )
    async with Client(transporte) as cliente:
        resultado = await cliente.call_tool(nome, argumentos)
        return resultado.data


def executar_comando(texto: str) -> tuple[str, Any]:
    comando = interpretar_comando(texto)
    if comando is None:
        return (
            "orientacao",
            "Comando nao reconhecido. Use: listar; listar abertos; "
            "historico do cliente N; alterar chamado N para STATUS.",
        )

    nome_tool, argumentos = comando
    try:
        resposta = asyncio.run(chamar_tool(nome_tool, argumentos))
        return "resultado", {"tool": nome_tool, "resultado": resposta}
    except Exception as erro:
        return "erro", {"tool": nome_tool, "mensagem": str(erro)}


def main() -> None:
    st.set_page_config(page_title="Helpdesk MCP", page_icon="H", layout="centered")
    st.title("Helpdesk MCP")
    st.caption("Consulta e atualização de chamados via servidor MCP local")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for mensagem in st.session_state.messages:
        with st.chat_message(mensagem["role"]):
            if mensagem["kind"] == "resultado":
                st.json(mensagem["content"])
            else:
                st.write(mensagem["content"])

    entrada = st.chat_input(
        "Ex.: listar, listar abertos, historico do cliente 101"
    )
    if entrada:
        st.session_state.messages.append(
            {"role": "user", "kind": "texto", "content": entrada}
        )
        with st.chat_message("user"):
            st.write(entrada)

        tipo, conteudo = executar_comando(entrada)
        st.session_state.messages.append(
            {"role": "assistant", "kind": tipo, "content": conteudo}
        )
        with st.chat_message("assistant"):
            if tipo == "resultado":
                st.json(conteudo)
            else:
                st.write(conteudo)


if __name__ == "__main__":
    main()