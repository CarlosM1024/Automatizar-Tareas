import os
from heapq import merge

import flet as ft

from fusionar_pdf import fusionar_pdf
from borrar_dup import find_dup, delete_file
from organizar import organizar_folder
from redimensiona import batch_resize
from convertidor import convertir_imagen
from extraer_audio import extraer_audio
from cambiar_nombre import cambiar_nombre

def main(page: ft.Page):
    page.theme_mode=ft.ThemeMode.DARK
    page.bgcolor=ft.Colors.GREY_900
    page.title='Borrar duplicados'
    page.window.width=1000
    page.window.height=700
    page.padding=0

    #Tema personalizado------------------------------------------------------------------------------------------------------------------------------------------------------
    page.theme=ft.Theme(
        color_scheme_seed=ft.Colors.BLUE,
        visual_density=ft.VisualDensity.COMFORTABLE,
        color_scheme=ft.ColorScheme(
            primary=ft.Colors.BLUE,
            secondary=ft.Colors.ORANGE,
            background=ft.Colors.GREY_900,
            surface=ft.Colors.GREY_800,
        )
    )

    #Variables de estado--------------------------------------------------------------------------------------------------------------------------------------------
    state = {
        'current_duplicates': [],
        'current_view': 'duplicates',
        'resize_input_folder':'',
        'resize_output_folder':'',
        'selecting_resize_output': False,
        'convert_input_file':'',
        'audio_input_folder': '',
        'audio_extraction_progress': 0,
        'total_videos':0,
        'current_video':'',
        'pdf_input_folder':'',
        'rename_input_folder':'',
        'rename_option':'',
        'rename_value':'',
    }
    # Controles para eliminar archivos repetidos---------------------------------------------------------------------------------------------------------------
    selected_dir_text = ft.Text(
        'No se ha seleccionado ninguna carpeta',
        size=16,
        color=ft.Colors.BLUE_200,
    )
    result_text = ft.Text(size=16, weight=ft.FontWeight.BOLD)
    duplicates_list = ft.ListView(
        expand=1,
        spacing=10,
        height=200,
    )
    delete_all_btn = ft.ElevatedButton(
        'Eliminar todos los duplicados',
        color=ft.Colors.WHITE,
        bgcolor=ft.Colors.RED_900,
        icon=ft.Icons.DELETE_SWEEP,
        visible=False,
        on_click=lambda e: delete_all_duplicates(),
    )

    # Controles para la vista de organizar archivos----------------------------------------------------------------------------------------------------
    organize_dir_text = ft.Text(
        'No se ha seleccionado ninguna carpeta',
        size=16,
        color=ft.Colors.BLUE_200,
    )
    organize_result_text = ft.Text(
        size=16,
        weight=ft.FontWeight.BOLD
    )

    # Controles para la vista de redimensionar imagenes------------------------------------------------------------------------------------------------------
    resized_input_text = ft.Text(
        'Carpeta de entrada: No seleccionada',
        size=16,
        color=ft.Colors.BLUE_200,
    )
    resized_output_text = ft.Text(
        'Carpeta de salida: No seleccionada',
        size=16,
        weight=ft.FontWeight.BOLD
    )
    resized_result_text = ft.Text(
        size=16,
        weight=ft.FontWeight.BOLD
    )
    width_field=ft.TextField(
        label='Ancho',
        value='800',
        width=100,
        text_align=ft.TextAlign.RIGHT,
        keyboard_type=ft.KeyboardType.NUMBER,
    )
    height_field=ft.TextField(
        label='Alto',
        value='600',
        width=100,
        text_align=ft.TextAlign.RIGHT,
        keyboard_type=ft.KeyboardType.NUMBER,
    )

    # Controles para la vista de convertir imagenes----------------------------------------------------------------------------------------------------------------------
    convert_input_text = ft.Text(
        'No se ha seleccionado ninguna imagen',
        size=16,
        color=ft.Colors.BLUE_200,
    )
    convert_result_text = ft.Text(
        size=16,
        weight=ft.FontWeight.BOLD
    )
    formt_dropdown = ft.Dropdown(
        label='Formato de salida',
        width=200,
        options=[
            ft.dropdown.Option('PNG'),
            ft.dropdown.Option('JPG'),
            ft.dropdown.Option('JPEG'),
            ft.dropdown.Option('BMP'),
            ft.dropdown.Option('GIF'),
            ft.dropdown.Option('WEBP'),
        ],
        value='PNG',
    )

    #Controles para la extraccion de audio---------------------------------------------------------------------------------------------------------------------
    audio_input_text = ft.Text(
        'No se ha seleccionado ninguna carpeta',
        size=16,
        color=ft.Colors.BLUE_200,
    )

    audio_result_text = ft.Text(
        size=16,
        weight=ft.FontWeight.BOLD
    )
    audio_progress = ft.ProgressBar(
        width=400,
        visible=False,
    )
    current_video_text = ft.Text(
        size=16,
        color=ft.Colors.BLUE_200,
    )

    #Controle para la vista de fusion de PDFS----------------------------------------------------------------------------------------------------------------------
    pdf_input_text = ft.Text(
        'No se ha seleccionado ninguna carpeta para PDFs',
        size=16,
        color=ft.Colors.BLUE_200,
    )

    pdf_result_text = ft.Text(
        size=16,
        weight=ft.FontWeight.BOLD
    )

    #Controles para renombrar archivos---------------------------------------------------------------------------------------------------------------------------------
    rename_input_text = ft.Text(
        'No se ha seleccionado ninguna carpeta',
        size=16,
        color=ft.Colors.BLUE_200,
    )
    rename_result_text = ft.Text(
        size=16,
        weight=ft.FontWeight.BOLD
    )

    def on_rename_option_change(e):
        is_cambiar = e.control.value=='Cambiar'
        rename_search_text.visible = is_cambiar
        rename_replace_text.visible = is_cambiar
        rename_prefix_text.visible = not is_cambiar
        rename_search_text.update()
        rename_replace_text.update()
        rename_prefix_text.update()

    rename_option_dropdown = ft.Dropdown(
        label='Opcion de renombrado',
        width=200,
        options=[
            ft.dropdown.Option('Cambiar'),
            ft.dropdown.Option('Prefijo'),
        ],
        value='Cambiar',
        on_change=on_rename_option_change
    )
    rename_search_text = ft.TextField(
        label='Palabra a buscar',
        width=200,
        visible=True
    )
    rename_replace_text = ft.TextField(
        label='Reemplazar por',
        width=200,
        visible=True
    )

    rename_prefix_text = ft.TextField(
        label='Prefijo a agregar',
        width=200,
        visible=False
    )

    #Funciones------------------------------------------------------------------------------------------------------------------------------------------

    def rename_files ():
        try:
            if not state['rename_input_folder']:
                rename_result_text.value = 'Error: Selecciona una carpeta para renombrar'
                rename_result_text.color = ft.Colors.RED_400
                rename_result_text.update()
                return

            option = rename_option_dropdown.value
            if option == 'Cambiar':
                if not rename_search_text.value:
                    rename_result_text.value = 'Error: Ingresar la palabra a buscar'
                    rename_result_text.color = ft.Colors.RED_400
                    rename_result_text.update()
                    return
                value = [rename_search_text.value, rename_replace_text.value]
            else:
                if not rename_prefix_text.value:
                    rename_result_text.value = 'Error: Ingresar el prefijo'
                    rename_result_text.color = ft.Colors.RED_400
                    rename_result_text.update()
                    return
                value = rename_prefix_text.value
            cambiar_nombre(state['rename_input_folder'], option, value)
            rename_result_text.value = 'Archivos renombrados exitosamente'
            rename_result_text.color = ft.Colors.GREEN_400
            rename_result_text.update()

        except Exception as e:
            rename_result_text.value = f'Error al renombrar: {str(e)}'
            rename_result_text.color = ft.Colors.RED_400
            rename_result_text.update()

    def extract_audio():
        try:
            if not state['audio_input_folder']:
                audio_result_text.value = 'Error: Selecciona carpeta con videos'
                audio_result_text.color = ft.Colors.RED_400
                audio_result_text.update()
                return

            input_folder = state['audio_input_folder']
            output_folder = os.path.join(input_folder, 'audios')
            os.makedirs(output_folder, exist_ok=True)

            audio_progress.value = 0
            audio_progress.visible = True
            audio_progress.update()

            def progress_callback(current, total, archivo):
                progress = (current / total)
                audio_progress.value = progress
                audio_progress.update()
                current_video_text.value = f'Procesando video {archivo}: {current} de {total}'
                current_video_text.update()

            #Llamar funcion extraer_audiio con el callback de progreso
            extraer_audio(input_folder, output_folder, progress_callback)

            audio_result_text.value = 'Audio extraido exitosamente'
            audio_result_text.color = ft.Colors.GREEN_400
            audio_result_text.update()
            current_video_text.value = 'Proceso finalizado'

        except Exception as e:
            audio_result_text.value = f'Error durante la extraccion: {str(e)}'
            audio_result_text.color = ft.Colors.RED_400
            audio_result_text.update()

        finally:
            audio_progress.visible = False #Ocultar barra de progreso al finalizar
            audio_progress.update()

        audio_result_text.update()
        current_video_text.update()

    def merge_pdfs():
        try:
            if not state['pdf_input_folder']:
                pdf_result_text.value = 'Error: Selecciona una carpeta para PDFs'
                pdf_result_text.color = ft.Colors.RED_400
                pdf_result_text.update()
                return
            output_folder = os.path.join(state['pdf_input_folder'], 'pdfs_fusionados.pdf')
            fusionar_pdf(state['pdf_input_folder'], output_folder)
            pdf_result_text.value = f'PDFs fusionados en {output_folder}'
            pdf_result_text.color = ft.Colors.GREEN_400
            pdf_result_text.update()

        except Exception as e:
            pdf_result_text.value = f'Error al fusionar pdfs: {str(e)}'
            pdf_result_text.color = ft.Colors.RED_400
            pdf_result_text.update()


    def change_view(e):
        selected_view=e.control.selected_index
        if selected_view==0:
            state['current_view']='duplicates'
            content_area.content = duplicados_files_view
        elif selected_view==1:
            state['current_view']='organize'
            content_area.content = organizar_files_view
        elif selected_view ==2:
            state['current_view'] = 'resize'
            content_area.content = resized_files_view
        elif selected_view == 3:
            state['current_view'] = 'convert'
            content_area.content = convert_files_view
        elif selected_view == 4:
            state['current_view'] = 'audio'
            content_area.content = extract_audio_view
        elif selected_view == 5:
            state['current_view'] = 'merge_pdfs'
            content_area.content = merge_pdfs_view
        elif selected_view == 6:
            state['current_view'] = 'rename'
            content_area.content = rename_file_view
        content_area.update()

    def handler_file_picker(e: ft.FilePickerResultEvent):
        if e.files and len(e.files)>0:
            file_path=e.files[0].path
            state['convert_input_file']=file_path
            convert_input_text.value = f'Imagen seleccionada: {file_path}'
            convert_input_text.update()

    def handler_folder_picker(e: ft.FilePickerResultEvent):
        if e.path:
            if state['current_view']=='duplicates':
                selected_dir_text.value=f'Carpeta seleccionada: {e.path}'
                selected_dir_text.update()
                scan_directory(e.path)
            elif state['current_view']=='organize':
                organize_dir_text.value = f'Carpeta seleccionada:{e.path}'
                organize_dir_text.update()
                organize_directory(e.path)
            elif state['current_view']=='resize':
                if state['selecting_resize_output']:
                    state['resize_output_folder']=e.path
                    resized_output_text.value = f'Carpeta de salida seleccionada: {e.path}'
                    resized_output_text.update()
                else:
                    state['resize_input_folder']=e.path
                    resized_input_text.value = f'Carpeta de entrada seleccionada: {e.path}'
                    resized_input_text.update()
            elif state ['current_view'] == 'audio':
                state['audio_input_folder'] = e.path
                audio_input_text.value = f'Carpeta de entrada seleccionada: {e.path}'
                audio_input_text.update()
            elif state['current_view'] == 'merge_pdfs':
                state['pdf_input_folder'] = e.path
                pdf_input_text.value = f'Carpeta de entrada seleccionada: {e.path}'
                pdf_input_text.update()
            elif state['current_view'] == 'rename':
                state['rename_input_folder'] = e.path
                rename_input_text.value = f'Carpeta de entrada seleccionada: {e.path}'
                rename_input_text.update()


    def select_input_folder():
        state['selecting_resize_output']=False
        folder_picker.get_directory_path()

    def select_output_folder():
        state['selecting_resize_output']=True
        folder_picker.get_directory_path()

    def convert_image():
        try:
            if not state['convert_input_file']:
                convert_result_text.value = 'Error: Selecciona imagen'
                convert_result_text.color = ft.Colors.RED_400
                convert_result_text.update()
                return
            if not formt_dropdown.value:
                convert_result_text.value = 'Error: Seleciona formato de salida'
                convert_result_text.color = ft.Colors.RED_400
                convert_result_text.update()
                return
            convertir_imagen(state['convert_input_file'], formt_dropdown.value)
            convert_result_text.value = 'Imagen convertida exitosamente'
            convert_result_text.color = ft.Colors.GREEN_400
            convert_result_text.update()

        except Exception as e:
            convert_result_text.value = f'Error al convertir imagen: {str(e)}'
            convert_result_text.color = ft.Colors.RED_400
            convert_result_text.update()


    def resize_images():
        try:
            if not state['resize_input_folder'] or not state['resize_output_folder']:
                resized_result_text.value = 'Error: Seleccione las carpetas de entrada y salida'
                resized_result_text.color = ft.Colors.RED_400
                resized_result_text.update()
                return

            width = int(width_field.value)
            height = int(height_field.value)

            if width <= 0 or height <= 0:
                resized_result_text.value = 'Error: Las dimensiones deben de ser mayor a 0'
                resized_result_text.color=ft.Colors.RED_400
                resized_result_text.update()
                return

            batch_resize(state['resize_input_folder'], state['resize_output_folder'], width, height)
            resized_result_text.value = 'Imagenes redimensionadas exitosamente'
            resized_result_text.color = ft.Colors.GREEN_400
            resized_result_text.update()

        except ValueError:
            resized_result_text.value = 'Error: Ingresa dimensiones validas'
            resized_result_text.color = ft.Colors.RED_400
            resized_result_text.update()

        except Exception as e:
            resized_result_text.value = f'Error al redimensionar imagenes: {str(e)}'
            resized_result_text.color = ft.Colors.RED_400
            resized_result_text.update()


    def organize_directory(directory):
        try:
            organizar_folder(directory)
            organize_result_text.value='Archivos organizados exitosamente'
            organize_result_text.color=ft.Colors.GREEN_400
        except Exception as e:
            organize_result_text.value='Error al organizar archivos'
            organize_result_text.color=ft.Colors.RED_400
            print(e)
        organize_result_text.update()

    def scan_directory(directory):
        duplicates_list.controls.clear()
        state['current_duplicates'] = find_dup(directory)
        if not state['current_duplicates']:
            result_text.value='No se encontraron duplicados'
            result_text.color=ft.Colors.GREEN_400
            delete_all_btn.visible=False
        else:
            result_text.value=f'Se encontraron {len(state["current_duplicates"])} archivos duplicados'
            result_text.color=ft.Colors.ORANGE_400
            delete_all_btn.visible=True
            for dup_file, original in state['current_duplicates']:
                dup_row = ft.Row([
                    ft.Text(
                        f'Duplicado: {dup_file}\nOriginal: {original}',
                        size=12,
                        expand=True,
                        color=ft.Colors.BLUE_200,
                    ),
                    ft.ElevatedButton(
                        'Eliminar',
                        icon=ft.Icons.DELETE,
                        color=ft.Colors.WHITE,
                        bgcolor=ft.Colors.RED_900,
                        on_click=lambda e, path=dup_file: delete_duplicate(path)
                    )
                ])
                duplicates_list.controls.append(dup_row)
        duplicates_list.update()
        result_text.update()
        delete_all_btn.update()

    def delete_duplicate(filepath):
        if delete_file(filepath):
            result_text.value=f'Archivo eliminado: {filepath}'
            result_text.color=ft.Colors.GREEN_400
            for control in duplicates_list.controls[:]:
                if filepath in control.controls[0].value:
                    duplicates_list.controls.remove(control)
            state['current_duplicates'] = [(dup, orig) for dup, orig in state['current_duplicates'] if dup != filepath]
            if not state ['current_duplicates']:
                delete_all_btn.visible=False
        else:
            result_text.value=f'Error al eliminar archivo: {filepath}'
            result_text.color=ft.Colors.RED_400
        duplicates_list.update()
        result_text.update()
        delete_all_btn.update()


    def delete_all_duplicates():
        deleted_count=0
        failed_count=0
        for dup_file, _ in state['current_duplicates'][:]:
            if delete_file(dup_file):
                deleted_count+=1
            else:
                failed_count+=1

        duplicates_list.controls.clear()
        state['current_duplicates']=[]
        delete_all_btn.visible=False

        if failed_count == 0:
            result_text.value=f'Se eliminaron exitosamente {deleted_count} archivos duplicados'
            result_text.color=ft.Colors.GREEN_400
        else:
            result_text.value=f'Se eliminaron {deleted_count} archivos duplicados. Fallaron {failed_count} archivos'
            result_text.color=ft.Colors.RED_400
        duplicates_list.update()
        result_text.update()
        delete_all_btn.update()

    #Configurar los selectores de archivos ------------------------------------------------------------------------------------------------------------------------------------------------------
    file_picker = ft.FilePicker(
        on_result=handler_file_picker,
    )
    file_picker.file_type=ft.FilePickerFileType.IMAGE
    file_picker.allowed_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']

    #Configurar el selector de carpetas ------------------------------------------------------------------------------------------------------------------------------------------------------
    folder_picker = ft.FilePicker(on_result=handler_folder_picker)
    page.overlay.extend([folder_picker, file_picker])

    #Vista de archivos duplicados ------------------------------------------------------------------------------------------------------------------------------------------------------
    duplicados_files_view=ft.Container(
        content=ft.Column([
            ft.Container(
                content=ft.Text(
                    'Archivos duplicados',
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_200,
                ),
                margin=ft.margin.only(bottom=10)
            ),
            ft.Row([
                ft.ElevatedButton(
                    'Seleccionar Carpeta',
                    icon=ft.Icons.FOLDER_OPEN,
                    color=ft.Colors.WHITE,
                    bgcolor=ft.Colors.BLUE_900,
                    on_click=lambda _: folder_picker.get_directory_path(),
                ),
                delete_all_btn,
            ]),
            ft.Container(
                content=selected_dir_text,
                margin=ft.margin.only(top=10, bottom=10)
            ),
            result_text,
            ft.Container(
                content=duplicates_list,
                border=ft.border.all(2, ft.Colors.BLUE_400),
                border_radius=10,
                padding=20,
                margin=ft.margin.only(top=10),
                bgcolor=ft.Colors.BLUE_GREY_800,
                expand=True,
            )
        ]),
        padding=30,
        expand=True,
    )

    #Vista de organizar archivos------------------------------------------------------------------------------------------------------------------------------------------------------
    organizar_files_view=ft.Container(
        content=ft.Column([
            ft.Container(
                content=ft.Text(
                    'Organizar archivos',
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_200,
                ),
                margin=ft.margin.only(bottom=10)
            ),
            ft.ElevatedButton(
                'Seleccionar Carpeta',
                icon=ft.Icons.FOLDER_OPEN,
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.BLUE_900,
                on_click=lambda _: folder_picker.get_directory_path(),
            ),
            ft.Container(
                content=organize_dir_text,
                margin=ft.margin.only(top=10, bottom=10)
            ),
            organize_result_text,
            ft.Container(
                content=ft.Column([
                    ft.Text(
                        'Los archivos serán organizados en las siguientes carpetas:',
                        size=16,
                        color=ft.Colors.BLUE_200,
                    ),
                    ft.Text('* Imagenes (.jpeg, .jpg, .png, .gif)', size=14),
                    ft.Text('* Videos (.mp4, .mov, .avi, .mkv)', size=14),
                    ft.Text('* Documentos (.pdf, .docx, .doc, .txt)', size=14),
                    ft.Text('* Datasets (.xlsx, .csv, .sav)', size=14),
                    ft.Text('* Comprimidos (.zip, .rar, .7z)', size=14),
                ]),
                border=ft.border.all(2, ft.Colors.BLUE_400),
                border_radius=10,
                padding=20,
                margin=ft.margin.only(top=10),
                bgcolor=ft.Colors.BLUE_GREY_800,
            )
        ]),
        padding=30,
        expand=True,

    )

    #Vista de redimensionar imagenes------------------------------------------------------------------------------------------------------------------------------------------------------
    resized_files_view=ft.Container(
        content=ft.Column([
            ft.Container(
                content=ft.Text(
                    'Redimensionar imagenes',
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_200,
                ),
                margin=ft.margin.only(bottom=10)
            ),
            ft.Row([
                ft.ElevatedButton(
                    'Seleccionar Carpeta de entrada',
                    icon=ft.Icons.FOLDER_OPEN,
                    color=ft.Colors.WHITE,
                    bgcolor=ft.Colors.BLUE_900,
                    on_click=lambda _: select_input_folder(),
                ),
                ft.ElevatedButton(
                    'Seleccionar Carpeta de salida',
                    icon=ft.Icons.FOLDER_OPEN,
                    color=ft.Colors.WHITE,
                    bgcolor=ft.Colors.BLUE_900,
                    on_click=lambda _: select_output_folder(),
                )
            ]),
            ft.Container(
                content=ft.Column([
                    resized_input_text,
                    resized_output_text,
                ]),
                margin=ft.margin.only(top=10, bottom=10)
            ),
            ft.Container(
                content= ft.Column([
                    ft.Text(
                        'Dimensiones de la imagen',
                        size=16,
                        color=ft.Colors.BLUE_200,
                    ),
                    ft.Row([
                        width_field,
                        ft.Text('x',size=20),
                        height_field,
                        ft.Text('pixeles', size=16),
                    ])
                ]),
                margin=ft.margin.only(bottom=10)
            ),
            ft.ElevatedButton(
                'Redimensionar imagenes',
                icon=ft.Icons.PHOTO_SIZE_SELECT_LARGE,
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.BLUE_900,
                on_click=lambda _: resize_images(),
            ),
            resized_result_text,
            ft.Container(
                content=ft.Column([
                    ft.Text(
                        'Informacion:',
                        size=16,
                        color=ft.Colors.BLUE_200,
                    ),
                    ft.Text('* Se procesarán archivos .jpg, .jpeg y .png', size=14),
                    ft.Text('* Las imagenes originales no seran modificadas', size=14),
                    ft.Text("* Las imagenes dimensionadas se guardaran con el prefijo 'resized_'", size=14),
                ]),
                border=ft.border.all(2, ft.Colors.BLUE_400),
                border_radius=10,
                padding=20,
                margin=ft.margin.only(top=10),
                bgcolor=ft.Colors.BLUE_GREY_800,
            )
        ]),
        padding=30,
        expand=True,
    )

    # Vista de convertir imagenes------------------------------------------------------------------------------------------------------------------------------------------------------
    convert_files_view=ft.Container(
        content=ft.Column([
            ft.Container(
                content=ft.Text(
                    'Convertir imagenes',
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_200,
                ),
                margin=ft.margin.only(bottom=10)
            ),
            ft.ElevatedButton(
                'Seleccionar Carpeta',
                icon=ft.Icons.IMAGE,
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.BLUE_900,
                on_click=lambda _: file_picker.pick_files(),
            ),
            ft.Container(
                content=convert_input_text,
                margin=ft.margin.only(top=10, bottom=10),
            ),
            formt_dropdown,
            ft.Container(
                margin=ft.margin.only(top=10),
                content=ft.ElevatedButton(
                    'Convertir imagen',
                    icon=ft.Icons.TRANSFORM,
                    color=ft.Colors.WHITE,
                    bgcolor=ft.Colors.BLUE_900,
                    on_click=lambda _: convert_image()
                ),
            ),
            convert_result_text,
            ft.Container(
                content=ft.Column([
                    ft.Text(
                        'Informacion:',
                        size=16,
                        color=ft.Colors.BLUE_200,
                    ),
                    ft.Text('* Formatos soportados: PNG, JPEG, JPGm WEBP, BMP, GIF', size=14),
                    ft.Text('* La imagen original no será modificada', size=14),
                    ft.Text("* La imagen convertida se guardará en la misma carpeta", size=14),
                    ft.Text("* Al convertir a JPEG, las imagenes con transparencia se convertirán a fondo blanco", size=14),
                ]),
                border=ft.border.all(2, ft.Colors.BLUE_400),
                border_radius=10,
                padding=20,
                margin=ft.margin.only(top=10),
                bgcolor=ft.Colors.BLUE_GREY_800,
            )
        ]),
        padding=30,
        expand=True,
    )

    #Vista de extraccion de audio------------------------------------------------------------------------------------------------------------------------------------------------------
    extract_audio_view=ft.Container(
        content=ft.Column([
            ft.Container(
                content=ft.Text(
                    'Extraer audio de los videos',
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_200,
                ),
                margin=ft.margin.only(bottom=10)
            ),
            ft.ElevatedButton(
                'Seleccionar Carpeta',
                icon=ft.Icons.FOLDER_OPEN,
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.BLUE_900,
                on_click=lambda _: folder_picker.get_directory_path(),
            ),
            ft.Container(
                content=audio_input_text,
                margin=ft.margin.only(top=10, bottom=10),
            ),
            ft.ElevatedButton(
                'Extraer audio',
                icon = ft.Icons.AUDIOTRACK,
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.BLUE_900,
                on_click=lambda _: extract_audio()
            ),
            current_video_text,
            audio_progress,
            audio_result_text,
            ft.Container(
                content=ft.Column([
                    ft.Text(
                        'Informacion:',
                        size=16,
                        color=ft.Colors.BLUE_200,
                    ),
                    ft.Text('* Formatos soportados: MP4, AVI, MOV, MKV', size=14),
                    ft.Text('* Los archivos de audio se extraeran en formato MP3', size=14),
                    ft.Text("* Los audios extraido se guardarán en una carpeta 'audios dentro de la carpeta de los videos", size=14),
                    ft.Text("* Los archivos de video originales no serán modificados", size=14),
                ]),
                border=ft.border.all(2, ft.Colors.BLUE_400),
                border_radius=10,
                padding=20,
                margin=ft.margin.only(top=10),
                bgcolor=ft.Colors.BLUE_GREY_800,
            )
        ]),
        padding=30,
        expand=True,
    )

    # Vista de fusion de pdfs------------------------------------------------------------------------------------------------------------------------------------------------------
    merge_pdfs_view = ft.Container(
        content=ft.Column([
            ft.Container(
                content=ft.Text(
                    'Fusionar archivos PDF',
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_200,
                ),
                margin=ft.margin.only(bottom=10)
            ),
            ft.ElevatedButton(
                'Seleccionar Carpeta',
                icon=ft.Icons.FOLDER_OPEN,
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.BLUE_900,
                on_click=lambda _: folder_picker.get_directory_path(),
            ),
            ft.Container(
                content=pdf_input_text,
                margin=ft.margin.only(top=10, bottom=10),
            ),
            ft.ElevatedButton(
                'fusionar PDFs',
                icon=ft.Icons.MERGE_TYPE,
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.BLUE_900,
                on_click=lambda _: merge_pdfs()
            ),
            pdf_result_text,
        ]),
        padding=30,
        expand=True,
    )

    # Vista de renombrar archivos------------------------------------------------------------------------------------------------------------------------------------------------------
    rename_file_view = ft.Container(
        content=ft.Column([
            ft.Container(
                content=ft.Text(
                    'Renombrar archivos',
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_200,
                ),
                margin=ft.margin.only(bottom=10)
            ),
            ft.ElevatedButton(
                'Seleccionar Carpeta',
                icon=ft.Icons.FOLDER_OPEN,
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.BLUE_900,
                on_click=lambda _: folder_picker.get_directory_path(),
            ),
            ft.Container(
                content=rename_input_text,
                margin=ft.margin.only(top=10, bottom=10),
            ),
            ft.Container(
                content=ft.Column([
                    rename_option_dropdown,
                    rename_search_text,
                    rename_replace_text,
                    rename_prefix_text,
                ]), margin=ft.margin.only(top=10, bottom=10),
            ),
            ft.ElevatedButton(
                'Renombrar archivos',
                icon=ft.Icons.MERGE_TYPE,
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.BLUE_900,
                on_click=lambda _: rename_files()
            ),
            rename_result_text,
        ]),
        padding=30,
        expand=True,
    )

    #Pantalla principal ----------------------------------------------------------------------------------------------------------------------------------------------
    content_area = ft.Container(
        content=duplicados_files_view,
        expand=True,
    )

    #Menu lateral------------------------------------------------------------------------------------------------------------------------------------------------------
    rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=100,
        min_extended_width=200,
        group_alignment=-0.9,
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.Icons.DELETE_FOREVER,
                selected_icon=ft.Icons.DELETE_FOREVER,
                label='Duplicados'
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.FOLDER_COPY,
                selected_icon=ft.Icons.FOLDER_COPY,
                label='Organizar'
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.PHOTO_SIZE_SELECT_LARGE,
                selected_icon=ft.Icons.PHOTO_SIZE_SELECT_LARGE,
                label='Redimensionar'
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.TRANSFORM,
                selected_icon=ft.Icons.TRANSFORM,
                label='Convertir'
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.AUDIOTRACK,
                selected_icon=ft.Icons.AUDIOTRACK,
                label='Extraer audio'
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.MERGE_TYPE,
                selected_icon=ft.Icons.MERGE_TYPE,
                label='Fusionar PDFs'
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.EDIT,
                selected_icon=ft.Icons.EDIT,
                label='Renombrar'
            ),
        ],
        on_change=change_view,
        bgcolor=ft.Colors.BLUE_GREY_900,
    )

    fila = ft.Row([
        rail,
        ft.VerticalDivider(width=1),
        content_area
    ],
        expand=True,
    )

    page.add(fila)

if __name__=='__main__':
    ft.app(target=main)
