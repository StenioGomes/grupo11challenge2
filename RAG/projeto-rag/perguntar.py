from rag import perguntar

print("Assistente RAG (digite 'sair' para encerrar)")

while True:
    pergunta = input("\nPergunta: ").strip()
    
    if pergunta.lower() in ("sair", "exit"):
        break
    if not pergunta:
        continue
        
    resposta, trechos = perguntar(pergunta)
    print("\n" + resposta)
    print("\nFontes:", ", ".join(sorted({t["fonte"] for t in trechos})))