import pandas as pd
from io import BytesIO

def extract_sections(content):
    lines = content.split('\n')

    accommodation_data = []
    auth_data = []
    events_data = []

    section = None

    for line in lines:
        line = line.strip()

        if line.startswith("Accommodation Data:"):
            section = 'accommodation'
            continue
        elif line.startswith("Auth Data:"):
            section = 'auth'
            continue
        elif line.startswith("Events Data:"):
            section = 'events'
            continue

        # Asignar datos a la sección correspondiente
        if section == 'accommodation' and line:
            accommodation_data.append(line)
        elif section == 'auth' and line:
            auth_data.append(line)
        elif section == 'events' and line:
            events_data.append(line)

    return accommodation_data, auth_data, events_data


def generate_excel(accommodation_data, auth_data, events_data):
    """
    Genera un archivo Excel con tres hojas (Accommodation, Auth, Events) y lo devuelve como un BytesIO.
    """
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')

    # Crear DataFrames para cada sección
    df_accommodation = pd.DataFrame(
        [x.split(" - ") for x in accommodation_data],
        columns=['Name', 'Location', 'Price', 'Status', 'Image URL']
    )
    df_auth = pd.DataFrame([x.split(" - ") for x in auth_data], columns=['Username', 'Email'])
    df_events = pd.DataFrame(
        [x.split(" - ") for x in events_data],
        columns=['Event Name', 'Date', 'Price', 'Status']
    )

    # Escribir los DataFrames en diferentes hojas del archivo Excel
    df_accommodation.to_excel(writer, sheet_name='Accommodation', index=False)
    df_auth.to_excel(writer, sheet_name='Auth', index=False)
    df_events.to_excel(writer, sheet_name='Events', index=False)

    # Cerrar el escritor para guardar el archivo
    writer.close()
    output.seek(0)

    return output
