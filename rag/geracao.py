"""
CONSULTA – PASSO 2: geração fundamentada (o "G" do RAG).

O LLM recebe a pergunta + os trechos recuperados, numerados [1]..[k], e
três regras:
  1. responder SÓ com base nos trechos;
  2. citar o número do trecho depois de cada afirmação;
  3. dizer explicitamente quando os trechos não respondem a pergunta.

Depois da geração, NÃO confiamos cegamente na resposta: o código confere
as citações (existem? apontam para trechos que realmente foram enviados?)
e marca a resposta como "sem fundamentação" se não houver nenhuma. Isso é
a "evidência das fontes utilizadas": cada [n] da resposta é ligado a um
documento, página/seção e URL verificáveis.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from . import config
from .recuperacao import Trecho

MENSAGEM_SEM_CONTEXTO = (
    "Não encontrei, na base de conhecimento, trechos relevantes o suficiente para "
    "responder a esta pergunta com segurança. Tente reformular a pergunta ou "
    "adicionar ao catálogo uma fonte que trate do tema."
)

PROMPT_SISTEMA = """Você é uma assistente de educação financeira que responde \
EXCLUSIVAMENTE com base nos trechos de documentos públicos fornecidos.

Regras obrigatórias:
1. Use somente informações presentes nos TRECHOS. Não use conhecimento externo.
2. Depois de cada frase com informação factual, cite o(s) trecho(s) de origem \
no formato [n] ou [n, m], usando os números dos trechos.
3. Se os trechos não contiverem a resposta (ou só parte dela), diga isso \
claramente: "As fontes consultadas não informam ...".
4. Não invente números, datas, leis ou instituições.
5. Responda em português do Brasil, de forma clara e objetiva, em até 3 parágrafos.
6. Trechos em inglês podem ser usados; traduza a informação na resposta.
"""

PROMPT_USUARIO = """TRECHOS RECUPERADOS:
{contexto}

PERGUNTA: {pergunta}

RESPOSTA (com citações [n]):"""


def montar_contexto(trechos: list[Trecho]) -> str:
    blocos = []
    for i, t in enumerate(trechos, start=1):
        blocos.append(f"[{i}] Fonte: {t.referencia()}\n{t.texto}")
    return "\n\n---\n\n".join(blocos)


_CITACAO = re.compile(r"\[(\d+(?:\s*[,;–-]\s*\d+)*)\]")


def extrair_citacoes(texto: str) -> list[int]:
    numeros: list[int] = []
    for grupo in _CITACAO.findall(texto):
        partes = re.split(r"\s*[,;]\s*", grupo)
        for parte in partes:
            if re.search(r"[–-]", parte):            # intervalo "1-3"
                a, b = re.split(r"\s*[–-]\s*", parte)
                numeros.extend(range(int(a), int(b) + 1))
            else:
                numeros.append(int(parte))
    return sorted(set(numeros))


@dataclass
class Resposta:
    pergunta: str
    texto: str
    trechos: list[Trecho]
    citados: list[int] = field(default_factory=list)          # índices 1-based válidos
    citacoes_invalidas: list[int] = field(default_factory=list)
    fundamentada: bool = False
    modelo: str = ""

    @property
    def fontes_citadas(self) -> list[Trecho]:
        return [self.trechos[i - 1] for i in self.citados]


def validar(pergunta: str, texto: str, trechos: list[Trecho], modelo: str) -> Resposta:
    numeros = extrair_citacoes(texto)
    validos = [n for n in numeros if 1 <= n <= len(trechos)]
    invalidos = [n for n in numeros if n not in validos]
    return Resposta(
        pergunta=pergunta,
        texto=texto.strip(),
        trechos=trechos,
        citados=validos,
        citacoes_invalidas=invalidos,
        fundamentada=bool(validos),
        modelo=modelo,
    )


def criar_llm():
    from langchain_ollama import ChatOllama

    return ChatOllama(
        model=config.LLM_MODEL,
        temperature=config.LLM_TEMPERATURE,
        base_url=config.OLLAMA_BASE_URL,
        # Janela de contexto: o padrão do Ollama pode ser 2048-4096 tokens e,
        # se o prompt passar disso, o INÍCIO é cortado em silêncio (perde-se
        # justamente as regras e os primeiros trechos). 8192 dá folga.
        num_ctx=config.LLM_NUM_CTX,
        # Limite de tamanho da resposta: evita gerações longas e lentas.
        num_predict=config.LLM_MAX_TOKENS,
        # Mantém o modelo carregado na memória entre consultas
        # (a 1ª consulta é lenta porque carrega o modelo; as seguintes, não).
        keep_alive="15m",
    )


def gerar(pergunta: str, trechos: list[Trecho], llm=None, ao_vivo: bool = False) -> Resposta:
    """
    ao_vivo=True imprime a resposta à medida que o LLM gera (streaming),
    para que fique visível que o sistema está trabalhando.
    """
    # Sem trechos acima do limiar -> nem chama o LLM. Melhor admitir que não
    # sabe do que deixar o modelo "completar" com conhecimento próprio.
    if not trechos:
        return Resposta(pergunta=pergunta, texto=MENSAGEM_SEM_CONTEXTO, trechos=[], modelo="(nenhum)")

    llm = llm or criar_llm()
    mensagens = [
        ("system", PROMPT_SISTEMA),
        ("human", PROMPT_USUARIO.format(contexto=montar_contexto(trechos), pergunta=pergunta)),
    ]
    if ao_vivo and hasattr(llm, "stream"):
        import time
        inicio = time.time()
        print(f"\n⏳ Gerando resposta com {getattr(llm, 'model', '?')} "
              f"(a 1ª consulta carrega o modelo e pode levar ~30 s)...\n", flush=True)
        partes = []
        primeiro = None
        for pedaco in llm.stream(mensagens):
            conteudo = getattr(pedaco, "content", "") or ""
            if conteudo and primeiro is None:
                primeiro = time.time() - inicio
            partes.append(conteudo)
            print(conteudo, end="", flush=True)
        texto = "".join(partes)
        print(f"\n\n(1º token em {primeiro or 0:.1f}s; total {time.time() - inicio:.1f}s)", flush=True)
    else:
        saida = llm.invoke(mensagens)
        texto = getattr(saida, "content", str(saida))
    nome_modelo = getattr(llm, "model", config.LLM_MODEL)
    return validar(pergunta, texto, trechos, nome_modelo)
