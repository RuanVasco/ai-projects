import time
import math
import random

from src.board import estado_aleatorio, contar_conflitos, vizinho_aleatorio


def tempera_simulada(
    temp_inicial: float = 100.0,
    taxa_resfriamento: float = 0.995,
    temp_min: float = 0.01,
    max_iteracoes: int = 50_000,
    semente: int | None = None,
) -> dict:
    if semente is not None:
        random.seed(semente)

    inicio = time.perf_counter()

    estado_atual = estado_aleatorio()
    conflitos_atual = contar_conflitos(estado_atual)

    melhor_estado = estado_atual[:]
    melhor_conflitos = conflitos_atual

    temperatura = temp_inicial

    amostra_a_cada = max(1, max_iteracoes // 500)
    historico_conflitos = []
    historico_temperatura = []

    iteracao = 0
    for iteracao in range(max_iteracoes):
        if conflitos_atual == 0:
            break

        if temperatura < temp_min:
            break

        if iteracao % amostra_a_cada == 0:
            historico_conflitos.append(conflitos_atual)
            historico_temperatura.append(round(temperatura, 6))

        vizinho = vizinho_aleatorio(estado_atual)
        conflitos_vizinho = contar_conflitos(vizinho)

        delta = conflitos_vizinho - conflitos_atual

        if delta < 0:
            estado_atual = vizinho
            conflitos_atual = conflitos_vizinho
        else:
            if temperatura > 1e-10:
                probabilidade = math.exp(-delta / temperatura)
                if random.random() < probabilidade:
                    estado_atual = vizinho
                    conflitos_atual = conflitos_vizinho

        if conflitos_atual < melhor_conflitos:
            melhor_estado = estado_atual[:]
            melhor_conflitos = conflitos_atual

        temperatura *= taxa_resfriamento

    historico_conflitos.append(melhor_conflitos)
    historico_temperatura.append(round(temperatura, 6))

    tempo_ms = (time.perf_counter() - inicio) * 1000
    return {
        "algoritmo": "Têmpera Simulada",
        "solucao": melhor_estado,
        "conflitos": melhor_conflitos,
        "iteracoes": iteracao + 1,
        "tempo_ms": tempo_ms,
        "sucesso": melhor_conflitos == 0,
        "temperatura_final": round(temperatura, 6),
        "historico_conflitos": historico_conflitos,
        "historico_temperatura": historico_temperatura,
    }
