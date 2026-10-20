# Planejamento: listar chamados

As tarefas são pequenas e devem ser executadas na ordem abaixo. Não incluir funcionalidades das Fases 2 e 3.

0. **Preparar o projeto**
   - Criar o ambiente virtual `.venv` e registrar `fastmcp` e `pytest` em `requirements.txt`.
   - Criar a estrutura inicial de arquivos com `servidor.py` e o diretório `tests/`.

1. **Definir a base de persistência**
   - Criar a conexão SQLite usando um caminho configurável por variável de ambiente, com um caminho local como padrão.
   - Permitir que os testes definam a variável de ambiente para usar bancos temporários isolados.
   - Garantir a criação da tabela `chamados` conforme o modelo da Constituição.

2. **Implementar inicialização idempotente**
   - Verificar se a tabela está vazia.
   - Inserir dados exclusivamente fictícios, cobrindo os três status, apenas quando estiver vazia.
   - Confirmar que uma inicialização posterior não duplica exemplos nem altera dados existentes.

3. **Implementar a consulta**
   - Criar a tool FastMCP `listar_chamados` com `status` opcional.
   - Validar o filtro contra `aberto`, `em_andamento` e `fechado` antes da consulta.
   - Para status inválido, levantar `ToolError` do `fastmcp` com mensagem que liste os status aceitos; não retornar um objeto de erro normal.
   - Consultar todos os registros ou filtrar pelo status, ordenando por `criado_em` e `id` em ordem crescente.
   - Converter os resultados para a lista de objetos com os campos especificados; retornar `[]` quando não houver correspondências.

4. **Expor e conferir a tool MCP**
   - Registrar a tool no servidor que usa transporte stdio.
   - Garantir que logs e mensagens de inicialização não sejam enviados a `stdout`.

5. **Adicionar testes automatizados**
   - Cobrir listagem geral, cada filtro válido, ausência de resultados, status inválido e ausência de mutações.
   - Cobrir banco novo, tabela vazia e banco já preenchido na inicialização.
   - Cobrir a descoberta e a chamada da tool via MCP, além dos testes das funções de persistência/consulta.

6. **Documentar e configurar o cliente local**
   - Atualizar `README.md` com instalação, execução do servidor e execução dos testes.
   - Criar `.vscode/mcp.json` apontando para o interpretador Python dentro de `.venv` e configurando o servidor para transporte stdio.

7. **Executar validação da fase**
   - Rodar a suíte pytest e corrigir falhas desta fase.
   - No Copilot Chat, executar os três cenários manuais descritos em `validacao.md` e conferir em cada um que `listar_chamados` foi realmente chamada.
