"""
PASSO 0 – Coleta: baixa os documentos do catálogo para data/raw/.

    python baixar_fontes.py            # baixa só o que ainda não existe
    python baixar_fontes.py --forcar   # baixa tudo de novo
    python baixar_fontes.py --apenas lei_maria_da_penha

Comportamento:
- mostra o progresso de cada download (KB recebidos e tempo);
- cada URL tem um PRAZO TOTAL (padrão 120 s): servidor lento não trava o script;
- se a URL principal falhar, tenta as `alternativas` do catálogo, em ordem;
- detecta pelo conteúdo se recebeu PDF ou HTML e salva com a extensão certa;
- se o certificado HTTPS não puder ser verificado (comum em sites .gov.br/.mil.br
  com cadeia ICP-Brasil), tenta de novo sem verificação e REGISTRA isso no
  manifesto. A integridade do arquivo fica registrada pelo SHA-256.

O data/raw/manifesto.json guarda, para cada fonte, a URL que funcionou,
o tamanho, o SHA-256 e a data: é o registro de PROVENIÊNCIA da base.

Se ainda assim algum site bloquear, baixe pelo navegador e salve como
data/raw/<id>.pdf (ou .html). O pipeline usa o arquivo local normalmente.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import threading
import time
from datetime import datetime
from urllib.parse import urljoin

import requests
import urllib3
from bs4 import BeautifulSoup

from rag import config
from rag.catalogo import Fonte, carregar_catalogo

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CABECALHOS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/126.0 Safari/537.36",
    "Accept": "text/html,application/pdf;q=0.9,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
}
TIMEOUT_CONEXAO = 10      # s para abrir a conexão
TIMEOUT_LEITURA = 30      # s sem receber nenhum byte
MINIMO_SUCESSOS = 20


class PrazoEsgotado(Exception):
    pass


def _eh_pdf(conteudo: bytes) -> bool:
    return conteudo[:5] == b"%PDF-"


def _parece_pagina_de_erro(conteudo: bytes) -> bool:
    inicio = conteudo[:3000].lower()
    return len(conteudo) < 2000 or b"404" in inicio and b"not found" in inicio


def _procurar_link_pdf(html: bytes, url_base: str) -> str | None:
    """Páginas como as do gov.br mostram o PDF dentro de uma página HTML."""
    sopa = BeautifulSoup(html, "html.parser")
    for a in sopa.find_all("a", href=True):
        href = a["href"]
        if href.lower().split("?")[0].endswith(".pdf") or "@@download" in href:
            return urljoin(url_base, href)
    return None


def _get(url: str, sessao: requests.Session, prazo: float, verificar_ssl: bool) -> tuple[bytes, str]:
    """Download em blocos, com prazo total e progresso na mesma linha."""
    inicio = time.time()
    with sessao.get(url, headers=CABECALHOS, stream=True, allow_redirects=True,
                    timeout=(TIMEOUT_CONEXAO, TIMEOUT_LEITURA), verify=verificar_ssl) as resp:
        resp.raise_for_status()
        partes, recebido = [], 0
        for bloco in resp.iter_content(chunk_size=8 * 1024):
            partes.append(bloco)
            recebido += len(bloco)
            decorrido = time.time() - inicio
            print(f"\r      {recebido / 1024:8,.0f} KB  {decorrido:5.1f}s", end="", flush=True)
            if decorrido > prazo:
                raise PrazoEsgotado(f"passou de {prazo:.0f}s (servidor muito lento)")
        print("\r" + " " * 40 + "\r", end="", flush=True)
        return b"".join(partes), resp.url


def _get_com_ssl(url, sessao, prazo, avisos: list) -> tuple[bytes, str]:
    try:
        return _get(url, sessao, prazo, verificar_ssl=True)
    except requests.exceptions.SSLError:
        print("\r      certificado não verificável; tentando sem verificação SSL...", flush=True)
        avisos.append("ssl_nao_verificado")
        return _get(url, sessao, prazo, verificar_ssl=False)


def baixar_url(url: str, esperado: str, sessao: requests.Session, prazo: float, avisos: list) -> tuple[bytes, str, str]:
    conteudo, url_final = _get_com_ssl(url, sessao, prazo, avisos)
    if esperado == "pdf" and not _eh_pdf(conteudo):
        link = _procurar_link_pdf(conteudo, url_final)
        if not link:
            raise ValueError("esperava PDF, recebeu uma página HTML sem link para o PDF")
        conteudo, url_final = _get_com_ssl(link, sessao, prazo, avisos)
        if not _eh_pdf(conteudo):
            raise ValueError("o link encontrado também não devolveu um PDF")
    if not _eh_pdf(conteudo) and _parece_pagina_de_erro(conteudo):
        raise ValueError("página vazia ou de erro")
    formato = "pdf" if _eh_pdf(conteudo) else "html"
    return conteudo, url_final, formato


def _com_prazo_duro(funcao, prazo: float, *args):
    """
    Executa `funcao` numa thread e desiste depois de `prazo` segundos.
    Necessário porque um servidor que envia poucos bytes por vez nunca
    dispara o timeout de leitura do requests: sem isso, o script "trava".
    """
    resultado: dict = {}

    def alvo():
        try:
            resultado["valor"] = funcao(*args)
        except Exception as erro:  # repassa o erro para a thread principal
            resultado["erro"] = erro

    t = threading.Thread(target=alvo, daemon=True)
    t.start()
    t.join(prazo)
    if t.is_alive():
        raise PrazoEsgotado(f"sem concluir em {prazo:.0f}s (servidor lento ou travado)")
    if "erro" in resultado:
        raise resultado["erro"]
    return resultado["valor"]


def baixar(fonte: Fonte, sessao: requests.Session, prazo: float) -> dict:
    erros = []
    for i, url in enumerate(fonte.urls):
        rotulo = "principal" if i == 0 else f"alternativa {i}"
        print(f"    → {rotulo}: {url[:95]}", flush=True)
        avisos: list = []
        # numa alternativa aceitamos qualquer formato (ex.: lei em PDF em vez de HTML)
        esperado = fonte.formato if i == 0 else "qualquer"
        try:
            conteudo, url_final, formato = _com_prazo_duro(
                baixar_url, prazo + 5, url, esperado, sessao, prazo, avisos)
        except Exception as erro:
            print("\r" + " " * 40 + "\r", end="")
            print(f"      falhou: {str(erro)[:120]}", flush=True)
            erros.append(f"{url}: {erro}")
            continue

        for ext in ("pdf", "html"):  # remove versão antiga em outro formato
            antigo = config.DIR_BRUTOS / f"{fonte.id}.{ext}"
            if antigo.exists():
                antigo.unlink()
        destino = config.DIR_BRUTOS / f"{fonte.id}.{formato}"
        destino.write_bytes(conteudo)
        return {
            "id": fonte.id,
            "url_catalogo": fonte.url,
            "url_usada": url,
            "url_final": url_final,
            "formato": formato,
            "bytes": len(conteudo),
            "sha256": hashlib.sha256(conteudo).hexdigest(),
            "baixado_em": datetime.now().isoformat(timespec="seconds"),
            "avisos": avisos,
            "status": "ok",
        }
    raise RuntimeError(" | ".join(erros))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--forcar", action="store_true", help="baixa de novo mesmo se o arquivo existir")
    parser.add_argument("--apenas", nargs="*", help="ids específicos do catálogo")
    parser.add_argument("--prazo", type=float, default=120, help="tempo máximo por URL, em segundos (padrão 120)")
    args = parser.parse_args()

    config.DIR_BRUTOS.mkdir(parents=True, exist_ok=True)
    caminho_manifesto = config.DIR_BRUTOS / "manifesto.json"
    manifesto = json.loads(caminho_manifesto.read_text()) if caminho_manifesto.exists() else {}

    todas = carregar_catalogo()
    fontes = [f for f in todas if not args.apenas or f.id in set(args.apenas)]

    sessao = requests.Session()
    inicio = time.time()
    for n, f in enumerate(fontes, start=1):
        prefixo = f"[{n:2d}/{len(fontes)}] {f.id}"
        if f.caminho_bruto.exists() and not args.forcar:
            print(f"{prefixo}  = já existe ({f.caminho_bruto.stat().st_size / 1024:,.0f} KB)")
            manifesto.setdefault(f.id, {"id": f.id, "url_catalogo": f.url, "status": "ok (local)"})
            continue
        print(prefixo, flush=True)
        t0 = time.time()
        try:
            reg = baixar(f, requests.Session(), args.prazo)
            manifesto[f.id] = reg
            extra = "  (SSL não verificado)" if reg["avisos"] else ""
            print(f"    ✓ {reg['bytes'] / 1024:,.0f} KB, {reg['formato']}, {time.time() - t0:.1f}s{extra}")
        except Exception as erro:
            manifesto[f.id] = {"id": f.id, "url_catalogo": f.url, "status": f"erro: {erro}"}
            print(f"    ✗ todas as URLs falharam")
        # salva o manifesto a cada fonte: se você interromper, nada se perde
        caminho_manifesto.write_text(json.dumps(manifesto, ensure_ascii=False, indent=2), encoding="utf-8")
        time.sleep(0.3)

    disponiveis = [f for f in todas if f.caminho_bruto.exists()]
    print(f"\n{len(disponiveis)}/{len(todas)} documentos disponíveis em data/raw/  ({time.time() - inicio:.0f}s)")
    faltando = [f for f in todas if not f.caminho_bruto.exists()]
    if faltando:
        print("Faltando (baixe pelo navegador e salve com o nome indicado):")
        for f in faltando:
            print(f"  - data/raw/{f.id}.{f.formato}   <- {f.url}")
    if len(disponiveis) < MINIMO_SUCESSOS:
        print(f"\n⚠️  Menos de {MINIMO_SUCESSOS} documentos: o requisito mínimo da base não foi atingido.")
        return 1
    print(f"✓ Requisito de {MINIMO_SUCESSOS}+ documentos atingido. Próximo passo: python ingerir.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
