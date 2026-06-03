"""
generate_data.py — Gerador do input_estresse.json
Meta: 10.000 documentos simulados com vocabulário jurídico de ~50.000 palavras únicas
"""

import json
import random
import uuid
import os      

# ── vocabulário jurídico base ──────────────────────────────────────────────────

TERMOS_JURIDICOS = [
    "furto", "roubo", "homicídio", "lesão", "dano", "culpa", "dolo", "pena",
    "reclusão", "detenção", "multa", "absolvição", "condenação", "sentença",
    "recurso", "apelação", "agravo", "habeas", "corpus", "mandado", "segurança",
    "injunção", "tutela", "antecipada", "liminar", "cautelar", "medida",
    "contrato", "rescisão", "indenização", "reparação", "responsabilidade",
    "negligência", "imprudência", "imperícia", "nexo", "causalidade",
    "legítima", "defesa", "estado", "necessidade", "excludente", "ilicitude",
    "culpabilidade", "imputabilidade", "prescrição", "decadência", "prazo",
    "empregado", "empregador", "justa", "causa", "aviso", "prévio", "férias",
    "salário", "décimo", "terceiro", "fgts", "verbas", "rescisórias",
    "vínculo", "empregatício", "subordinação", "habitualidade", "pessoalidade",
    "onerosidade", "contrato", "trabalho", "temporário", "terceirização",
    "propriedade", "posse", "usucapião", "hipoteca", "penhor", "servidão",
    "usufruto", "enfiteuse", "alienação", "fiduciária", "registro", "imóvel",
    "herança", "testamento", "inventário", "partilha", "doação", "legado",
    "sucessão", "herdeiro", "legatário", "espólio", "meação", "divórcio",
    "alimentos", "guarda", "tutela", "curatela", "adoção", "filiação",
    "casamento", "união", "estável", "dissolução", "separação", "regime",
    "bens", "comunhão", "separação", "participação", "aquestos",
    "crime", "contravenção", "tipicidade", "antijuridicidade", "punibilidade",
    "tentativa", "consumação", "concurso", "agentes", "coautoria", "participação",
    "reincidência", "atenuante", "agravante", "qualificadora", "privilegiada",
    "execução", "penal", "progressão", "regime", "fechado", "semiaberto",
    "aberto", "livramento", "condicional", "sursis", "medida", "segurança",
    "internação", "tratamento", "ambulatorial", "periculosidade", "inimputável",
    "tribunal", "juiz", "promotor", "defensor", "advogado", "perito",
    "testemunha", "prova", "ônus", "contraditório", "ampla", "defesa",
    "devido", "processo", "legal", "jurisdição", "competência", "foro",
    "vara", "câmara", "turma", "pleno", "órgão", "especial", "relator",
    "acórdão", "ementa", "voto", "divergente", "unânime", "maioria",
    "constitucional", "inconstitucional", "controle", "difuso", "concentrado",
    "ação", "direta", "arguição", "descumprimento", "preceito", "fundamental",
    "súmula", "vinculante", "jurisprudência", "precedente", "ratio",
    "decidendi", "obiter", "dictum", "analogia", "costumes", "princípios",
    "norma", "regra", "ordenamento", "vigência", "validade", "eficácia",
    "promulgação", "sanção", "veto", "decreto", "portaria", "resolução",
    "regulamento", "lei", "ordinária", "complementar", "delegada", "medida",
    "provisória", "emenda", "constitucional", "reforma", "tributária",
    "imposto", "taxa", "contribuição", "melhoria", "fiscal", "tributário",
    "lançamento", "crédito", "débito", "parcelamento", "remissão", "anistia",
    "isenção", "imunidade", "alíquota", "base", "cálculo", "fato", "gerador",
]

FONTES = [
    "Constituição Federal", "Código Penal", "Código Civil", "CLT",
    "Código de Processo Civil", "Código de Processo Penal",
    "Estatuto da Criança", "Lei de Execução Penal",
    "Jurisprudência STF", "Jurisprudência STJ", "Jurisprudência TST",
    "Lei de Improbidade", "Lei Anticorrupção", "Lei do Consumidor",
]

PREFIXOS_TITULO = [
    "Art.", "Súmula", "Enunciado", "Acórdão", "Ementa",
    "Jurisprudência", "Precedente", "Resolução",
]


def gerar_palavra_sintetica(prefixo: str, numero: int) -> str:
    """Gera palavras únicas combinando prefixo jurídico + sufixo numérico."""
    sufixos = ["ção", "mento", "dade", "ismo", "ário", "ivo", "ório", "ante", "ência", "ância"]
    sufixo = sufixos[numero % len(sufixos)]
    return f"{prefixo}{sufixo}{numero}"


def gerar_conteudo(doc_index: int, palavras_unicas: list) -> str:
    """
    Gera conteúdo textual para um documento.
    Mistura termos jurídicos reais com palavras sintéticas únicas
    para garantir as 50k palavras únicas no corpus total.
    """
    # termos jurídicos reais para este documento
    n_reais = random.randint(15, 30)
    termos_reais = random.choices(TERMOS_JURIDICOS, k=n_reais)

    # palavras sintéticas únicas deste documento
    n_sinteticas = random.randint(3, 7)
    inicio = (doc_index * n_sinteticas) % len(palavras_unicas)
    termos_sinteticos = palavras_unicas[inicio: inicio + n_sinteticas]

    todos = termos_reais + termos_sinteticos
    random.shuffle(todos)
    return " ".join(todos)


def gerar_documento(doc_index: int, palavras_unicas: list) -> dict:
    prefixo = random.choice(PREFIXOS_TITULO)
    numero = random.randint(1, 9999)
    fonte = random.choice(FONTES)
    return {
        "id": f"doc{doc_index:05d}",
        "title": f"{prefixo} {numero} — {fonte}",
        "source": fonte,
        "content": gerar_conteudo(doc_index, palavras_unicas),
    }


def gerar_queries(n: int = 20) -> list:
    queries = []
    termos_sample = random.sample(TERMOS_JURIDICOS, min(n, len(TERMOS_JURIDICOS)))
    for i, termo in enumerate(termos_sample):
        prefixo = termo[:max(3, len(termo) // 2)]
        queries.append({
            "id": f"q{i+1:03d}",
            "term": termo,
            "prefix": prefixo,
        })
    return queries


def main():
    print("Gerando vocabulário sintético único...")

    # gerar ~45k palavras sintéticas únicas (+ ~300 termos reais = ~50k total)
    prefixos_base = ["jur", "leg", "proc", "penal", "civil", "trib", "const",
                     "exec", "crim", "adm", "fis", "prev", "trab", "amb"]
    palavras_unicas = []
    for prefixo in prefixos_base:
        for i in range(3300):
            palavras_unicas.append(gerar_palavra_sintetica(prefixo, i))

    random.shuffle(palavras_unicas)
    print(f"  Vocabulário sintético: {len(palavras_unicas):,} palavras")

    print("Gerando 10.000 documentos...")
    N_DOCS = 10_000
    documentos = [gerar_documento(i, palavras_unicas) for i in range(1, N_DOCS + 1)]

    print("Gerando queries...")
    queries = gerar_queries(20)

    payload = {
        "documents": documentos,
        "queries": queries,
    }

    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, "input_estresse.json")
    print(f"Salvando em {output_path}...")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    # estatísticas
    todas_palavras = set()
    for doc in documentos:
        todas_palavras.update(doc["content"].split())

    tamanho_mb = len(json.dumps(payload, ensure_ascii=False).encode()) / (1024 * 1024)
    print(f"\n✓ Geração concluída!")
    print(f"  Documentos  : {len(documentos):,}")
    print(f"  Queries     : {len(queries)}")
    print(f"  Palavras únicas no corpus: {len(todas_palavras):,}")
    print(f"  Tamanho do arquivo: {tamanho_mb:.1f} MB")


if __name__ == "__main__":
    main()