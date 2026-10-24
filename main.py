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

    # Cargar datos anteriores para respaldo seguro
    old_data = {}
    if os.path.exists('status.json'):
        try:
            with open('status.json', 'r', encoding='utf-8') as f:
                old_data = json.load(f)
        except:
            pass

    old_resumen = old_data.get('resumen', '')
    old_hora_comunicado = old_data.get('hora_comunicado', hora_actual_str)

    rss_url = "https://rss.app/feeds/GnQwSF23WseTfEtQ.xml"
    
    # Valores por defecto basados en el último estado conocido
    nuevo_estado = old_data.get('estado', 'VERIFICANDO...')
    nuevo_resumen = old_data.get('resumen', 'Sincronizando feed RSS...')
    vehiculos = old_data.get('vehiculos_permitidos', 'Consultando...')

    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(rss_url, headers=headers, timeout=20)
        
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            item = root.find('.//item')
            
            if item is not None:
                title_el = item.find('title')
                desc_el = item.find('description')
                
                title = title_el.text if title_el is not None and title_el.text else ""
                description = desc_el.text if desc_el.text is not None and desc_el.text else ""
                
                texto_completo = f"{title}\n\n{description}".strip()
                if texto_completo:
                    nuevo_resumen = texto_completo[:500]
                    
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
            print(f"Advertencia: El servidor RSS respondió con código {response.status_code}")

    except Exception as e:
        print(f"Aviso menor procesando RSS: {e}")

    # Si el texto cambió, actualizamos la hora del comunicado. Si es igual, la preservamos.
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
    
    print(f"Ejecución finalizada con éxito a las {hora_actual_str}")

if __name__ == "__main__":
    extraer_estado_rss()
