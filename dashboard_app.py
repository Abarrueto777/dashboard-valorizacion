import streamlit as st
import pandas as pd

# CONFIG
st.set_page_config(page_title="Dashboard Valorización", layout="wide")

st.title("📊 Dashboard de Valorización")

# CARGA DE DATOS
df = pd.read_excel("resultado.xlsx")

# LIMPIEZA
df["Fecha emisión"] = pd.to_datetime(df["Fecha emisión"], errors="coerce")

# FILTROS
col1, col2, col3 = st.columns(3)

with col1:
    comuna = st.selectbox("Comuna", ["Todas"] + list(df["Sucursal"].dropna().unique()))

with col2:
    valorizador = st.selectbox("Valorizador", ["Todos"] + list(df["Valorizador"].dropna().unique()))

with col3:
    patente = st.selectbox("Patente", ["Todas"] + list(df["Patente"].dropna().unique()))

# FILTRADO
filtered = df.copy()

if comuna != "Todas":
    filtered = filtered[filtered["Sucursal"] == comuna]

if valorizador != "Todos":
    filtered = filtered[filtered["Valorizador"] == valorizador]

if patente != "Todas":
    filtered = filtered[filtered["Patente"] == patente]

# KPIs
st.subheader("📌 Indicadores clave")

col1, col2, col3 = st.columns(3)

col1.metric("Total registros", len(filtered))
col2.metric("Valorizadores únicos", filtered["Valorizador"].nunique())
col3.metric("Comunas activas", filtered["Sucursal"].nunique())

# GRÁFICOS
st.subheader("📊 Análisis")

col1, col2 = st.columns(2)

with col1:
    st.write("Distribución por comuna")
    st.bar_chart(filtered["Sucursal"].value_counts())

with col2:
    st.write("Top valorizadores")
    st.bar_chart(filtered["Valorizador"].value_counts())

# EVOLUCIÓN EN EL TIEMPO 🔥
st.subheader("⏳ Evolución en el tiempo")

time_data = filtered.copy()
time_data["Mes"] = time_data["Fecha emisión"].dt.to_period("M").astype(str)

evolucion = time_data.groupby("Mes").size()

st.line_chart(evolucion)

# TABLA FINAL
st.subheader("📄 Datos detallados")
st.dataframe(filtered, use_container_width=True)