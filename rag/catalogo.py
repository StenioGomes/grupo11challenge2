"""
Leitura e validação do catálogo de fontes (fontes/catalogo.yaml).

O catálogo é a "fonte da verdade" da base de conhecimento curada. Validar
os campos logo no início evita descobrir, no meio da ingestão, que uma
fonte não tem URL ou que dois documentos têm o mesmo id.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path

import yaml

from . import config

CAMPOS_OBRIGATORIOS = ["id", "titulo", "instituicao", "ano", "url", "formato", "idioma", "eixo"]
FORMATOS_VALIDOS = {"pdf", "html"}


@dataclass(frozen=True)
class Fonte:
    id: str
    titulo: str
    instituicao: str
    ano: int
    url: str
    formato: str
    idioma: str
    eixo: str
    foco_mulheres: bool = False
    por_que: str = ""
    alternativas: tuple = ()

    @property
    def urls(self) -> list[str]:
        """URL principal seguida das alternativas, na ordem em que são tentadas."""
        return [self.url, *self.alternativas]

    @property
    def caminho_bruto(self) -> Path:
        """
        Arquivo baixado em data/raw/. Se a fonte veio de uma URL alternativa
        em outro formato (ex.: lei em PDF em vez de HTML), usa o que existir.
        """
        preferido = config.DIR_BRUTOS / f"{self.id}.{self.formato}"
        if preferido.exists():
            return preferido
        for ext in ("pdf", "html"):
            outro = config.DIR_BRUTOS / f"{self.id}.{ext}"
            if outro.exists():
                return outro
        return preferido

    def metadados(self) -> dict:
        """Metadados que serão copiados para CADA chunk desta fonte."""
        dados = asdict(self)
        dados["fonte_id"] = dados.pop("id")
        dados.pop("por_que", None)
        dados.pop("alternativas", None)
        return dados


def carregar_catalogo(caminho: Path = config.CATALOGO) -> list[Fonte]:
    with open(caminho, encoding="utf-8") as f:
        bruto = yaml.safe_load(f)

    fontes: list[Fonte] = []
    vistos: set[str] = set()
    for i, item in enumerate(bruto.get("fontes", []), start=1):
        faltando = [c for c in CAMPOS_OBRIGATORIOS if not item.get(c)]
        if faltando:
            raise ValueError(f"Fonte #{i} ({item.get('id')}) sem campos: {faltando}")
        if item["id"] in vistos:
            raise ValueError(f"id duplicado no catálogo: {item['id']}")
        if item["formato"] not in FORMATOS_VALIDOS:
            raise ValueError(f"{item['id']}: formato inválido '{item['formato']}'")
        vistos.add(item["id"])
        fontes.append(
            Fonte(
                id=item["id"],
                titulo=item["titulo"],
                instituicao=item["instituicao"],
                ano=int(item["ano"]),
                url=item["url"],
                formato=item["formato"],
                idioma=item["idioma"],
                eixo=item["eixo"],
                foco_mulheres=bool(item.get("foco_mulheres", False)),
                por_que=item.get("por_que", ""),
                alternativas=tuple(item.get("alternativas") or ()),
            )
        )
    return fontes


def por_id(fontes: list[Fonte]) -> dict[str, Fonte]:
    return {f.id: f for f in fontes}
