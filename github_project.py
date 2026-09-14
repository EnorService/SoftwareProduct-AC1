from __future__ import annotations

import json
import unicodedata
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from config import (
    GITHUB_API_URL,
    GITHUB_PROJECT_NUMBER,
    GITHUB_PROJECT_OWNER,
    GITHUB_PROJECT_OWNER_TYPE,
    GITHUB_TOKEN,
)


class GitHubProjectError(RuntimeError):
    """Erro amigável de comunicação ou configuração do GitHub Projects."""


def _fold(value: Any) -> str:
    text = str(value or "").strip()
    return "".join(
        char
        for char in unicodedata.normalize("NFKD", text)
        if not unicodedata.combining(char)
    ).lower()


def normalize_board_status(value: Any) -> str:
    """Converte o status do GitHub para os três status do board local."""
    status = _fold(value)
    if status in {"done", "complete", "completed", "concluido", "concluida", "finalizado", "finalizada"}:
        return "CONCLUIDO"
    if status in {"in progress", "inprogress", "doing", "em progresso", "em andamento"}:
        return "EM_PROGRESSO"
    return "NAO_INICIADO"


class GitHubProjectsClient:
    """Cliente mínimo para leitura e atualização de um GitHub Project v2."""

    def __init__(self) -> None:
        self.token = (GITHUB_TOKEN or "").strip()
        self.owner = (GITHUB_PROJECT_OWNER or "").strip()
        self.owner_type = (GITHUB_PROJECT_OWNER_TYPE or "user").strip().lower()
        try:
            self.project_number = int(GITHUB_PROJECT_NUMBER) if GITHUB_PROJECT_NUMBER else None
        except (TypeError, ValueError):
            self.project_number = None

    @property
    def configured(self) -> bool:
        return bool(
            self.token
            and self.owner
            and self.project_number
            and self.owner_type in {"user", "organization"}
        )

    @property
    def project_url(self) -> str | None:
        if not self.owner or not self.project_number:
            return None
        prefix = "orgs" if self.owner_type == "organization" else "users"
        return f"https://github.com/{prefix}/{quote(self.owner)}/projects/{self.project_number}"

    def _require_configuration(self) -> None:
        if self.owner_type not in {"user", "organization"}:
            raise GitHubProjectError("GITHUB_PROJECT_OWNER_TYPE deve ser 'user' ou 'organization'.")
        if not self.token:
            raise GitHubProjectError("Configure LANCHONETE_GITHUB_TOKEN no arquivo .env.")
        if not self.owner:
            raise GitHubProjectError("Configure LANCHONETE_GITHUB_OWNER no arquivo .env.")
        if not self.project_number:
            raise GitHubProjectError("Configure LANCHONETE_GITHUB_PROJECT_NUMBER no arquivo .env.")

    def _graphql(self, query: str, variables: dict[str, Any]) -> dict[str, Any]:
        self._require_configuration()
        payload = json.dumps({"query": query, "variables": variables}).encode("utf-8")
        http_request = Request(
            GITHUB_API_URL,
            data=payload,
            method="POST",
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
                "User-Agent": "LanchoneteAgil-GitHubProjects",
            },
        )
        try:
            with urlopen(http_request, timeout=25) as response:
                body = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            try:
                details = exc.read().decode("utf-8")
            except Exception:
                details = ""
            raise GitHubProjectError(
                f"O GitHub recusou a solicitação ({exc.code}). {details[:240]}"
            ) from exc
        except URLError as exc:
            raise GitHubProjectError(
                "Não foi possível acessar o GitHub. Verifique sua internet e tente novamente."
            ) from exc
        except (TimeoutError, json.JSONDecodeError) as exc:
            raise GitHubProjectError("O GitHub não retornou uma resposta válida.") from exc

        errors = body.get("errors") or []
        if errors:
            message = "; ".join(str(error.get("message") or "Erro GraphQL") for error in errors)
            raise GitHubProjectError(message)
        return body.get("data") or {}

    def fetch_project_items(self) -> dict[str, Any]:
        """Consulta o projeto, seus status e todos os itens visíveis."""
        root = self.owner_type
        query = f"""
        query($login: String!, $number: Int!, $after: String) {{
          {root}(login: $login) {{
            projectV2(number: $number) {{
              id
              number
              title
              fields(first: 100) {{
                nodes {{
                  ... on ProjectV2SingleSelectField {{
                    id
                    name
                    options {{ id name }}
                  }}
                }}
              }}
              items(first: 100, after: $after) {{
                pageInfo {{ hasNextPage endCursor }}
                nodes {{
                  id
                  content {{
                    __typename
                    ... on DraftIssue {{ title body }}
                    ... on Issue {{ title body number url repository {{ nameWithOwner }} }}
                    ... on PullRequest {{ title body number url repository {{ nameWithOwner }} }}
                  }}
                  fieldValues(first: 50) {{
                    nodes {{
                      ... on ProjectV2ItemFieldSingleSelectValue {{
                        name
                        field {{
                          ... on ProjectV2SingleSelectField {{ name }}
                        }}
                      }}
                    }}
                  }}
                }}
              }}
            }}
          }}
        }}
        """

        after: str | None = None
        project: dict[str, Any] | None = None
        raw_items: list[dict[str, Any]] = []

        while True:
            data = self._graphql(
                query,
                {"login": self.owner, "number": self.project_number, "after": after},
            )
            owner_data = data.get(root) or {}
            current_project = owner_data.get("projectV2")
            if not current_project:
                raise GitHubProjectError(
                    "Não encontrei esse GitHub Project. Confira o usuário/organização e o número do projeto."
                )
            if project is None:
                project = current_project
            page = current_project.get("items") or {}
            raw_items.extend(page.get("nodes") or [])
            page_info = page.get("pageInfo") or {}
            if not page_info.get("hasNextPage"):
                break
            after = page_info.get("endCursor")
            if not after:
                break

        assert project is not None
        status_field = next(
            (
                field
                for field in (project.get("fields", {}).get("nodes") or [])
                if _fold(field.get("name")) == "status"
            ),
            None,
        )
        status_options = [
            {
                "id": option.get("id"),
                "name": option.get("name") or "",
                "key": normalize_board_status(option.get("name")),
            }
            for option in ((status_field or {}).get("options") or [])
        ]

        normalized_items: list[dict[str, Any]] = []
        for item in raw_items:
            content = item.get("content") or {}
            title = str(content.get("title") or "").strip()
            if not title:
                continue

            remote_status = ""
            for field_value in (item.get("fieldValues", {}).get("nodes") or []):
                field = field_value.get("field") or {}
                if _fold(field.get("name")) == "status":
                    remote_status = str(field_value.get("name") or "").strip()
                    break

            remote_status_key = normalize_board_status(remote_status)
            selected_option = next(
                (
                    option
                    for option in status_options
                    if option.get("key") == remote_status_key
                ),
                None,
            )
            repository = (content.get("repository") or {}).get("nameWithOwner")
            normalized_items.append(
                {
                    "github_item_id": item.get("id"),
                    "github_project_id": project.get("id"),
                    "github_status_field_id": (status_field or {}).get("id"),
                    "github_status_option_id": (selected_option or {}).get("id"),
                    "github_item_type": content.get("__typename") or "Item",
                    "github_issue_number": content.get("number"),
                    "github_repository": repository or "",
                    "github_url": content.get("url") or self.project_url or "",
                    "github_status": remote_status or "Sem status",
                    "titulo": title,
                    "descricao": str(content.get("body") or "").strip(),
                    "status": remote_status_key,
                }
            )

        return {
            "project": {
                "id": project.get("id"),
                "number": project.get("number"),
                "title": project.get("title") or "GitHub Project",
            },
            "status_options": status_options,
            "items": normalized_items,
        }

    def update_item_status(self, item: dict[str, Any], local_status: str) -> dict[str, str]:
        """Atualiza no GitHub o status de um item que veio do Project."""
        snapshot = self.fetch_project_items()
        option = next(
            (
                option
                for option in snapshot["status_options"]
                if option["key"] == local_status
            ),
            None,
        )
        if not option:
            raise GitHubProjectError(
                "O seu Project não possui uma opção de status compatível com esse board."
            )

        project_id = item.get("github_project_id") or snapshot["project"].get("id")
        field_id = item.get("github_status_field_id")
        if not field_id:
            raise GitHubProjectError("Não encontrei o campo Status do GitHub Project.")

        mutation = """
        mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $optionId: String!) {
          updateProjectV2ItemFieldValue(
            input: {
              projectId: $projectId
              itemId: $itemId
              fieldId: $fieldId
              value: { singleSelectOptionId: $optionId }
            }
          ) {
            projectV2Item { id }
          }
        }
        """
        self._graphql(
            mutation,
            {
                "projectId": project_id,
                "itemId": item.get("github_item_id"),
                "fieldId": field_id,
                "optionId": option["id"],
            },
        )
        return {"name": option["name"], "id": option["id"]}
