import streamlit as st

st.set_page_config(
    page_title="8 Queens Solver",
    page_icon="♛",
    layout="wide",
)

st.title("♛ Problema das 8 Rainhas")
st.caption("Comparação entre Subida de Encosta, Têmpera Simulada e Algoritmo Genético")

st.divider()

col_hc, col_sa, col_ga = st.columns(3)

with col_hc:
    st.subheader("Subida de Encosta")
    st.caption("Com Reinício Aleatório")

with col_sa:
    st.subheader("Têmpera Simulada")
    st.caption("Simulated Annealing")

with col_ga:
    st.subheader("Algoritmo Genético")
    st.caption("Genetic Algorithm")

st.divider()
st.info("Implemente os algoritmos em `src/algorithms/` e adicione os controles aqui.")
