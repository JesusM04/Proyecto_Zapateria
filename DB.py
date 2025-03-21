import flet as ft
import pandas as pd
from flet import FilePicker, FilePickerResultEvent
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Declarar la base
Base = declarative_base()


# Definir la clase para la base de datos
class Persona(Base):
    __tablename__ = 'personas'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, nullable=False)
    apellido = Column(String, nullable=False)
    telefono = Column(String, nullable=False)
    correo = Column(String, nullable=False)
    edad = Column(Integer, nullable=False)
    cedula = Column(String, unique=True, nullable=False)

    def __repr__(self):
        return f"<Persona(id={self.id}, nombre={self.nombre}, apellido={self.apellido}, telefono={self.telefono}, correo={self.correo}, edad={self.edad}, cedula={self.cedula})>"


# Crear la base de datos en SQLite
db_file = 'personas.db'
if not os.path.exists(db_file):
    engine = create_engine(f'sqlite:///{db_file}')
    Base.metadata.create_all(engine)
else:
    engine = create_engine(f'sqlite:///{db_file}')

# Crear la sesión
Session = sessionmaker(bind=engine)
session = Session()


# Función para ver personas en el ListView
def ver_personas(page):
    personas = session.query(Persona).all()

    list_view = ft.Column(
        controls=[
            ft.Row(
                controls=[
                    ft.Container(ft.Text("ID", size=16, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE), width=60,
                                 bgcolor=ft.colors.BLUE_800),
                    ft.Container(ft.Text("Nombre", size=16, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                                 width=180, bgcolor=ft.colors.BLUE_800),
                    ft.Container(ft.Text("Teléfono", size=16, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                                 width=140, bgcolor=ft.colors.BLUE_800),
                    ft.Container(ft.Text("Correo", size=16, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                                 width=220, bgcolor=ft.colors.BLUE_800),
                    ft.Container(ft.Text("Edad", size=16, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE), width=100,
                                 bgcolor=ft.colors.BLUE_800),
                    ft.Container(ft.Text("Cédula", size=16, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                                 width=140, bgcolor=ft.colors.BLUE_800)
                ],
                alignment=ft.MainAxisAlignment.START,
            ),
            *[
                ft.Row(
                    controls=[
                        ft.Container(ft.Text(str(p.id), size=14, color=ft.colors.BLACK), width=60,
                                     bgcolor=ft.colors.CYAN_100, border_radius=5),
                        ft.Container(ft.Text(f"{p.nombre} {p.apellido}", size=14, color=ft.colors.BLACK), width=180,
                                     bgcolor=ft.colors.CYAN_100, border_radius=5),
                        ft.Container(ft.Text(p.telefono, size=14, color=ft.colors.BLACK), width=140,
                                     bgcolor=ft.colors.CYAN_100, border_radius=5),
                        ft.Container(ft.Text(p.correo, size=14, color=ft.colors.BLACK), width=220,
                                     bgcolor=ft.colors.CYAN_100, border_radius=5),
                        ft.Container(ft.Text(str(p.edad), size=14, color=ft.colors.BLACK), width=100,
                                     bgcolor=ft.colors.CYAN_100, border_radius=5),
                        ft.Container(ft.Text(p.cedula, size=14, color=ft.colors.BLACK), width=140,
                                     bgcolor=ft.colors.CYAN_100, border_radius=5),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    height=40,
                ) for p in personas
            ]
        ],
        spacing=5,
        alignment=ft.MainAxisAlignment.START,
    )

    page.clean()
    page.add(list_view)


# Función para cargar datos de Excel a la base de datos
# Función para cargar los datos de un archivo Excel a la base de datos
def cargar_excel_a_bd(page):
    # Variable global
    archivo_excel = None

    # Configurar el FilePicker
    def seleccionar_archivo_excel(e: FilePickerResultEvent):
        nonlocal archivo_excel
        if e.files:
            archivo_excel = e.files[0].path
            mensaje.value = f"Archivo Excel seleccionado: {archivo_excel}"
        else:
            mensaje.value = "Ningún archivo seleccionado."
        page.update()

    # Función para cargar los datos a la base de datos
    def cargar_datos(e):
        if archivo_excel is None:
            mensaje.value = "Por favor, selecciona un archivo Excel."
            page.update()
            return

        try:
            # Cargar el archivo Excel y eliminar espacios en los nombres de las columnas
            df = pd.read_excel(archivo_excel, engine="openpyxl")

            # Eliminar espacios en los nombres de las columnas
            df.columns = df.columns.str.strip()

            # Convertir todas las columnas a minúsculas para evitar problemas de mayúsculas/minúsculas
            df.columns = df.columns.str.lower()

            # Mostrar las columnas del archivo para verificar
            print(f"Columnas en el archivo Excel: {df.columns.tolist()}")

            # Verificar si todas las columnas necesarias están presentes (ignorando mayúsculas/minúsculas)
            columnas_requeridas = ["nombre", "apellido", "telefono", "correo", "edad", "cedula"]
            if not all(col in df.columns for col in columnas_requeridas):
                mensaje.value = "El archivo Excel debe contener las columnas: 'nombre', 'apellido', 'telefono', 'correo', 'edad', 'cedula'."
                page.update()
                return

            # Crear una sesión de base de datos
            DATABASE_URL = "sqlite:///mi_base_de_datos.db"  # Cambia esto a tu base de datos
            engine = create_engine(DATABASE_URL)
            Session = sessionmaker(bind=engine)
            session = Session()

            # Cargar cada fila a la base de datos
            for _, row in df.iterrows():
                persona = Persona(
                    nombre=row["nombre"],
                    apellido=row["apellido"],
                    telefono=row["telefono"],
                    correo=row["correo"],
                    edad=row["edad"],
                    cedula=row["cedula"]
                )
                session.add(persona)

            # Confirmar los cambios en la base de datos
            session.commit()

            mensaje.value = f"Datos cargados exitosamente desde {archivo_excel} a la base de datos."
        except Exception as e:
            mensaje.value = f"Error: {str(e)}"
        page.update()

    # Configuración de los controles de la interfaz gráfica con Flet
    file_picker = FilePicker(on_result=seleccionar_archivo_excel)
    page.overlay.append(file_picker)

    # Elementos de la interfaz
    mensaje = ft.Text(value="Selecciona un archivo Excel para cargar los datos.", color="blue")
    boton_seleccionar_archivo = ft.ElevatedButton(
        "Seleccionar archivo Excel", on_click=lambda _: file_picker.pick_files()
    )
    boton_cargar_datos = ft.ElevatedButton(
        "Cargar Datos a la Base de Datos", on_click=cargar_datos
    )

    # Contenido de la ventana de carga de datos
    contenido_carga_datos = ft.Column(
        [
            mensaje,
            boton_seleccionar_archivo,
            boton_cargar_datos,
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    page.clean()
    page.add(contenido_carga_datos)


# Función para la ventana principal (Home)
def ventana_home(page):
    title = ft.Text("Bienvenido a DigiWork Solutions", size=30, weight=ft.FontWeight.BOLD, color=ft.colors.CYAN_600)

    # Botones para navegar
    btn_ver_datos = ft.ElevatedButton("Ver Datos", on_click=lambda _: ver_personas(page), bgcolor=ft.colors.PINK_400,
                                      color=ft.colors.WHITE)
    btn_excel_unificado = ft.ElevatedButton("Excel Unificado", on_click=lambda _: combinar_archivos(page),
                                            bgcolor=ft.colors.PINK_400, color=ft.colors.WHITE)
    btn_cargar_excel_bd = ft.ElevatedButton("Cargar Excel a Base de Datos", on_click=lambda _: cargar_excel_a_bd(page),
                                            bgcolor=ft.colors.PINK_400, color=ft.colors.WHITE)
    btn_salir = ft.ElevatedButton("Salir", on_click=lambda _: page.window_close(), bgcolor=ft.colors.RED_500,
                                  color=ft.colors.WHITE)

    page.add(title, btn_ver_datos, btn_excel_unificado, btn_cargar_excel_bd, btn_salir)


def combinar_archivos(page: ft.Page):
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


# Función principal de la aplicación
def main(page):
    ventana_home(page)


# Iniciar la aplicación
ft.app(target=main)
