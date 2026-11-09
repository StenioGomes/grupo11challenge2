"""
Teste de fumaça (smoke test) do pipeline completo, SEM Ollama e SEM internet.

Usa documentos sintéticos minúsculos, o embedding baseline "hash" e um LLM
falso que devolve uma resposta pronta. Serve para verificar que todas as
peças se encaixam (carregar -> limpar -> dividir -> indexar -> recuperar ->
gerar -> validar citações -> relatório) antes de gastar tempo com os
modelos reais.

    python tests/teste_fumaca.py
"""

from __future__ import annotations

import os
import shutil
import sys
import tempfile
import textwrap
from pathlib import Path

os.environ["EMBEDDING_PROVIDER"] = "hash"
os.environ["COLLECTION_NAME"] = "teste_fumaca"
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rag import banco_vetorial, config, evidencias  # noqa: E402
from rag.carregadores import carregar  # noqa: E402
from rag.catalogo import Fonte  # noqa: E402
from rag.chunking import dividir  # noqa: E402
from rag.geracao import extrair_citacoes, gerar  # noqa: E402
from rag.limpeza import limpar_unidades  # noqa: E402
from rag.recuperacao import recuperar  # noqa: E402

TMP = Path(tempfile.mkdtemp(prefix="rag_fumaca_"))
config.DIR_BRUTOS = TMP / "raw"
config.DIR_CHROMA = TMP / "chroma"
config.DIR_SAIDAS = TMP / "saidas"
config.DIR_BRUTOS.mkdir(parents=True)

LEI_HTML = """<html><head><meta charset="utf-8"></head><body>
<p>LEI DE TESTE Nº 1, DE 2006</p>
<p>Art. 1º Esta lei de teste cria mecanismos para coibir a violência doméstica e familiar contra a mulher.</p>
<p>Art. 7º São formas de violência, entre outras: I - a violência física; IV - a violência patrimonial,
entendida como qualquer conduta que configure retenção, subtração, destruição parcial ou total de seus objetos,
instrumentos de trabalho, documentos pessoais, bens, valores e direitos ou recursos econômicos.</p>
<p><strike>Art. 8º Texto revogado que NAO pode aparecer na base.</strike></p>
</body></html>"""

CREDITO_HTML = """<html><body><main>
<h2>Crédito e mulheres empreendedoras</h2>
<p>Estudo de teste indica que mulheres donas de pequenos negócios pagam juros mais altos no crédito,
embora apresentem taxas de inadimplência semelhantes às dos homens.</p>
<h2>Barreiras</h2>
<p>Entre as barreiras citadas estão exigência de garantias, menor histórico de crédito formal e burocracia.</p>
</main></body></html>"""

PAGINAS_PDF = [
    "Orçamento doméstico: anote todas as receitas e despesas do mês, separando gastos fixos e varia-\nveis.",
    "Reserva de emergência é o dinheiro guardado para imprevistos, como perda de renda ou despesas médicas.",
    "Recomenda-se acumular o equivalente a alguns meses de despesas essenciais em aplicação de alta liquidez.",
    "Evite compras por impulso: espere um dia antes de decidir e compare preços.",
    "O crédito deve ser usado com planejamento; o rotativo do cartão tem juros muito altos.",
    "Planejar a aposentadoria cedo permite aproveitar o efeito dos juros compostos.",
]


def criar_pdf(caminho: Path) -> bool:
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
    except ImportError:
        return False
    c = canvas.Canvas(str(caminho), pagesize=A4)
    for i, texto in enumerate(PAGINAS_PDF, start=1):
        c.drawString(50, 800, "Cartilha Teste - Educacao Financeira")   # cabeçalho repetido
        y = 760
        for linha in texto.split("\n"):
            for pedaco in textwrap.wrap(linha, 80):
                c.drawString(50, y, pedaco)
                y -= 16
        c.drawString(300, 40, str(i))                                    # nº de página
        c.showPage()
    c.save()
    return True


def fonte(id_, formato, titulo):
    return Fonte(id=id_, titulo=titulo, instituicao="Instituição Teste", ano=2024,
                 url=f"https://exemplo.gov.br/{id_}", formato=formato, idioma="pt", eixo="teste")


class LLMFalso:
    model = "llm-falso"

    def invoke(self, mensagens):
        class Saida:
            content = "Violência patrimonial é a retenção ou destruição de bens e recursos da mulher [1]. Ver também [2, 9]."
        return Saida()


def main():
    fontes = [fonte("lei_teste", "html", "Lei de Teste"), fonte("credito_teste", "html", "Estudo de Crédito")]
    (config.DIR_BRUTOS / "lei_teste.html").write_text(LEI_HTML, encoding="utf-8")
    (config.DIR_BRUTOS / "credito_teste.html").write_text(CREDITO_HTML, encoding="utf-8")
    if criar_pdf(config.DIR_BRUTOS / "cartilha_teste.pdf"):
        fontes.append(fonte("cartilha_teste", "pdf", "Cartilha de Teste"))
    else:
        print("(reportlab não instalado: pulando o PDF sintético)")

    db = banco_vetorial.abrir()
    for f in fontes:
        unidades = limpar_unidades(carregar(f.caminho_bruto, f.formato))
        chunks = dividir(f, unidades, doc_hash="abc")
        banco_vetorial.adicionar(db, chunks)
        print(f"  {f.id}: {len(unidades)} unidades -> {len(chunks)} chunks")
        if f.formato == "pdf":
            todos = " ".join(c.texto for c in chunks)
            assert "Cartilha Teste - Educacao Financeira" not in todos, "cabeçalho repetido não foi removido"
            assert "variaveis" in todos or "variáveis" in todos, "hifenização não foi corrigida"
            assert any(c.metadados["pagina"] == 2 for c in chunks), "página não registrada"
        if f.id == "lei_teste":
            todos = " ".join(c.texto for c in chunks)
            assert "revogado" not in todos, "texto riscado (revogado) entrou na base"
            assert any(c.metadados["secao"].startswith("Art. 7") for c in chunks), "seção do artigo não detectada"

    # idempotência: mesmos chunks, mesmos ids -> contagem não muda
    n = banco_vetorial.total(db)
    f0 = fontes[0]
    banco_vetorial.adicionar(db, dividir(f0, limpar_unidades(carregar(f0.caminho_bruto, f0.formato)), "abc"))
    assert banco_vetorial.total(db) == n, "reindexar o mesmo documento duplicou chunks"
    assert banco_vetorial.hash_indexado(db, "lei_teste") == "abc"

    trechos, candidatos = recuperar(db, "o que é violência patrimonial", k=3)
    print(f"  métrica do índice: {banco_vetorial.metrica(db)} | candidatos: {len(candidatos)}")
    assert trechos, f"nenhum trecho passou do limiar; similaridades: {[c.similaridade for c in candidatos]}"
    print(f"  top-1: {trechos[0].fonte_id} {trechos[0].localizador} sim={trechos[0].similaridade}")
    assert trechos[0].fonte_id == "lei_teste" and trechos[0].secao.startswith("Art. 7")

    if any(f.formato == "pdf" for f in fontes):
        trechos_r, _ = recuperar(db, "reserva de emergência para imprevistos", k=3)
        assert trechos_r[0].fonte_id == "cartilha_teste", trechos_r[0].fonte_id
        assert trechos_r[0].pagina in (2, 3)

    resposta = gerar("o que é violência patrimonial", trechos, llm=LLMFalso())
    assert resposta.fundamentada and 1 in resposta.citados
    assert 9 in resposta.citacoes_invalidas, "citação inexistente não foi detectada"
    assert extrair_citacoes("a [1-3] b [5; 6]") == [1, 2, 3, 5, 6]

    sem = gerar("pergunta qualquer", [], llm=LLMFalso())
    assert not sem.fundamentada and "Não encontrei" in sem.texto

    md, js = evidencias.salvar(resposta, candidatos)
    conteudo = md.read_text(encoding="utf-8")
    assert "Evidência das fontes utilizadas" in conteudo and "[1]" in conteudo
    print(f"  relatório de exemplo: {md}")
    print("\nOK – todas as verificações passaram.")


if __name__ == "__main__":
    try:
        main()
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
