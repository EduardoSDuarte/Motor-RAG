
class TrieNode:
    """Nó individual da Trie."""

    def __init__(self):
       
        self.children: dict[str, "TrieNode"] = {}
        self.is_end_of_word: bool = False
        self.doc_ids: list[int] = []


class Trie:
    def __init__(self):
        self.root = TrieNode()
        self._word_count = 0

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

    def autocomplete(self, prefix: str, max_results: int = 5) -> list[tuple[str, list[int]]]:
    
        prefix = prefix.lower().strip()
        results: list[tuple[str, list[int]]] = []

        prefix_node = self._find_node(prefix)
        if prefix_node is None:
            return results

        stack: list[tuple[TrieNode, str]] = [(prefix_node, prefix)]

        while stack and len(results) < max_results:
            node, current_word = stack.pop()

            if node.is_end_of_word:
                results.append((current_word, list(node.doc_ids)))

            for char in sorted(node.children.keys(), reverse=True):
                child_node = node.children[char]
                stack.append((child_node, current_word + char))

        return results

    def starts_with(self, prefix: str) -> bool:
        """Verifica se alguma palavra começa com o prefixo."""
        prefix = prefix.lower().strip()
        return self._find_node(prefix) is not None

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
    @classmethod
    def build_from_documents(cls, documents: list[dict]) -> "Trie":

        trie = cls()
        for doc in documents:
            doc_id = doc.get("id")
            content = doc.get("content", "")
            for word in _tokenize(content):
                trie.insert(word, doc_id=doc_id)
        return trie

def _tokenize(text: str) -> list[str]:
    """Tokeniza texto em palavras simples (sem pontuação)."""
    import re
    return re.findall(r"[a-záéíóúâêôãõüçà]+", text.lower())