from pathlib import Path
import chromadb
import fitz  # PyMuPDF
from sentence_transformers import SentenceTransformer
from config import (PASTA_DOCS, PASTA_BANCO, NOME_COLECAO, MODELO_EMB,
                    TAMANHO_CHUNK, SOBREPOSICAO)


def ler(arquivo: Path) -> str:
    if arquivo.suffix.lower() == ".pdf":
        with fitz.open(arquivo) as doc:
            return "\n".join(pagina.get_text() for pagina in doc)
    return arquivo.read_text(encoding="utf-8")


def limpar(texto: str) -> str:
    return " ".join(texto.split())


def dividir(texto: str, tamanho: int, sobreposicao: int) -> list[str]:
    """Divide em chunks de até `tamanho` caracteres sem cortar palavras,
    repetindo ~`sobreposicao` caracteres do fim de um chunk no início do próximo."""
    palavras = texto.split()
    pedacos, atual = [], []
    for palavra in palavras:
        if atual and len(" ".join(atual + [palavra])) > tamanho:
            pedacos.append(" ".join(atual))
            # mantém as últimas palavras como sobreposição
            sobra = []
            while atual and len(" ".join([atual[-1]] + sobra)) <= sobreposicao:
                sobra.insert(0, atual.pop())
            atual = sobra
        atual.append(palavra)
    if atual:
        pedacos.append(" ".join(atual))
    return pedacos


print("Carregando modelo de embeddings...")
emb = SentenceTransformer(MODELO_EMB)
print("Limite do modelo (tokens):", emb.max_seq_length)

db = chromadb.PersistentClient(path=PASTA_BANCO)
try:
    db.delete_collection(NOME_COLECAO)
except Exception:
    pass
colecao = db.create_collection(NOME_COLECAO, metadata={"hnsw:space": "cosine"})

total = 0
truncados = 0
for arq in sorted(Path(PASTA_DOCS).iterdir()):
    if arq.suffix.lower() not in (".pdf", ".txt", ".md"):
        continue
    pedacos = dividir(limpar(ler(arq)), TAMANHO_CHUNK, SOBREPOSICAO)
    if not pedacos:
        print(f"AVISO: nenhum texto extraído de {arq.name}")
        continue
    truncados += sum(
        len(emb.tokenizer.tokenize(p)) > emb.max_seq_length - 2 for p in pedacos
    )
    colecao.add(
        ids=[f"{arq.name}-{i}" for i in range(len(pedacos))],
        documents=pedacos,
        embeddings=emb.encode(pedacos, normalize_embeddings=True).tolist(),
        metadatas=[{"fonte": arq.name, "chunk": i} for i in range(len(pedacos))],
    )
    total += len(pedacos)
    print(f"{arq.name}: {len(pedacos)} chunks")

print(f"Indexação concluída: {total} chunks ({truncados} truncados pelo modelo).")
