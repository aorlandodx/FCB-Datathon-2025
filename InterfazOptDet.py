import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Escenarios de implementación del modelo de Optimización")

df1 = pd.read_csv("Minimizar.csv")
df2 = pd.read_csv("Maximizar.csv")

if 'mostrar_df1' not in st.session_state:
    st.session_state.mostrar_df1 = False

# Botón para primer dataset
if st.button("Mostrar/Ocultar Escenario 1"):
    st.session_state.mostrar_df1 = not st.session_state.mostrar_df1

if st.session_state.mostrar_df1:
    st.subheader("Minimización de costo de comisiones")
    st.dataframe(df1)
    

if 'mostrar_df2' not in st.session_state:
    st.session_state.mostrar_df2 = False

# Botón para segundo dataset
if st.button("Mostrar/Ocultar Escenario 2"):
    st.session_state.mostrar_df2 = not st.session_state.mostrar_df2

if st.session_state.mostrar_df2:
    st.subheader("Maximización de la cobranza")
    st.dataframe(df2)



st.title("Bancos por Emisora")
try:
    df = pd.read_csv("CatEmisora.csv")

    st.write("Vista previa del CSV:")
    st.dataframe(df.head())
    posibles_columnas = [col for col in df.columns if 'emiso' in col.lower()]

    if posibles_columnas:
        emisora_col = st.selectbox("Selecciona la columna de emisora:", posibles_columnas)

        if emisora_col:
            tipos_emisora = df[emisora_col].dropna().unique()
            tipos_emisora.sort()

            st.success(f"Se encontraron {len(tipos_emisora)} tipos de emisoras.")
            for tipo in tipos_emisora:
                st.subheader(f"Emisora: {tipo}")
                df_filtrado = df[df[emisora_col] == tipo]
                st.dataframe(df_filtrado)
    else:
        st.error("No se encontró ninguna columna que parezca ser 'emisora'. Asegúrate de que exista en el CSV.")

except FileNotFoundError:
    st.error("El archivo no se encuentra en el directorio.")


st.title("Listas de Cobro por Banco")
@st.cache_data
def cargar_datos():
    df_cobros = pd.read_csv("ListaCobro.csv")
    df_bancos = pd.read_csv("CatBanco.csv")
    df_cobros['fechaCreacionLista'] = pd.to_datetime(df_cobros['fechaCreacionLista'], format="%d/%m/%Y %I:%M%p")
    df_cobros['fechaEnvioCobro'] = pd.to_datetime(df_cobros['fechaEnvioCobro'], format="%d/%m/%Y")
    df_cobros['idBanco'] = df_cobros['idBanco'].astype(str)
    df_bancos['IdBanco'] = df_bancos['IdBanco'].astype(str)
    df = df_cobros.merge(df_bancos, left_on="idBanco", right_on="IdBanco", how="left")
    df['dias_procesamiento'] = (df['fechaEnvioCobro'] - df['fechaCreacionLista']).dt.days
    return df

df = cargar_datos()
bancos_disponibles = sorted(df['Nombre'].dropna().unique())
bancos_seleccionados = st.multiselect("Selecciona banco(s):", bancos_disponibles, default=bancos_disponibles)

df_filtrado = df[df['Nombre'].isin(bancos_seleccionados)]

st.subheader("Datos filtrados")
st.dataframe(df_filtrado[['idListaCobro', 'fechaCreacionLista', 'fechaEnvioCobro', 'Nombre',]])

st.subheader("Listas de cobro por día")
listas_por_dia = df_filtrado.groupby(df_filtrado['fechaCreacionLista'].dt.date).size().reset_index(name='conteo')
fig1 = px.bar(listas_por_dia, x='fechaCreacionLista', y='conteo', labels={'fechaCreacionLista': 'Fecha', 'conteo': 'Listas'}, title="Número de listas creadas por día")
st.plotly_chart(fig1, use_container_width=True)


st.subheader("Listas por fecha y banco")

heatmap_data = df_filtrado.copy()
heatmap_data['fecha'] = heatmap_data['fechaCreacionLista'].dt.date
pivot_table = heatmap_data.pivot_table(
    index='Nombre',        
    columns='fecha',       
    values='idListaCobro', 
    aggfunc='count',
    fill_value=0
)


fig3 = px.imshow(
    pivot_table,
    labels=dict(x="Fecha", y="Banco", color="Cantidad"),
    aspect="auto",
    title="Cantidad de listas de cobro por banco y fecha"
)


st.plotly_chart(fig3, use_container_width=True)


st.subheader("Tendencia mensual de listas de cobro")
df['mes'] = df['fechaCreacionLista'].dt.to_period('M').astype(str)
listas_por_mes = df.groupby('mes').size().reset_index(name='conteo')
fig_mes = px.line(listas_por_mes, x='mes', y='conteo', title="Listas de cobro creadas por mes",
                  labels={'mes': 'Mes', 'conteo': 'Cantidad'})
st.plotly_chart(fig_mes, use_container_width=True)

