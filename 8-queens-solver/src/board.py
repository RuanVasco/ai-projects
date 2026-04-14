import random
import plotly.graph_objects as go


def estado_aleatorio() -> list[int]:
    return [random.randint(0, 7) for _ in range(8)]


def contar_conflitos(estado: list[int]) -> int:
    conflitos = 0
    n = len(estado)
    for i in range(n):
        for j in range(i + 1, n):
            if estado[i] == estado[j]:
                conflitos += 1
            if abs(estado[i] - estado[j]) == abs(i - j):
                conflitos += 1
    return conflitos


def obter_vizinhos(estado: list[int]) -> list[list[int]]:
    vizinhos = []
    for col in range(8):
        for linha in range(8):
            if linha != estado[col]:
                novo_estado = estado[:]
                novo_estado[col] = linha
                vizinhos.append(novo_estado)
    return vizinhos


def melhor_vizinho(estado: list[int]) -> tuple[list[int], int]:
    vizinhos = obter_vizinhos(estado)
    conflitos_vizinhos = [(v, contar_conflitos(v)) for v in vizinhos]
    min_conflitos = min(c for _, c in conflitos_vizinhos)
    melhores = [v for v, c in conflitos_vizinhos if c == min_conflitos]
    escolhido = random.choice(melhores)
    return escolhido, min_conflitos


def vizinho_aleatorio(estado: list[int]) -> list[int]:
    novo_estado = estado[:]
    col = random.randint(0, 7)
    linha_atual = estado[col]
    nova_linha = random.choice([r for r in range(8) if r != linha_atual])
    novo_estado[col] = nova_linha
    return novo_estado


def criar_figura_tabuleiro(estado: list[int], titulo: str = "") -> go.Figure:
    z = [[(r + c) % 2 for c in range(8)] for r in range(8)]

    fig = go.Figure()

    fig.add_trace(go.Heatmap(
        z=z,
        colorscale=[[0, "#f0d9b5"], [1, "#b58863"]],
        showscale=False,
        xgap=1,
        ygap=1,
        hoverinfo="none",
    ))

    em_conflito = set()
    for i in range(8):
        for j in range(i + 1, 8):
            if estado[i] == estado[j] or abs(estado[i] - estado[j]) == abs(i - j):
                em_conflito.add(i)
                em_conflito.add(j)

    xs = list(range(8))
    ys = list(estado)
    cores = ["red" if col in em_conflito else "green" for col in range(8)]
    textos_hover = [
        f"Coluna {c}, Linha {estado[c]} — {'em conflito' if c in em_conflito else 'sem conflito'}"
        for c in range(8)
    ]

    fig.add_trace(go.Scatter(
        x=xs,
        y=ys,
        mode="text",
        text=["♛"] * 8,
        textfont=dict(size=30, color=cores),
        hovertext=textos_hover,
        hoverinfo="text",
        showlegend=False,
    ))

    fig.update_layout(
        title=dict(text=titulo, x=0.5, font=dict(size=14)),
        height=320,
        margin=dict(l=5, r=5, t=35, b=5),
        xaxis=dict(showticklabels=False, showgrid=False, zeroline=False, range=[-0.5, 7.5]),
        yaxis=dict(showticklabels=False, showgrid=False, zeroline=False, scaleanchor="x", range=[-0.5, 7.5]),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )

    return fig
