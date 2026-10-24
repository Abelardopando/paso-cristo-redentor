import json
from datetime import datetime
from zoneinfo import ZoneInfo
import requests
import xml.etree.ElementTree as ET
import os

def extraer_estado_rss():
    chile_tz = ZoneInfo('America/Santiago')
    ahora = datetime.now(chile_tz)
    hora_actual_str = ahora.strftime('%d/%m/%Y %I:%M %p').replace('AM', 'a. m.').replace('PM', 'p. m.')

    # Cargar datos anteriores para respaldo y comparación de cambios
    old_data = {}
    if os.path.exists('status.json'):
        try:
            with open('status.json', 'r', encoding='utf-8') as f:
                old_data = json.load(f)
        except:
            pass

    old_resumen = old_data.get('resumen', '')
    old_hora_comunicado = old_data.get('hora_comunicado', hora_actual_str)

    # 🔗 REEMPLAZA ESTA LÍNEA CON TU ENLACE RSS REAL
    rss_url = "TU_URL_DE_RSS_AQUÍ" 
    
    nuevo_estado = "VERIFICANDO..."
    nuevo_resumen = "Sincronizando feed RSS de la cordillera..."
    vehiculos = "Consultando..."

    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(rss_url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            # Parsear el XML del RSS de forma nativa en Python
            root = ET.fromstring(response.content)
            item = root.find('.//item') # Toma la primera entrada (la más reciente)
            
            if item is not None:
                title = item.find('title').text if item.find('title'] is not None else ""
                # Si el campo title no está, intentamos con text directamente o description
                description = item.find('description').text if item.find('description') is not None else ""
                
                # Unimos título y descripción para tener el comunicado completo
                texto_completo = f"{title}\n\n{description}".strip()
                nuevo_resumen = texto_completo[:500] # Limitamos longitud visual
                
                texto_upper = texto_completo.upper()
                if "CERRADO" in texto_upper or "SUSPENDIDO" in texto_upper:
                    nuevo_estado = "CERRADO"
                    vehiculos = "Tránsito suspendido temporalmente"
                elif "ETAPAS" in texto_upper or "PARCIAL" in texto_upper or "RESTRICCIÓN" in texto_upper:
                    nuevo_estado = "ABIERTO - ETAPAS"
                    vehiculos = "Sujeto a restricciones por tramos"
                elif "HABILITADO" in texto_upper or "ABIERTO" in texto_upper:
                    nuevo_estado = "HABILITADO"
                    vehiculos = "Todo tipo de vehículos habilitados"
                else:
                    nuevo_estado = "INFORME OFICIAL DISPONIBLE"
                    vehiculos = "Verificar detalle en el reporte"
            else:
                nuevo_estado = "FEED VACÍO"
                nuevo_resumen = "El feed RSS respondió correctamente pero no contiene entradas recientes."
        else:
            raise Exception(f"Código HTTP {response.status_code}")

    except Exception as e:
        print(f"Aviso leyendo RSS: {e}")
        # Si hay un fallo de red puntual, mantenemos el último estado seguro conocido
        nuevo_estado = old_data.get('estado', 'ACTUALIZACIÓN PENDIENTE')
        nuevo_resumen = old_data.get('resumen', 'Reintentando conexión con el feed RSS.')
        vehiculos = old_data.get('vehiculos_permitidos', 'Pendiente')

    # Si el texto del comunicado cambió, actualizamos la hora del comunicado. Si es idéntico, la mantenemos.
    if nuevo_resumen.strip() != old_resumen.strip():
        hora_comunicado = hora_actual_str
    else:
        hora_comunicado = old_hora_comunicado

    estado_data = {
        "estado": nuevo_estado,
        "resumen": nuevo_resumen,
        "vehiculos_permitidos": vehiculos,
        "hora_comunicado": hora_comunicado,
        "ultima_sincronizacion": hora_actual_str
    }

    with open('status.json', 'w', encoding='utf-8') as f:
        json.dump(estado_data, f, ensure_ascii=False, indent=4)
    
    print(f"RSS procesado con éxito a las {hora_actual_str}")

if __name__ == "__main__":
    extraer_estado_rss()
