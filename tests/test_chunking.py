from src.rag.chunking import chunk_text, split_paragraphs

def test_split_paragraphs_ignore_les_vides():
    assert split_paragraphs("a\n\n\n b \n\n") == ["a", "b"]

def test_chunk_respecte_la_taille_max():
    pages = [(1, "\n\n".join("phrase " * 40 for _ in range(10)))]
    chunks = chunk_text("doc", pages, max_chars=500, overlap=0)
    assert chunks and all(len(c.text) <= 600 for c in chunks)

def test_chunk_conserve_le_numero_de_page():
    chunks = chunk_text("doc", [(3, "un paragraphe")])
    assert chunks[0].page == 3
    assert chunks[0].doc_id == "doc"
