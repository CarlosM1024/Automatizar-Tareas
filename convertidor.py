import os
from PIL import Image

def convertir_imagen(ruta_entrada, formato_salida):
    '''
    Convierte una imagen al formato especificado

    Arg:
        ruta_entrada(str): Ruta de la imagen original
    formato_salida(str): Formato de salida(ejemplo: .PNG, .JPG, .JPEG)
    '''
    try:
        #Obtener el nombre del archivo sin extension
        nombre_base=os.path.splitext(ruta_entrada)[0]
        #Abrir imagen
        with Image.open(ruta_entrada) as img:
            #Si la imagen esta en modo RGBA y v¿cnvertimos a JPEG, convertir a RGB
            if img.mode in ('RGBA', 'LA') and formato_salida.upper() == 'JPEG':
                img = img.convert('RGB')

            #Crear el nombre del archivo de salida
            ruta_salida=f'{nombre_base}.{formato_salida.lower()}'

            #Guardar imagen en nuevo formato
            img.save(ruta_salida, formato_salida.upper())
            print(f'Imagen convertida exitosamente: {ruta_salida}')

    except Exception as e:
        print(f'Error al convertir la imagen: {str(e)}')