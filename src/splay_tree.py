"""
RF03 — Árvore Splay para Cache de Metadados dos Documentos
Implementação manual sem uso de bibliotecas de alto nível.

A Splay Tree é uma BST auto-ajustável: cada acesso (busca, inserção)
realiza a operação "splay" que move o nó acessado para a raiz.
Isso garante que os elementos mais recentemente acessados fiquem
próximos da raiz — comportamento ideal para um cache LRU-like.

Complexidade (amortizada):
  - access / insert / delete: O(log n) amortizado
  - splay:                    O(log n) amortizado
  - get_recent(k):            O(k log n)

Por que Splay Tree para cache?
  Os documentos mais buscados "flutuam" naturalmente para o topo da
  árvore, reduzindo o custo médio de acesso subsequente — exatamente
  o comportamento desejado em um motor RAG onde certos documentos são
  consultados com frequência.
"""


class SplayNode:
    """Nó da Splay Tree."""

    def __init__(self, doc_id: int, metadata: dict):
        self.doc_id: int = doc_id          # chave da BST
        self.metadata: dict = metadata     # payload (título, score, acessos, etc.)
        self.access_count: int = 1         # quantas vezes este doc foi acessado
        self.left: "SplayNode | None" = None
        self.right: "SplayNode | None" = None
        self.parent: "SplayNode | None" = None


class SplayTree:
    """
    Cache de metadados de documentos baseado em Splay Tree.

    Uso típico:
        cache = SplayTree()
        cache.access(doc_id=3, metadata={"title": "Deep Learning", "score": 0.95})
        cache.access(doc_id=1, metadata={"title": "Python Guide", "score": 0.80})
        recent = cache.get_recent(k=2)
        # -> lista dos 2 docs mais acessados recentemente
    """

    def __init__(self, capacity: int = 100):
        self.root: SplayNode | None = None
        self.size: int = 0
        self.capacity: int = capacity  # limite do cache

    # ------------------------------------------------------------------
    # Interface pública
    # ------------------------------------------------------------------
    def access(self, doc_id: int, metadata: dict) -> SplayNode:
        """
        Registra acesso a um documento.
        - Se já existe: faz splay para a raiz e incrementa access_count.
        - Se não existe: insere e faz splay.
        - Se capacity excedida: remove o nó menos recente (mais profundo à esquerda).
        """
        node = self._find(doc_id)

        if node is not None:
            # Já existe — atualiza e move para raiz
            node.access_count += 1
            node.metadata.update(metadata)
            self._splay(node)
            return self.root  # type: ignore

        # Novo documento
        new_node = SplayNode(doc_id, metadata)
        self._insert_node(new_node)
        self._splay(new_node)

        # Controle de capacidade: remove o menos recente
        if self.size > self.capacity:
            self._evict_lru()

        return self.root  # type: ignore

    def get_metadata(self, doc_id: int) -> dict | None:
        """Busca os metadados de um documento (realiza splay)."""
        node = self._find(doc_id)
        if node is None:
            return None
        self._splay(node)
        return dict(self.root.metadata)  # type: ignore

    def get_recent(self, k: int) -> list[dict]:
        """
        Retorna os k documentos mais recentemente acessados,
        ordenados por access_count decrescente.
        Faz traversal in-order e coleta os nós.
        """
        all_nodes: list[SplayNode] = []
        self._inorder(self.root, all_nodes)

        # Ordena por access_count desc, depois por doc_id para desempate
        all_nodes.sort(key=lambda n: (-n.access_count, n.doc_id))

        return [
            {"doc_id": n.doc_id, "access_count": n.access_count, **n.metadata}
            for n in all_nodes[:k]
        ]

    def contains(self, doc_id: int) -> bool:
        return self._find(doc_id) is not None

    # ------------------------------------------------------------------
    # Rotações fundamentais
    # ------------------------------------------------------------------
    def _rotate_right(self, x: SplayNode) -> None:
        """Rotação à direita em torno de x."""
        y = x.left
        if y is None:
            return

        x.left = y.right
        if y.right:
            y.right.parent = x

        y.parent = x.parent
        if x.parent is None:
            self.root = y
        elif x == x.parent.right:
            x.parent.right = y
        else:
            x.parent.left = y

        y.right = x
        x.parent = y

    def _rotate_left(self, x: SplayNode) -> None:
        """Rotação à esquerda em torno de x."""
        y = x.right
        if y is None:
            return

        x.right = y.left
        if y.left:
            y.left.parent = x

        y.parent = x.parent
        if x.parent is None:
            self.root = y
        elif x == x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y

        y.left = x
        x.parent = y

    # ------------------------------------------------------------------
    # Operação Splay — move o nó para a raiz
    # ------------------------------------------------------------------
    def _splay(self, x: SplayNode) -> None:
        """
        Move o nó x para a raiz através de rotações zig/zig-zig/zig-zag.
        Esta operação é o coração da Splay Tree.
        """
        while x.parent is not None:
            p = x.parent      # parent
            g = p.parent      # grandparent

            if g is None:
                # Zig: x é filho direto da raiz
                if x == p.left:
                    self._rotate_right(p)
                else:
                    self._rotate_left(p)

            elif x == p.left and p == g.left:
                # Zig-Zig: x e p são ambos filhos esquerdos
                self._rotate_right(g)
                self._rotate_right(p)

            elif x == p.right and p == g.right:
                # Zig-Zig: x e p são ambos filhos direitos
                self._rotate_left(g)
                self._rotate_left(p)

            elif x == p.right and p == g.left:
                # Zig-Zag: x é filho direito, p é filho esquerdo
                self._rotate_left(p)
                self._rotate_right(g)

            else:
                # Zig-Zag: x é filho esquerdo, p é filho direito
                self._rotate_right(p)
                self._rotate_left(g)

    # ------------------------------------------------------------------
    # Busca interna — NÃO faz splay (use access() para isso)
    # ------------------------------------------------------------------
    def _find(self, doc_id: int) -> SplayNode | None:
        node = self.root
        while node is not None:
            if doc_id == node.doc_id:
                return node
            elif doc_id < node.doc_id:
                node = node.left
            else:
                node = node.right
        return None

    # ------------------------------------------------------------------
    # Inserção BST padrão (sem splay — chamado antes do splay externo)
    # ------------------------------------------------------------------
    def _insert_node(self, new_node: SplayNode) -> None:
        if self.root is None:
            self.root = new_node
            self.size += 1
            return

        current = self.root
        while True:
            if new_node.doc_id < current.doc_id:
                if current.left is None:
                    current.left = new_node
                    new_node.parent = current
                    self.size += 1
                    return
                current = current.left
            else:
                if current.right is None:
                    current.right = new_node
                    new_node.parent = current
                    self.size += 1
                    return
                current = current.right

    # ------------------------------------------------------------------
    # Evict: remove o nó menos recente (leftmost = menor doc_id = mais antigo)
    # ------------------------------------------------------------------
    def _evict_lru(self) -> None:
        """Remove o documento menos recentemente acessado (nó mais à esquerda)."""
        if self.root is None:
            return

        node = self.root
        while node.left is not None:
            node = node.left

        # Faz splay do LRU para a raiz e remove
        self._splay(node)
        self._remove_root()

    def _remove_root(self) -> None:
        """Remove a raiz atual, unindo as duas subárvores."""
        if self.root is None:
            return

        left_tree = self.root.left
        right_tree = self.root.right

        if left_tree:
            left_tree.parent = None
        if right_tree:
            right_tree.parent = None

        if left_tree is None:
            self.root = right_tree
        elif right_tree is None:
            self.root = left_tree
        else:
            # Encontra o máximo da subárvore esquerda e faz splay nela
            self.root = left_tree
            max_left = left_tree
            while max_left.right is not None:
                max_left = max_left.right
            self._splay(max_left)
            # Agora max_left é raiz da subárvore esquerda, anexa direita
            self.root.right = right_tree
            right_tree.parent = self.root

        self.size -= 1

    # ------------------------------------------------------------------
    # Traversal in-order (para coleta de todos os nós)
    # ------------------------------------------------------------------
    def _inorder(self, node: SplayNode | None, result: list) -> None:
        if node is None:
            return
        self._inorder(node.left, result)
        result.append(node)
        self._inorder(node.right, result)