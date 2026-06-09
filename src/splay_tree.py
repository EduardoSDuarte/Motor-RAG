
class SplayNode:

    def __init__(self, doc_id: int, metadata: dict):
        self.doc_id: int = doc_id          
        self.metadata: dict = metadata     
        self.access_count: int = 1         
        self.left: "SplayNode | None" = None
        self.right: "SplayNode | None" = None
        self.parent: "SplayNode | None" = None


class SplayTree:

    def __init__(self, capacity: int = 100):
        self.root: SplayNode | None = None
        self.size: int = 0
        self.capacity: int = capacity  # limite do cache

    def access(self, doc_id: int, metadata: dict) -> SplayNode:
        node = self._find(doc_id)

        if node is not None:
            node.access_count += 1
            node.metadata.update(metadata)
            self._splay(node)
            return self.root  

        new_node = SplayNode(doc_id, metadata)
        self._insert_node(new_node)
        self._splay(new_node)

        if self.size > self.capacity:
            self._evict_lru()

        return self.root  

    def get_metadata(self, doc_id: int) -> dict | None:

        node = self._find(doc_id)
        if node is None:
            return None
        self._splay(node)
        return dict(self.root.metadata) 

    def get_recent(self, k: int) -> list[dict]:

        all_nodes: list[SplayNode] = []
        self._inorder(self.root, all_nodes)

        all_nodes.sort(key=lambda n: (-n.access_count, n.doc_id))

        return [
            {"doc_id": n.doc_id, "access_count": n.access_count, **n.metadata}
            for n in all_nodes[:k]
        ]

    def contains(self, doc_id: int) -> bool:
        return self._find(doc_id) is not None

    def _rotate_right(self, x: SplayNode) -> None:
      
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

    def _splay(self, x: SplayNode) -> None:
        while x.parent is not None:
            p = x.parent     
            g = p.parent      

            if g is None:
    
                if x == p.left:
                    self._rotate_right(p)
                else:
                    self._rotate_left(p)

            elif x == p.left and p == g.left:              
                self._rotate_right(g)
                self._rotate_right(p)

            elif x == p.right and p == g.right:             
                self._rotate_left(g)
                self._rotate_left(p)

            elif x == p.right and p == g.left:              
                self._rotate_left(p)
                self._rotate_right(g)

            else:
                self._rotate_right(p)
                self._rotate_left(g)

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

    def _evict_lru(self) -> None:

        if self.root is None:
            return

        node = self.root
        while node.left is not None:
            node = node.left

        self._splay(node)
        self._remove_root()

    def _remove_root(self) -> None:
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

            self.root = left_tree
            max_left = left_tree
            while max_left.right is not None:
                max_left = max_left.right
            self._splay(max_left)

            self.root.right = right_tree
            right_tree.parent = self.root

        self.size -= 1

    def _inorder(self, node: SplayNode | None, result: list) -> None:
        if node is None:
            return
        self._inorder(node.left, result)
        result.append(node)
        self._inorder(node.right, result)