"""
ETAPA 2 DA INGESTÃO: limpeza / normalização do texto extraído.

Texto que sai de PDF é "sujo": hifenização de fim de linha, quebras de
linha no meio de frases, cabeçalhos e rodapés repetidos em toda página,
espaços duplicados. Esse ruído atrapalha o embedding (o vetor passa a
representar "Banco Central do Brasil – página 12" em vez do conteúdo) e
desperdiça espaço no contexto do LLM.

Regra de ouro: limpar o suficiente para melhorar a recuperação, sem
reescrever o conteúdo (a citação precisa continuar fiel à fonte).
"""

from __future__ import annotations

import re
import unicodedata
from collections import Counter

from .carregadores import Unidade

_HIFEN_FIM_LINHA = re.compile(r"(\w)-\n(\w)")           # "finan-\nças" -> "finanças"
_QUEBRA_NO_MEIO = re.compile(r"(?<![.:;!?\n])\n(?!\n)")  # quebra simples dentro de parágrafo
_ESPACOS = re.compile(r"[ \t\u00a0]+")
_MUITAS_QUEBRAS = re.compile(r"\n{3,}")
_SO_NUMERO = re.compile(r"^\s*[-–]?\s*\d{1,4}\s*[-–]?\s*$")  # linhas que são só nº de página
_CONTROLE = re.compile(r"[\u0000-\u0008\u000b\u000c\u000e-\u001f\u200b\ufeff]")


def normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFC", texto)   # acentos em forma canônica
    texto = _CONTROLE.sub("", texto)
    texto = texto.replace("\r\n", "\n").replace("\r", "\n")
    texto = texto.replace("●", "•").replace("\uf0b7", "•")
    texto = _HIFEN_FIM_LINHA.sub(r"\1\2", texto)
    texto = _ESPACOS.sub(" ", texto)
    linhas = [l.strip() for l in texto.split("\n")]
    linhas = [l for l in linhas if not _SO_NUMERO.match(l)]
    texto = "\n".join(linhas)
    texto = _QUEBRA_NO_MEIO.sub(" ", texto)
    texto = _MUITAS_QUEBRAS.sub("\n\n", texto)
    return texto.strip()


def linhas_repetidas(unidades: list[Unidade], fracao_minima: float = 0.5) -> set[str]:
    """
    Detecta cabeçalhos/rodapés: linhas curtas que aparecem em pelo menos
    `fracao_minima` das páginas do documento.
    """
    if len(unidades) < 4:  # documento curto: não dá para inferir padrão
        return set()
    contagem: Counter[str] = Counter()
    for u in unidades:
        linhas = {l.strip() for l in u.texto.split("\n") if 0 < len(l.strip()) <= 120}
        contagem.update(linhas)
    limite = max(3, int(len(unidades) * fracao_minima))
    return {linha for linha, n in contagem.items() if n >= limite}


def limpar_unidades(unidades: list[Unidade]) -> list[Unidade]:
    repetidas = linhas_repetidas(unidades)
    limpas = []
    for u in unidades:
        linhas = [l for l in u.texto.split("\n") if l.strip() not in repetidas]
        texto = normalizar("\n".join(linhas))
        if texto:
            limpas.append(Unidade(texto=texto, pagina=u.pagina, secao=u.secao))
    return limpas
