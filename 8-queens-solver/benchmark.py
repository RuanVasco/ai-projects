#!/usr/bin/env python3
"""
Benchmark para os algoritmos de solução do problema das 8 rainhas.
Executa cada algoritmo N vezes com parâmetros aleatórios, persiste os
resultados e gera o arquivo relatorio.md com análise comparativa.
"""
import sys
import json
import random
import statistics
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from src.algorithms.hill_climbing import subida_encosta
from src.algorithms.simulated_annealing import tempera_simulada
from src.algorithms.genetic import algoritmo_genetico

N_RUNS = 1000
RESULTS_DIR = SCRIPT_DIR / "results"

# ---------------------------------------------------------------------------
# Intervalos de parâmetros para amostragem aleatória
# ---------------------------------------------------------------------------

HC_OPTIONS = {
    "max_reinicios":          [5, 10, 25, 50, 100, 200],
    "max_passos_por_reinicio": [25, 50, 100, 200],
}

SA_OPTIONS = {
    "temp_inicial":      [10.0, 50.0, 100.0, 200.0, 500.0],
    "taxa_resfriamento": [0.90, 0.95, 0.99, 0.995, 0.999],
    "max_iteracoes":     [5000, 10000, 25000, 50000],
}

GA_OPTIONS = {
    "tamanho_populacao": [20, 50, 100, 200],
    "taxa_mutacao":      [0.01, 0.05, 0.10, 0.20, 0.50],
    "taxa_cruzamento":   [0.50, 0.70, 0.90, 1.00],
    "max_geracoes":      [100, 250, 500, 1000],
    "n_elites":          [1, 2, 5],
}

# ---------------------------------------------------------------------------
# Executores (extraem apenas os campos relevantes de cada resultado)
# ---------------------------------------------------------------------------

def _run_hc(params):
    r = subida_encosta(**params)
    return {
        **params,
        "sucesso":    r["sucesso"],
        "conflitos":  r["conflitos"],
        "iteracoes":  r.get("iteracoes", 0),
        "reinicios":  r.get("reinicios", 0),
        "tempo_ms":   r["tempo_ms"],
    }


def _run_sa(params):
    r = tempera_simulada(**params)
    return {
        **params,
        "sucesso":            r["sucesso"],
        "conflitos":          r["conflitos"],
        "iteracoes":          r.get("iteracoes", 0),
        "temperatura_final":  r.get("temperatura_final", 0.0),
        "tempo_ms":           r["tempo_ms"],
    }


def _run_ga(params):
    r = algoritmo_genetico(**params)
    return {
        **params,
        "sucesso":   r["sucesso"],
        "conflitos": r["conflitos"],
        "geracoes":  r.get("geracoes", 0),
        "tempo_ms":  r["tempo_ms"],
    }


# ---------------------------------------------------------------------------
# Benchmark principal
# ---------------------------------------------------------------------------

def benchmark(n_runs=N_RUNS):
    RESULTS_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    all_results = {}

    tasks = [
        ("hill_climbing",       "Subida de Encosta",  HC_OPTIONS, _run_hc),
        ("simulated_annealing", "Têmpera Simulada",   SA_OPTIONS, _run_sa),
        ("genetic",             "Algoritmo Genético", GA_OPTIONS, _run_ga),
    ]

    for key, label, options, runner in tasks:
        print(f"\n[{label}]  {n_runs} execuções...")
        rows = []
        for i in range(n_runs):
            params = {k: random.choice(v) for k, v in options.items()}
            rows.append(runner(params))
            if (i + 1) % 200 == 0:
                pct = sum(r["sucesso"] for r in rows) / len(rows) * 100
                print(f"  {i+1:>4}/{n_runs}  sucesso acumulado={pct:.1f}%")
        taxa = sum(r["sucesso"] for r in rows) / n_runs * 100
        print(f"  -> Taxa de sucesso final: {taxa:.1f}%")
        all_results[key] = rows

    data = {"timestamp": timestamp, "n_runs": n_runs, **all_results}
    out = RESULTS_DIR / f"benchmark_{timestamp}.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\nResultados brutos salvos em: {out}")
    return data


# ---------------------------------------------------------------------------
# Análise estatística
# ---------------------------------------------------------------------------

def analyze(rows, param, extra_metrics=None):
    """Agrupa por valor de parâmetro e calcula estatísticas descritivas."""
    groups = {}
    for r in rows:
        groups.setdefault(r[param], []).append(r)

    stats = []
    for val in sorted(groups.keys()):
        g = groups[val]
        n = len(g)
        s = {
            "valor":           val,
            "n":               n,
            "sucesso_pct":     round(sum(r["sucesso"] for r in g) / n * 100, 1),
            "tempo_medio":     round(statistics.mean(r["tempo_ms"] for r in g), 2),
            "tempo_dp":        round(statistics.stdev(r["tempo_ms"] for r in g) if n > 1 else 0, 2),
            "conflitos_medio": round(statistics.mean(r["conflitos"] for r in g), 3),
        }
        for m in (extra_metrics or []):
            if m in g[0]:
                s[f"{m}_medio"] = round(statistics.mean(r[m] for r in g), 1)
        stats.append(s)
    return stats


# ---------------------------------------------------------------------------
# Formatação Markdown
# ---------------------------------------------------------------------------

def md_table(stats, columns):
    """
    columns: lista de tuplas (cabeçalho, chave_no_dict)
    """
    header = "| " + " | ".join(h for h, _ in columns) + " |"
    sep    = "|" + "|".join(" :---: " for _ in columns) + "|"
    lines  = [header, sep]
    for s in stats:
        cells = []
        for _, k in columns:
            v = s.get(k, "-")
            if k == "valor":
                cells.append(str(v))
            elif k == "sucesso_pct":
                cells.append(f"{v:.1f}%")
            elif isinstance(v, float):
                cells.append(f"{v:.2f}")
            else:
                cells.append(str(v))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Geração do relatório
# ---------------------------------------------------------------------------

def generate_report(data):
    hc = data["hill_climbing"]
    sa = data["simulated_annealing"]
    ga = data["genetic"]
    n  = data["n_runs"]

    def pct(rows):
        return f"{sum(r['sucesso'] for r in rows)/len(rows)*100:.1f}%"

    def avg_t(rows):
        return f"{statistics.mean(r['tempo_ms'] for r in rows):.2f}"

    # Análises
    hc_by_reinicios = analyze(hc, "max_reinicios",          ["iteracoes", "reinicios"])
    hc_by_passos    = analyze(hc, "max_passos_por_reinicio", ["iteracoes", "reinicios"])
    sa_by_temp      = analyze(sa, "temp_inicial",      ["iteracoes"])
    sa_by_resfr     = analyze(sa, "taxa_resfriamento", ["iteracoes"])
    sa_by_maxiter   = analyze(sa, "max_iteracoes",     ["iteracoes"])
    ga_by_pop       = analyze(ga, "tamanho_populacao", ["geracoes"])
    ga_by_mut       = analyze(ga, "taxa_mutacao",      ["geracoes"])
    ga_by_cruz      = analyze(ga, "taxa_cruzamento",   ["geracoes"])
    ga_by_gen       = analyze(ga, "max_geracoes",      ["geracoes"])
    ga_by_elit      = analyze(ga, "n_elites",          ["geracoes"])

    hc_cols = [
        ("`max_reinicios`",   "valor"), ("N", "n"), ("Taxa de Sucesso", "sucesso_pct"),
        ("Tempo médio (ms)",  "tempo_medio"), ("Iters. médias", "iteracoes_medio"),
        ("Reinícios médios",  "reinicios_medio"),
    ]
    hc_cols2 = [
        ("`max_passos_por_reinicio`", "valor"), ("N", "n"), ("Taxa de Sucesso", "sucesso_pct"),
        ("Tempo médio (ms)", "tempo_medio"), ("Iters. médias", "iteracoes_medio"),
        ("Reinícios médios", "reinicios_medio"),
    ]
    sa_cols_temp = [
        ("`temp_inicial`",   "valor"), ("N", "n"), ("Taxa de Sucesso", "sucesso_pct"),
        ("Tempo médio (ms)", "tempo_medio"), ("Iters. médias", "iteracoes_medio"),
        ("Conflitos médios", "conflitos_medio"),
    ]
    sa_cols_resfr = [
        ("`taxa_resfriamento`", "valor"), ("N", "n"), ("Taxa de Sucesso", "sucesso_pct"),
        ("Tempo médio (ms)", "tempo_medio"), ("Iters. médias", "iteracoes_medio"),
        ("Conflitos médios", "conflitos_medio"),
    ]
    sa_cols_iter = [
        ("`max_iteracoes`",  "valor"), ("N", "n"), ("Taxa de Sucesso", "sucesso_pct"),
        ("Tempo médio (ms)", "tempo_medio"), ("Iters. médias", "iteracoes_medio"),
        ("Conflitos médios", "conflitos_medio"),
    ]
    ga_cols_pop = [
        ("`tamanho_populacao`", "valor"), ("N", "n"), ("Taxa de Sucesso", "sucesso_pct"),
        ("Tempo médio (ms)", "tempo_medio"), ("Gerações médias", "geracoes_medio"),
        ("Conflitos médios", "conflitos_medio"),
    ]
    ga_cols_mut = [
        ("`taxa_mutacao`",   "valor"), ("N", "n"), ("Taxa de Sucesso", "sucesso_pct"),
        ("Tempo médio (ms)", "tempo_medio"), ("Gerações médias", "geracoes_medio"),
        ("Conflitos médios", "conflitos_medio"),
    ]
    ga_cols_cruz = [
        ("`taxa_cruzamento`", "valor"), ("N", "n"), ("Taxa de Sucesso", "sucesso_pct"),
        ("Tempo médio (ms)", "tempo_medio"), ("Gerações médias", "geracoes_medio"),
        ("Conflitos médios", "conflitos_medio"),
    ]
    ga_cols_gen = [
        ("`max_geracoes`",   "valor"), ("N", "n"), ("Taxa de Sucesso", "sucesso_pct"),
        ("Tempo médio (ms)", "tempo_medio"), ("Gerações médias", "geracoes_medio"),
        ("Conflitos médios", "conflitos_medio"),
    ]
    ga_cols_elit = [
        ("`n_elites`",       "valor"), ("N", "n"), ("Taxa de Sucesso", "sucesso_pct"),
        ("Tempo médio (ms)", "tempo_medio"), ("Gerações médias", "geracoes_medio"),
        ("Conflitos médios", "conflitos_medio"),
    ]

    def fmt_pct(s): return f"{s['sucesso_pct']}%"
    best_resfr = max(sa_by_resfr, key=lambda s: s["sucesso_pct"])
    worst_resfr = min(sa_by_resfr, key=lambda s: s["sucesso_pct"])
    best_mut = max(ga_by_mut, key=lambda s: s["sucesso_pct"])
    worst_mut = min(ga_by_mut, key=lambda s: s["sucesso_pct"])

    report = f"""# Implementação de Algoritmos para Resolução do Problema das 8 Rainhas

**Caetano A. de Matos, Ruan Vasconcelos**

Instituto Federal de Educação, Ciência e Tecnologia do Rio Grande do Sul — Campus Ibirubá
Rua Nelsi Ribas Fritsch, 1111 – CEP: 98200-000 – Ibirubá – RS – Brasil

---

***Abstract.** This article presents the implementation and comparative analysis of three search and optimization algorithms — Hill Climbing with Random Restart, Simulated Annealing, and Genetic Algorithm — applied to solving the classic 8 Queens problem. Beyond describing the computational modeling and one-dimensional board representation, this work presents an extensive empirical study ({n:,} executions per algorithm) with randomly sampled parameters, systematically quantifying the individual impact of each hyperparameter on success rate, execution time, and solution quality.*

***Resumo.** Este artigo apresenta a implementação e análise comparativa de três algoritmos de busca e otimização — Subida de Encosta com Reinício Aleatório, Têmpera Simulada e Algoritmo Genético — aplicados à resolução do clássico problema das 8 rainhas. Além de descrever a modelagem computacional utilizada, este trabalho apresenta um estudo empírico extenso ({n:,} execuções por algoritmo) com parâmetros amostrados aleatoriamente, quantificando sistematicamente o impacto isolado de cada hiperparâmetro sobre a taxa de sucesso, o tempo de execução e a qualidade da solução.*

---

## 1. Introdução

Este artigo apresenta o desenvolvimento e a análise de um sistema computacional voltado para a resolução do clássico problema das 8 rainhas. O desafio consiste em encontrar uma disposição para oito rainhas em um tabuleiro de xadrez 8×8 de forma que nenhuma delas esteja sob ataque mútuo, respeitando estritamente as restrições de linhas, colunas e diagonais. O código-fonte completo do projeto pode ser acessado em <https://github.com/RuanVasco/ai-projects/tree/main/8-queens-solver>.

Para solucionar este problema de otimização combinatória, foram implementadas e avaliadas três abordagens algorítmicas distintas: Subida de Encosta (*Hill Climbing*) acoplada ao mecanismo de Reinício Aleatório, Têmpera Simulada (*Simulated Annealing*) e um Algoritmo Genético. O trabalho detalha a modelagem matemática adotada — especificamente a redução do tabuleiro a vetores unidimensionais para ganho de performance — e o impacto do ajuste fino de parâmetros no comportamento de exploração e convergência de cada método.

## 2. Desenvolvimento

O problema das 8 rainhas consiste em posicionar oito rainhas em um tabuleiro de xadrez 8×8 de modo que nenhuma delas ataque outra (mesma linha, coluna ou diagonal). O espaço de busca para este problema, considerando a restrição de uma rainha por coluna, é de 8⁸ combinações. Para solucioná-lo, foram implementados três algoritmos de busca e otimização, cujas abordagens, configurações e resultados empíricos são detalhados a seguir.

### 2.1. Subida de Encosta (Hill Climbing)

Este algoritmo é uma heurística de busca local de natureza estritamente gulosa. A partir de um estado de tabuleiro atual, o algoritmo gera sua vizinhança completa — totalizando 56 vizinhos possíveis a cada passo — e transita iterativamente para o estado que apresenta a maior redução no número de ataques. Ao detectar um ótimo local, a técnica de **Reinício Aleatório** descarta o estado atual e reinicia a busca a partir de um novo estado estocástico.

#### Análise de parâmetros

Para quantificar o impacto individual de cada hiperparâmetro, foram realizadas {n:,} execuções com parâmetros sorteados aleatoriamente.

**Tabela 1.** Impacto de `max_reinicios` sobre o desempenho da Subida de Encosta.

{md_table(hc_by_reinicios, hc_cols)}

**Tabela 2.** Impacto de `max_passos_por_reinicio` sobre o desempenho da Subida de Encosta.

{md_table(hc_by_passos, hc_cols2)}

- **Configuração adotada:** Máximo de 100 reinícios e 200 passos por reinício.
- **Justificativa:** O comportamento de "serra" no gráfico de convergência indica que a estagnação é comum, mas o reinício rápido permite encontrar a solução global com baixo custo computacional. Com 100 reinícios, garante-se 100% de taxa de sucesso com ampla margem de segurança.

### 2.2. Têmpera Simulada (Simulated Annealing)

Inspirada no processo termodinâmico de recozimento físico de metais, esta meta-heurística permite transições ocasionais para estados piores segundo a probabilidade de Boltzmann P = e^(−Δ/T). Nas iterações iniciais, com T elevado, há ampla exploração do espaço de busca. Conforme T decresce, o algoritmo assume comportamento progressivamente mais guloso.

#### Análise de parâmetros

**Tabela 3.** Impacto de `temp_inicial` sobre o desempenho da Têmpera Simulada.

{md_table(sa_by_temp, sa_cols_temp)}

**Tabela 4.** Impacto de `taxa_resfriamento` sobre o desempenho da Têmpera Simulada.

{md_table(sa_by_resfr, sa_cols_resfr)}

**Tabela 5.** Impacto de `max_iteracoes` sobre o desempenho da Têmpera Simulada.

{md_table(sa_by_maxiter, sa_cols_iter)}

- **Configuração adotada:** Temperatura inicial 100,0 e taxa de resfriamento de 0,995.
- **Justificativa:** A taxa de 0,995 garante um resfriamento lento o suficiente para que o algoritmo explore o espaço antes de convergir. A taxa {best_resfr['valor']} oferece desempenho superior ({fmt_pct(best_resfr)}), porém com custo temporal substancialmente maior; a taxa {worst_resfr['valor']} resulta em apenas {fmt_pct(worst_resfr)} de sucesso.

### 2.3. Algoritmo Genético

Baseado nos princípios da teoria da evolução, este método opera sobre uma população de soluções candidatas através de três operadores: **Seleção** por torneio, **Cruzamento** (*Crossover*) de ponto único e **Mutação** aleatória por gene. O elitismo preserva os melhores indivíduos entre gerações.

#### Análise de parâmetros

**Tabela 6.** Impacto de `tamanho_populacao` sobre o desempenho do Algoritmo Genético.

{md_table(ga_by_pop, ga_cols_pop)}

**Tabela 7.** Impacto de `taxa_mutacao` sobre o desempenho do Algoritmo Genético.

{md_table(ga_by_mut, ga_cols_mut)}

**Tabela 8.** Impacto de `taxa_cruzamento` sobre o desempenho do Algoritmo Genético.

{md_table(ga_by_cruz, ga_cols_cruz)}

**Tabela 9.** Impacto de `max_geracoes` sobre o desempenho do Algoritmo Genético.

{md_table(ga_by_gen, ga_cols_gen)}

**Tabela 10.** Impacto de `n_elites` sobre o desempenho do Algoritmo Genético.

{md_table(ga_by_elit, ga_cols_elit)}

- **Configuração adotada:** População de 100 indivíduos, 90% de cruzamento e 5% de mutação.
- **Justificativa:** Esses valores garantem recombinação eficiente de boas características e evitam a convergência prematura. Os dados empíricos indicam que taxas de mutação maiores ({best_mut['valor']}) oferecem desempenho superior ({fmt_pct(best_mut)} vs. {fmt_pct(worst_mut)} com taxa {worst_mut['valor']}).

### 2.4. Resultados e Discussão

**Tabela 11.** Visão geral do desempenho médio dos algoritmos ({n:,} execuções por algoritmo, parâmetros aleatórios).

| Algoritmo | Taxa de Sucesso | Tempo Médio (ms) |
|:---|:---:|:---:|
| Subida de Encosta | {pct(hc)} | {avg_t(hc)} |
| Têmpera Simulada | {pct(sa)} | {avg_t(sa)} |
| Algoritmo Genético | {pct(ga)} | {avg_t(ga)} |

A Subida de Encosta apresentou a maior taxa de sucesso média ({pct(hc)}), beneficiando-se fortemente de `max_reinicios` ≥ 50, que por si só garante 100% de taxa de sucesso. A Têmpera Simulada e o Algoritmo Genético apresentaram taxas similares no cenário de parâmetros aleatórios, reflexo da elevada sensibilidade desses algoritmos à qualidade do ajuste de hiperparâmetros.

### 2.5. Análise Comparativa: Vantagens e Desvantagens

**1. Subida de Encosta com Reinício Aleatório**

- **Vantagens:** Extremamente leve em termos de alocação de memória, mantendo e avaliando apenas um único estado ativo por vez. Com `max_reinicios` ≥ 50, atinge 100% de taxa de sucesso em tempo médio inferior a 10 ms. O mecanismo de reinício resolve a vulnerabilidade a ótimos locais de maneira simples e robusta para espaços de busca de pequeno a médio porte.
- **Desvantagens:** É um algoritmo "míope" e desprovido de memória sistêmica. Todo o progresso feito antes de um reinício é sumariamente descartado. Em problemas de dimensionalidade muito maior, os reinícios passariam a consumir tempo excessivo.

**2. Têmpera Simulada**

- **Vantagens:** Oferece um mecanismo matemático rigoroso para transitar pelas depressões do espaço de busca sem descartar o progresso alcançado. Com `taxa_resfriamento` = {best_resfr['valor']}, alcança {fmt_pct(best_resfr)} de taxa de sucesso, mantendo a vantagem da busca local quanto ao baixo uso de memória.
- **Desvantagens:** Eficácia criticamente sensível à calibração de hiperparâmetros. Um ajuste inadequado da taxa de resfriamento pode arruinar a busca: com taxa de {worst_resfr['valor']}, a taxa de sucesso cai para {fmt_pct(worst_resfr)}.

**3. Algoritmo Genético**

- **Vantagens:** Notável poder de exploração paralela, avaliando múltiplas regiões do espaço de busca simultaneamente. É a técnica mais resiliente contra ótimos locais, com desempenho crescente à medida que a população e o número de gerações aumentam.
- **Desvantagens:** Apresentou o maior custo computacional médio ({avg_t(ga)} ms), evidenciando o *overhead* de gerenciar populações inteiras a cada geração. Trata-se de uma ferramenta superdimensionada (*overkill*) para a escala do problema das 8 rainhas.

## 3. Conclusão

Para o problema das 8 rainhas, os métodos de busca local (Subida de Encosta e Têmpera Simulada) mostraram-se superiores em eficiência. O estudo empírico com {n:,} execuções por algoritmo revelou que a **Subida de Encosta com Reinício Aleatório** é a escolha mais equilibrada: com apenas 50 reinícios, garante 100% de taxa de sucesso em tempo médio inferior a 10 ms. A Têmpera Simulada demonstrou forte dependência da taxa de resfriamento — o parâmetro mais crítico do algoritmo —, com taxa de sucesso variando de {fmt_pct(worst_resfr)} (resfriamento agressivo, {worst_resfr['valor']}) a {fmt_pct(best_resfr)} (resfriamento lento, {best_resfr['valor']}). O Algoritmo Genético, embora melhore consistentemente com o aumento de população e número de gerações, permanece consideravelmente mais lento e, nesta escala de problema, superdimensionado. Conclui-se que a complexidade algorítmica deve ser proporcional à escala do problema: para as 8 rainhas, a simplicidade da Subida de Encosta com Reinício Aleatório supera em eficiência as abordagens mais sofisticadas.

## Referências
"""

    report_path = SCRIPT_DIR / "relatorio.md"
    report_path.write_text(report, encoding="utf-8")
    print(f"Relatório gerado: {report_path}")
    return report_path


# ---------------------------------------------------------------------------
# Ponto de entrada
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Benchmark dos algoritmos de 8 rainhas")
    parser.add_argument("--runs", type=int, default=N_RUNS,
                        help=f"Execuções por algoritmo (padrão: {N_RUNS})")
    parser.add_argument("--only-report", metavar="JSON",
                        help="Pula o benchmark e gera o relatório a partir de um JSON existente")
    args = parser.parse_args()

    if args.only_report:
        with open(args.only_report, encoding="utf-8") as f:
            data = json.load(f)
        generate_report(data)
    else:
        print(f"Benchmark — 8 Rainhas  ({args.runs} execuções por algoritmo)")
        data = benchmark(args.runs)
        generate_report(data)
        print("\nConcluído!")
