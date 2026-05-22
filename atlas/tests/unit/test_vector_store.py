from app.services.vector_store import InMemoryVectorStore


def test_vector_store_add_and_search():
    store = InMemoryVectorStore()
    ids = store.add([[1.0, 0.0], [0.9, 0.1], [0.0, 1.0]], metadatas=[{"label": "A"}, {"label": "B"}, {"label": "C"}])
    assert len(ids) == 3
    assert store.count() == 3

    # Query similar to first two
    res = store.similarity_search([1.0, 0.05], k=2)
    assert len(res) == 2
    labels = {r["metadata"]["label"] for r in res}
    assert labels == {"A", "B"}

    # Delete one
    removed = store.delete([ids[0]])
    assert removed == 1
    assert store.count() == 2


def test_vector_store_empty_search():
    store = InMemoryVectorStore()
    res = store.similarity_search([0.0, 0.0], k=5)
    assert res == []
