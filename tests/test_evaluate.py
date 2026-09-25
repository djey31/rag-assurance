from src.rag.evaluate import normaliser, passage_trouve

def test_normaliser():
    assert normaliser("  Deux   JOURS\nouvrés ") == "deux jours ouvrés"

def test_passage_trouve_renvoie_le_rang():
    passages = [{"text": "autre chose"}, {"text": "Le délai est de deux jours ouvrés."}]
    assert passage_trouve("deux jours ouvrés", passages) == 2

def test_passage_absent_renvoie_none():
    assert passage_trouve("introuvable", [{"text": "rien"}]) is None
