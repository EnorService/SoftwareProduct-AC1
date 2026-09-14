from __future__ import annotations

import os
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any

from flask import Flask, flash, redirect, render_template, request, session, url_for

from config import EXCEL_FILE, HOST, PORT, SECRET_KEY
from storage.excel_db import DataError, ExcelDB


BASE_DIR = Path(__file__).resolve().parent
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", SECRET_KEY)
db = ExcelDB(EXCEL_FILE)

ADMIN_PASSWORD = os.getenv("LANCHONETE_ADMIN_PASSWORD", "123")
FEATURE_CATALOG = [
    {
        "key": "ac1",
        "title": "AC1 · Produtos",
        "description": "Cadastro, alteração, exclusão e visualização dos produtos.",
    },
    {
        "key": "ac2",
        "title": "AC2 · Clientes",
        "description": "Cadastro, alteração, exclusão e visualização dos clientes.",
    },
    {
        "key": "ac3",
        "title": "AC3 · Fornecedores",
        "description": "Cadastro, alteração, exclusão e visualização dos fornecedores.",
    },
    {
        "key": "final",
        "title": "Prova final · Filiais e pedidos",
        "description": "Filiais, criação de pedidos e efetivação com baixa de estoque.",
    },
]

def parse_decimal(value: str | None, field_name: str = "Valor") -> float:
    value = (value or "").strip()
    if not value:
        raise DataError(f"Informe o campo {field_name}.")
    normalized = value.replace("R$", "").replace(" ", "")
    if "," in normalized:
        normalized = normalized.replace(".", "").replace(",", ".")
    try:
        number = float(normalized)
    except ValueError as exc:
        raise DataError(f"O campo {field_name} deve conter um número válido.") from exc
    if number < 0:
        raise DataError(f"O campo {field_name} não pode ser negativo.")
    return round(number, 2)


def parse_integer(value: str | None, field_name: str, required: bool = True) -> int | None:
    value = (value or "").strip()
    if not value and not required:
        return None
    try:
        number = int(value)
    except ValueError as exc:
        raise DataError(f"O campo {field_name} deve conter um número inteiro.") from exc
    if number < 0:
        raise DataError(f"O campo {field_name} não pode ser negativo.")
    return number


def form_bool(name: str, default: bool = True) -> bool:
    if name not in request.form:
        return default
    return request.form.get(name) in {"on", "true", "1", "sim"}


def now_value() -> str:
    return datetime.now().isoformat(timespec="minutes")


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("admin_authenticated"):
            flash("Informe a senha administrativa para continuar.", "error")
            return redirect(url_for("admin_login", next=request.path))
        return view(*args, **kwargs)

    return wrapped


def feature_required(feature_key: str):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if not db.feature_enabled(feature_key) and not session.get("admin_authenticated"):
                flash("Esta funcionalidade está desabilitada pelo administrador.", "error")
                return redirect(url_for("dashboard"))
            return view(*args, **kwargs)

        return wrapped

    return decorator


@app.template_filter("money")
def money(value: Any) -> str:
    try:
        number = float(value or 0)
    except (TypeError, ValueError):
        number = 0
    return f"R$ {number:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


@app.template_filter("date_br")
def date_br(value: Any) -> str:
    if not value:
        return "-"
    if isinstance(value, datetime):
        return value.strftime("%d/%m/%Y %H:%M")
    try:
        return datetime.fromisoformat(str(value)).strftime("%d/%m/%Y %H:%M")
    except ValueError:
        return str(value)


def common_context() -> dict[str, Any]:
    return {
        "features": db.feature_flags(),
        "is_admin": bool(session.get("admin_authenticated")),
        "nav_counts": {
            "produtos": len(db.list_records("Produtos", active_only=True)),
            "clientes": len(db.list_records("Clientes", active_only=True)),
            "pedidos": len(db.list_records("Pedidos")),
        }
    }


@app.context_processor
def inject_common_context() -> dict[str, Any]:
    return common_context()


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if session.get("admin_authenticated"):
        return redirect(url_for("admin_panel"))
    if request.method == "POST":
        if request.form.get("senha", "") == ADMIN_PASSWORD:
            session["admin_authenticated"] = True
            flash("Acesso administrativo liberado.", "success")
            return redirect(request.args.get("next") or url_for("admin_panel"))
        flash("Senha administrativa incorreta.", "error")
    return render_template("admin/login.html")


@app.route("/admin")
@admin_required
def admin_panel():
    flags = db.feature_flags()
    features = [{**item, "enabled": flags.get(item["key"], True)} for item in FEATURE_CATALOG]
    return render_template("admin/panel.html", features=features)


@app.post("/admin/funcionalidades")
@admin_required
def update_features():
    flags = {
        item["key"]: request.form.get(f"feature_{item['key']}") == "on"
        for item in FEATURE_CATALOG
    }
    db.set_feature_flags(flags)
    flash("Visibilidade das funcionalidades atualizada.", "success")
    return redirect(url_for("admin_panel"))


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_authenticated", None)
    flash("Acesso administrativo encerrado.", "success")
    return redirect(url_for("dashboard"))


@app.route("/")
def dashboard():
    return render_template("dashboard.html", summary=db.dashboard())


@app.route("/produtos")
@feature_required("ac1")
def products():
    query = request.args.get("q", "").strip().lower()
    records = db.list_records("Produtos")
    if query:
        records = [
            row
            for row in records
            if query in " ".join(str(row.get(field) or "") for field in ("nome", "categoria", "descricao")).lower()
        ]
    suppliers = {row["id"]: row["nome"] for row in db.list_records("Fornecedores")}
    for row in records:
        row["fornecedor_nome"] = suppliers.get(row.get("id_fornecedor"), "-")
    return render_template(
        "entity_list.html",
        title="Produtos",
        subtitle="AC1 · Catálogo de produtos da lanchonete",
        create_url=url_for("new_product"),
        list_url=url_for("products"),
        search=query,
        rows=records,
        columns=[
            ("id", "ID"),
            ("nome", "Produto"),
            ("categoria", "Categoria"),
            ("preco", "Preço"),
            ("estoque", "Estoque"),
            ("fornecedor_nome", "Fornecedor"),
            ("ativo", "Status"),
        ],
        entity="produto",
    )


@app.route("/produtos/novo", methods=["GET", "POST"])
@feature_required("ac1")
def new_product():
    if request.method == "POST":
        try:
            validate_required(request.form.get("nome"), "Nome")
            validate_required(request.form.get("categoria"), "Categoria")
            db.insert(
                "Produtos",
                {
                    "nome": request.form.get("nome", "").strip(),
                    "descricao": request.form.get("descricao", "").strip(),
                    "categoria": request.form.get("categoria", "").strip(),
                    "preco": parse_decimal(request.form.get("preco"), "Preço"),
                    "estoque": parse_integer(request.form.get("estoque"), "Estoque"),
                    "id_fornecedor": parse_integer(request.form.get("id_fornecedor"), "Fornecedor", False),
                    "ativo": form_bool("ativo"),
                    "criado_em": now_value(),
                },
            )
            flash("Produto cadastrado com sucesso.", "success")
            return redirect(url_for("products"))
        except (DataError, ValueError) as exc:
            flash(str(exc), "error")
    return render_template(
        "entity_form.html",
        title="Novo produto",
        subtitle="Cadastre um item que poderá ser utilizado em pedidos.",
        back_url=url_for("products"),
        action_url=url_for("new_product"),
        fields=product_fields(),
        values=request.form,
    )


@app.route("/produtos/<int:record_id>/editar", methods=["GET", "POST"])
@feature_required("ac1")
def edit_product(record_id: int):
    product = db.get("Produtos", record_id)
    if not product:
        flash("Produto não encontrado.", "error")
        return redirect(url_for("products"))
    if request.method == "POST":
        try:
            validate_required(request.form.get("nome"), "Nome")
            validate_required(request.form.get("categoria"), "Categoria")
            db.update(
                "Produtos",
                record_id,
                {
                    "nome": request.form.get("nome", "").strip(),
                    "descricao": request.form.get("descricao", "").strip(),
                    "categoria": request.form.get("categoria", "").strip(),
                    "preco": parse_decimal(request.form.get("preco"), "Preço"),
                    "estoque": parse_integer(request.form.get("estoque"), "Estoque"),
                    "id_fornecedor": parse_integer(request.form.get("id_fornecedor"), "Fornecedor", False),
                    "ativo": form_bool("ativo"),
                },
            )
            flash("Produto atualizado com sucesso.", "success")
            return redirect(url_for("products"))
        except (DataError, ValueError) as exc:
            flash(str(exc), "error")
            product = {**product, **request.form.to_dict()}
    return render_template(
        "entity_form.html",
        title="Alterar produto",
        subtitle="Atualize as informações do produto.",
        back_url=url_for("products"),
        action_url=url_for("edit_product", record_id=record_id),
        fields=product_fields(),
        values=product,
    )


@app.route("/produtos/<int:record_id>")
@feature_required("ac1")
def view_product(record_id: int):
    product = db.get("Produtos", record_id)
    if not product:
        flash("Produto não encontrado.", "error")
        return redirect(url_for("products"))
    supplier = db.get("Fornecedores", int(product.get("id_fornecedor") or 0))
    return render_template(
        "entity_detail.html",
        title="Detalhes do produto",
        subtitle="Informações cadastradas",
        record=product,
        details=[
            ("Nome", product.get("nome")),
            ("Descrição", product.get("descricao")),
            ("Categoria", product.get("categoria")),
            ("Preço", money(product.get("preco"))),
            ("Estoque", product.get("estoque")),
            ("Fornecedor", supplier.get("nome") if supplier else "Não informado"),
            ("Status", "Ativo" if db._is_active(product) else "Inativo"),
            ("Criado em", date_br(product.get("criado_em"))),
        ],
        back_url=url_for("products"),
        edit_url=url_for("edit_product", record_id=record_id),
    )


@app.post("/produtos/<int:record_id>/excluir")
@feature_required("ac1")
def delete_product(record_id: int):
    try:
        result = db.delete_or_deactivate("Produtos", record_id)
        flash(
            "Produto inativado porque já está vinculado a um pedido." if result == "inativado" else "Produto excluído com sucesso.",
            "success",
        )
    except DataError as exc:
        flash(str(exc), "error")
    return redirect(url_for("products"))


def product_fields() -> list[dict[str, Any]]:
    return [
        {"name": "nome", "label": "Nome", "type": "text", "required": True},
        {"name": "descricao", "label": "Descrição", "type": "textarea"},
        {"name": "categoria", "label": "Categoria", "type": "text", "required": True},
        {"name": "preco", "label": "Preço", "type": "money", "required": True},
        {"name": "estoque", "label": "Estoque", "type": "number", "required": True, "min": 0},
        {
            "name": "id_fornecedor",
            "label": "Fornecedor",
            "type": "select",
            "options": [(row["id"], row["nome"]) for row in db.list_records("Fornecedores", active_only=True)],
        },
        {"name": "ativo", "label": "Produto ativo", "type": "checkbox", "default": True},
    ]


@app.route("/clientes")
@feature_required("ac2")
def clients():
    query = request.args.get("q", "").strip().lower()
    records = db.list_records("Clientes")
    if query:
        records = [
            row for row in records if query in " ".join(str(row.get(field) or "") for field in ("nome", "cpf", "telefone", "email")).lower()
        ]
    return render_template(
        "entity_list.html",
        title="Clientes",
        subtitle="AC2 · Pessoas que realizam pedidos",
        create_url=url_for("new_client"),
        list_url=url_for("clients"),
        search=query,
        rows=records,
        columns=[("id", "ID"), ("nome", "Nome"), ("cpf", "CPF"), ("telefone", "Telefone"), ("email", "E-mail"), ("ativo", "Status")],
        entity="cliente",
    )


@app.route("/clientes/novo", methods=["GET", "POST"])
@feature_required("ac2")
def new_client():
    if request.method == "POST":
        try:
            validate_required(request.form.get("nome"), "Nome")
            db.insert("Clientes", client_values())
            flash("Cliente cadastrado com sucesso.", "success")
            return redirect(url_for("clients"))
        except DataError as exc:
            flash(str(exc), "error")
    return render_template("entity_form.html", title="Novo cliente", subtitle="Cadastre os dados do cliente.", back_url=url_for("clients"), action_url=url_for("new_client"), fields=client_fields(), values=request.form)


@app.route("/clientes/<int:record_id>/editar", methods=["GET", "POST"])
@feature_required("ac2")
def edit_client(record_id: int):
    record = db.get("Clientes", record_id)
    if not record:
        flash("Cliente não encontrado.", "error")
        return redirect(url_for("clients"))
    if request.method == "POST":
        try:
            validate_required(request.form.get("nome"), "Nome")
            db.update("Clientes", record_id, client_values(include_created=False))
            flash("Cliente atualizado com sucesso.", "success")
            return redirect(url_for("clients"))
        except DataError as exc:
            flash(str(exc), "error")
            record = {**record, **request.form.to_dict()}
    return render_template("entity_form.html", title="Alterar cliente", subtitle="Atualize os dados do cliente.", back_url=url_for("clients"), action_url=url_for("edit_client", record_id=record_id), fields=client_fields(), values=record)


@app.route("/clientes/<int:record_id>")
@feature_required("ac2")
def view_client(record_id: int):
    record = db.get("Clientes", record_id)
    if not record:
        flash("Cliente não encontrado.", "error")
        return redirect(url_for("clients"))
    return render_template("entity_detail.html", title="Detalhes do cliente", subtitle="Informações cadastradas", record=record, details=[("Nome", record.get("nome")), ("CPF", record.get("cpf")), ("Telefone", record.get("telefone")), ("E-mail", record.get("email")), ("Endereço", record.get("endereco")), ("Status", "Ativo" if db._is_active(record) else "Inativo"), ("Criado em", date_br(record.get("criado_em")))], back_url=url_for("clients"), edit_url=url_for("edit_client", record_id=record_id))


@app.post("/clientes/<int:record_id>/excluir")
@feature_required("ac2")
def delete_client(record_id: int):
    try:
        result = db.delete_or_deactivate("Clientes", record_id)
        flash("Cliente inativado por possuir pedidos." if result == "inativado" else "Cliente excluído com sucesso.", "success")
    except DataError as exc:
        flash(str(exc), "error")
    return redirect(url_for("clients"))


def validate_required(value: str | None, field_name: str) -> None:
    if not (value or "").strip():
        raise DataError(f"Informe o campo {field_name}.")


def client_values(include_created: bool = True) -> dict[str, Any]:
    values = {
        "nome": request.form.get("nome", "").strip(),
        "cpf": request.form.get("cpf", "").strip(),
        "telefone": request.form.get("telefone", "").strip(),
        "email": request.form.get("email", "").strip(),
        "endereco": request.form.get("endereco", "").strip(),
        "ativo": form_bool("ativo"),
    }
    if include_created:
        values["criado_em"] = now_value()
    return values


def client_fields() -> list[dict[str, Any]]:
    return [
        {"name": "nome", "label": "Nome", "type": "text", "required": True},
        {"name": "cpf", "label": "CPF", "type": "text"},
        {"name": "telefone", "label": "Telefone", "type": "text"},
        {"name": "email", "label": "E-mail", "type": "email"},
        {"name": "endereco", "label": "Endereço", "type": "text"},
        {"name": "ativo", "label": "Cliente ativo", "type": "checkbox", "default": True},
    ]


@app.route("/fornecedores")
@feature_required("ac3")
def suppliers():
    query = request.args.get("q", "").strip().lower()
    records = db.list_records("Fornecedores")
    if query:
        records = [row for row in records if query in " ".join(str(row.get(field) or "") for field in ("nome", "cnpj", "telefone", "email")).lower()]
    return render_template("entity_list.html", title="Fornecedores", subtitle="AC3 · Parceiros que abastecem a lanchonete", create_url=url_for("new_supplier"), list_url=url_for("suppliers"), search=query, rows=records, columns=[("id", "ID"), ("nome", "Nome"), ("cnpj", "CNPJ"), ("telefone", "Telefone"), ("email", "E-mail"), ("ativo", "Status")], entity="fornecedor")


@app.route("/fornecedores/novo", methods=["GET", "POST"])
@feature_required("ac3")
def new_supplier():
    if request.method == "POST":
        try:
            validate_required(request.form.get("nome"), "Nome")
            db.insert("Fornecedores", supplier_values())
            flash("Fornecedor cadastrado com sucesso.", "success")
            return redirect(url_for("suppliers"))
        except DataError as exc:
            flash(str(exc), "error")
    return render_template("entity_form.html", title="Novo fornecedor", subtitle="Cadastre os dados do fornecedor.", back_url=url_for("suppliers"), action_url=url_for("new_supplier"), fields=supplier_fields(), values=request.form)


@app.route("/fornecedores/<int:record_id>/editar", methods=["GET", "POST"])
@feature_required("ac3")
def edit_supplier(record_id: int):
    record = db.get("Fornecedores", record_id)
    if not record:
        flash("Fornecedor não encontrado.", "error")
        return redirect(url_for("suppliers"))
    if request.method == "POST":
        try:
            validate_required(request.form.get("nome"), "Nome")
            db.update("Fornecedores", record_id, supplier_values(False))
            flash("Fornecedor atualizado com sucesso.", "success")
            return redirect(url_for("suppliers"))
        except DataError as exc:
            flash(str(exc), "error")
            record = {**record, **request.form.to_dict()}
    return render_template("entity_form.html", title="Alterar fornecedor", subtitle="Atualize os dados do fornecedor.", back_url=url_for("suppliers"), action_url=url_for("edit_supplier", record_id=record_id), fields=supplier_fields(), values=record)


@app.route("/fornecedores/<int:record_id>")
@feature_required("ac3")
def view_supplier(record_id: int):
    record = db.get("Fornecedores", record_id)
    if not record:
        flash("Fornecedor não encontrado.", "error")
        return redirect(url_for("suppliers"))
    return render_template("entity_detail.html", title="Detalhes do fornecedor", subtitle="Informações cadastradas", record=record, details=[("Nome", record.get("nome")), ("CNPJ", record.get("cnpj")), ("Telefone", record.get("telefone")), ("E-mail", record.get("email")), ("Endereço", record.get("endereco")), ("Status", "Ativo" if db._is_active(record) else "Inativo"), ("Criado em", date_br(record.get("criado_em")))], back_url=url_for("suppliers"), edit_url=url_for("edit_supplier", record_id=record_id))


@app.post("/fornecedores/<int:record_id>/excluir")
@feature_required("ac3")
def delete_supplier(record_id: int):
    try:
        result = db.delete_or_deactivate("Fornecedores", record_id)
        flash("Fornecedor inativado por possuir produtos vinculados." if result == "inativado" else "Fornecedor excluído com sucesso.", "success")
    except DataError as exc:
        flash(str(exc), "error")
    return redirect(url_for("suppliers"))


def supplier_values(include_created: bool = True) -> dict[str, Any]:
    values = {"nome": request.form.get("nome", "").strip(), "cnpj": request.form.get("cnpj", "").strip(), "telefone": request.form.get("telefone", "").strip(), "email": request.form.get("email", "").strip(), "endereco": request.form.get("endereco", "").strip(), "ativo": form_bool("ativo")}
    if include_created:
        values["criado_em"] = now_value()
    return values


def supplier_fields() -> list[dict[str, Any]]:
    return [{"name": "nome", "label": "Nome / Razão social", "type": "text", "required": True}, {"name": "cnpj", "label": "CNPJ", "type": "text"}, {"name": "telefone", "label": "Telefone", "type": "text"}, {"name": "email", "label": "E-mail", "type": "email"}, {"name": "endereco", "label": "Endereço", "type": "text"}, {"name": "ativo", "label": "Fornecedor ativo", "type": "checkbox", "default": True}]


@app.route("/filiais")
@feature_required("final")
def branches():
    query = request.args.get("q", "").strip().lower()
    records = db.list_records("Filiais")
    if query:
        records = [row for row in records if query in " ".join(str(row.get(field) or "") for field in ("nome", "cidade", "uf", "cnpj")).lower()]
    return render_template("entity_list.html", title="Filiais", subtitle="Prova final · Unidades da lanchonete", create_url=url_for("new_branch"), list_url=url_for("branches"), search=query, rows=records, columns=[("id", "ID"), ("nome", "Filial"), ("cidade", "Cidade"), ("uf", "UF"), ("telefone", "Telefone"), ("ativo", "Status")], entity="filial")


@app.route("/filiais/novo", methods=["GET", "POST"])
@feature_required("final")
def new_branch():
    if request.method == "POST":
        try:
            validate_required(request.form.get("nome"), "Nome")
            db.insert("Filiais", branch_values())
            flash("Filial cadastrada com sucesso.", "success")
            return redirect(url_for("branches"))
        except DataError as exc:
            flash(str(exc), "error")
    return render_template("entity_form.html", title="Nova filial", subtitle="Cadastre uma unidade da lanchonete.", back_url=url_for("branches"), action_url=url_for("new_branch"), fields=branch_fields(), values=request.form)


@app.route("/filiais/<int:record_id>/editar", methods=["GET", "POST"])
@feature_required("final")
def edit_branch(record_id: int):
    record = db.get("Filiais", record_id)
    if not record:
        flash("Filial não encontrada.", "error")
        return redirect(url_for("branches"))
    if request.method == "POST":
        try:
            validate_required(request.form.get("nome"), "Nome")
            db.update("Filiais", record_id, branch_values(False))
            flash("Filial atualizada com sucesso.", "success")
            return redirect(url_for("branches"))
        except DataError as exc:
            flash(str(exc), "error")
            record = {**record, **request.form.to_dict()}
    return render_template("entity_form.html", title="Alterar filial", subtitle="Atualize os dados da filial.", back_url=url_for("branches"), action_url=url_for("edit_branch", record_id=record_id), fields=branch_fields(), values=record)


@app.route("/filiais/<int:record_id>")
@feature_required("final")
def view_branch(record_id: int):
    record = db.get("Filiais", record_id)
    if not record:
        flash("Filial não encontrada.", "error")
        return redirect(url_for("branches"))
    return render_template("entity_detail.html", title="Detalhes da filial", subtitle="Informações cadastradas", record=record, details=[("Nome", record.get("nome")), ("CNPJ", record.get("cnpj")), ("Telefone", record.get("telefone")), ("Endereço", record.get("endereco")), ("Cidade", record.get("cidade")), ("UF", record.get("uf")), ("Status", "Ativa" if db._is_active(record) else "Inativa"), ("Criada em", date_br(record.get("criado_em")))], back_url=url_for("branches"), edit_url=url_for("edit_branch", record_id=record_id))


@app.post("/filiais/<int:record_id>/excluir")
@feature_required("final")
def delete_branch(record_id: int):
    try:
        result = db.delete_or_deactivate("Filiais", record_id)
        flash("Filial inativada por possuir pedidos." if result == "inativado" else "Filial excluída com sucesso.", "success")
    except DataError as exc:
        flash(str(exc), "error")
    return redirect(url_for("branches"))


def branch_values(include_created: bool = True) -> dict[str, Any]:
    values = {"nome": request.form.get("nome", "").strip(), "cnpj": request.form.get("cnpj", "").strip(), "telefone": request.form.get("telefone", "").strip(), "endereco": request.form.get("endereco", "").strip(), "cidade": request.form.get("cidade", "").strip(), "uf": request.form.get("uf", "").strip().upper(), "ativo": form_bool("ativo")}
    if include_created:
        values["criado_em"] = now_value()
    return values


def branch_fields() -> list[dict[str, Any]]:
    return [{"name": "nome", "label": "Nome da filial", "type": "text", "required": True}, {"name": "cnpj", "label": "CNPJ", "type": "text"}, {"name": "telefone", "label": "Telefone", "type": "text"}, {"name": "endereco", "label": "Endereço", "type": "text"}, {"name": "cidade", "label": "Cidade", "type": "text", "required": True}, {"name": "uf", "label": "UF", "type": "text", "required": True, "maxlength": 2}, {"name": "ativo", "label": "Filial ativa", "type": "checkbox", "default": True}]


@app.route("/pedidos")
@feature_required("final")
def orders():
    status = request.args.get("status", "").strip().upper()
    records = db.enriched_orders()
    if status:
        records = [row for row in records if str(row.get("status")).upper() == status]
    return render_template("orders/list.html", title="Pedidos", subtitle="Prova final · Criação e acompanhamento de pedidos", rows=records, status=status)


@app.route("/pedidos/novo", methods=["GET", "POST"])
@feature_required("final")
def new_order():
    clients = db.list_records("Clientes", active_only=True)
    branches_list = db.list_records("Filiais", active_only=True)
    products_list = db.list_records("Produtos", active_only=True)
    if request.method == "POST":
        try:
            client_id = parse_integer(request.form.get("id_cliente"), "Cliente")
            branch_id = parse_integer(request.form.get("id_filial"), "Filial")
            product_ids = request.form.getlist("produto_id[]")
            quantities = request.form.getlist("quantidade[]")
            items = []
            for product_id, quantity in zip(product_ids, quantities):
                if product_id:
                    items.append((parse_integer(product_id, "Produto"), parse_integer(quantity, "Quantidade")))
            order = db.create_order(client_id, branch_id, items, request.form.get("observacao", ""))
            flash(f"Pedido {order['numero']} criado com sucesso.", "success")
            return redirect(url_for("view_order", order_id=order["id"]))
        except (DataError, ValueError) as exc:
            flash(str(exc), "error")
    return render_template("orders/form.html", clients=clients, branches=branches_list, products=products_list, values=request.form)


@app.route("/pedidos/<int:order_id>")
@feature_required("final")
def view_order(order_id: int):
    details = db.order_details(order_id)
    if not details:
        flash("Pedido não encontrado.", "error")
        return redirect(url_for("orders"))
    return render_template("orders/detail.html", details=details)


@app.post("/pedidos/<int:order_id>/efetivar")
@feature_required("final")
def finalize_order(order_id: int):
    try:
        order = db.finalize_order(order_id)
        flash(f"Pedido {order['numero']} efetivado e estoque atualizado.", "success")
    except DataError as exc:
        flash(str(exc), "error")
    return redirect(url_for("view_order", order_id=order_id))


@app.post("/pedidos/<int:order_id>/cancelar")
@feature_required("final")
def cancel_order(order_id: int):
    try:
        order = db.cancel_order(order_id)
        flash(f"Pedido {order['numero']} cancelado.", "success")
    except DataError as exc:
        flash(str(exc), "error")
    return redirect(url_for("view_order", order_id=order_id))


@app.route("/documentacao")
@feature_required("final")
def documentation():
    return render_template("documentation.html")


if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=True)
