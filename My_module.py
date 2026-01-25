import json
import requests
import os
import re
import pandas as pd # Como usarlo: https://pandas.pydata.org/docs/getting_started/index.html
import statistics as stats # Para sacar estadisticas: https://docs.python.org/3/library/statistics.html
import openpyxl
import matplotlib.pyplot as plt
from collections import Counter


def verificar_archivos(ruta):
    if validar_ruta(ruta):
        print("El archivo se encuentra en: " + ruta)
        return True
    else:
        print("El archivo no se encontró o la ruta es inválida: " + ruta)
        return False
        
def validar_ruta(ruta):
    #La siguiente linea valida si la ruta existe y re.match devuelve un objeto de coincidencia 
    #Si ambas de estas son ciertas, devuelve True y la ruta
    #La expresion regular valida si en ese conjunto hay alguna letra, espacio, punto, guion y guion bajo
    # ^ y $, empieza con: y termina con: respectivamente
    return os.path.exists(ruta) and re.match(r'^[\w\s._-]+$', ruta)
    

def pedir_limite(): 
    while True:
        limite = input("Cuantas paginas de informacion quieres que se muestren? Pagina=25. Limite=3. ")
        if re.match(r"^\d+$", limite):
            return int(limite)
        else:
            print("Ingrese un valor valido")


def animes_redu(limite):
    limite_peticion = "https://api.jikan.moe/v4/anime?limit=25&page="
    animes_redu = list()
    try:
        for i in range(1, limite + 1):
            limite_peticion = f"{limite_peticion}{i}"
            respuesta = requests.get(limite_peticion)
            mi_dict = respuesta.json()

        #Se guarda solo la informacion importante
            for item in mi_dict["data"]:
                mi_dict_redu = {
                "Title":item["title"],
                "Type":item["type"],
                "Episodes":item["episodes"],
                "Status":item["status"],
                "Score":item["score"],
                "Rank":item["rank"],
                "Popularity":item["popularity"],
                "Favorites":item["favorites"],
                "Synopsis": limpiar_sinopsis(item["synopsis"]), # Uso de la funcion limpiar sinopsis
                "Genres": [genre["name"] for genre in item["genres"]] if item["genres"] else [None], # Este ultimo condicional agrega None en caso de que este vacia
                "Producers":[producer["name"] for producer in item["producers"]] if item["producers"] else [None], # Nuevamente None si está vacia
                "Studios":[studio["name"] for studio in item["studios"]],
                "Licenses":[license["name"] for license in item["licensors"]]
            }
                animes_redu.append(mi_dict_redu)
    
    except KeyError as e:
        print("Error al ingresar los datos.")

    
    except KeyError as e:
        print("Error al ingresar los datos.")

    return animes_redu


def limpiar_sinopsis(sinopsis):
    # La siguiente linea de codigo va a eliminar saltos de linea y otros caracteres encontrados en los json dentro de los diccionarios
    sinopsis = re.sub(r"\n+", " ", sinopsis) # re.sub busca y reemplaza partes del texto a lo que tu escojas
    sinopsis = re.sub(r"\u2014+", "-", sinopsis) # Se cambia un guion largo, por uno corto, se insertaba \u2014 
    return sinopsis

def guardar_info_animes(animes):
    try:
        #utf-8 permite una gran variedad de caracteres, por si entran ganas de meter el nombre del anime en japones
        with open(ruta_info_anime, "w", encoding="utf-8") as file: 
            json.dump(animes, file, indent=4)

    except FileNotFoundError:
        print("La ruta no existe")

    except OSError as e:
        print("Error del sistema: " + str(e))

    except Exception as e:
        print("Se produjo un error inesperado: " + str(e))
            
def info_pd(): # Funcion para sacar estadisticas del Jikan_info_anime.json, pd = pandas
    df = pd.read_json(ruta_info_anime, encoding="utf-8")
    title_type_score = df[["Title", "Type", "Episodes", "Score", "Rank", "Popularity", "Favorites", "Genres"]]
    title_type_score.index = range(1, len(title_type_score) + 1) # Tabla principal que se muestra en el excel
    
    # Calcular las estadísticas
    mean_values = title_type_score[["Episodes", "Score", "Rank", "Popularity", "Favorites"]].mean().round(2) # media aritmetica
    
    variance_values = title_type_score[["Episodes", "Score", "Rank", "Popularity", "Favorites"]].var().round(2) # Varianza

    max_favorites = title_type_score["Favorites"].max() # Valor maximo de favoritos

    mode_episodes = title_type_score["Episodes"].mode().iloc[0] if not title_type_score['Episodes'].mode().empty else None # Moda de episodios

# Crear un DataFrame ordenar las estadísticas debajo de la tabla principal
    stats_df = pd.DataFrame({
        "Episodes": [mean_values["Episodes"], variance_values["Episodes"], mode_episodes],
        "Score": [mean_values["Score"], variance_values["Score"], None],
        "Rank": [mean_values["Rank"], variance_values["Rank"], None],
        "Popularity": [mean_values["Popularity"], variance_values["Popularity"], None],
        "Favorites": [mean_values["Favorites"], variance_values["Favorites"], max_favorites]
    }, index=["Media", "Varianza", "Moda/Max"])


# Se concatena el primer DataFrame con el nuevo DataFrame de estadísticas
    df_final = pd.concat([title_type_score, stats_df])

    all_genres = [genre for sublist in df["Genres"] for genre in sublist] # Junta a los generos en una segunda lista
    genre_counts = Counter(all_genres) # Cuenta ahora los generos en esa segunda lista

    labels = [f"{genre} ({count})" for genre, count in genre_counts.items()] # Se muestra en la grafica el genero y cuantas ocurrencias tuvo en la grafica
    plt.figure(figsize=(10, 8))
    plt.pie(genre_counts.values(), labels=labels, autopct='%1.1f%%')
    plt.title("Distribución de géneros")
    plt.show()



    top_8 = title_type_score.head(8) # La grafica se limita a los primeros 8 animes encontrados

    # Crear la gráfica de barras usando los datos limitados
    plt.figure(figsize=(18, 6))
    plt.bar(top_8["Title"], top_8["Episodes"], color="skyblue", width=0.3)

    # Títulos y etiquetas
    plt.title('Episodios por Anime (Top 8)', fontsize=16)
    plt.xlabel('Title', fontsize=10)
    plt.ylabel('Episodios', fontsize=10)
    plt.xticks(rotation=45)  # Rotar los títulos para mejor legibilidad
    plt.show()



    top_5_ranked = title_type_score.sort_values(by="Rank").head(5) # Grafica para mostrar los top 5 por rango

    fig, ax = plt.subplots(figsize=(14, 5))
    ax.bar(top_5_ranked["Title"], top_5_ranked["Rank"])

    colors1= ["magenta", "tan", "skyblue", "lightcoral", "lightgreen"]

    # Etiquetas de las barras
    ax.bar_label(ax.bar(top_5_ranked["Title"], top_5_ranked["Rank"], color=colors1))

    # Títulos y etiquetas
    plt.title("Top 5 Animes mejor valorados (por Rank)", fontsize=14)
    plt.xlabel("Titulo", fontsize=12)
    plt.ylabel("Rank", fontsize=12)
    plt.xticks(rotation=45)  # Rotar los títulos para mejor legibilidad
    plt.show()


    top_5_popular = title_type_score.sort_values(by="Popularity").head(5) # Grafica de los top 5 de popularidad

    # Crear la gráfica de barras
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(top_5_popular['Title'], top_5_popular["Popularity"])

    colors2= ["lightcyan", "wheat", "lavender", "yellowgreen", "pink"]

    # Etiquetas de las barras
    ax.bar_label(ax.bar(top_5_popular["Title"], top_5_popular["Popularity"], color=colors2))

    # Títulos y etiquetas
    plt.title("Top 5 Animes más populares", fontsize=14)
    plt.xlabel("Titulo", fontsize=12)
    plt.ylabel("Popularity", fontsize=12)
    plt.xticks(rotation=45)  # Rotar los títulos para mejor legibilidad

    plt.show()


    return  df_final


def df_to_excel(df_final): # esta funcion utiliza la tabla con la informacion y estadisticas juntas y las manda a un excel
	df_final.to_excel("Jikan_anime.xlsx")

# Ruta de mis json
ruta_info_anime = "Jikan_info_anime.json"