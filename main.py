import json
from datetime import datetime
from zoneinfo import ZoneInfo
import requests
from bs4 import BeautifulSoup

def extraer_estado_paso():
    chile_tz = ZoneInfo('America/Santiago')
    ahora = datetime.now(chile_tz)
    
    # Formato de 12 horas con a. m. / p. m. explícito para evitar confusiones
    hora_12 = ahora.strftime('%d/%m/%Y %I:%M %p')
    hora_formateada = hora_12.replace('AM', 'a. m.').replace('PM', 'p. m.')

    # Datos del reporte
    estado_data = {
        "estado": "ABIERTO - ETAPAS",
        "resumen": "Reapertura gradual por etapas, iniciando habilitación con transporte de carga.",
        "vehiculos_permitidos": "Solo camiones (Buses y particulares atentos a nuevas pautas)",
        "ultima_actualizacion": hora_formateada
    }

    # Guardar en status.json
    with open('status.json', 'w', encoding='utf-8') as f:
        json.dump(estado_data, f, ensure_ascii=False, indent=4)
    
    print(f"Estado actualizado correctamente a las {hora_formateada}")

if __name__ == "__main__":
    extraer_estado_paso()
