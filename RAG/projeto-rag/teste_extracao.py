import fitz  # Importa o PyMuPDF

# Abre o documento PDF
doc = fitz.open("docs/caderno_cidadania_financeira.pdf")

# Quantidade total de páginas
print("Páginas:", len(doc))

# Extrai o texto da página 12 (índice 11) e limita aos primeiros 800 caracteres
texto_pagina = doc[11].get_text()
print(texto_pagina[:800])

# Boa prática: fechar o documento ao terminar
doc.close()