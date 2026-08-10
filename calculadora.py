import pandas as pd

import streamlit as st
import os
import subprocess
import sys

try:
    import openpyxl
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "openpyxl"])
    import openpyxl 

st.title("Calculadora de Materiales")

st.write("Ingresa las estructuras y sus cantidades para calcular el consolidado de materiales.")

 

@st.cache_data

def cargar_datos():

    try:

        ruta_absoluta = os.path.join(os.path.dirname(__file__), "base_datos.xlsx")
        df = pd.read_excel(ruta_absoluta, sheet_name="UUTT2")

        df.columns = df.columns.str.strip()

        for col in df.columns:

            df[col] = df[col].astype(str)

        return df

    except Exception as e:

        st.error(f"Error al cargar el archivo de Excel: {e}")

        return None

 

df = cargar_datos()

 

if df is not None:

    entrada_usuario = st.text_area(

        "Ingresa las estructuras y cantidades (Formato: ESTRUCTURA CANTIDAD)",

        placeholder="Ejemplo:\n1CDA-MT 2\nCDA-MT1 3"

    )

 

    if st.button("Calcular Materiales"):

        if entrada_usuario.strip() == "":

            st.warning("Por favor, ingresa al menos una estructura.")

        else:

            lineas = entrada_usuario.strip().split("\n")

            solicitudes = []

 

            for linea in lineas:

                partes = linea.strip().split()

                if len(partes) >= 2:

                    est = partes[0].strip()

                    try:

                        cant = float(partes[1])

                        solicitudes.append({"Estructura": est, "Cantidad": cant})

                    except ValueError:

                        st.error(f"La cantidad para '{partes[0]}' debe ser un número.")

 

            if solicitudes:

                st.success("¡Cálculo realizado con éxito!")

               

                lista_acumulada = []

 

                for item in solicitudes:

                    est_buscada = item["Estructura"]

                    multiplicador = item["Cantidad"]

                   

                    coincidencias = df[df['UU_TT'].str.strip().str.lower() == est_buscada.lower()]

                   

                    if not coincidencias.empty:

                        for _, row in coincidencias.iterrows():

                            try:

                                cant_base = float(row.get("Cantidad Materiales", 1))

                            except ValueError:

                                cant_base = 1.0

                               

                            cantidad_total_material = cant_base * multiplicador

                           

                            lista_acumulada.append({

                                "Código SAP": row.get("Codigo SAP", ""),

                                "Descripción Material": row.get("Descripción_MAT", ""),

                                "Unidad": row.get("Unidad", ""),

                                "Cantidad Total": cantidad_total_material

                            })

                    else:

                        st.warning(f"No se encontró la estructura '{est_buscada}' en la base de datos.")

 

                if lista_acumulada:

                    df_resul = pd.DataFrame(lista_acumulada)

                   

                    # Agrupamos y sumamos los materiales repetidos

                    df_final = df_resul.groupby(

                        ["Código SAP", "Descripción Material", "Unidad"],

                        as_index=False

                    )["Cantidad Total"].sum()

 

                    st.subheader("Consolidado Total de Materiales:")

                    st.dataframe(df_final, use_container_width=True)

else:

    st.warning("No se pudo encontrar la base de datos de Excel en la carpeta.")
