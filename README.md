# Motor RAG Local — Projeto 1

> **Disciplina:** Estruturas de Dados e Algoritmos  
> **Projeto:** Motor de Busca Vetorial e Textual para IA Offline

---

## Membros da Equipe

| Nome | Responsabilidade | GitHub |
|---|---|---|
| Monique | RF01 (Hash Index) · RF04 (HeapSort) · CLI · Gerador de dados | [@Moniquebelliny](https://github.com/Moniquefrancielly) |
| Eduardo | RF02 (Trie) · RF03 (Splay Tree) · Docs · README | [@EduardoSDuarte](https://github.com/EduardoSDuarte) |

---

## Descrição do Projeto

Este projeto implementa o núcleo algorítmico de um **Motor RAG (Retrieval-Augmented Generation) Local** — um sistema de busca e recuperação de documentos jurídicos que funciona completamente offline, sem acesso à internet.

A base documental simula artigos da Constituição Federal, Código Penal, Código Civil, CLT e jurisprudências. O sistema é composto por quatro estruturas de dados implementadas manualmente:

| RF | Estrutura | Função |
|---|---|---|
| RF01 | **Tabela Hash** (Índice Invertido) | Mapeia palavras → IDs de documentos em O(1) |
| RF02 | **Árvore Trie** (DFS) | Autocompletar baseado no vocabulário |
| RF03 | **Árvore Splay** | Cache dos documentos mais acessados |
| RF04 | **HeapSort** | Ordenação por relevância TF, exibe Top-5 |

---

## Estrutura do Repositório

```
Motor-RAG/
├── src/
│   ├── main.py          # CLI principal — lê input.json, grava output.json
│   ├── trie.py          # RF02: Árvore Trie com DFS para autocompletar
│   ├── splay_tree.py    # RF03: Splay Tree para cache de metadados
│   ├── hash_index.py    # RF01: Tabela Hash / Índice Invertido
│   ├── heap_sort.py     # RF04: HeapSort + TF score
│   └── tests.py         # Testes unitários
├── data/
│   ├── input_basico.json       # 10 docs, casos simples
│   ├── input_avancado.json     # 15 docs, edge cases
│   ├── input_estresse.json     # 10.000 docs, gerado automaticamente
│   └── generate_data.py        # Gerador dos três níveis de input
├── docs/
│   └── documentacao_tecnica.md # Justificativas de complexidade
├── run.sh                       # Script de execução (Linux/Mac)
├── run.bat                      # Script de execução (Windows)
└── README.md
```

---

## Pré-requisitos

- Python 3.10 ou superior
- Sem dependências externas (apenas biblioteca padrão do Python)

---

## Compilação e Execução

### Usando o script padrão (recomendado)

**Linux/Mac:**
```bash
chmod +x run.sh
bash run.sh
```

**Windows:**
```bat
.\run.bat
```

O script executa automaticamente:
1. Geração do arquivo de estresse (`input_estresse.json`)
2. Processamento dos 3 cenários (básico, avançado, estresse)
3. Geração dos arquivos de saída em `data/`

### Execução manual

```bash
# Input básico
python src/main.py --input data/input_basico.json --output data/output_basico.json

# Input avançado
python src/main.py --input data/input_avancado.json --output data/output_avancado.json

# Input de estresse
python src/main.py --input data/input_estresse.json --output data/output_estresse.json
```

### Gerar arquivo de estresse manualmente

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
      "id": "doc01",
      "title": "Art. 5° CF — Direitos e Garantias Fundamentais",
      "source": "Constituição Federal",
      "content": "todos são iguais perante a lei..."
    }
  ],
  "queries": [
    {
      "id": "q01",
      "term": "furto",
      "prefix": "fur"
    }
  ]
}
```

### output.json

```json
{
  "meta": {
    "total_documents": 10,
    "unique_terms_indexed": 428,
    "trie_vocabulary_size": 433,
    "processing_time_seconds": 0.01
  },
  "results": [
    {
      "query_id": "q01",
      "term": "furto",
      "prefix": "fur",
      "autocomplete": [
        {"word": "furto", "doc_ids": ["doc03"]}
      ],
      "top5_documentos": [
        {
          "rank": 1,
          "doc_id": "doc03",
          "title": "Art. 155 CP — Furto",
          "source": "Código Penal",
          "score": 0.052631
        }
      ],
      "splay_root": {
        "doc_id_int": 123456,
        "title": "Art. 155 CP — Furto",
        "access_count": 1
      }
    }
  ],
  "cache_estado_final": []
}
```

---

## Complexidade Assintótica

| Estrutura | Operação | Complexidade |
|---|---|---|
| **Hash Index** | insert / search | O(1) amortizado |
| **Trie** | insert / search | O(m) — m = tamanho da palavra |
| **Trie** | autocomplete (DFS) | O(m + k) — k = resultados |
| **Splay Tree** | access / search | O(log n) amortizado |
| **Splay Tree** | get_recent | O(n) |
| **HeapSort** | ordenação Top-5 | O(n log n) |

Para justificativas detalhadas, consulte [`docs/documentacao_tecnica.md`](docs/documentacao_tecnica.md).

---

## Restrições Respeitadas

- ✅ Nenhuma biblioteca de alto nível usada para o núcleo (`TreeMap`, `networkx`, pacotes npm, etc.)
- ✅ Todas as estruturas implementadas manualmente do zero
- ✅ Sistema funciona via linha de comando (CLI)
- ✅ Lê `input.json` e grava `output.json` deterministicamente
- ✅ Três níveis de input: básico (10 docs), avançado (15 docs), estresse (10.000 docs)
- ✅ Geração automatizada dos dados de teste via script

---

## Resultados do Teste de Estresse

| Cenário | Documentos | Termos Indexados | Tempo |
|---|---|---|---|
| Básico | 10 | 428 | 0.01s |
| Avançado | 15 | 297 | 0.01s |
| Estresse | 10.000 | 31.719 | ~11s |