import json
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import requests
import xml.etree.ElementTree as ET
import os
from email.utils import parsedate_to_datetime
from bs4 import BeautifulSoup

def obtener_tiempo_relativo(pub_date_str):
    if not pub_date_str:
        return "Hace un momento"
    try:
        chile_tz = ZoneInfo('America/Santiago')
        ahora_chile = datetime.now(chile_tz)
        
        pub_dt = None
        try:
            pub_dt = parsedate_to_datetime(pub_date_str)
        except Exception:
            pass
            
        if not pub_dt:
            try:
                clean_date = pub_date_str.replace('Z', '+00:00')
                pub_dt = datetime.fromisoformat(clean_date)
            except Exception:
                pass
                
        if not pub_dt:
            return "Hace un momento"
            
        if pub_dt.tzinfo is None:
            pub_dt = pub_dt.replace(tzinfo=timezone.utc)
            
        pub_dt_chile = pub_dt.astimezone(chile_tz)
        
        diff = ahora_chile - pub_dt_chile
        segundos = diff.total_seconds()
        
        if segundos < 0:
            return "Hace un momento"
        elif segundos < 60:
            return "Hace un momento"
        elif segundos < 3600:
            minutos = int(segundos // 60)
            return f"Hace {minutos} min" if minutos == 1 else f"Hace {minutos} minutos"
        elif segundos < 86400:
            horas = int(segundos // 3600)
            return f"Hace {horas} hora" if horas == 1 else f"Hace {horas} horas"
        else:
            dias = int(segundos // 86400)
            return f"Hace {dias} día" if dias == 1 else f"Hace {dias} días"
    except Exception as e:
        print(f"Error calculando tiempo relativo: {e}")
        return "Hace un momento"

def extraer_estado_rss():
    chile_tz = ZoneInfo('America/Santiago')
    ahora = datetime.now(chile_tz)
    hora_actual_str = ahora.strftime('%d/%m/%Y %I:%M %p').replace('AM', 'a. m.').replace('PM', 'p. m.')

    old_data = {}
    if os.path.exists('status.json'):
        try:
            with open('status.json', 'r', encoding='utf-8') as f:
                old_data = json.load(f)
        except:
            pass

    rss_url = "https://rss.app/feeds/GnQwSF23WseTfEtQ.xml"
    
    nuevo_estado = old_data.get('estado', 'VERIFICANDO...')
    nuevo_resumen = old_data.get('resumen', 'Sincronizando feed RSS...')
    vehiculos = old_data.get('vehiculos_permitidos', 'Consultando...')
    tiempo_relativo = old_data.get('tiempo_comunicado', 'Hace un momento')

    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(rss_url, headers=headers, timeout=20)
        
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            items = root.findall('.//item')
            
            item_encontrado = None
            
            # FILTRO INTELIGENTE: Buscamos en el historial del feed el post que hable específicamente de Cristo Redentor
            for item in items:
                title_el = item.find('title')
                desc_el = item.find('description')
                
                title = title_el.text if title_el is not None and title_el.text else ""
                description = desc_el.text if desc_el.text is not None and desc_el.text else ""
                
                texto_control = f"{title} {description}".upper()
                
                if "CRISTO REDENTOR" in texto_control or "LIBERTADORES" in texto_control:
                    item_encontrado = item
                    break # Encontramos el comunicado correcto, salimos del ciclo
            
            # Si no encontró ninguno específico en el lote actual, tomamos el primero como respaldo
            if not item_encontrado and items:
                item_encontrado = items[0]

            if item_encontrado is not None:
                title_el = item_encontrado.find('title')
                desc_el = item_encontrado.find('description')
                pub_date_el = item_encontrado.find('pubDate')
                
                title = title_el.text if title_el is not None and title_el.text else ""
                description = desc_el.text if desc_el.text is not None and desc_el.text else ""
                pub_date_raw = pub_date_el.text if pub_date_el is not None and pub_date_el.text else ""
                
                description_limpia = BeautifulSoup(description, 'html.parser').get_text(strip=True) if description else ""
                
                if description_limpia and len(description_limpia) > len(title):
                    texto_completo = description_limpia
                else:
                    texto_completo = title
                
                if texto_completo:
                    nuevo_resumen = texto_completo
                    tiempo_relativo = obtener_tiempo_relativo(pub_date_raw)
                    
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
            print(f"Advertencia: Servidor RSS respondió con código {response.status_code}")

    except Exception as e:
        print(f"Aviso procesando RSS: {e}")

    estado_data = {
        "estado": nuevo_estado,
        "resumen": nuevo_resumen,
        "vehiculos_permitidos": vehiculos,
        "tiempo_comunicado": tiempo_relativo,
        "ultima_sincronizacion": hora_actual_str
    }

    with open('status.json', 'w', encoding='utf-8') as f:
        json.dump(estado_data, f, ensure_ascii=False, indent=4)
    
    print(f"Sincronización con filtro completada con éxito a las {hora_actual_str}")

if __name__ == "__main__":
    extraer_estado_rss()
