"""Pacote do RAG de educação financeira para mulheres.

Módulos, na ordem do pipeline:
  catalogo      -> quais fontes compõem a base (curadoria)
  carregadores  -> extrai texto de PDF/HTML        (ingestão 1)
  limpeza       -> normaliza o texto               (ingestão 2)
  chunking      -> divide em trechos               (ingestão 3)
  embeddings    -> texto -> vetor                  (ingestão 4)
  banco_vetorial-> grava/consulta no ChromaDB      (ingestão 5)
  recuperacao   -> busca os trechos relevantes     (consulta 1)
  geracao       -> resposta com citações           (consulta 2)
  evidencias    -> relatório de rastreabilidade    (consulta 3)
"""
