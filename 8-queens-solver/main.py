import streamlit as st
import plotly.express as px
import pandas as pd

from src.board import criar_figura_tabuleiro
from src.algorithms.hill_climbing import subida_encosta
from src.algorithms.simulated_annealing import tempera_simulada
from src.algorithms.genetic import algoritmo_genetico

st.set_page_config(
    page_title="8 Queens Solver",
    page_icon="♛",
    layout="wide",
)

if "resultados" not in st.session_state:
    st.session_state["resultados"] = {}

st.title("♛ Problema das 8 Rainhas")
st.caption(
    "Comparação entre **Subida de Encosta**, **Têmpera Simulada** e **Algoritmo Genético**. "
    "Configure os parâmetros, selecione os algoritmos e execute."
)
st.divider()

col_hc, col_sa, col_ga = st.columns(3)

with col_hc:
    executar_hc = st.checkbox("**Subida de Encosta**", value=True, key="chk_hc")
    st.caption("Com Reinício Aleatório")

    with st.expander("Parâmetros", expanded=True):
        hc_max_reinicios = st.number_input(
            "Máximo de Reinícios",
            min_value=1,
            max_value=2000,
            value=100,
            step=10,
            key="hc_reinicios",
            help="Quantas vezes o algoritmo pode reiniciar ao ficar preso em um ótimo local.",
        )
        hc_max_passos = st.number_input(
            "Passos por Reinício",
            min_value=10,
            max_value=1000,
            value=200,
            step=10,
            key="hc_passos",
            help="Limite de movimentos antes de forçar um reinício.",
        )

with col_sa:
    executar_sa = st.checkbox("**Têmpera Simulada**", value=True, key="chk_sa")
    st.caption("Simulated Annealing")

    with st.expander("Parâmetros", expanded=True):
        sa_temp_inicial = st.slider(
            "Temperatura Inicial",
            min_value=10.0,
            max_value=500.0,
            value=100.0,
            step=10.0,
            key="sa_temp",
            help="Temperatura de partida. Valores altos permitem maior exploração inicial.",
        )
        sa_taxa_resfriamento = st.slider(
            "Taxa de Resfriamento",
            min_value=0.900,
            max_value=0.9999,
            value=0.995,
            step=0.001,
            format="%.4f",
            key="sa_resfriamento",
            help="Fator de redução da temperatura por iteração. Próximo de 1 = resfriamento lento.",
        )
        sa_max_iter = st.number_input(
            "Máximo de Iterações",
            min_value=1_000,
            max_value=200_000,
            value=50_000,
            step=5_000,
            key="sa_iter",
            help="Limite máximo de iterações do algoritmo.",
        )

with col_ga:
    executar_ga = st.checkbox("**Algoritmo Genético**", value=True, key="chk_ga")
    st.caption("Genetic Algorithm")

    with st.expander("Parâmetros", expanded=True):
        ga_pop = st.slider(
            "Tamanho da População",
            min_value=20,
            max_value=500,
            value=100,
            step=10,
            key="ga_pop",
            help="Número de indivíduos em cada geração.",
        )
        ga_mutacao = st.slider(
            "Taxa de Mutação",
            min_value=0.01,
            max_value=0.50,
            value=0.05,
            step=0.01,
            format="%.2f",
            key="ga_mutacao",
            help="Probabilidade de mutação por gene do cromossomo.",
        )
        ga_cruzamento = st.slider(
            "Taxa de Cruzamento",
            min_value=0.50,
            max_value=1.00,
            value=0.90,
            step=0.05,
            format="%.2f",
            key="ga_cruzamento",
            help="Probabilidade de cruzamento entre dois pais selecionados.",
        )
        ga_geracoes = st.number_input(
            "Máximo de Gerações",
            min_value=100,
            max_value=5_000,
            value=1_000,
            step=100,
            key="ga_geracoes",
            help="Limite máximo de gerações evolutivas.",
        )

algos_selecionados = executar_hc or executar_sa or executar_ga

col_btn, col_clear = st.columns([3, 1])
with col_btn:
    executar = st.button(
        "▶ Executar Algoritmos Selecionados",
        key="btn_executar",
        type="primary",
        disabled=not algos_selecionados,
        use_container_width=True,
    )
with col_clear:
    if st.button("Limpar Resultados", key="btn_limpar", use_container_width=True):
        st.session_state["resultados"] = {}
        st.rerun()

if executar:
    if executar_hc:
        with st.spinner("Executando Subida de Encosta..."):
            resultado = subida_encosta(
                max_reinicios=hc_max_reinicios,
                max_passos_por_reinicio=hc_max_passos,
            )
            st.session_state["resultados"]["hc"] = resultado

    if executar_sa:
        with st.spinner("Executando Têmpera Simulada..."):
            resultado = tempera_simulada(
                temp_inicial=sa_temp_inicial,
                taxa_resfriamento=sa_taxa_resfriamento,
                max_iteracoes=sa_max_iter,
            )
            st.session_state["resultados"]["sa"] = resultado

    if executar_ga:
        with st.spinner("Executando Algoritmo Genético..."):
            resultado = algoritmo_genetico(
                tamanho_populacao=ga_pop,
                taxa_mutacao=ga_mutacao,
                taxa_cruzamento=ga_cruzamento,
                max_geracoes=ga_geracoes,
            )
            st.session_state["resultados"]["ga"] = resultado

st.divider()

resultados = st.session_state["resultados"]

if resultados:
    col_hc_r, col_sa_r, col_ga_r = st.columns(3)
    cols_resultado = {"hc": col_hc_r, "sa": col_sa_r, "ga": col_ga_r}
    titulos = {
        "hc": "Subida de Encosta",
        "sa": "Têmpera Simulada",
        "ga": "Algoritmo Genético",
    }

    for chave, col in cols_resultado.items():
        if chave not in resultados:
            continue
        r = resultados[chave]
        with col:
            with st.container(border=True):
                st.subheader(titulos[chave])
                if r["sucesso"]:
                    st.success("Solução encontrada!")
                else:
                    st.warning(f"Melhor: {8 - r['conflitos']} rainhas sem conflito")

                fig_tab = criar_figura_tabuleiro(r["solucao"], titulo=f"Tabuleiro — {titulos[chave]}")
                st.plotly_chart(fig_tab, width='stretch', key=f"tab_{chave}")

                m1, m2 = st.columns(2)
                m1.metric("Conflitos", r["conflitos"])
                m2.metric("Tempo (ms)", f"{r['tempo_ms']:.1f}")
                if chave == "hc":
                    m1.metric("Reinícios", r["reinicios"])
                    m2.metric("Iterações", r["iteracoes"])
                elif chave == "sa":
                    m1.metric("Iterações", r["iteracoes"])
                    m2.metric("Temp. Final", f"{r['temperatura_final']:.4f}")
                elif chave == "ga":
                    m1.metric("Gerações", r["geracoes"])
                    m2.metric("Fitness Final", 28 - r["conflitos"])

st.divider()
st.subheader("Comparação dos Algoritmos")

if len(resultados) < 2:
    algoritmos_faltando = 2 - len(resultados)
    st.info(
        f"Execute pelo menos **2 algoritmos** para ver a comparação "
        f"({'falta ' + str(algoritmos_faltando) + ' algoritmo' if algoritmos_faltando == 1 else 'faltam ' + str(algoritmos_faltando) + ' algoritmos'})."
    )
else:
    nomes = {
        "hc": "Subida de Encosta",
        "sa": "Têmpera Simulada",
        "ga": "Algoritmo Genético",
    }

    chaves = list(resultados.keys())
    nomes_exibidos = [nomes[k] for k in chaves]
    dados = [resultados[k] for k in chaves]

    comp1, comp2, comp3 = st.columns(3)

    with comp1:
        fig_tempo = px.bar(
            x=nomes_exibidos,
            y=[r["tempo_ms"] for r in dados],
            labels={"x": "Algoritmo", "y": "Tempo (ms)"},
            title="Tempo de Execução (ms)",
            color=nomes_exibidos,
            color_discrete_sequence=px.colors.qualitative.Plotly,
            text_auto=".1f",
        )
        fig_tempo.update_layout(height=300, showlegend=False, margin=dict(l=5, r=5, t=45, b=5))
        st.plotly_chart(fig_tempo, width='stretch', key="comp_tempo")

    with comp2:
        iters = []
        for k in chaves:
            r = resultados[k]
            iters.append(r.get("iteracoes") or r.get("geracoes") or 0)

        fig_iter = px.bar(
            x=nomes_exibidos,
            y=iters,
            labels={"x": "Algoritmo", "y": "Iterações / Reinícios"},
            title="Iterações ou Reinícios",
            color=nomes_exibidos,
            color_discrete_sequence=px.colors.qualitative.Plotly,
            text_auto=True,
        )
        fig_iter.update_layout(height=300, showlegend=False, margin=dict(l=5, r=5, t=45, b=5))
        st.plotly_chart(fig_iter, width='stretch', key="comp_iter")

    with comp3:
        fig_qualidade = px.bar(
            x=nomes_exibidos,
            y=[8 - r["conflitos"] for r in dados],
            labels={"x": "Algoritmo", "y": "Rainhas Sem Conflito"},
            title="Qualidade da Solução",
            color=nomes_exibidos,
            color_discrete_sequence=px.colors.qualitative.Plotly,
            text_auto=True,
        )
        fig_qualidade.update_layout(
            height=300,
            showlegend=False,
            margin=dict(l=5, r=5, t=45, b=5),
            yaxis=dict(range=[0, 8]),
        )
        st.plotly_chart(fig_qualidade, width='stretch', key="comp_qualidade")

    linhas = []
    for k in chaves:
        r = resultados[k]
        iters_val = r.get("iteracoes") or r.get("geracoes") or None
        reinicios_val = r.get("reinicios", None)
        linhas.append({
            "Algoritmo": nomes[k],
            "Sucesso": "Sim" if r["sucesso"] else "Não",
            "Tempo (ms)": round(r["tempo_ms"], 2),
            "Iterações / Gerações": iters_val,
            "Reinícios": reinicios_val,
            "Rainhas sem conflito": 8 - r["conflitos"],
            "Conflitos": r["conflitos"],
        })

    df = pd.DataFrame(linhas)
    st.dataframe(df, width='stretch', hide_index=True)
