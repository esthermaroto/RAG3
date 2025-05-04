from markitdown import MarkItDown
import os
import re
from rich import print
from rich.console import Console

# Esta es la herramienta que nos ayudará a convertir en formato markdown lo que le pasemos
md = MarkItDown()

# Crear una consola de rich
console = Console()

# Para este ejemplo usamos documentación de YouTube relacionadas con los canales y sus vídeos
URLs = [
    {"url": "https://support.google.com/youtube/answer/9527654?hl=es", "name": "Configurar la audiencia de un canal o un vídeo"},
    {"url": "https://support.google.com/youtube/answer/11913617?sjid=11557296865847177507-EU", "name": "Consejos para subir vídeos de YouTube"},
    {"url": "https://support.google.com/youtube/answer/11908409?sjid=11557296865847177507-EU", "name": "Consejos para optimizar vídeos"},
    {"url": "https://support.google.com/youtube/answer/12340300?sjid=11557296865847177507-EU", "name": "Consejos sobre miniaturas y títulos"},
    {"url": "https://support.google.com/youtube/answer/12948449?sjid=11557296865847177507-EU", "name": "Consejos para las descripciones de los vídeos"},
    {"url": "https://support.google.com/youtube/answer/13616979?sjid=11557296865847177507-EU", "name": "Consejos para programar subidas"},
    {"url": "https://support.google.com/youtube/answer/11913513?sjid=11557296865847177507-EU", "name": "Consejos sobre equipos de vídeo"},
    {"url": "https://support.google.com/youtube/answer/12340105?sjid=11557296865847177507-EU", "name": "Consejos de grabación"},
    {"url": "https://support.google.com/youtube/answer/12948118?sjid=11557296865847177507-EU", "name": "Consejos para grabar con un dispositivo móvil"},
    {"url": "https://support.google.com/youtube/answer/11221953?sjid=11557296865847177507-EU", "name": "Consejos para editar vídeos"},
    {"url": "https://support.google.com/youtube/answer/15575746?sjid=11557296865847177507-EU", "name": "Consejos para las retiradas por infracción de derechos de autor"},
    {"url": "https://support.google.com/youtube/answer/15577610?sjid=11557296865847177507-EU", "name": "Consejos para encontrar música de uso autorizado"},
    {"url": "https://support.google.com/youtube/answer/11912631?sjid=11557296865847177507-EU", "name": "Consejos sobre las publicaciones"},
    {"url": "https://support.google.com/youtube/answer/12929858?sjid=11557296865847177507-EU", "name": "Consejos para conseguir más acuerdos de marca"},
    {"url": "https://support.google.com/youtube/answer/11912533?sjid=11557296865847177507-EU", "name": "Consejos para ganar dinero en YouTube"},
    {"url": "https://support.google.com/youtube/answer/13615784?sjid=11557296865847177507-EU", "name": "Consejos sobre usuarios nuevos y recurrentes"},
    {"url": "https://support.google.com/youtube/answer/13616340?sjid=11557296865847177507-EU", "name": "Consejos para saber qué contenido crear"},
    {"url": "https://support.google.com/youtube/answer/11912632?sjid=11557296865847177507-EU", "name": "Consejos sobre Estadísticas de YouTube"},
    {"url": "https://support.google.com/youtube/answer/11914225?sjid=11557296865847177507-EU", "name": "Consejos de búsqueda y descubrimiento"},
    {"url": "https://support.google.com/youtube/answer/15086271?sjid=11557296865847177507-EU", "name": "Consejos para evitar que disminuya el tiempo de visualización"},
    {"url": "https://support.google.com/youtube/answer/12950272?sjid=11557296865847177507-EU", "name": "Consejos sobre el banner del canal y la imagen de perfil"},
    {"url": "https://support.google.com/youtube/answer/12356784?sjid=11557296865847177507-EU", "name": "Consejos sobre los estrenos de YouTube"},
]

# Se crea un directorio para guardar los archivos si no existe
output_dir = "youtube_guides"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    console.print(f":file_folder: [bold green]Directorio creado:[/bold green] {output_dir}")

# Función para crear un nombre de archivo válido, que no tenga 
def create_valid_filename(name):
    # Reemplazar caracteres no válidos y espacios
    valid_name = re.sub(r'[^\w\s-]', '', name.lower())
    valid_name = re.sub(r'[-\s]+', '_', valid_name)
    return valid_name

# Convertir URLs a Markdown y guardar en archivos
for item in URLs:
    url = item["url"]
    name = item["name"]
    
    # Convertir la URL a contenido markdown
    result = md.convert(url)
    
    # Crear nombre de archivo válido
    filename = create_valid_filename(name) + ".md"
    filepath = os.path.join(output_dir, filename)
    
    # Guardar contenido en el archivo
    if result:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# {name}\n\n")
            # Convertir el resultado a string si no lo es ya
            f.write(result.markdown) 
        console.print(f":white_check_mark: [bold cyan]Archivo guardado:[/bold cyan] {filepath}")
    else:
        console.print(f":x: [bold red]No se pudo convertir la URL:[/bold red] {url}")
