import streamlit as st
import pandas as pd

# CONFIGURACIÓN
st.set_page_config(page_title="Dashboard Valorización", layout="wide")

st.title("♻️ Dashboard de Valorización")

# SIDEBAR
st.sidebar.header("⚙️ Configuración")

# MODO HÍBRIDO
modo = st.sidebar.radio("Modo de uso", ["Datos compartidos", "Subir mi archivo"])

# CARGA DE DATOS
if modo == "Datos compartidos":
    try:
        df = pd.read_excel("resultado.xlsx")
    except:
        st.error("No se encontró el archivo 'resultado.xlsx' en el repositorio")
        st.stop()
else:
    archivo = st.sidebar.file_uploader("Sube tu archivo Excel", type=["xlsx"])
    if archivo is not None:
        df = pd.read_excel(archivo)
    else:
        st.warning("Sube un archivo para continuar")
        st.stop()

# LIMPIEZA DE DATOS
df["Fecha emisión"] = pd.to_datetime(df["Fecha emisión"], errors="coerce")

# FILTROS
st.sidebar.subheader("🔎 Filtros")

comuna = st.sidebar.selectbox("Comuna", ["Todas"] + list(df["Sucursal"].dropna().unique()))
valorizador = st.sidebar.selectbox("Valorizador", ["Todos"] + list(df["Valorizador"].dropna().unique()))
patente = st.sidebar.selectbox("Patente", ["Todas"] + list(df["Patente"].dropna().unique()))

# FILTRADO
filtered = df.copy()

if comuna != "Todas":
    filtered = filtered[filtered["Sucursal"] == comuna]

if valorizador != "Todos":
    filtered = filtered[filtered["Valorizador"] == valorizador]

if patente != "Todas":
    filtered = filtered[filtered["Patente"] == patente]

# KPIs
st.subheader("📊 Indicadores clave")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total registros", len(filtered))
col2.metric("Valorizadores", filtered["Valorizador"].nunique())
col3.metric("Comunas", filtered["Sucursal"].nunique())

# CRECIMIENTO MENSUAL
filtered["Mes"] = filtered["Fecha emisión"].dt.to_period("M")

mensual = filtered.groupby("Mes").size().reset_index(name="Cantidad")

if len(mensual) >= 2:
    anterior = mensual["Cantidad"].iloc[-2]
    actual = mensual["Cantidad"].iloc[-1]
    crecimiento = ((actual - anterior) / anterior) * 100 if anterior != 0 else 0
    col4.metric("Crecimiento mensual", f"{crecimiento:.1f}%")
else:
    col4.metric("Crecimiento mensual", "N/A")

# GRÁFICOS
st.subheader("📈 Análisis")

col1, col2 = st.columns(2)

with col1:
    st.write("📍 Distribución por comuna")
    st.bar_chart(filtered["Sucursal"].value_counts())

with col2:
    st.write("🏆 Top valorizadores")
    st.bar_chart(filtered["Valorizador"].value_counts())

# EVOLUCIÓN EN EL TIEMPO
st.subheader("⏳ Evolución en el tiempo")

mensual["Mes"] = mensual["Mes"].astype(str)
st.line_chart(mensual.set_index("Mes"))

# RANKING
st.subheader("🥇 Ranking valorizadores")

ranking = filtered["Valorizador"].value_counts().reset_index()
ranking.columns = ["Valorizador", "Cantidad"]

st.dataframe(ranking, use_container_width=True)

# TABLA DETALLADA
st.subheader("📄 Datos detallados")

st.dataframe(filtered, use_container_width=True)
