import os

def cambiar_nombre(directorio, opcion, valor):
    '''

    Cambia el nombre d elos archivos en el directorio espeficado.

    :param directorio: Ruta del directorio donde se encuentran los archivos
    :param opcion: Opcion de renombrado ('cambiar' para cambiar una palabra, 'prefijo' para agregar un prefijo)
    :param valor: La palabra a cambiar o el prefijo a agregar
    '''

    for nombre_archivo in os.listdir(directorio):
        ruta_archivo = os.path.join(directorio, nombre_archivo)
        if os.path.isfile(ruta_archivo):
            nuevo_nombre = ''
            if opcion == 'Cambiar':
                nuevo_nombre = nombre_archivo.replace(valor[0], valor[1])
            elif opcion == 'Prefijo':
                nuevo_nombre = f'{valor[0]}_{nombre_archivo}' if isinstance(valor, list) else f'{valor}_{nombre_archivo}'
            else:
                print("Opcion no valida. Usa 'cambiar' o 'prefijo'.")
                return

            nueva_ruta = os.path.join(directorio, nuevo_nombre)
            os.rename(ruta_archivo, nueva_ruta)
            print(f'Renombrado: {nombre_archivo} a {nuevo_nombre}')

ruta= "C:\\Users\\antho\\Documents\\Escritorio\\pdf"
#cambiar_nombre(ruta,'cambiar', ['2024__', ''])