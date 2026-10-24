import json
from datetime import datetime
from zoneinfo import ZoneInfo

def actualizar_estado():
    # Zona horaria oficial de Chile usando la librería nativa de Python
    chile_tz = ZoneInfo('America/Santiago')
    ahora = datetime.now(chile_tz)
    
    # Formato legible: Ej. "24/10/2026 15:30 hrs"
    hora_formateada = ahora.strftime('%d/%m/%Y %H:%M hrs')

    # Datos del reporte
    data = {
        "estado": "ABIERTO - ETAPAS",
        "resumen": "Reapertura gradual por etapas, iniciando habilitación con transporte de carga.",
        "vehiculos_permitidos": "Solo camiones (Buses y particulares atentos a nuevas pautas)",
        "ultima_actualizacion": hora_formateada
    }

    # Guardar en status.json
    with open('status.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    print(f"Estado actualizado correctamente a las {hora_formateada}")

if __name__ == "__main__":
    actualizar_estado()
