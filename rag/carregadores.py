"""
ETAPA 1 DA INGESTÃO: carregar (extrair texto) dos arquivos brutos.

Saída comum para qualquer formato: uma lista de "Unidades", cada uma com
texto + localização dentro do documento. A localização é o que depois
permite citar "p. 12" (PDF) ou "seção Art. 7º" (HTML).

- PDF  -> uma unidade por PÁGINA  (localizador = número da página)
- HTML -> uma unidade por SEÇÃO   (localizador = título h1..h4 mais próximo)
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import logging

from bs4 import BeautifulSoup
from pypdf import PdfReader

# O pypdf avisa sobre fontes que não consegue analisar por completo
# ("fontTools is required..."). O texto é extraído mesmo assim; o aviso só
# polui o terminal, então mostramos apenas erros de verdade.
logging.getLogger("pypdf").setLevel(logging.ERROR)


@dataclass
class Unidade:
    texto: str
    pagina: int | None = None   # 1-based, só para PDF
    secao: str | None = None    # só para HTML


# --------------------------------------------------------------------------
# PDF
# --------------------------------------------------------------------------
def carregar_pdf(caminho: Path) -> list[Unidade]:
    leitor = PdfReader(str(caminho))
    unidades = []
    for numero, pagina in enumerate(leitor.pages, start=1):
        try:
            texto = pagina.extract_text() or ""
        except Exception as erro:  # páginas corrompidas não devem derrubar o documento todo
            print(f"    aviso: falha ao extrair p.{numero} de {caminho.name}: {erro}")
            texto = ""
        unidades.append(Unidade(texto=texto, pagina=numero))
    return unidades


# --------------------------------------------------------------------------
# HTML
# --------------------------------------------------------------------------
# Elementos que quase nunca são conteúdo: menus, rodapés, scripts...
# <strike>/<s>/<del>: nas leis do Planalto, texto riscado = dispositivo REVOGADO.
# Se ficasse na base, o RAG poderia "citar" uma regra que não vale mais.
_TAGS_RUIDO = [
    "script", "style", "noscript", "nav", "header", "footer", "aside",
    "form", "button", "iframe", "svg", "strike", "s", "del",
]
_TAGS_TITULO = {"h1", "h2", "h3", "h4"}
_TAGS_TEXTO = {"p", "li", "td", "th", "blockquote", "dd", "dt", "pre"}
# Em textos legais, cada artigo funciona como um "título": "Art. 7º", "Art. 104-A"...
_INICIO_ARTIGO = re.compile(r"^(Art\.?\s*\d+[º°o]?(?:-[A-Z])?)", re.IGNORECASE)


def _ler_html(caminho: Path) -> BeautifulSoup:
    bruto = caminho.read_bytes()
    # BeautifulSoup detecta a codificação (o Planalto ainda usa windows-1252)
    return BeautifulSoup(bruto, "html.parser")


def carregar_html(caminho: Path) -> list[Unidade]:
    sopa = _ler_html(caminho)
    for tag in sopa(_TAGS_RUIDO):
        tag.decompose()

    # Tenta isolar o conteúdo principal; se a página não marcar, usa o body.
    raiz = sopa.find("main") or sopa.find("article") or sopa.body or sopa

    unidades: list[Unidade] = []
    secao_atual = None
    buffer: list[str] = []

    def descarregar():
        texto = "\n".join(buffer).strip()
        if texto:
            unidades.append(Unidade(texto=texto, secao=secao_atual))
        buffer.clear()

    for elemento in raiz.find_all(list(_TAGS_TITULO | _TAGS_TEXTO)):
        # evita duplicar texto de <p> dentro de <li> (só pega folhas de texto)
        if elemento.name in _TAGS_TEXTO and elemento.find(list(_TAGS_TEXTO)):
            continue
        texto = elemento.get_text(" ", strip=True)
        if not texto:
            continue
        artigo = _INICIO_ARTIGO.match(texto)
        if elemento.name in _TAGS_TITULO:
            descarregar()
            secao_atual = texto[:120]
            buffer.append(texto)  # o título também vai para o texto (ajuda a busca)
        elif artigo:
            descarregar()
            secao_atual = artigo.group(1)
            buffer.append(texto)
        else:
            buffer.append(texto)
    descarregar()

    # Páginas sem marcação semântica (ex.: leis do Planalto usam só <p>):
    # tudo cai em uma única unidade sem seção. Tudo bem: o chunking divide depois.
    if not unidades:
        texto = raiz.get_text("\n", strip=True)
        if texto:
            unidades.append(Unidade(texto=texto))
    return unidades


def detectar_formato(caminho: Path) -> str:
    """Decide pelo conteúdo (bytes iniciais), não pela extensão."""
    with open(caminho, "rb") as f:
        return "pdf" if f.read(5) == b"%PDF-" else "html"


def carregar(caminho: Path, formato: str | None = None) -> list[Unidade]:
    formato = detectar_formato(caminho)
    if formato == "pdf":
        return carregar_pdf(caminho)
    if formato == "html":
        return carregar_html(caminho)
    raise ValueError(f"Formato não suportado: {formato}")
