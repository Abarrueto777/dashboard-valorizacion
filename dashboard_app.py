import streamlit as st
import pandas as pd

# CONFIG
st.set_page_config(page_title="Informe Ejecutivo", layout="wide")

st.markdown("## 📊 Informe Ejecutivo de Valorización")
st.markdown("Análisis consolidado para toma de decisiones")

# SIDEBAR
st.sidebar.header("⚙️ Configuración")

modo = st.sidebar.radio("Modo de uso", ["Datos compartidos", "Subir archivo"])

# CARGA DE DATOS
if modo == "Datos compartidos":
    df = pd.read_excel("resultado.xlsx")
else:
    archivo = st.sidebar.file_uploader("Sube Excel", type=["xlsx"])
    if archivo:
        df = pd.read_excel(archivo)
    else:
        st.stop()

# LIMPIEZA FECHAS (CLAVE 🔥)
df["Fecha emisión"] = pd.to_datetime(
    df["Fecha emisión"],
    dayfirst=True,
    errors="coerce"
)

# ELIMINAR FILAS SIN FECHA VÁLIDA
df = df.dropna(subset=["Fecha emisión"])

# FILTRO POR FECHA
st.sidebar.subheader("📅 Periodo")

fecha_min = df["Fecha emisión"].min()
fecha_max = df["Fecha emisión"].max()

rango = st.sidebar.date_input("Rango", [fecha_min, fecha_max])

filtered = df.copy()

if len(rango) == 2:
    inicio = pd.to_datetime(rango[0])
    fin = pd.to_datetime(rango[1]) + pd.Timedelta(days=1)

    filtered = filtered[
        (filtered["Fecha emisión"] >= inicio) &
        (filtered["Fecha emisión"] < fin)
    ]

# FILTROS
st.sidebar.subheader("🔎 Segmentación")

comuna = st.sidebar.selectbox("Comuna", ["Todas"] + list(df["Sucursal"].dropna().unique()))
valorizador = st.sidebar.selectbox("Valorizador", ["Todos"] + list(df["Valorizador"].dropna().unique()))

if comuna != "Todas":
    filtered = filtered[filtered["Sucursal"] == comuna]

if valorizador != "Todos":
    filtered = filtered[filtered["Valorizador"] == valorizador]

# KPIs
st.markdown("### 📌 Resumen Ejecutivo")

col1, col2, col3, col4 = st.columns(4)

total = len(filtered)
valorizadores = filtered["Valorizador"].nunique()
comunas = filtered["Sucursal"].nunique()

# ===== EVOLUCIÓN Y CRECIMIENTO (CORREGIDO 🔥) =====
filtered_valid = filtered.copy()

filtered_valid["Mes"] = filtered_valid["Fecha emisión"].dt.to_period("M")

mensual = filtered_valid.groupby("Mes").size().reset_index(name="Cantidad")
mensual = mensual.sort_values("Mes")

if len(mensual) >= 2:
    actual = mensual["Cantidad"].iloc[-1]
    anterior = mensual["Cantidad"].iloc[-2]

    if anterior != 0:
        crecimiento = ((actual - anterior) / anterior) * 100
    else:
        crecimiento = 0
else:
    crecimiento = 0

col1.metric("Operaciones", total)
col2.metric("Valorizadores", valorizadores)
col3.metric("Cobertura", comunas)
col4.metric("Crecimiento", f"{crecimiento:.1f}%")

# INSIGHTS AUTOMÁTICOS
st.markdown("### 🧠 Insights Clave")

if not filtered.empty:
    top_valorizador = filtered["Valorizador"].value_counts().idxmax()
    top_comuna = filtered["Sucursal"].value_counts().idxmax()

    st.info(f"""
• El valorizador con mayor actividad es **{top_valorizador}**  
• La comuna con mayor volumen es **{top_comuna}**  
• El crecimiento mensual es de **{crecimiento:.1f}%**
""")
else:
    st.warning("No hay datos para generar insights")

# GRÁFICOS
st.markdown("### 📈 Análisis")

col1, col2 = st.columns(2)

with col1:
    if not filtered.empty:
        st.bar_chart(filtered["Sucursal"].value_counts())
    else:
        st.warning("Sin datos para comuna")

with col2:
    if not filtered.empty:
        st.bar_chart(filtered["Valorizador"].value_counts())
    else:
        st.warning("Sin datos para valorizadores")

# EVOLUCIÓN
st.markdown("### ⏳ Evolución")

if not mensual.empty:
    mensual["Mes"] = mensual["Mes"].astype(str)
    st.line_chart(mensual.set_index("Mes"))
else:
    st.warning("No hay datos suficientes para mostrar evolución")

# RANKING
st.markdown("### 🏆 Ranking")

if not filtered.empty:
    ranking = filtered["Valorizador"].value_counts().reset_index()
    ranking.columns = ["Valorizador", "Cantidad"]

    st.dataframe(ranking, use_container_width=True)
else:
    st.warning("No hay datos para ranking")

# EXPORTAR
st.markdown("### 📤 Exportación")

if not filtered.empty:
    csv = filtered.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Descargar reporte",
        csv,
        "reporte.csv",
        "text/csv"
    )

# TABLA FINAL (FORMATO CHILENO SOLO VISUAL 🔥)
st.markdown("### 📄 Detalle")

if not filtered.empty:
    tabla_mostrar = filtered.copy()
    tabla_mostrar["Fecha emisión"] = tabla_mostrar["Fecha emisión"].dt.strftime("%d-%m-%Y")

    st.dataframe(tabla_mostrar, use_container_width=True)
else:
    st.warning("No hay datos para mostrar")
