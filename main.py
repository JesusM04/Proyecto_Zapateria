import flet as ft
import pandas as pd

def ventana_combinador(page: ft.Page):
    """Función principal para la interfaz gráfica de la ruta /exceloption"""
    page.title = "Combinador de Archivos Excel"
    page.theme_mode = "light"
    page.padding = 20

    # Variables para almacenar las rutas de los archivos y la carpeta de destino
    archivos = []
    carpeta_destino = None
    num_hoas = 0  # Definimos esta variable aquí para poder usarla en las funciones internas

    # Función para combinar archivos
    def combinar_archivos(e):
        nonlocal num_hoas, archivos, carpeta_destino  # Asegúrate de usar nonlocal si necesitas modificar las variables fuera de la función
        if len(archivos) < num_hoas:
            mensaje.value = f"Por favor, selecciona {num_hoas} archivos."
            page.update()
            return
        if not carpeta_destino:
            mensaje.value = "Por favor, selecciona una carpeta de destino."
            page.update()
            return

        try:
            # Verificar si openpyxl está instalado
            try:
                import openpyxl
            except ImportError:
                mensaje.value = "Error: 'openpyxl' no está instalado. Ejecuta 'pip install openpyxl'."
                page.update()
                return

            # Cargar los archivos Excel
            dfs = []
            for archivo in archivos:
                try:
                    df = pd.read_excel(archivo, engine="openpyxl")
                    dfs.append(df)
                except Exception as e:
                    mensaje.value = f"Error al leer el archivo {archivo}: {str(e)}"
                    page.update()
                    return

            # Determinar el número mínimo de filas entre todos los DataFrames
            num_filas = min(len(df) for df in dfs)

            # Truncar todos los DataFrames para que tengan el mismo número de filas
            dfs = [df.head(num_filas) for df in dfs]

            # Combinar los DataFrames basados en el índice (orden de las filas)
            df_final = dfs[0]
            for df in dfs[1:]:
                # Renombrar columnas duplicadas para evitar conflictos
                columnas_duplicadas = set(df_final.columns) & set(df.columns)
                df = df.rename(columns={col: f"{col}_df{dfs.index(df) + 1}" for col in columnas_duplicadas})
                # Combinar los DataFrames
                df_final = df_final.join(df)

            # Guardar en un nuevo archivo Excel
            archivo_salida = f"{carpeta_destino}/archivo_combinado.xlsx"
            df_final.to_excel(archivo_salida, index=False, engine="openpyxl")
            mensaje.value = f"¡Archivo combinado guardado como '{archivo_salida}'!"
        except Exception as e:
            mensaje.value = f"Error: {str(e)}"
        page.update()

    # Función para manejar la selección de archivos
    def seleccionar_archivo(e: ft.FilePickerResultEvent):
        nonlocal archivos  # Asegúrate de que 'archivos' sea modificable
        if e.files:
            archivos.append(e.files[0].path)
            mensaje.value = f"Archivos seleccionados: {len(archivos)}/{num_hoas}"
            if len(archivos) == num_hoas:
                boton_seleccionar_archivo.disabled = True  # Deshabilitar el botón de selección
                boton_combinar.disabled = False  # Habilitar el botón de combinar
            page.update()
        else:
            mensaje.value = "Ningún archivo seleccionado."
        page.update()

    # Función para manejar la selección de la carpeta de destino
    def seleccionar_carpeta_destino(e: ft.FilePickerResultEvent):
        nonlocal carpeta_destino  # Asegúrate de que 'carpeta_destino' sea modificable
        if e.path:
            carpeta_destino = e.path
            mensaje.value = f"Carpeta de destino seleccionada: {carpeta_destino}"
            if len(archivos) == num_hoas:
                boton_combinar.disabled = False  # Habilitar el botón de combinar
        else:
            mensaje.value = "Ninguna carpeta seleccionada."
        page.update()

    # Función para retroceder
    def retroceder(e):
        nonlocal num_hoas, archivos  # Modificamos num_hoas y archivos para restablecerlos
        num_hoas = 0
        archivos = []
        mensaje.value = "Selecciona cuántas hojas deseas unir."
        boton_seleccionar_archivo.disabled = False  # Habilitar el botón de selección
        boton_combinar.disabled = True  # Deshabilitar el botón de combinar
        page.controls.clear()
        page.add(contenido_inicial)
        page.update()

    # Función para avanzar a la selección de archivos
    def avanzar_seleccion_archivos():
        nonlocal num_hoas  # Aseguramos que num_hoas es modificable
        try:
            num_hoas = int(input_hoas.value)
            if num_hoas < 1:
                mensaje.value = "El número de hojas debe ser al menos 1."
                page.update()
                return
            mensaje.value = f"Selecciona {num_hoas} archivos."
            page.controls.clear()
            page.add(
                ft.Column(
                    [
                        mensaje,
                        ft.Row([boton_retroceder], alignment=ft.MainAxisAlignment.CENTER),
                        ft.Row([boton_seleccionar_archivo], alignment=ft.MainAxisAlignment.CENTER),
                        ft.Row([boton_seleccionar_carpeta], alignment=ft.MainAxisAlignment.CENTER),
                        ft.Row([boton_combinar], alignment=ft.MainAxisAlignment.CENTER),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                )
            )
            boton_seleccionar_archivo.disabled = False  # Habilitar el botón de selección
        except ValueError:
            mensaje.value = "Por favor, ingresa un número válido."
        page.update()

    # Función para ir a la vista de ExcelOption
    def ir_a_exceloption(e):
        page.go("/excelOption")

    # Configurar el FilePicker
    file_picker = ft.FilePicker(on_result=seleccionar_archivo)
    folder_picker = ft.FilePicker(on_result=seleccionar_carpeta_destino)
    page.overlay.extend([file_picker, folder_picker])

    # Elementos de la interfaz
    mensaje = ft.Text(value="Selecciona cuántas hojas deseas unir.", color="blue")
    input_hoas = ft.TextField(label="Número de hojas", width=200)
    boton_confirmar_hoas = ft.ElevatedButton(
        "Confirmar",
        on_click=lambda e: avanzar_seleccion_archivos(),
    )
    boton_retroceder = ft.ElevatedButton(
        "Retroceder",
        on_click=retroceder,
    )
    boton_seleccionar_archivo = ft.ElevatedButton(
        "Seleccionar Archivo",
        on_click=lambda _: file_picker.pick_files(),
        disabled=True,  # Deshabilitado inicialmente
    )
    boton_seleccionar_carpeta = ft.ElevatedButton(
        "Seleccionar Carpeta de Destino",
        on_click=lambda _: folder_picker.get_directory_path(),
    )
    boton_combinar = ft.ElevatedButton(
        "Combinar Archivos",
        on_click=combinar_archivos,
        disabled=True,  # Deshabilitado inicialmente
    )

    # Botón para ir a la ruta /exceloption
    boton_ir_a_exceloption = ft.ElevatedButton(
        "Ir a ExcelOption",
        on_click=ir_a_exceloption,
    )

    boton_volver = ft.ElevatedButton(
        "Volver",
        on_click=lambda _: page.go("/"),
        style=ft.ButtonStyle(
            bgcolor=ft.colors.RED_500,
            color=ft.colors.WHITE,
            shape=ft.RoundedRectangleBorder(radius=8),
            padding=ft.padding.all(12),
        ),
    )

    # Contenido inicial
    contenido_inicial = ft.Column(
        [
            mensaje,
            input_hoas,
            ft.Row([boton_confirmar_hoas, boton_retroceder], alignment=ft.MainAxisAlignment.CENTER),
            boton_ir_a_exceloption,  # Añadir el botón de redirección
            boton_volver
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # Iniciar la ventana con el contenido inicial
    return ft.View("/excelOption", [contenido_inicial])

def home_page(page):
    page.theme_mode = "light"
    page.bgcolor = ft.colors.WHITE  # Fondo inicial blanco

    # Cambiar el fondo entre blanco y negro

    """Página Principal - Diseño minimalista y elegante"""
    return ft.View(
        "/",
        [
            ft.AppBar(
                title=ft.Text("DigiWork Solutions"),
                bgcolor=ft.colors.BLUE_GREY_900,
                color=ft.colors.WHITE,
            ),
            ft.ResponsiveRow(
                controls=[
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Icon(
                                    ft.icons.BUSINESS,
                                    size=120,
                                    color=ft.colors.BLUE_500
                                ),
                                ft.Text(
                                    "Gestión eficiente de clientes operativos",
                                    size=20,
                                    weight=ft.FontWeight.BOLD,
                                    text_align=ft.TextAlign.CENTER,
                                    color=ft.colors.BLUE_GREY_800,
                                ),
                                ft.Row(
                                    [
                                        ft.ElevatedButton(
                                            "Configuración",
                                            on_click=lambda _: page.go("/config"),
                                            style=ft.ButtonStyle(
                                                bgcolor=ft.colors.GREEN_500,
                                                color=ft.colors.WHITE,
                                                shape=ft.RoundedRectangleBorder(radius=8),
                                                padding=ft.padding.all(12),
                                            ),
                                        ),
                                        ft.ElevatedButton(
                                            "Perfil",
                                            on_click=lambda _: page.go("/profile"),
                                            style=ft.ButtonStyle(
                                                bgcolor=ft.colors.BLUE_500,
                                                color=ft.colors.WHITE,
                                                shape=ft.RoundedRectangleBorder(radius=8),
                                                padding=ft.padding.all(12),
                                            ),
                                        ),
                                        ft.ElevatedButton(
                                            "Excel",
                                            on_click=lambda _: page.go("/excelOption"),
                                            style=ft.ButtonStyle(
                                                bgcolor=ft.colors.BLUE_500,
                                                color=ft.colors.WHITE,
                                                shape=ft.RoundedRectangleBorder(radius=8),
                                                padding=ft.padding.all(12),
                                            ),
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.CENTER,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        alignment=ft.alignment.center,
                        expand=True,
                        padding=20,
                        col={"xs": 12, "sm": 8, "md": 6, "lg": 4},  # Columnas responsivas
                        width=600, # Max width
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        ]
    )

def config_page(page):
    """Segunda ventana - Dashboard de Configuración con estilo mejorado"""
    return ft.View(
        "/config",
        [
            ft.AppBar(
                title=ft.Text("Configuración"),
                bgcolor=ft.colors.BLUE_GREY_900,
                color=ft.colors.WHITE,
            ),
            ft.ResponsiveRow(
                controls=[
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(
                                    "Panel de Usuario",
                                    size=28,
                                    weight=ft.FontWeight.BOLD,
                                    text_align=ft.TextAlign.CENTER,
                                    color=ft.colors.BLUE_GREY_800,
                                ),
                                ft.ElevatedButton(
                                    "Volver",
                                    on_click=lambda _: page.go("/"),
                                    style=ft.ButtonStyle(
                                        bgcolor=ft.colors.RED_500,
                                        color=ft.colors.WHITE,
                                        shape=ft.RoundedRectangleBorder(radius=10),
                                        padding=ft.padding.all(15),
                                        elevation=5,
                                    ),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        alignment=ft.alignment.center,
                        expand=True,
                        padding=20,
                        col={"xs": 12, "sm": 8, "md": 6, "lg": 4},  # Columnas responsivas
                        width=600, # Max width
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        ]
    )


def profile_page(page):
    """Perfil de Usuario con paginación funcional y diseño responsivo"""

    # Variables de estado
    current_page = 0
    rows_per_page = 6  # Definir cuántas filas se muestran por página

    # Datos de usuario
    user_info = [
        ("Nombre", "Juan Pérez"),
        ("Correo", "juan.perez@example.com"),
        ("Teléfono", "+123 456 789"),
        ("Dirección", "Calle Ficticia 123"),
        ("Fecha de Nacimiento", "01/01/1990"),
        ("Género", "Masculino"),
        ("País", "España"),
        ("Estado Civil", "Soltero"),
        ("Ocupación", "Desarrollador de Software"),
        ("Educación", "Ingeniería en Sistemas"),
        ("Lenguas", "Español, Inglés"),
        ("Hobbies", "Programación, Lectura"),
        ("Redes Sociales", "Instagram: @juanperez, Twitter: @juanperez"),
        ("Tiempo de experiencia", "5 años"),
        ("Proyectos destacados", "Aplicación móvil XYZ, Sitio web ABC"),
    ]

    # Función para obtener datos según la página
    def get_data_for_page(page_num):
        """Obtiene los datos correspondientes a la página actual."""
        start_index = page_num * rows_per_page
        end_index = start_index + rows_per_page
        return user_info[start_index:end_index]

    # Función para construir la tabla
    def build_data_table():
        """Construir la tabla con los datos para la página actual"""
        current_data = get_data_for_page(current_page)
        return ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Campo")),
                ft.DataColumn(ft.Text("Valor")),
            ],
            rows=[ft.DataRow(cells=[ft.DataCell(ft.Text(field)), ft.DataCell(ft.Text(value))]) for field, value in current_data],
            border=ft.border.all(1, ft.Colors.BLUE_GREY_400),
            column_spacing=50,
        )

    # Funciones para los botones de paginación
    def on_next_click(e):
        nonlocal current_page
        if (current_page + 1) * rows_per_page < len(user_info):
            current_page += 1
            update_ui()  # Actualizar la interfaz de usuario

    def on_prev_click(e):
        nonlocal current_page
        if current_page > 0:
            current_page -= 1
            update_ui()  # Actualizar la interfaz de usuario

    # Función para actualizar la UI
    def update_ui():
        """Actualiza la interfaz de usuario con los datos de la página actual."""
        current_data = get_data_for_page(current_page)
        data_table.rows = [ft.DataRow(cells=[ft.DataCell(ft.Text(field)), ft.DataCell(ft.Text(value))]) for field, value in current_data]
        prev_button.disabled = current_page == 0
        next_button.disabled = (current_page + 1) * rows_per_page >= len(user_info)
        page.update()  # Actualizar la vista

    # Construir la tabla inicial
    data_table = build_data_table()

    # Botones de paginación
    prev_button = ft.IconButton(
        ft.Icons.ARROW_BACK,
        on_click=on_prev_click,
        disabled=current_page == 0,
        icon_color=ft.Colors.WHITE,
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.BLUE_GREY_800,
            shape=ft.RoundedRectangleBorder(radius=10),
        )
    )

    next_button = ft.IconButton(
        ft.Icons.ARROW_FORWARD,
        on_click=on_next_click,
        disabled=(current_page + 1) * rows_per_page >= len(user_info),
        icon_color=ft.Colors.WHITE,
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.BLUE_GREY_800,
            shape=ft.RoundedRectangleBorder(radius=10),
        )
    )

    # Vista completa responsiva
    return ft.View(
        "/profile",
        [

            ft.AppBar(title=ft.Text("Perfil del Usuario"), bgcolor=ft.Colors.BLUE_GREY_900, color=ft.Colors.WHITE),
            ft.ResponsiveRow(
                controls=[
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(
                                    "Información del Usuario",
                                    size=28,
                                    weight=ft.FontWeight.BOLD,
                                    text_align=ft.TextAlign.CENTER,
                                    color=ft.Colors.BLUE_GREY_800,
                                ),
                                data_table,  # Usar la tabla inicial
                                ft.Row(
                                    controls=[prev_button, next_button],
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    spacing=20,
                                ),
                                ft.ElevatedButton(
                                    "Volver",
                                    on_click=lambda _: page.go("/"),
                                    style=ft.ButtonStyle(
                                        bgcolor=ft.Colors.BLUE_500,
                                        color=ft.Colors.WHITE,
                                        shape=ft.RoundedRectangleBorder(radius=10),
                                        padding=ft.padding.all(15),
                                        elevation=5,
                                    ),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        alignment=ft.alignment.center,
                        expand=True,
                        padding=20,
                        col={"xs": 12, "sm": 8, "md": 6, "lg": 4},  # Columnas responsivas
                        width=600,  # Ancho máximo
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        ]
    )

import flet as ft

def main(page: ft.Page):
    """Función principal para manejar la navegación y cambio de fondo"""

    # Funciones de navegación
    def route_change(route):
        page.views.clear()
        if page.route == "/":
            page.views.append(home_page(page))
        elif page.route == "/config":
            page.views.append(config_page(page))
        elif page.route == "/profile":
            page.views.append(profile_page(page))
        elif page.route == "/excelOption":
            page.views.append(ventana_combinador(page))
        page.update()

    page.on_route_change = route_change
    page.go(page.route)




ft.app(target=main, view=ft.AppView.FLET_APP)  # Ejecutar en ventana nativa
