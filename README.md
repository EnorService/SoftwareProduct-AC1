# Lanchonete Ágil

Aplicação web acadêmica para demonstrar o desenvolvimento incremental baseado no Manifesto Ágil.

O projeto possui front-end, back-end e persistência no mesmo diretório. Ele não utiliza SQL: os dados ficam em um único arquivo Excel, `data/lanchonete.xlsx`, dividido em abas.

## Funcionalidades por avaliação

### 1ª AC — Produtos

- Cadastrar produtos.
- Alterar produtos.
- Excluir ou inativar produtos vinculados a pedidos.
- Visualizar produtos.

### 2ª AC — Clientes

- Cadastrar clientes.
- Alterar clientes.
- Excluir ou inativar clientes vinculados a pedidos.
- Visualizar clientes.

### 3ª AC — Fornecedores

- Cadastrar fornecedores.
- Alterar fornecedores.
- Excluir ou inativar fornecedores vinculados a produtos.
- Visualizar fornecedores.

### Prova final

- Cadastrar, alterar, excluir e visualizar filiais.
- Criar um pedido relacionado a cliente, filial e produtos.
- Efetivar o pedido, validar estoque e atualizar o saldo dos produtos.
- Apresentar os diagramas de casos de uso e classes disponíveis em `docs/`.

## Tecnologias

- Python 3.10 ou superior.
- Flask.
- HTML, CSS e JavaScript.
- Excel (`openpyxl`) como persistência local.

## Como executar no VSCode

No terminal, dentro da pasta do projeto:

### Windows

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python init_db.py
python app.py
```

### Linux ou macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python init_db.py
python app.py
```

Depois, abra `http://127.0.0.1:5000` no navegador.

O comando `python init_db.py` cria o arquivo Excel e adiciona alguns registros de demonstração apenas se as abas estiverem vazias.

## Administração das ACs

O acesso administrativo está disponível em `Acesso administrativo`, no rodapé do sistema, ou diretamente em `/admin/login`.

- Senha padrão do projeto acadêmico: `123`.
- O administrador pode habilitar ou ocultar AC1, AC2, AC3 e a prova final.
- A configuração fica salva na aba `Configuracoes` do mesmo arquivo Excel.
- Uma funcionalidade desabilitada fica oculta no dashboard e bloqueada mesmo se sua URL for digitada diretamente.

## Estrutura do Excel

O arquivo `data/lanchonete.xlsx` possui as abas:

- `Produtos`
- `Clientes`
- `Fornecedores`
- `Filiais`
- `Pedidos`
- `ItensPedido`

## GitHub e avaliações

Recomenda-se usar uma branch ou tag para cada entrega:

```text
ac1-produtos
ac2-clientes
ac3-fornecedores
prova-final
```

Os registros de backlog, Sprints, casos de uso e classes estão em `docs/`.

## Board de acompanhamento integrado ao GitHub

O projeto possui um board local acessível em `/board`. Ele continua usando o
Excel como persistência e também pode importar os itens de um GitHub Project v2,
mantendo o título, a descrição, o status e o link da Issue ou Pull Request.

### Como configurar depois de subir o projeto

1. Crie ou abra o repositório no GitHub e envie os arquivos manualmente.
2. Crie uma Issue para cada AC e adicione as Issues ao seu Project em modo Board.
3. Copie `.env.example` para `.env` na máquina em que a aplicação será executada.
4. Preencha no `.env`:

```env
LANCHONETE_GITHUB_TOKEN=seu_token_com_acesso_ao_project
LANCHONETE_GITHUB_OWNER=seu_usuario_ou_organizacao
LANCHONETE_GITHUB_OWNER_TYPE=user
LANCHONETE_GITHUB_PROJECT_NUMBER=1
```

Para um Project de organização, altere `LANCHONETE_GITHUB_OWNER_TYPE` para
`organization`. O número do projeto é o número exibido na URL do Project, como
`/users/seu-usuario/projects/1` ou `/orgs/sua-organizacao/projects/1`.

5. Instale as dependências e execute a aplicação normalmente.
6. Acesse **Board das ACs**, entre como administrador e clique em
   **Sincronizar GitHub**.

Os itens importados aparecem com o selo GitHub e com o botão **Abrir no GitHub**.
Demandas criadas diretamente no sistema ficam como itens locais. Arrastar um
item local altera apenas o board local; arrastar um item importado também tenta
atualizar o status do Project, desde que o token tenha permissão de escrita.

O arquivo `.env` está ignorado pelo Git para evitar o envio do token ao
repositório. Nunca coloque esse token em HTML ou JavaScript do navegador.
