import sys
from rag import recuperar

pergunta = " ".join(sys.argv[1:])

for i, t in enumerate(recuperar(pergunta), start=1):
    print(f"--- #{i} | {t['fonte']} | distancia={t['distancia']:.3f}")
    print(t["texto"][:400])