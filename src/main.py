"""
main.py — Motor RAG Jurídico (Projeto 1)
CLI que integra os 4 módulos implementados:
  RF01 — HashIndex   (índice invertido)
  RF02 — Trie        (autocompletar via DFS)
  RF03 — SplayTree   (cache de documentos recentes)
  RF04 — HeapSort    (ranking por relevância TF)

Uso:
  python main.py --input data/input_basico.json --output data/output.json
"""

import json
import sys
import os
import argparse
import time

sys.path.insert(0, os.path.dirname(__file__))

from hash_index import HashIndex
from heap_sort import heap_sort_by_relevance
from trie import Trie
from splay_tree import SplayTree


def load_input(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_output(data: dict, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def build_doc_map(documents: list[dict]) -> dict:
    """Dicionário {doc_id_str: doc_dict} para acesso O(1) pelo HeapSort."""
    return {doc["id"]: doc for doc in documents}


def build_id_mapping(documents: list[dict]) -> tuple[dict, dict]:
    """
    Trie e SplayTree usam doc_id como int internamente.
    Criamos dois mapas:
      str_to_int: {"doc01": 0, "doc02": 1, ...}
      int_to_str: {0: "doc01", 1: "doc02", ...}
    """
    str_to_int = {}
    int_to_str = {}
    for i, doc in enumerate(documents):
        str_to_int[doc["id"]] = i
        int_to_str[i] = doc["id"]
    return str_to_int, int_to_str


def build_structures(documents: list[dict], str_to_int: dict):
    """
    Constrói os 4 módulos a partir do corpus.
    Retorna (hash_index, trie, splay_tree).
    """
    # RF01 — HashIndex: usa doc_id como string
    hash_index = HashIndex()
    hash_index.build_from_documents(documents)

    # RF02 — Trie: precisa de doc_id como int → adaptamos os docs
    docs_com_int_id = [
        {"id": str_to_int[doc["id"]], "content": doc["content"]}
        for doc in documents
        if doc.get("content")
    ]
    trie = Trie.build_from_documents(docs_com_int_id)

    # RF03 — SplayTree: inicializa vazia, alimentada a cada query
    splay = SplayTree(capacity=500)

    return hash_index, trie, splay

def process_query(
    query: dict,
    hash_index: HashIndex,
    trie: Trie,
    splay: SplayTree,
    doc_map: dict,
    int_to_str: dict,
) -> dict:
    """
    Processa uma query e retorna o resultado com saídas dos 4 RFs.
    """
    term: str = query.get("term", "").lower().strip()
    prefix: str = query.get("prefix", "").lower().strip()
    query_id: str = query.get("id", "")

    result = {
        "query_id": query_id,
        "term": term,
        "prefix": prefix,
    }

    sugestoes_raw = trie.autocomplete(prefix, max_results=5)
    result["autocomplete"] = [
        {
            "word": palavra,
            "doc_ids": [int_to_str.get(i, str(i)) for i in ids],
        }
        for palavra, ids in sugestoes_raw
    ]

    doc_ids_encontrados: list[str] = hash_index.search(term)

    if doc_ids_encontrados:
        top5 = heap_sort_by_relevance(
            term=term,
            doc_ids=doc_ids_encontrados,
            doc_map=doc_map,
            top_k=5,
        )
    else:
        top5 = []

    result["top5_documentos"] = top5

    for item in top5:
        doc_id_str: str = item["doc_id"]
        doc_id_int: int = hash(doc_id_str) & 0x7FFFFFFF  

        metadata = {
            "title": item.get("title", ""),
            "source": item.get("source", ""),
            "score": item.get("score", 0.0),
            "term": term,
        }
        splay.access(doc_id_int, metadata)

    if splay.root is not None:
        result["splay_root"] = {
            "doc_id_int": splay.root.doc_id,
            "title": splay.root.metadata.get("title", ""),
            "access_count": splay.root.access_count,
        }
    else:
        result["splay_root"] = None

    return result


def main():
    parser = argparse.ArgumentParser(description="Motor RAG Jurídico")
    parser.add_argument(
        "--input", required=True,
        help="Caminho para o arquivo JSON de entrada (ex: data/input_basico.json)"
    )
    parser.add_argument(
        "--output", required=True,
        help="Caminho para o arquivo JSON de saída (ex: data/output.json)"
    )
    args = parser.parse_args()

    print(f"[RAG Jurídico] Carregando: {args.input}")
    t0 = time.time()

    payload = load_input(args.input)
    documents: list[dict] = payload.get("documents", [])
    queries: list[dict] = payload.get("queries", [])

    print(f"  Documentos : {len(documents):,}")
    print(f"  Queries    : {len(queries)}")

    str_to_int, int_to_str = build_id_mapping(documents)
    doc_map = build_doc_map(documents)

    print("  Construindo estruturas de dados...")
    hash_index, trie, splay = build_structures(documents, str_to_int)
    print(f"  HashIndex  : {len(hash_index):,} termos únicos indexados")
    print(f"  Trie       : {trie.word_count:,} palavras no vocabulário")

    print("  Processando queries...")
    resultados = []
    for query in queries:
        res = process_query(query, hash_index, trie, splay, doc_map, int_to_str)
        resultados.append(res)

    t1 = time.time()
    output = {
        "meta": {
            "input_file": args.input,
            "total_documents": len(documents),
            "total_queries": len(queries),
            "unique_terms_indexed": len(hash_index),
            "trie_vocabulary_size": trie.word_count,
            "processing_time_seconds": round(t1 - t0, 4),
        },
        "results": resultados,
        "cache_estado_final": splay.get_recent(10),
    }

    save_output(output, args.output)
    print(f"\n✓ Concluído em {t1 - t0:.2f}s → {args.output}")


if __name__ == "__main__":
    main()