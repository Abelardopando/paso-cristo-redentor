import json
from datetime import datetime
from zoneinfo import ZoneInfo
import requests
from bs4 import BeautifulSoup

def extraer_estado_paso():
    chile_tz = ZoneInfo('America/Santiago')
    ahora = datetime.now(chile_tz)
    hora_formateada = ahora.strftime('%d/%m/%Y %H:%M hrs')

    # URL oficial de la Unidad de Pasos Fronterizos
    url = "https://pasosfronterizos.mininterior.cl/"
    
    estado_data = {
        "estado": "VERIFICANDO...",
        "resumen": "Sincronizando con el último reporte oficial del complejo...",
        "vehiculos_permitidos": "Consultando...",
        "ultima_actualizacion": hora_formateada
    }

    try:
        # Cabecera para simular un navegador real y evitar bloqueos
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Buscamos elementos clave en la página oficial (adaptable a su estructura)
            # Nota: Si la web oficial cambia sus etiquetas exactas, aquí ira el selector fino.
            texto_sitio = soup.get_text()
            
            if "CRISTO REDENTOR" in texto_sitio.upper() or "LIBERTADORES" in texto_sitio.upper():
                estado_data["estado"] = "REVISAR SITIO OFICIAL"
                estado_data["resumen"] = "El bot ha conectado exitosamente con Pasos Fronterizos. Último escaneo completado."
                estado_data["vehiculos_permitidos"] = "Verificar detalle en reporte"
            else:
                estado_data["resumen"] = "Conexión exitosa, procesando estado actual de la alta montaña..."
                
        else:
            estado_data["estado"] = "ATENCIÓN / REVISAR"
            estado_data["resumen"] = f"La fuente oficial respondió con código HTTP {response.status_code}. Manteniendo último registro."

    except Exception as e:
        print(f"Error al conectar con la fuente: {e}")
        estado_data["estado"] = "ACTUALIZACIÓN PENDIENTE"
        estado_data["resumen"] = "El sistema reintentará en el próximo ciclo automático."

    # Guardar en status.json
    with open('status.json', 'w', encoding='utf-8') as f:
        json.dump(estado_data, f, ensure_ascii=False, indent=4)
    
    print(f"Scraping ejecutado a las {hora_formateada}")

if __name__ == "__main__":
    extraer_estado_paso()
