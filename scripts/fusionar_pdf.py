import os
from PyPDF2 import PdfMerger
from pathlib import Path

def fusionar_pdf(carpeta_entrada, archivo_salida='pdfs_fusionados.pdf'):
    '''
    Fusiona todos los archivos PDF en una carpeta especifica.

    Args:
        carpeta_entrada (str): Ruta de la carpeta que contiene los PDFs
        archivo_salida(str): Nombre del archivo PDf resultante
    '''

    try:
        #Crear el merger
        merger = PdfMerger()

        # Verificar si la carpeta existe
        if not os.path.exists(carpeta_entrada):
            print(f'Error: La carpeta "{carpeta_entrada}" no existe.')
            return
        #Obtener todos los archvios PDF de la carpeta
        pdfs = [f for f in Path(carpeta_entrada).glob('*.pdf')]
        if not pdfs:
            print(f'No se encontraron archivos PDF en {carpeta_entrada}')
            return
        print(f'Encontrados {len(pdfs)} archivos PDF en {carpeta_entrada}')

        #Agregar cada PDF al merger
        for pdf in pdfs:
            print(f'Agregando: {pdf.name}')
            merger.append(str(pdf))

        #Guardar el PDF fusionado
        merger.write(archivo_salida)
        merger.close()
        print(f'\nFusionado exitosamente en {archivo_salida}')

    except Exception as e:
        print(f'Error al fusionar los archivos: {str(e)}')

if __name__ == '__main__':
    ruta= "C:\\Users\\antho\\Documents\\Escritorio\\pdf"
    fusionar_pdf(ruta)