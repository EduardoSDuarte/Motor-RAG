# Documentação Técnica — Motor RAG Local

## Visão Geral do Sistema

O Motor RAG (Retrieval-Augmented Generation) Local é composto por quatro estruturas de dados principais que trabalham em conjunto para recuperar documentos relevantes sem acesso à internet. Este documento detalha as estruturas implementadas por Eduardo: **RF02 (Trie)** e **RF03 (Splay Tree)**.

---

## RF02 — Árvore Trie (Autocompletar)

### Descrição

A **Trie** (também chamada de *Prefix Tree* ou *Digital Tree*) é uma árvore de busca ordenada onde cada nó representa um caractere. O caminho da raiz até um nó marcado como fim de palavra forma uma palavra completa do vocabulário.

### Estrutura Interna

```
root
├── m
│   └── a
│       └── c
│           └── h [is_end=True, doc_ids=[0,1]]
│               └── i
│                   └── n
│                       └── e [is_end=True, doc_ids=[0,1]]
└── l
    └── e
        └── a
            └── r
                └── n [is_end=True, doc_ids=[0,2]]
```

Cada `TrieNode` contém:
- `children: dict[str, TrieNode]` — filhos indexados por caractere
- `is_end_of_word: bool` — marca fim de palavra válida
- `doc_ids: list[int]` — documentos que contêm esta palavra

### Algoritmos Implementados

#### Inserção — O(m)

```
Para cada caractere c em palavra:
    Se c não é filho do nó atual:
        Criar novo TrieNode para c
    Avançar para o filho c
Marcar nó final como is_end_of_word = True
Adicionar doc_id se ainda não presente
```

Onde **m** é o comprimento da palavra. A inserção é linear no tamanho da palavra, independentemente do tamanho do vocabulário.

#### Autocompletar com DFS — O(m + k)

```
1. Navegar até o nó correspondente ao prefixo  [O(m)]
2. DFS iterativo a partir deste nó:             [O(k)]
   - Pilha: [(nó_atual, palavra_acumulada)]
   - Para cada nó visitado:
     * Se is_end_of_word: adicionar à lista de resultados
     * Adicionar filhos (ordem alfabética reversa) à pilha
   - Parar quando max_results atingido ou pilha vazia
```

**Complexidade:** O(m + k) onde:
- **m** = comprimento do prefixo (navegação inicial)
- **k** = número de palavras com o prefixo encontradas

O uso de **DFS iterativo** (pilha explícita) evita estouro de pilha de chamadas (*stack overflow*) para vocabulários grandes — importante no cenário de estresse.

#### Por que DFS e não BFS?

| Critério | DFS (adotado) | BFS |
|---|---|---|
| Memória | O(profundidade) | O(largura máxima) |
| Ordem de retorno | Lexicográfica | Por comprimento |
| Implementação | Pilha explícita | Fila explícita |
| Adequação | ✅ Vocabulário denso | ⚠️ Vocabulário largo e raso |

Para vocabulários técnicos (palavras longas, prefixos comuns como "ma-", "al-"), o DFS consome menos memória e retorna palavras em ordem natural para o usuário.

### Complexidade Assintótica

| Operação | Tempo | Espaço |
|---|---|---|
| `insert(word)` | O(m) | O(m) por palavra |
| `search(word)` | O(m) | O(1) |
| `starts_with(prefix)` | O(m) | O(1) |
| `autocomplete(prefix, k)` | O(m + k) | O(profundidade + k) |
| Espaço total da Trie | — | O(N × m) no pior caso |

Onde **N** = total de palavras, **m** = comprimento médio.

Na prática, o compartilhamento de prefixos reduz significativamente o espaço. Ex.: "machine", "machining", "machines" compartilham o nó "machin".

---

## RF03 — Árvore Splay (Cache de Metadados)

### Descrição

A **Splay Tree** é uma Árvore de Busca Binária (BST) auto-ajustável. Após cada operação de acesso (busca, inserção ou deleção), o nó acessado é movido para a raiz através de rotações chamadas coletivamente de **operação Splay**. Isso garante que elementos acessados com frequência fiquem permanentemente próximos da raiz.

### Por que Splay Tree para Cache?

Em um motor RAG, alguns documentos são consultados muito mais do que outros (distribuição de Pareto / Lei de Zipf). A Splay Tree explora isso naturalmente:

- Documentos populares → ficam na raiz → acesso em O(1) prático
- Documentos raros → afundam na árvore → custo amortizado O(log n)
- Não requer metadados extras (sem contador de acesso na BST em si)
- O padrão de acesso "molda" a árvore automaticamente

### Operação Splay — Rotações

A operação splay identifica três casos com base na relação entre o nó alvo (x), seu pai (p) e seu avô (g):

#### Caso Zig (x é filho direto da raiz)

```
      p                x
     / \     →        / \
    x   C            A   p
   / \                  / \
  A   B                B   C
```
Uma única rotação (direita ou esquerda) coloca x na raiz.

#### Caso Zig-Zig (x e p no mesmo lado)

```
        g               x
       / \             / \
      p   D    →      A   p
     / \                 / \
    x   C               B   g
   / \                     / \
  A   B                   C   D
```
Rotaciona g primeiro, depois p. Isso preserva o balanceamento melhor que duas rotações simples.

#### Caso Zig-Zag (x e p em lados opostos)

```
      g              x
     / \            / \
    p   D    →     p   g
   / \            / \ / \
  A   x          A  B C  D
     / \
    B   C
```
Rotaciona p, depois g. Equivalente a uma rotação dupla AVL.

### Complexidade Assintótica

| Operação | Tempo Amortizado | Pior Caso |
|---|---|---|
| `access(doc_id)` | O(log n) | O(n) |
| `get_metadata(doc_id)` | O(log n) | O(n) |
| `get_recent(k)` | O(n) | O(n) |
| `_evict_lru()` | O(log n) | O(n) |
| Espaço | — | O(n) |

**Nota sobre o pior caso O(n):** Ocorre em sequências degeneradas (ex.: inserções em ordem crescente). O custo *amortizado* O(log n) garante que m operações quaisquer custam no máximo O(m log n) total — demonstrável pelo método do potencial (Φ = soma dos log(tamanho das subárvores)).

### Controle de Capacidade (Eviction LRU)

Quando o cache atinge sua capacidade máxima, o documento menos recente é removido. Na Splay Tree, o elemento "mais antigo" (menos acessado recentemente) tende a estar no nó mais à esquerda (menor doc_id dentre os menos splayed). O processo de eviction:

1. Caminhar até o nó mais à esquerda (leftmost)
2. Fazer splay dele para a raiz
3. Remover a raiz unindo as duas subárvores

---

## Integração entre RF02 e RF03

```
                    input.json
                        │
                  ┌─────▼─────┐
                  │   main.py  │
                  └─────┬─────┘
                        │
          ┌─────────────┼─────────────┐
          │             │             │
    ┌─────▼─────┐ ┌─────▼─────┐ ┌────▼──────┐
    │  HashIndex │ │   Trie    │ │SplayTree  │
    │  (RF01)    │ │  (RF02)   │ │  (RF03)   │
    └─────┬─────┘ └─────┬─────┘ └────┬──────┘
          │             │             │
          │  TF scores  │ autocomplete│  metadados
          └──────┬──────┘             │
                 │                    │
           ┌─────▼─────┐             │
           │  HeapSort  │             │
           │  (RF04)    │             │
           └─────┬─────┘             │
                 │ Top-5             │
                 └──────────────────►│ cache.access()
                                     │
                               output.json
```

### Fluxo de dados

1. `main.py` lê `input.json` e instancia o `RAGEngine`
2. Para cada documento: `HashIndex.index_document()` + `Trie.insert()` para cada palavra
3. Para cada query: `HashIndex.search()` → `heap_sort_by_relevance()` → `SplayTree.access()`
4. Para cada prefixo de autocomplete: `Trie.autocomplete()`
5. Estado final do cache: `SplayTree.get_recent()`

---

## Justificativas de Design

### Por que não usar `dict` built-in como Trie?
O enunciado proíbe estruturas de alto nível que "resolvam o núcleo do problema". Um simples dicionário aninhado não implementa DFS, controle de `doc_ids` por nó, nem a semântica de fim de palavra — seria apenas uma delegação ao hashmap do Python.

### Por que não usar `sortedcontainers.SortedList` na Splay?
Além de ser proibido pelo enunciado, um `SortedList` não tem a propriedade de auto-ajuste por frequência de acesso que torna a Splay Tree adequada para cache.

### Por que DFS iterativo e não recursivo na Trie?
Python tem limite de recursão (~1000 chamadas por padrão). Em vocabulários de 10.000+ palavras com prefixos longos, a recursão causaria `RecursionError`. A versão iterativa com pilha explícita é robusta para o caso de estresse.

---

*Documentação elaborada por Eduardo — RF02 (Trie) e RF03 (Splay Tree)*