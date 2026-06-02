"""
RF02 — Árvore Trie com DFS para Autocompletar
Implementação manual sem uso de bibliotecas de alto nível.

Complexidade:
  - insert:     O(m)   onde m = comprimento da palavra
  - search:     O(m)
  - autocomplete: O(m + k) onde k = número de palavras com o prefixo
  - DFS interno: O(n)  onde n = total de nós na subárvore
"""


class TrieNode:
    """Nó individual da Trie."""

    def __init__(self):
        # Dicionário de filhos: caractere -> TrieNode
        self.children: dict[str, "TrieNode"] = {}
        # Marca se este nó representa o fim de uma palavra válida
        self.is_end_of_word: bool = False
        # IDs dos documentos que contêm esta palavra (útil para integração com o índice)
        self.doc_ids: list[int] = []


class Trie:
    """
    Árvore Trie para autocompletar baseado no vocabulário do corpus.

    Uso típico:
        trie = Trie()
        trie.insert("machine", doc_id=0)
        trie.insert("machine", doc_id=1)
        trie.insert("learning", doc_id=0)
        results = trie.autocomplete("mac", max_results=5)
        # -> [("machine", [0, 1])]
    """

    def __init__(self):
        self.root = TrieNode()
        self._word_count = 0

    # ------------------------------------------------------------------
    # Inserção — O(m)
    # ------------------------------------------------------------------
    def insert(self, word: str, doc_id: int | None = None) -> None:
        """Insere uma palavra na Trie e associa opcionalmente um doc_id."""
        word = word.lower().strip()
        if not word:
            return

        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]

        if not node.is_end_of_word:
            node.is_end_of_word = True
            self._word_count += 1

        if doc_id is not None and doc_id not in node.doc_ids:
            node.doc_ids.append(doc_id)

    # ------------------------------------------------------------------
    # Busca exata — O(m)
    # ------------------------------------------------------------------
    def search(self, word: str) -> tuple[bool, list[int]]:
        """
        Verifica se uma palavra existe na Trie.
        Retorna (encontrado, lista_de_doc_ids).
        """
        word = word.lower().strip()
        node = self._find_node(word)
        if node is None or not node.is_end_of_word:
            return False, []
        return True, list(node.doc_ids)

    # ------------------------------------------------------------------
    # Autocompletar com DFS — O(m + k)
    # ------------------------------------------------------------------
    def autocomplete(self, prefix: str, max_results: int = 5) -> list[tuple[str, list[int]]]:
        """
        Retorna até max_results palavras que começam com o prefixo dado.
        Usa DFS (caminhamento em profundidade) a partir do nó do prefixo.

        Retorna lista de tuplas (palavra, doc_ids) ordenada lexicograficamente.
        """
        prefix = prefix.lower().strip()
        results: list[tuple[str, list[int]]] = []

        prefix_node = self._find_node(prefix)
        if prefix_node is None:
            return results

        # DFS iterativo para evitar estouro de pilha em vocabulários grandes
        # Pilha: (nó_atual, string_acumulada)
        stack: list[tuple[TrieNode, str]] = [(prefix_node, prefix)]

        while stack and len(results) < max_results:
            node, current_word = stack.pop()

            if node.is_end_of_word:
                results.append((current_word, list(node.doc_ids)))

            # Adiciona filhos em ordem alfabética inversa para que
            # o DFS processe em ordem alfabética (pilha é LIFO)
            for char in sorted(node.children.keys(), reverse=True):
                child_node = node.children[char]
                stack.append((child_node, current_word + char))

        return results

    # ------------------------------------------------------------------
    # Verificação de prefixo — O(m)
    # ------------------------------------------------------------------
    def starts_with(self, prefix: str) -> bool:
        """Verifica se alguma palavra começa com o prefixo."""
        prefix = prefix.lower().strip()
        return self._find_node(prefix) is not None

    # ------------------------------------------------------------------
    # Helpers internos
    # ------------------------------------------------------------------
    def _find_node(self, prefix: str) -> TrieNode | None:
        """Caminha pela Trie até o nó correspondente ao prefixo."""
        node = self.root
        for char in prefix:
            if char not in node.children:
                return None
            node = node.children[char]
        return node

    def get_all_words(self) -> list[str]:
        """Retorna todas as palavras armazenadas (DFS completo)."""
        return [word for word, _ in self.autocomplete("", max_results=self._word_count + 1)]

    @property
    def word_count(self) -> int:
        return self._word_count

    # ------------------------------------------------------------------
    # Build a partir de uma lista de documentos
    # ------------------------------------------------------------------
    @classmethod
    def build_from_documents(cls, documents: list[dict]) -> "Trie":
        """
        Constrói a Trie a partir de uma lista de documentos no formato:
            [{"id": 0, "content": "texto do documento"}, ...]
        """
        trie = cls()
        for doc in documents:
            doc_id = doc.get("id")
            content = doc.get("content", "")
            for word in _tokenize(content):
                trie.insert(word, doc_id=doc_id)
        return trie


# ------------------------------------------------------------------
# Utilitário de tokenização (compartilhado com outros módulos)
# ------------------------------------------------------------------
def _tokenize(text: str) -> list[str]:
    """Tokeniza texto em palavras simples (sem pontuação)."""
    import re
    return re.findall(r"[a-záéíóúâêôãõüçà]+", text.lower())