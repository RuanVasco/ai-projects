import time
import random

from src.board import estado_aleatorio, contar_conflitos, melhor_vizinho


def subida_encosta(
    max_reinicios: int = 100,
    max_passos_por_reinicio: int = 200,
    semente: int | None = None,
) -> dict:
    if semente is not None:
        random.seed(semente)

    inicio = time.perf_counter()
    reinicios = 0
    total_iteracoes = 0
    historico_conflitos = []

    melhor_global = estado_aleatorio()
    melhor_conflitos_global = contar_conflitos(melhor_global)

    for _ in range(max_reinicios + 1):
        estado_atual = estado_aleatorio()
        conflitos_atual = contar_conflitos(estado_atual)

        for _ in range(max_passos_por_reinicio):
            historico_conflitos.append(conflitos_atual)
            total_iteracoes += 1

            if conflitos_atual == 0:
                tempo_ms = (time.perf_counter() - inicio) * 1000
                return {
                    "algoritmo": "Subida de Encosta",
                    "solucao": estado_atual,
                    "conflitos": 0,
                    "reinicios": reinicios,
                    "iteracoes": total_iteracoes,
                    "tempo_ms": tempo_ms,
                    "sucesso": True,
                    "historico_conflitos": historico_conflitos,
                }

            proximo_estado, conflitos_proximo = melhor_vizinho(estado_atual)

            if conflitos_proximo >= conflitos_atual:
                break

            estado_atual = proximo_estado
            conflitos_atual = conflitos_proximo

        if conflitos_atual < melhor_conflitos_global:
            melhor_global = estado_atual
            melhor_conflitos_global = conflitos_atual

        reinicios += 1

    tempo_ms = (time.perf_counter() - inicio) * 1000
    return {
        "algoritmo": "Subida de Encosta",
        "solucao": melhor_global,
        "conflitos": melhor_conflitos_global,
        "reinicios": reinicios,
        "iteracoes": total_iteracoes,
        "tempo_ms": tempo_ms,
        "sucesso": False,
        "historico_conflitos": historico_conflitos,
    }
