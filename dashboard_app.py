import streamlit as st
import pandas as pd

# CONFIG
st.set_page_config(page_title="Informe Ejecutivo", layout="wide")

st.markdown("## 📊 Informe Ejecutivo de Valorización")
st.markdown("Análisis consolidado para toma de decisiones")

# SIDEBAR
st.sidebar.header("⚙️ Configuración")

modo = st.sidebar.radio("Modo de uso", ["Datos compartidos", "Subir archivo"])

# CARGA DATOS
if modo == "Datos compartidos":
    df = pd.read_excel("resultado.xlsx")
else:
    archivo = st.sidebar.file_uploader("Sube Excel", type=["xlsx"])
    if archivo:
        df = pd.read_excel(archivo)
    else:
        st.stop()

# ===== LIMPIEZA DE FECHAS (CLAVE) =====
df["Fecha emisión"] = pd.to_datetime(
    df["Fecha emisión"],
    dayfirst=True,
    errors="coerce"
)

# eliminar fechas inválidas
df = df.dropna(subset=["Fecha emisión"])

# ===== FILTRO POR FECHA =====
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

# ===== FILTROS =====
st.sidebar.subheader("🔎 Segmentación")

comuna = st.sidebar.selectbox("Comuna", ["Todas"] + list(df["Sucursal"].dropna().unique()))
valorizador = st.sidebar.selectbox("Valorizador", ["Todos"] + list(df["Valorizador"].dropna().unique()))

if comuna != "Todas":
    filtered = filtered[filtered["Sucursal"] == comuna]

if valorizador != "Todos":
    filtered = filtered[filtered["Valorizador"] == valorizador]

# ===== KPIs =====
st.markdown("### 📌 Resumen Ejecutivo")

col1, col2, col3, col4 = st.columns(4)

total = len(filtered)
valorizadores = filtered["Valorizador"].nunique()
comunas = filtered["Sucursal"].nunique()

# ===== EVOLUCIÓN (SOLUCIÓN ROBUSTA 🔥) =====
if not filtered.empty:

    df_time = filtered.copy()

# asegurarse que es datetime real
df_time["Fecha emisión"] = pd.to_datetime(df_time["Fecha emisión"], errors="coerce")

# eliminar nulos
df_time = df_time.dropna(subset=["Fecha emisión"])

# setear índice correctamente
df_time = df_time.set_index("Fecha emisión")

# 🔥 usar 'MS' en vez de 'M' (más estable en cloud)
mensual = df_time.resample("MS").size().reset_index()

mensual.columns = ["Fecha", "Cantidad"]

    # crecimiento
    if len(mensual) >= 2:
        actual = mensual["Cantidad"].iloc[-1]
        anterior = mensual["Cantidad"].iloc[-2]

        if anterior != 0:
            crecimiento = ((actual - anterior) / anterior) * 100
        else:
            crecimiento = 0
    else:
        crecimiento = 0

else:
    mensual = pd.DataFrame()
    crecimiento = 0

col1.metric("Operaciones", total)
col2.metric("Valorizadores", valorizadores)
col3.metric("Cobertura", comunas)
col4.metric("Crecimiento", f"{crecimiento:.1f}%")

# ===== INSIGHTS =====
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
    st.warning("No hay datos disponibles")

# ===== GRÁFICOS =====
st.markdown("### 📈 Análisis")

col1, col2 = st.columns(2)

with col1:
    if not filtered.empty:
        st.bar_chart(filtered["Sucursal"].value_counts())
    else:
        st.warning("Sin datos")

with col2:
    if not filtered.empty:
        st.bar_chart(filtered["Valorizador"].value_counts())
    else:
        st.warning("Sin datos")

# ===== EVOLUCIÓN =====
st.markdown("### ⏳ Evolución")

if not mensual.empty:
    mensual["Fecha"] = mensual["Fecha"].dt.strftime("%m-%Y")
    st.line_chart(mensual.set_index("Fecha"))
else:
    st.warning("No hay datos suficientes para mostrar evolución")

# ===== RANKING =====
st.markdown("### 🏆 Ranking")

if not filtered.empty:
    ranking = filtered["Valorizador"].value_counts().reset_index()
    ranking.columns = ["Valorizador", "Cantidad"]
    st.dataframe(ranking, use_container_width=True)

# ===== EXPORTAR =====
st.markdown("### 📤 Exportación")

if not filtered.empty:
    csv = filtered.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Descargar reporte",
        csv,
        "reporte.csv",
        "text/csv"
    )

# ===== TABLA FINAL =====
st.markdown("### 📄 Detalle")

if not filtered.empty:
    tabla_mostrar = filtered.copy()
    tabla_mostrar["Fecha emisión"] = tabla_mostrar["Fecha emisión"].dt.strftime("%d-%m-%Y")

    st.dataframe(tabla_mostrar, use_container_width=True)
