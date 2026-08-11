import pandas as pd
import streamlit as st
import os

st.title("Calculadora de Materiales")
st.write("Selecciona una estructura y su cantidad para añadirla a la lista de cálculo.")

@st.cache_data
def cargar_datos():
    try:
        ruta_absoluta = os.path.join(os.path.dirname(__file__), "base_datos.xlsx")
        df = pd.read_excel(ruta_absoluta, sheet_name="UUTT2")
        df.columns = df.columns.str.strip()
        # Limpiar lista de estructuras únicas para el selectbox
        df['UU_TT'] = df['UU_TT'].astype(str).str.strip()
        return df
    except Exception as e:
        st.error(f"Error al cargar el archivo de Excel: {e}")
        return None

df = cargar_datos()

if df is not None:
    # Inicializar estado para guardar las selecciones
    if 'lista_estructuras' not in st.session_state:
        st.session_state.lista_estructuras = []

    # Selector de estructura y cantidad
    lista_opciones = sorted(df['UU_TT'].unique())
    col1, col2 = st.columns([3, 1])
    
    with col1:
        seleccion_est = st.selectbox("Selecciona la Estructura:", lista_opciones)
    with col2:
        cantidad_est = st.number_input("Cantidad:", min_value=1, value=1)

    if st.button("Agregar a la lista"):
        st.session_state.lista_estructuras.append({"Estructura": seleccion_est, "Cantidad": cantidad_est})

    # Mostrar lista actual
    if st.session_state.lista_estructuras:
        st.write("### Estructuras seleccionadas:")
        for i, item in enumerate(st.session_state.lista_estructuras):
            st.write(f"{i+1}. {item['Estructura']} - Cantidad: {item['Cantidad']}")
        
        if st.button("Limpiar lista"):
            st.session_state.lista_estructuras = []
            st.rerun()

        if st.button("Calcular Consolidado Final"):
            lista_acumulada = []
            for item in st.session_state.lista_estructuras:
                coincidencias = df[df['UU_TT'].str.lower() == item["Estructura"].lower()]
                for _, row in coincidencias.iterrows():
                    try:
                        cant_base = float(row.get("Cantidad Materiales", 1))
                    except:
                        cant_base = 1.0
                    
                    lista_acumulada.append({
                        "Código SAP": row.get("Codigo SAP", ""),
                        "Descripción Material": row.get("Descripción_MAT", ""),
                        "Unidad": row.get("Unidad", ""),
                        "Cantidad Total": cant_base * item["Cantidad"]
                    })

            if lista_acumulada:
                df_resul = pd.DataFrame(lista_acumulada)
                df_final = df_resul.groupby(["Código SAP", "Descripción Material", "Unidad"], as_index=False)["Cantidad Total"].sum()
                st.success("¡Cálculo realizado con éxito!")
                st.subheader("Consolidado Total de Materiales:")
                st.dataframe(df_final, use_container_width=True)
else:
    st.warning("No se pudo encontrar la base de datos de Excel.")
