# Motor RAG Local — Projeto 1

> **Disciplina:** Estruturas de Dados e Algoritmos  
> **Projeto:** Motor de Busca Vetorial e Textual para IA Offline

---

## Membros da Equipe

| Nome | Responsabilidade | GitHub |
|---|---|---|
| [Nome da Parceira] | RF01 (Hash Index) · RF04 (HeapSort) · CLI · Gerador de dados | @parceira |
| Eduardo | RF02 (Trie) · RF03 (Splay Tree) · Docs · README | @eduardo |

---

## Descrição do Projeto

Este projeto implementa o núcleo algorítmico de um **Motor RAG (Retrieval-Augmented Generation) Local** — um sistema de busca e recuperação de documentos que funciona completamente offline, sem acesso à internet.

O sistema é composto por quatro estruturas de dados implementadas manualmente:

| RF | Estrutura | Função |
|---|---|---|
| RF01 | **Tabela Hash** (Índice Invertido) | Mapeia palavras → IDs de documentos |
| RF02 | **Árvore Trie** (DFS) | Autocompletar baseado no vocabulário |
| RF03 | **Árvore Splay** | Cache dos documentos mais acessados |
| RF04 | **HeapSort** | Ordenação por relevância, exibe Top-5 |

---

## Estrutura do Repositório

```
rag-motor/
├── src/
│   ├── main.py          # CLI principal — lê input.json, grava output.json
│   ├── trie.py          # RF02: Árvore Trie com DFS para autocompletar
│   ├── splay_tree.py    # RF03: Splay Tree para cache de metadados
│   ├── hash_index.py    # RF01: Tabela Hash / Índice Invertido (parceira)
│   ├── heap_sort.py     # RF04: HeapSort + TF score (parceira)
│   └── tests.py         # Testes unitários (RF02 + RF03)
├── data/
│   ├── input_basico.json       # 5 docs, casos simples
│   ├── input_avancado.json     # 10 docs, edge cases
│   ├── input_estresse.json     # 1000 docs, gerado automaticamente
│   └── generate_data.py        # Gerador dos três níveis de input
├── docs/
│   └── documentacao_tecnica.md # Justificativas de complexidade
├── run.sh                       # Script de execução padrão
└── README.md
```

---

## Pré-requisitos

- Python 3.10 ou superior
- Sem dependências externas (apenas biblioteca padrão do Python)

---

## Compilação e Execução

### Usando o script padrão (recomendado)

```bash
# Tornar executável (primeira vez)
chmod +x run.sh

# Executar com input básico
./run.sh basico

# Executar com input avançado
./run.sh avancado

# Executar com input de estresse
./run.sh estresse
```

### Execução manual

```bash
# Input básico
python src/main.py --input data/input_basico.json --output data/output.json

# Input avançado
python src/main.py --input data/input_avancado.json --output data/output.json

# Input de estresse
python src/main.py --input data/input_estresse.json --output data/output.json
```

### Gerar arquivo de estresse

```bash
python data/generate_data.py
```

### Rodar os testes

```bash
python src/tests.py
```

---

## Formato dos Arquivos JSON

### input.json

```json
{
  "documents": [
    {
      "id": 0,
      "title": "Título do Documento",
      "content": "Conteúdo textual do documento..."
    }
  ],
  "queries": [
    {
      "id": 1,
      "query": "termos de busca",
      "top_k": 5
    }
  ],
  "autocomplete_tests": [
    {
      "prefix": "ma",
      "max_results": 5
    }
  ]
}
```

### output.json

```json
{
  "metadata": {
    "total_documents": 5,
    "vocabulary_size": 312
  },
  "search_results": [
    {
      "query_id": 1,
      "query": "machine learning",
      "top_k": 5,
      "results": [
        {
          "doc_id": 0,
          "title": "Introduction to Machine Learning",
          "score": 2,
          "snippet": "primeiros 200 caracteres do documento..."
        }
      ]
    }
  ],
  "autocomplete_results": [
    {
      "prefix": "ma",
      "suggestions": ["machine", "mathematics", "matrix"]
    }
  ],
  "cache_state": [
    {
      "doc_id": 0,
      "access_count": 3,
      "title": "Introduction to Machine Learning",
      "score": 2
    }
  ]
}
```

---

## Complexidade Assintótica

| Estrutura | Operação | Complexidade |
|---|---|---|
| **Trie** | insert / search | O(m) — m = tamanho da palavra |
| **Trie** | autocomplete | O(m + k) — k = resultados |
| **Splay Tree** | access / search | O(log n) amortizado |
| **Splay Tree** | get_recent | O(n) |
| **Hash Index** | insert / search | O(1) amortizado |
| **HeapSort** | ordenação Top-K | O(n log n) |

Para justificativas detalhadas, consulte [`docs/documentacao_tecnica.md`](docs/documentacao_tecnica.md).

---

## Restrições Respeitadas

- ✅ Nenhuma biblioteca de alto nível usada para o núcleo (`TreeMap`, `networkx`, pacotes npm, etc.)
- ✅ Todas as estruturas implementadas manualmente do zero
- ✅ Sistema funciona via linha de comando (CLI)
- ✅ Lê `input.json` e grava `output.json` deterministicamente
- ✅ Três níveis de input: básico, avançado e estresse

---

## Como Contribuir (Para a Equipe)

1. Faça commits frequentes com mensagens descritivas
2. Nunca faça commit diretamente na `main` — use branches (`feature/rf02-trie`)
3. Cada membro deve ter commits significativos de código-fonte
4. Antes de fazer merge, rode `python src/tests.py` e confirme que todos passam