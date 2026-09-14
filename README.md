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

### Adicionar as ACs ao GitHub Project

As quatro demandas estão descritas em `docs/issues/`. Ao enviar este projeto
para a branch `main` no GitHub, o workflow `.github/workflows/criar-issues-acs.yml`
cria automaticamente uma Issue para **AC1 — Produtos**, **AC2 — Clientes**,
**AC3 — Fornecedores** e **Prova final — Filiais e pedidos**. Ele confere
inclusive as Issues fechadas para não criar outra com o mesmo título ao rodar
novamente. A aplicação Flask não possui board nem conexão com o GitHub.

Para usar o board que você criou no GitHub:

1. Confirme que **Issues** e **Actions** estão habilitados no repositório.
2. Suba os arquivos, inclusive a pasta `.github`, para a branch `main`.
3. Em **Actions > Criar Issues das ACs**, confirme que a execução terminou.
   Se ela não iniciou no primeiro envio, use **Run workflow** nessa tela.
4. Abra seu GitHub Project, clique em **Add item**, selecione
   `EnorService/SoftwareProduct-AC1` e adicione as quatro Issues à coluna
   desejada. Depois, arraste os cartões entre **Todo**, **In Progress** e **Done**.

Se aparecer “No items to add”, confira se as Issues existem na aba **Issues**
do repositório e se você está selecionando o repositório correto. O Project
guarda o status; o repositório guarda o título e a descrição de cada Issue.

Se o repositório usar uma branch principal diferente de `main`, ajuste o nome
da branch no workflow ou execute-o manualmente em **Actions**.

Recomenda-se usar uma branch ou tag para cada entrega:

```text
ac1-produtos
ac2-clientes
ac3-fornecedores
prova-final
```

Os registros de backlog, Sprints, casos de uso e classes estão em `docs/`.
