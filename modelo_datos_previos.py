#%%
import numpy as np
import pandas as pd

#%%
df_pre = pd.read_csv("datos2.csv", low_memory=False)
df_pre2 = pd.read_csv("clasificacion.csv")

#%%
df_pre2.rename(columns = {"Cliente" : "idCredito"}, inplace= True)
df_pre2.head()

#%%
df = df_pre.merge(df_pre2, on = "idCredito", how = "left")
df_prueba = pd.read_csv("pruebaFinal.csv", low_memory=False)

#%%
def recolectar_precios(df_prueba):
    condicion = (
        (df_prueba["idBanco"] == 12) &
        (df_prueba["montoCobrado"] != df_prueba["montoExigible"]) &
        (df_prueba["montoCobrado"] != 0)
    )
    df_prueba.loc[condicion, "Costo"] = 1.755

    condicion2 = (
        (df_prueba["idBanco"] == 12) &
        (df_prueba["montoCobrado"] == 0)
    )
    df_prueba.loc[condicion2, "Costo"] = 0

    total_costo = df_prueba["Costo"].sum()
    return total_costo

#%%
costo_modelo_antiguo = recolectar_precios(df_prueba)
print(f"Costo del modelo antiguo: {costo_modelo_antiguo}")

#%%
condicion_parcial = (
        (df_prueba["idBanco"] == 12) &
        (df_prueba["montoCobrado"] != df_prueba["montoExigible"]) &
        (df_prueba["montoCobrado"] != 0)
    )

total_parcial = df_prueba[condicion_parcial].shape[0]
total_bbva = df_prueba[df_prueba["idBanco"] == 12].shape[0]
porcentaje = (total_parcial / total_bbva) * 100 
print(f"Porcentaje de clientes parciales en bbva: {porcentaje:.2f}%")

#%%
condicion_nocobro = (
        (df_prueba["idBanco"] == 12) &
        (df_prueba["montoCobrado"] == 0)
    )

total_nocobro = df_prueba[condicion_nocobro].shape[0]
total_bbva = df_prueba[df_prueba["idBanco"] == 12].shape[0]
porcentaje = (total_nocobro / total_bbva) * 100 
print(f"Porcentaje de clientes que no pagaron en bbva: {porcentaje:.2f}%")
#%%

id_revision = ["01", "02", "03", "10", "11", "12", "23", "51", "52", "53", "88", "DD00021"]




def evaluar_cliente(dfCliente, prioridades):

    if dfCliente["idRespuestaBanco"] in id_revision:
        dfCliente["ProximaEmisora"] = "REVISION"
        return dfCliente
    
    score = dfCliente["Promedio de pago"]
    mensual = dfCliente["montoExigible"]
    interbancario = False
    if dfCliente["idBanco"] not in [12, 14, 2, 72]:
        interbancario = True
    if mensual <= 243:
        tipo_monto = "bajo"
    elif mensual > 243 and mensual <= 437:
        tipo_monto = "medio"
    else:
        tipo_monto = "alto"


    if score <= 1 and score > .97:
        ponderacion = ["BANAMEX TRADICIONAL"]
        dfCliente["ProximaEmisora"] = obtener_prioritaria(prioridades, ponderacion, interbancario)

    elif score <= .97 and score > .75:
        ponderacion = ["BANAMEX TRADICIONAL", "BBVA LINEA", "BANORTE LINEA"]
        dfCliente["ProximaEmisora"] = obtener_prioritaria(prioridades, ponderacion, interbancario)

    elif score <= .75 and score > .5:
        ponderacion = ["SANTANDER TRADICIONAL", "BBVA TRADICIONAL", "BBVA MATUTINO"]
        dfCliente["ProximaEmisora"] = obtener_prioritaria(prioridades, ponderacion, interbancario)
        
    elif score <= .5 and score > .25:
        ponderacion = ["BBVA TRADICIONAL", "BBVA MATUTINO", "SANTANDER TRADICIONAL"]
        dfCliente["ProximaEmisora"] = obtener_prioritaria(prioridades, ponderacion, interbancario)
    elif score <= .25 and score > .03:
        ponderacion = ["BBVA TRADICIONAL", "BBVA MATUTINO"]
        dfCliente["ProximaEmisora"] = obtener_prioritaria(prioridades, ponderacion, interbancario)
        
    else:
        ponderacion = ["BBVA TRADICIONAL", "BBVA MATUTINO", "BBVA EN LINEA"]
        
        dfCliente["ProximaEmisora"] = obtener_prioritaria(prioridades, ponderacion, interbancario)
    return dfCliente

def obtener_prioritaria(prioridades, ponderacion, interbancario): 
    diccionario = {
    'BANAMEX TRADICIONAL': {
        'id': 1,
        'costo': 98,
        'efectividad_tiempo_busqueda': 50,
        'efectividad_tiempo_respuesta': 100,
        'horarios': 70
    },
    'BANAMEX INTERBANCARIO': {
        'id': 2,
        'costo': 98 ,
        'efectividad_tiempo_busqueda': 60,
        'efectividad_tiempo_respuesta': 50,
        'horarios': 50
    },
    'BBVA TRADICIONAL': {
        'id': 3,
        'costo': 50,
        'efectividad_tiempo_busqueda': 90,
        'efectividad_tiempo_respuesta': 50,
        'horarios': 100
    },
    'BBVA PARCIAL': {
        'id': 4,
        'costo': 97,
        'efectividad_tiempo_busqueda': 90,
        'efectividad_tiempo_respuesta': 50,
        'horarios': 75
    },
    'BBVA MATUTINO': {
        'id': 5,
        'costo': 50,
        'efectividad_tiempo_busqueda': 90,
        'efectividad_tiempo_respuesta': 50,
        'horarios': 90
    },
    'BBVA EN LINEA': {
        'id': 6,
        'costo': 70,
        'efectividad_tiempo_busqueda': 50,
        'efectividad_tiempo_respuesta': 100,
        'horarios': 80
    },
     'BBVA INTERBANCARIO': {
        'id': 7,
        'costo': 60,
        'efectividad_tiempo_busqueda': 60,
        'efectividad_tiempo_respuesta': 50,
        'horarios': 50
    },
    'SANTANDER TRADICIONAL ACEPTADO': {
        'id': 8,
        'costo': 85,
        'efectividad_tiempo_busqueda': 95,
        'efectividad_tiempo_respuesta': 50,
        'horarios': 75
    },
    'SANTANDER TRADICIONAL RECHAZADO': {
        'id': 9,
        'costo': 88,
        'efectividad_tiempo_busqueda': 95,
        'efectividad_tiempo_respuesta': 50,
        'horarios': 75
    },
    'SANTANDER REINTENTO ACEPTADO': {
        'id': 10,
        'costo': 95,
        'efectividad_tiempo_busqueda': 95,
        'efectividad_tiempo_respuesta': 50,
        'horarios': 75
    },
    'SANTANDER REINTENTO RECHAZADO': {
        'id': 11,
        'costo': 100,
        'efectividad_tiempo_busqueda': 95,
        'efectividad_tiempo_respuesta': 50,
        'horarios': 75
    },
    'SANTANDER INTERBANCARIO ACEPTADO': {
        'id': 12,
        'costo': 80,
        'efectividad_tiempo_busqueda': 60,
        'efectividad_tiempo_respuesta': 50,
        'horarios': 50
    },
      'SANTANDER INTERBANCARIO RECHAZADO': {
        'id': 13,
        'costo': 87,
        'efectividad_tiempo_busqueda': 60,
        'efectividad_tiempo_respuesta': 50,
        'horarios': 50
    },
      'BANORTE TRADICIONAL': {
        'id': 14,
        'costo': 87,
        'efectividad_tiempo_busqueda': 100,
        'efectividad_tiempo_respuesta': 50,
        'horarios': 80
    },
       'BANORTE INTERBANCARIO': {
        'id': 15,
        'costo': 87,
        'efectividad_tiempo_busqueda': 60,
        'efectividad_tiempo_respuesta': 50,
        'horarios': 50
    },
        'BANORTE EN LINEA': {
        'id': 15,
        'costo': 65,
        'efectividad_tiempo_busqueda': 50,
        'efectividad_tiempo_respuesta': 100,
        'horarios': 100
    },
    
}
    df = pd.DataFrame.from_dict(diccionario, orient = "index")
    df["priorizado"] = sum(df[col] * peso for col, peso in prioridades)
    if interbancario:
        for id_ in ["BBVA INTERBANCARIO", "BANORTE INTERBANCARIO", "SANTANDER INTERBANCARIO ACEPTADO", "SANTANDER INTERBANCARIO RECHAZADO", "BANAMEX INTERBANCARIO"]:
            if id_ in df.index:
                df.loc[id_, "priorizado"] += 500
    else:
        for i in ponderacion:
            if i in df.index:
                df.loc[i, "priorizado"] += 50
    
    return df["priorizado"].idxmax()
        

                





    





#%%
prueba = df[:1000]  # toma las primeras 10 filas
prioridades = [("costo", .8), ("horarios", .2)]
resultados = []

for _, fila in prueba.iterrows():
    resultado = evaluar_cliente(fila, prioridades)
    resultados.append(resultado)

# Convertir lista de dicts/Series a DataFrame
df_resultados = pd.DataFrame(resultados)
df_resultados

#%%
prueba2 = df  # toma las primeras 10 filas
prioridades2 = [("horarios", .8), ("efectividad_tiempo_busqueda", .1), ("efectividad_tiempo_respuesta", .1)]
resultados2 = []

for _, fila in prueba2.iterrows():
    resultado2 = evaluar_cliente(fila, prioridades2)
    resultados2.append(resultado2)

# Convertir lista de dicts/Series a DataFrame
df_resultados2 = pd.DataFrame(resultados2)
df_resultados2["ProximaEmisora"].unique()






