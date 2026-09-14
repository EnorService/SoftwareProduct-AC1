# Planejamento Ágil — Lanchonete Ágil

## Visão do produto

Uma aplicação web simples para apoiar o cadastro e a operação de uma lanchonete, permitindo controlar produtos, clientes, fornecedores, filiais e pedidos.

## Usuários

- **Administrador:** mantém produtos, clientes, fornecedores e filiais.
- **Atendente:** cria e efetiva pedidos.
- **Gestor:** acompanha o dashboard e os pedidos registrados.

## Backlog do produto

| ID | História de usuário | Prioridade | Entrega |
|---|---|---:|---|
| US01 | Como administrador, quero cadastrar produtos para manter o catálogo da lanchonete. | Alta | AC1 |
| US02 | Como administrador, quero alterar produtos para manter os dados atualizados. | Alta | AC1 |
| US03 | Como administrador, quero excluir ou inativar produtos para evitar cadastros inválidos. | Alta | AC1 |
| US04 | Como administrador, quero visualizar produtos para consultar o catálogo. | Alta | AC1 |
| US05 | Como administrador, quero cadastrar clientes para identificar quem realiza os pedidos. | Alta | AC2 |
| US06 | Como administrador, quero alterar, excluir e visualizar clientes. | Alta | AC2 |
| US07 | Como administrador, quero cadastrar fornecedores para registrar a origem dos produtos. | Alta | AC3 |
| US08 | Como administrador, quero alterar, excluir e visualizar fornecedores. | Alta | AC3 |
| US09 | Como administrador, quero cadastrar filiais para separar as unidades da lanchonete. | Alta | Final |
| US10 | Como atendente, quero criar um pedido relacionando cliente, filial e produtos. | Alta | Final |
| US11 | Como atendente, quero efetivar um pedido para confirmar a venda e baixar o estoque. | Alta | Final |
| US12 | Como gestor, quero visualizar um dashboard para acompanhar os indicadores. | Média | Final |
| US13 | Como estudante, quero apresentar diagramas de casos de uso e classes. | Alta | Final |

## Sprints sugeridas

### Sprint 1 — AC1

Objetivo: entregar o cadastro completo de produtos.

Critérios de aceite:

- Produto possui nome, categoria, preço e estoque.
- É possível cadastrar, alterar, excluir e visualizar.
- O sistema impede preço e estoque negativos.

### Sprint 2 — AC2

Objetivo: entregar o cadastro completo de clientes.

Critérios de aceite:

- Cliente possui nome e dados de contato.
- É possível pesquisar e visualizar detalhes.
- Clientes relacionados a pedidos não são removidos do histórico; são inativados.

### Sprint 3 — AC3

Objetivo: entregar o cadastro completo de fornecedores.

Critérios de aceite:

- Fornecedor possui nome, documento e contato.
- Produto pode ser relacionado a um fornecedor.
- Fornecedor relacionado a produtos pode ser inativado.

### Sprint 4 — Prova final

Objetivo: concluir filiais, pedidos, dashboard e documentação.

Critérios de aceite:

- Pedido possui cliente, filial e pelo menos um produto.
- O total é calculado automaticamente.
- A efetivação valida estoque e diminui o saldo dos produtos.
- Os diagramas estão coerentes com as funcionalidades implementadas.

## Definição de pronto

Uma funcionalidade está pronta quando:

1. Está implementada no back-end e na tela.
2. Possui validações básicas.
3. Foi testada com dados de demonstração.
4. Está documentada no backlog.
5. Foi registrada em um commit do GitHub.

## Retrospectiva sugerida

- O que funcionou bem?
- Qual dificuldade apareceu?
- O que será melhorado na próxima Sprint?
- Alguma mudança foi adicionada ao backlog após o feedback?
