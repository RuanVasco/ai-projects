import time
import random
import statistics

from src.board import estado_aleatorio, contar_conflitos


def _fitness(individuo: list[int]) -> int:
    return 28 - contar_conflitos(individuo)


def _inicializar_populacao(tamanho: int) -> list[list[int]]:
    return [estado_aleatorio() for _ in range(tamanho)]


def _selecao_torneio(populacao: list[list[int]], k: int = 3) -> list[int]:
    participantes = random.choices(populacao, k=k)
    return max(participantes, key=_fitness)


def _cruzamento(pai1: list[int], pai2: list[int]) -> tuple[list[int], list[int]]:
    ponto_corte = random.randint(1, 7)
    filho1 = pai1[:ponto_corte] + pai2[ponto_corte:]
    filho2 = pai2[:ponto_corte] + pai1[ponto_corte:]
    return filho1, filho2


def _mutacao(individuo: list[int], taxa: float) -> list[int]:
    mutado = individuo[:]
    for i in range(8):
        if random.random() < taxa:
            valor_atual = mutado[i]
            nova_linha = random.choice([r for r in range(8) if r != valor_atual])
            mutado[i] = nova_linha
    return mutado


def algoritmo_genetico(
    tamanho_populacao: int = 100,
    taxa_mutacao: float = 0.05,
    taxa_cruzamento: float = 0.9,
    max_geracoes: int = 1000,
    n_elites: int = 2,
    semente: int | None = None,
) -> dict:
    if semente is not None:
        random.seed(semente)

    inicio = time.perf_counter()

    populacao = _inicializar_populacao(tamanho_populacao)

    historico_melhor_fitness = []
    historico_media_fitness = []

    melhor_individuo = None
    melhor_fitness_global = -1

    geracao = 0
    for geracao in range(max_geracoes):
        populacao.sort(key=_fitness, reverse=True)

        melhor_da_geracao = populacao[0]
        fitness_melhor = _fitness(melhor_da_geracao)
        fitness_valores = [_fitness(ind) for ind in populacao]
        media_fitness = statistics.mean(fitness_valores)

        historico_melhor_fitness.append(fitness_melhor)
        historico_media_fitness.append(round(media_fitness, 2))

        if fitness_melhor > melhor_fitness_global:
            melhor_individuo = melhor_da_geracao[:]
            melhor_fitness_global = fitness_melhor

        if fitness_melhor == 28:
            break

        nova_populacao = [ind[:] for ind in populacao[:n_elites]]

        while len(nova_populacao) < tamanho_populacao:
            pai1 = _selecao_torneio(populacao)
            pai2 = _selecao_torneio(populacao)

            if random.random() < taxa_cruzamento:
                filho1, filho2 = _cruzamento(pai1, pai2)
            else:
                filho1, filho2 = pai1[:], pai2[:]

            filho1 = _mutacao(filho1, taxa_mutacao)
            filho2 = _mutacao(filho2, taxa_mutacao)

            nova_populacao.append(filho1)
            if len(nova_populacao) < tamanho_populacao:
                nova_populacao.append(filho2)

        populacao = nova_populacao

    tempo_ms = (time.perf_counter() - inicio) * 1000
    conflitos_finais = contar_conflitos(melhor_individuo)

    return {
        "algoritmo": "Algoritmo Genético",
        "solucao": melhor_individuo,
        "conflitos": conflitos_finais,
        "geracoes": geracao + 1,
        "tempo_ms": tempo_ms,
        "sucesso": conflitos_finais == 0,
        "historico_melhor_fitness": historico_melhor_fitness,
        "historico_media_fitness": historico_media_fitness,
    }
