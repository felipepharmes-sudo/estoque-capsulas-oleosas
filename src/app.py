import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# ─── 1. CONEXÃO COM SEU GOOGLE SHEETS ─────────────────────────────
conn = st.connection("gsheets", type=GSheetsConnection)

# Lê a aba "Estoque Atual"
df = conn.read(
    worksheet="Estoque Atual",
    ttl="10s",  # recarrega a cada ~10 segundos
)

# Evita erro se não tiver dados
if df.empty:
    st.warning("Nenhum produto encontrado no Google Sheets. Verifique se a aba está com nome 'Estoque Atual'.")
    st.stop()

df = df.dropna(subset=["Produto"])  # remove linhas sem nome de produto

# ─── 2. DASHBOARD PRINCIPAL ───────────────────────────────────────

st.title("📦 Dashboard Estoque de Cápsulas Oleosas")
st.markdown("Dados atualizados diretamente do Google Sheets.")

# ────────────────────────────────────────────────────────────────
# 2.1. SELETOR DE PRODUTO + FOTO
# Assume que:
# - Coluna "Produto" = nome do produto
# - Coluna "Foto"  = URL da imagem (ex: Google Drive exposta)

produtos = df["Produto"].tolist()
produto_selecionado = st.selectbox(
    "Selecione o produto",
    options=produtos,
    index=0,
)

linha = df[df["Produto"] == produto_selecionado].iloc[0]
url_foto = linha["Foto"]

st.divider()
st.subheader(" Produto selecionado ")

if pd.notna(url_foto) and url_foto.strip():
    st.image(url_foto, width=200, caption="Foto do produto")
else:
    st.write("📘 Sem foto cadastrada.")

# Detalhes do produto em colunas
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Código"        , linha["Código"] )
    st.metric("Lote"          , linha["Lote"]   )
    st.metric("Fornecedor"    , linha["Fornecedor"] )

with col2:
    st.metric("Qtd Atual"     , linha["Qtd Atual"] )
    st.metric("Qtd Mínima"    , linha["Qtd Mínima"] )
    st.metric("Qtd Máxima"    , linha["Qtd Máxima"] )

with col3:
    st.metric("Preço Unitário", f"R$ {linha['Preço Unitário']:,.2f}")
    st.metric("Valor Total"   , f"R$ {linha['Valor Total']:,.2f}")
    st.metric("Status"        , linha["Status"] )

# ────────────────────────────────────────────────────────────────
# 2.2. INDICADORES GLOBAIS
st.divider()
st.subheader("📈 Indicadores Gerais")

estoque_total = df["Valor Total"].sum()
abaixo_minimo = (df["Status"] == "Abaixo Mínimo").sum()
vencer_2m     = df["Status"].str.contains("Vence 2 Meses",   na=False).sum()
vencer_3m     = df["Status"].str.contains("Vence 3 Meses",   na=False).sum()
estoque_ok    = (df["Status"] == "Estoque Estável").sum()

cols = st.columns(6)
cols[0].metric("Total Produtos" , len(df))
cols[1].metric("Valor Total"    , f"R$ {estoque_total:,.2f}")
cols[2].metric("Abaixo Mínimo"  , abaixo_minimo)
cols[3].metric("Vence 2 Meses"  , vencer_2m)
cols[4].metric("Vence 3 Meses"  , vencer_3m)
cols[5].metric("Estoque OK"     , estoque_ok)

# ────────────────────────────────────────────────────────────────
# 2.3. GRÁFICO DE STATUS
st.divider()
st.subheader("📊 Status de Estoque")

status_count = df["Status"].value_counts()
st.bar_chart(status_count)

# ────────────────────────────────────────────────────────────────
# 2.4. TABELA COMPLETA
st.divider()
st.subheader("📋 Estoque Completo")

st.dataframe(df)

