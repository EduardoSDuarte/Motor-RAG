"""
hash_index.py — Índice Invertido via Tabela Hash (RF01)

Implementação do zero: array de buckets com encadeamento (chaining) para colisões.
NÃO usa dict do Python como estrutura interna principal.

Complexidade:
  - insert : O(1) amortizado
  - search : O(1) amortizado
  - build  : O(D * W)  onde D = docs, W = palavras por doc
"""


# ── Nó da lista encadeada (encadeamento para colisões) ────────────────────────

class _Node:
    """Nó interno da lista encadeada dentro de cada bucket."""
    __slots__ = ("key", "doc_ids", "next")

    def __init__(self, key: str):
        self.key: str = key
        self.doc_ids: list[str] = []   # IDs dos documentos que contêm esta palavra
        self.next: "_Node | None" = None


# ── Tabela Hash ────────────────────────────────────────────────────────────────

class HashIndex:
    """
    Índice invertido: mapeia cada termo (str) para uma lista de IDs de documentos.

    Usa tabela hash com encadeamento externo (separate chaining).
    Redimensiona automaticamente quando load_factor > 0.75.
    """

    _INITIAL_CAPACITY = 1024  # potência de 2 para otimizar o módulo

    def __init__(self):
        self._capacity: int = self._INITIAL_CAPACITY
        self._size: int = 0                        # número de chaves únicas
        self._buckets: list[_Node | None] = [None] * self._capacity

    # ── hash ──────────────────────────────────────────────────────────────────

    def _hash(self, key: str) -> int:
        """
        Polynomial rolling hash (djb2 variant).
        Produz distribuição uniforme para strings de texto natural.
        """
        h = 5381
        for ch in key:
            h = (h * 33 ^ ord(ch)) & 0xFFFFFFFF
        return h % self._capacity

    # ── resize ────────────────────────────────────────────────────────────────

    def _resize(self) -> None:
        """Dobra a capacidade e re-hasha todas as chaves existentes."""
        old_buckets = self._buckets
        self._capacity *= 2
        self._buckets = [None] * self._capacity
        self._size = 0

        for head in old_buckets:
            node = head
            while node is not None:
                for doc_id in node.doc_ids:
                    self._raw_insert(node.key, doc_id)
                node = node.next

    def _raw_insert(self, term: str, doc_id: str) -> None:
        """Inserção interna sem checar load factor (usada no resize)."""
        idx = self._hash(term)
        node = self._buckets[idx]

        while node is not None:
            if node.key == term:
                if doc_id not in node.doc_ids:
                    node.doc_ids.append(doc_id)
                return
            node = node.next

        # chave nova — insere no início da cadeia (O(1))
        new_node = _Node(term)
        new_node.doc_ids.append(doc_id)
        new_node.next = self._buckets[idx]
        self._buckets[idx] = new_node
        self._size += 1

    # ── API pública ───────────────────────────────────────────────────────────

    def insert(self, term: str, doc_id: str) -> None:
        """
        Indexa um termo associando-o a um documento.

        Complexidade: O(1) amortizado.
        Redimensiona se load_factor > 0.75.
        """
        if self._size / self._capacity > 0.75:
            self._resize()
        self._raw_insert(term, doc_id)

    def search(self, term: str) -> list[str]:
        """
        Retorna lista de IDs de documentos que contêm o termo.
        Retorna lista vazia se o termo não existir.

        Complexidade: O(1) amortizado.
        """
        idx = self._hash(term)
        node = self._buckets[idx]

        while node is not None:
            if node.key == term:
                return list(node.doc_ids)
            node = node.next

        return []

    def build_from_documents(self, documents: list[dict]) -> None:
        """
        Constrói o índice a partir de uma lista de documentos.

        Cada documento deve ter os campos:
          - "id"      : str  — identificador único
          - "content" : str  — texto a ser indexado

        Complexidade: O(D * W) onde D = número de documentos, W = palavras por doc.
        """
        for doc in documents:
            doc_id: str = doc.get("id", "")
            content: str = doc.get("content", "")
            if not doc_id or not content:
                continue

            # normalização simples: lowercase, remove pontuação básica
            content = content.lower()
            for ch in ".,;:!?()[]{}\"'\\/-":
                content = content.replace(ch, " ")

            for word in content.split():
                if len(word) >= 2:          # ignora tokens muito curtos
                    self.insert(word, doc_id)

    # ── utilitários ───────────────────────────────────────────────────────────

    def __len__(self) -> int:
        """Número de termos únicos indexados."""
        return self._size

    def load_factor(self) -> float:
        return self._size / self._capacity

    def stats(self) -> dict:
        """Estatísticas da tabela para o relatório de estresse."""
        used_buckets = sum(1 for b in self._buckets if b is not None)
        max_chain = 0
        for head in self._buckets:
            length = 0
            node = head
            while node:
                length += 1
                node = node.next
            max_chain = max(max_chain, length)

        return {
            "unique_terms": self._size,
            "capacity": self._capacity,
            "load_factor": round(self.load_factor(), 4),
            "used_buckets": used_buckets,
            "max_chain_length": max_chain,
        }