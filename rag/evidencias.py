"""
CONSULTA – PASSO 3: evidências e rastreabilidade.

Gera o registro completo de uma consulta, em Markdown (para ler/entregar)
e JSON (para análise), contendo:
  - a pergunta e a configuração usada (modelos, k, limiar...);
  - TODOS os candidatos recuperados, com similaridade e se foram usados;
  - a resposta gerada;
  - a tabela "citação -> documento, página/seção, URL";
  - alertas de qualidade (resposta sem citações, citações inválidas).
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from . import config
from .geracao import Resposta
from .recuperacao import Trecho


def _resumir(texto: str, n: int = 350) -> str:
    corpo = texto.split("\n", 1)[-1]  # remove o cabeçalho contextual
    corpo = " ".join(corpo.split())
    return corpo if len(corpo) <= n else corpo[:n].rsplit(" ", 1)[0] + " …"


def markdown(resposta: Resposta, candidatos: list[Trecho]) -> str:
    agora = datetime.now().strftime("%d/%m/%Y %H:%M")
    ids_usados = {t.chunk_id for t in resposta.trechos}
    linhas = [
        f"# Demonstração RAG – {agora}",
        "",
        "## 1. Consulta submetida",
        "",
        f"> {resposta.pergunta}",
        "",
        "Configuração: " + ", ".join(f"`{k}={v}`" for k, v in config.resumo().items()),
        "",
        "## 2. Recuperação",
        "",
        f"Foram buscados {len(candidatos)} candidatos; {len(resposta.trechos)} passaram pelo "
        f"limiar de similaridade ({config.LIMIAR_SIMILARIDADE}) e pelo limite de "
        f"{config.MAX_POR_FONTE} trechos por fonte, e foram enviados ao LLM.",
        "",
        "| Rank | Similaridade | Enviado ao LLM | Fonte | Local |",
        "|---:|---:|:---:|---|---|",
    ]
    for t in candidatos[:15]:
        enviado = "✅" if t.chunk_id in ids_usados else "—"
        linhas.append(f"| {t.rank} | {t.similaridade:.3f} | {enviado} | {t.titulo} ({t.instituicao}) | {t.localizador} |")

    linhas += ["", "### Trechos enviados ao LLM (contexto)", ""]
    for i, t in enumerate(resposta.trechos, start=1):
        linhas += [f"**[{i}]** {t.referencia()} — similaridade {t.similaridade:.3f}", "", f"> {_resumir(t.texto)}", ""]

    linhas += ["## 3. Resposta fundamentada", "", resposta.texto, ""]

    linhas += ["## 4. Evidência das fontes utilizadas", ""]
    if resposta.fontes_citadas:
        linhas += ["| Citação | Documento | Instituição | Local | Link |", "|:---:|---|---|---|---|"]
        for n in resposta.citados:
            t = resposta.trechos[n - 1]
            linhas.append(f"| [{n}] | {t.titulo} | {t.instituicao} ({t.ano}) | {t.localizador} | [abrir]({t.url}) |")
    else:
        linhas.append("_Nenhuma fonte citada._")

    nao_citados = [i for i in range(1, len(resposta.trechos) + 1) if i not in resposta.citados]
    linhas += ["", "### Verificação automática", ""]
    linhas.append(f"- Resposta fundamentada (≥1 citação válida): **{'sim' if resposta.fundamentada else 'NÃO'}**")
    linhas.append(f"- Trechos citados: {resposta.citados or 'nenhum'}")
    linhas.append(f"- Trechos enviados mas não citados: {nao_citados or 'nenhum'}")
    if resposta.citacoes_invalidas:
        linhas.append(f"- ⚠️ Citações que não correspondem a nenhum trecho: {resposta.citacoes_invalidas}")
    linhas.append(f"- Modelo gerador: `{resposta.modelo}`")
    return "\n".join(linhas) + "\n"


def salvar(resposta: Resposta, candidatos: list[Trecho], pasta: Path | None = None) -> tuple[Path, Path]:
    pasta = pasta or (config.DIR_SAIDAS / "demonstracoes")
    pasta.mkdir(parents=True, exist_ok=True)
    carimbo = datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_md = pasta / f"consulta_{carimbo}.md"
    caminho_json = pasta / f"consulta_{carimbo}.json"
    caminho_md.write_text(markdown(resposta, candidatos), encoding="utf-8")
    dados = {
        "data": carimbo,
        "configuracao": config.resumo(),
        "pergunta": resposta.pergunta,
        "resposta": resposta.texto,
        "fundamentada": resposta.fundamentada,
        "citados": resposta.citados,
        "citacoes_invalidas": resposta.citacoes_invalidas,
        "trechos_enviados": [t.to_dict() for t in resposta.trechos],
        "candidatos": [{k: v for k, v in t.to_dict().items() if k != "texto"} for t in candidatos],
    }
    caminho_json.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
    return caminho_md, caminho_json


def imprimir_trechos(trechos: list[Trecho]) -> None:
    for i, t in enumerate(trechos, start=1):
        print(f"  [{i}] sim={t.similaridade:.3f}  {t.referencia()}")
        print(f"       {_resumir(t.texto, 160)}")


def imprimir_fontes(resposta: Resposta) -> None:
    print("\nFONTES CITADAS:")
    if resposta.fontes_citadas:
        for n in resposta.citados:
            t = resposta.trechos[n - 1]
            print(f"  [{n}] {t.referencia()}\n       {t.url}")
    else:
        print("  (nenhuma)")
    if resposta.trechos and not resposta.fundamentada and resposta.modelo != "(nenhum)":
        print("\n  ⚠️  A resposta não contém citações válidas: trate-a como NÃO fundamentada.")
    if resposta.citacoes_invalidas:
        print(f"\n  ⚠️  Citações inválidas (não existem no contexto): {resposta.citacoes_invalidas}")
    print()


def imprimir(resposta: Resposta, candidatos: list[Trecho]) -> None:
    """Versão de terminal, compacta."""
    print("\n" + "=" * 78)
    print(f"PERGUNTA: {resposta.pergunta}")
    print("=" * 78)
    print("\nTRECHOS RECUPERADOS (enviados ao LLM):")
    for i, t in enumerate(resposta.trechos, start=1):
        print(f"  [{i}] sim={t.similaridade:.3f}  {t.referencia()}")
        print(f"       {_resumir(t.texto, 160)}")
    print("\nRESPOSTA:\n")
    print(resposta.texto)
    print("\nFONTES CITADAS:")
    if resposta.fontes_citadas:
        for n in resposta.citados:
            t = resposta.trechos[n - 1]
            print(f"  [{n}] {t.referencia()}\n       {t.url}")
    else:
        print("  (nenhuma)")
    if resposta.trechos and not resposta.fundamentada and resposta.modelo != "(nenhum)":
        print("\n  ⚠️  A resposta não contém citações válidas: trate-a como NÃO fundamentada.")
    if resposta.citacoes_invalidas:
        print(f"\n  ⚠️  Citações inválidas (não existem no contexto): {resposta.citacoes_invalidas}")
    print()
