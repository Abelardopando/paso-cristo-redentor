import json
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import requests
import os
from bs4 import BeautifulSoup

def obtener_tiempo_relativo(pub_date_str):
    if not pub_date_str:
        return "Hace un momento"
    try:
        chile_tz = ZoneInfo('America/Santiago')
        ahora_chile = datetime.now(chile_tz)
        
        pub_dt = None
        try:
            from email.utils import parsedate_to_datetime
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

def analizar_vehiculos_y_restricciones(texto_upper):
    """Interpreta si hay restricciones de vehículos (camiones, autos, cadenas, etc.)"""
    detalle_vehiculos = "Todo tipo de vehículos habilitados"
    
    es_solo_camiones = "SOLO CAMIONES" in texto_upper or ("CAMIONES" in texto_upper and "AUTOS" not in texto_upper and "PARTICULARES" not in texto_upper)
    tiene_cadenas = "CADENAS" in texto_upper or "PORTACIÓN OBLIGATORIA" in texto_upper
    
    if es_solo_camiones:
        detalle_vehiculos = "Habilitado exclusivamente para transporte de cargas"
    elif "ÓMNIBUS" in texto_upper and "PARTICULARES" not in texto_upper:
        detalle_vehiculos = "Habilitado para buses y cargas (verificar particulares)"
    elif tiene_cadenas:
        detalle_vehiculos = "Habilitado con portación obligatoria de cadenas"
    
    return detalle_vehiculos

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

    # Usamos una fuente directa alternativa o el servicio web oficial que prefieras consultar
    fuente_url = "https://twitter.com/UPFronterizos" # O la url directa de respaldo que uses
    
    nuevo_estado = old_data.get('estado', 'VERIFICANDO...')
    nivel_alerta = old_data.get('nivel_alerta', 'verde')
    nuevo_resumen = old_data.get('resumen', 'Esperando el último reporte oficial del Paso Cristo Redentor...')
    vehiculos = old_data.get('vehiculos_permitidos', 'Consultando...')
    tiempo_relativo = old_data.get('tiempo_comunicado', 'Hace un momento')

    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(fuente_url, headers=headers, timeout=20)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Lógica adaptada para extraer los textos de la página directamente con BeautifulSoup
            textos_encontrados = []
            for p in soup.find_all(['p', 'div', 'article']):
                texto = p.get_text(strip=True)
                if "CRISTO REDENTOR" in texto.upper() or "LIBERTADORES" in texto.upper():
                    textos_encontrados.append(texto)
            
            if textos_encontrados:
                texto_completo = textos_encontrados[0]
                nuevo_resumen = texto_completo
                tiempo_relativo = "Hace un momento"
                
                texto_upper = texto_completo.upper()
                vehiculos = analizar_vehiculos_y_restricciones(texto_upper)
                
                if "CERRADO" in texto_upper or "SUSPENDIDO" in texto_upper or "INTRANSITABLE" in texto_upper:
                    nuevo_estado = "CERRADO"
                    nivel_alerta = "rojo"
                    vehiculos = "Tránsito suspendido temporalmente"
                elif "OBSERVACIONES" in texto_upper or "PRECAUCIÓN" in texto_upper or "RESTRICCIÓN" in texto_upper or "PARCIAL" in texto_upper or "ETAPAS" in texto_upper or "CADENAS" in texto_upper:
                    nuevo_estado = "HABILITADO CON OBSERVACIONES"
                    nivel_alerta = "amarillo"
                elif "HABILITADO" in texto_upper or "ABIERTO" in texto_upper:
                    nuevo_estado = "HABILITADO"
                    nivel_alerta = "verde"
                else:
                    nuevo_estado = "INFORME OFICIAL DISPONIBLE"
                    nivel_alerta = "amarillo"
            else:
                print("No se encontraron menciones recientes. Manteniendo último estado válido.")
                nuevo_estado = old_data.get('estado', 'HABILITADO')
                nivel_alerta = old_data.get('nivel_alerta', 'verde')
                nuevo_resumen = old_data.get('resumen', 'Monitoreo activo. Sin nuevos reportes de la autoridad.')
                vehiculos = old_data.get('vehiculos_permitidos', 'Verificar restricciones')
                tiempo_relativo = old_data.get('tiempo_comunicado', 'Hace un momento')
        else:
            print(f"Advertencia: El servidor respondió con código {response.status_code}")

    except Exception as e:
        print(f"Aviso procesando scraping: {e}")

    estado_data = {
        "estado": nuevo_estado,
        "nivel_alerta": nivel_alerta,
        "resumen": nuevo_resumen,
        "vehiculos_permitidos": vehiculos,
        "tiempo_comunicado": tiempo_relativo,
        "ultima_sincronizacion": hora_actual_str
    }

    with open('status.json', 'w', encoding='utf-8') as f:
        json.dump(estado_data, f, ensure_ascii=False, indent=4)
    
    print(f"Sincronización y análisis completados con éxito a las {hora_actual_str}")

if __name__ == "__main__":
    extraer_estado_rss()
