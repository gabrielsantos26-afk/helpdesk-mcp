from app.app import executar_comando, interpretar_comando


def test_interpreta_listar_todos():
    assert interpretar_comando("listar") == ("listar_chamados", {})


def test_interpreta_listar_abertos_sem_diferenciar_maiusculas():
    assert interpretar_comando("LISTAR ABERTOS") == (
        "listar_chamados",
        {"status": "aberto"},
    )


def test_interpreta_historico_com_id_inteiro():
    assert interpretar_comando("histórico do cliente 101") == (
        "buscar_historico_cliente",
        {"cliente_id": 101},
    )


def test_interpreta_atualizacao_com_status_normalizado():
    assert interpretar_comando("alterar chamado 12 para FECHADO") == (
        "atualizar_status",
        {"chamado_id": 12, "novo_status": "fechado"},
    )


def test_comando_desconhecido_nao_invoca_tool():
    assert interpretar_comando("abra o chamado 12") is None


def test_comando_desconhecido_mostra_orientacao():
    tipo, mensagem = executar_comando("abra o chamado 12")

    assert tipo == "orientacao"
    assert "listar abertos" in mensagem
    assert "historico do cliente N" in mensagem