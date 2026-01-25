#Api proyecto programación

import re
import My_module # Funciones de mi modulo

while True:
    condicion = input("¿Desea buscar nuevos resultados o usar los guardados? Usar guardados=1, Buscar nuevos=2. ")

    if re.match(r"^[12]$", str(condicion)):
        if condicion == "1":

            ruta = "Jikan_info_anime.json"
            hay_archivo = My_module.verificar_archivos(ruta)

            if hay_archivo == True:

                df_final = My_module.info_pd() # Se llama a la funcion para mostrar la tabla pandas y estadisticas

                My_module.df_to_excel(df_final) # Documento de excel generado con los datos numericos de las busquedas

            elif hay_archivo == False:
                print("No existen el archivo, intente nuevamente")

        elif condicion == "2":
                
                limit = My_module.pedir_limite() # El usuario indica a cuantos animes se les sacará información

                animes = My_module.animes_redu(limit) # Usando el limite dicho, lo busca

                anime_guardado = My_module.guardar_info_animes(animes) # Lo guarda en un archivo JSON

                df_final = My_module.info_pd() # Se llama a la funcion para mostrar la tabla pandas y estadisticas

                My_module.df_to_excel(df_final) # Documento de excel generado con los datos numericos de las busquedas 
        break
    else:
        print("Opción no válida. Por favor elige 1 o 2.")
