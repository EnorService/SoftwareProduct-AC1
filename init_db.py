from datetime import datetime
from pathlib import Path

from config import EXCEL_FILE
from storage.excel_db import ExcelDB


def seed() -> None:
    db = ExcelDB(EXCEL_FILE)

    if not db.list_records("Fornecedores"):
        supplier = db.insert(
            "Fornecedores",
            {
                "nome": "Distribuidora Sabor & Cia",
                "cnpj": "12.345.678/0001-90",
                "telefone": "(11) 3333-4444",
                "email": "contato@saborecia.com",
                "endereco": "Rua das Flores, 100",
                "ativo": True,
            },
        )
    else:
        supplier = db.list_records("Fornecedores")[0]

    if not db.list_records("Produtos"):
        db.insert(
            "Produtos",
            {
                "nome": "X-Salada",
                "descricao": "Pão, hambúrguer, queijo, alface e tomate.",
                "categoria": "Lanches",
                "preco": 18.90,
                "estoque": 30,
                "id_fornecedor": supplier["id"],
                "ativo": True,
            },
        )
        db.insert(
            "Produtos",
            {
                "nome": "Batata frita",
                "descricao": "Porção individual de batata frita.",
                "categoria": "Acompanhamentos",
                "preco": 9.50,
                "estoque": 50,
                "id_fornecedor": supplier["id"],
                "ativo": True,
            },
        )
        db.insert(
            "Produtos",
            {
                "nome": "Refrigerante lata",
                "descricao": "Lata de 350 ml.",
                "categoria": "Bebidas",
                "preco": 6.00,
                "estoque": 80,
                "id_fornecedor": supplier["id"],
                "ativo": True,
            },
        )

    if not db.list_records("Clientes"):
        db.insert(
            "Clientes",
            {
                "nome": "Cliente de demonstração",
                "cpf": "111.111.111-11",
                "telefone": "(11) 99999-1111",
                "email": "cliente@exemplo.com",
                "endereco": "Avenida Central, 10",
                "ativo": True,
            },
        )

    if not db.list_records("Filiais"):
        db.insert(
            "Filiais",
            {
                "nome": "Lanchonete Centro",
                "cnpj": "98.765.432/0001-10",
                "telefone": "(11) 3222-1111",
                "endereco": "Rua Central, 500",
                "cidade": "São Paulo",
                "uf": "SP",
                "ativo": True,
            },
        )

    if not db.list_board_items(include_inactive=True):
        board_items = [
            (
                "AC1 — Produtos",
                "Cadastro, alteração, exclusão e visualização dos produtos.",
                "CONCLUIDO",
            ),
            (
                "AC2 — Clientes",
                "Cadastro, alteração, exclusão e visualização dos clientes.",
                "CONCLUIDO",
            ),
            (
                "AC3 — Fornecedores",
                "Cadastro, alteração, exclusão e visualização dos fornecedores.",
                "CONCLUIDO",
            ),
            (
                "Prova final — Filiais e pedidos",
                "Concluir o fluxo de filiais, pedidos, estoque e apresentação.",
                "EM_PROGRESSO",
            ),
        ]
        timestamp = datetime.now().isoformat(timespec="minutes")
        for title, description, status in board_items:
            db.insert(
                "BoardItens",
                {
                    "titulo": title,
                    "descricao": description,
                    "status": status,
                    "origem": "LOCAL",
                    "ativo": True,
                    "criado_em": timestamp,
                    "atualizado_em": timestamp,
                },
            )


if __name__ == "__main__":
    seed()
    print(f"Banco Excel pronto em: {EXCEL_FILE}")
