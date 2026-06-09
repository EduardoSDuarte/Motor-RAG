"""
heap_sort.py — Ordenação por Relevância via HeapSort (RF04)

Implementação do zero: max-heap em array, sem uso de heapq.
Calcula score TF (Term Frequency) e retorna os Top 5 documentos.

Complexidade:
  - compute_scores : O(D * W)  onde D = docs candidatos, W = palavras por doc
  - heap_sort      : O(N log N)
  - top_k          : O(N log K)
"""


# ── Funções internas do Heap ──────────────────────────────────────────────────

def _parent(i: int) -> int:
    return (i - 1) // 2

def _left(i: int) -> int:
    return 2 * i + 1

def _right(i: int) -> int:
    return 2 * i + 2


def _sift_down(arr: list, i: int, n: int) -> None:
    """
    Desce o elemento arr[i] até sua posição correta na max-heap.
    Considera apenas os primeiros `n` elementos do array.

    Complexidade: O(log n)
    """
    largest = i
    l = _left(i)
    r = _right(i)

    if l < n and arr[l][1] > arr[largest][1]:
        largest = l
    if r < n and arr[r][1] > arr[largest][1]:
        largest = r

    if largest != i:
        arr[i], arr[largest] = arr[largest], arr[i]
        _sift_down(arr, largest, n)


def _build_max_heap(arr: list) -> None:
    """
    Constrói max-heap in-place a partir de um array desordenado.

    Complexidade: O(n)
    """
    n = len(arr)
    # começa no último nó interno e desce até a raiz
    for i in range(_parent(n - 1), -1, -1):
        _sift_down(arr, i, n)


def heap_sort(arr: list) -> list:
    """
    Ordena lista de tuplas (doc_id, score) em ordem decrescente de score.

    Algoritmo:
      1. Constrói max-heap              → O(n)
      2. Extrai máximo n vezes          → O(n log n)
      3. Resultado em ordem decrescente → inverte ao final

    Complexidade: O(n log n) — in-place exceto pela inversão final.
    """
    if not arr:
        return []

    arr = list(arr)          # cópia para não mudar o original
    n = len(arr)

    _build_max_heap(arr)

    for end in range(n - 1, 0, -1):
        # move o maior elemento (raiz) para o final
        arr[0], arr[end] = arr[end], arr[0]
        # restaura a heap sem o último elemento
        _sift_down(arr, 0, end)

    # heap_sort produz ordem crescente — invertemos para decrescente
    arr.reverse()
    return arr


# ── Score de Relevância ───────────────────────────────────────────────────────

def compute_tf_score(term: str, doc: dict) -> float:
    """
    Calcula TF (Term Frequency) normalizado para um termo em um documento.

    TF = (ocorrências do termo no doc) / (total de palavras do doc)

    Retorna 0.0 se o documento estiver vazio ou o termo ausente.
    """
    content: str = doc.get("content", "").lower()
    if not content:
        return 0.0

    words = content.split()
    total = len(words)
    if total == 0:
        return 0.0

    count = words.count(term.lower())
    return count / total


def compute_scores(term: str, doc_ids: list[str], doc_map: dict) -> list[tuple]:
    """
    Calcula score TF para cada documento candidato.

    Parâmetros:
      term     : termo buscado
      doc_ids  : lista de IDs retornada pelo HashIndex
      doc_map  : dicionário {doc_id: doc_dict} para acesso O(1)

    Retorna lista de tuplas (doc_id, score) — não ordenada.

    Complexidade: O(D * W)
    """
    scores = []
    for doc_id in doc_ids:
        doc = doc_map.get(doc_id)
        if doc is None:
            continue
        score = compute_tf_score(term, doc)
        if score > 0.0:
            scores.append((doc_id, score))
    return scores


# ── API principal ─────────────────────────────────────────────────────────────

def heap_sort_by_relevance(
    term: str,
    doc_ids: list[str],
    doc_map: dict,
    top_k: int = 5,
) -> list[dict]:
    """
    Retorna os top_k documentos mais relevantes para o termo buscado.

    Fluxo:
      1. Calcula TF score para cada documento candidato
      2. Ordena via HeapSort (O(n log n))
      3. Retorna os top_k com metadados

    Parâmetros:
      term    : termo da query
      doc_ids : candidatos retornados pelo HashIndex
      doc_map : {doc_id: doc_dict}
      top_k   : número de resultados (padrão 5, conforme enunciado)

    Retorno:
      Lista de dicts com: doc_id, title, source, score, rank
    """
    if not doc_ids:
        return []

    # 1. calcula scores
    scores = compute_scores(term, doc_ids, doc_map)

    if not scores:
        return []

    # 2. ordena por HeapSort decrescente
    sorted_scores = heap_sort(scores)

    # 3. monta resultado com metadados (top_k)
    results = []
    for rank, (doc_id, score) in enumerate(sorted_scores[:top_k], start=1):
        doc = doc_map.get(doc_id, {})
        content = doc.get("content", "")
        snippet = content[:150].strip() + "..." if len(content) > 150 else content
        
        results.append({
            "rank": rank,
            "doc_id": doc_id,
            "title": doc.get("title", ""),
            "source": doc.get("source", ""),
            "score": round(score, 6),
            "snippet": snippet,
        })

    return results