# Missão

## Propósito
Oferecer um servidor MCP que dê a agentes de IA acesso padronizado e controlado
aos chamados de um helpdesk, resolvendo o problema de cada aplicação precisar de
integração própria com o banco de dados de suporte.

## Quem utilizará as ferramentas
- Agentes de IA em clientes MCP (ex.: GitHub Copilot Chat no VS Code).
- Aplicações clientes de MCP (ex.: protótipo de chat em Streamlit, na Parte 2).

O servidor expõe **operações sobre dados**, não uma interface para o atendente.

## Escopo inicial
- Consultar chamados (com filtro por status).
- Consultar o histórico de chamados de um cliente.
- Atualizar o status de um chamado.

## Limites do exemplo
- Dados **fictícios**.
- Uso **local** (transporte stdio).
- **Sem autenticação** ou autorização reais.
- Sem criação ou exclusão de chamados.
- Sem interface própria (a interface é construída à parte).
