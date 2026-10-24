import json
from datetime import datetime
from zoneinfo import ZoneInfo
import requests
from bs4 import BeautifulSoup
import os

def extraer_estado_paso():
    chile_tz = ZoneInfo('America/Santiago')
    ahora = datetime.now(chile_tz)
    hora_actual_str = ahora.strftime('%d/%m/%Y %I:%M %p').replace('AM', 'a. m.').replace('PM', 'p. m.')

    # Cargar datos anteriores para comparar si el comunicado cambió
    old_data = {}
    if os.path.exists('status.json'):
        try:
            with open('status.json', 'r', encoding='utf-8') as f:
                old_data = json.load(f)
        except:
            pass

    old_resumen = old_data.get('resumen', '')
    old_hora_comunicado = old_data.get('hora_comunicado', hora_actual_str)

    # URL oficial de la Unidad de Pasos Fronterizos
    url = "https://pasosfronterizos.mininterior.cl/"
    
    nuevo_estado = "VERIFICANDO..."
    nuevo_resumen = "Sincronizando y analizando el último reporte oficial..."
    vehiculos = "Consultando..."

    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            texto_encontrado = ""
            elementos = soup.find_all(['div', 'article', 'section', 'p', 'li', 'span'])
            
            for el in elementos:
                texto = el.get_text(strip=True)
                if "CRISTO REDENTOR" in texto.upper() or "LIBERTADORES" in texto.upper():
                    if len(texto) > 40:
                        texto_encontrado = texto
                        break
            
            if texto_encontrado:
                nuevo_resumen = texto_encontrado[:500]
                texto_upper = texto_encontrado.upper()
                if "CERRADO" in texto_upper or "SUSPENDIDO" in texto_upper:
                    nuevo_estado = "CERRADO"
                    vehiculos = "Tránsito suspendido temporalmente"
                elif "ETAPAS" in texto_upper or "PARCIAL" in texto_upper or "RESTRICCIÓN" in texto_upper:
                    nuevo_estado = "ABIERTO - ETAPAS"
                    vehiculos = "Sujeto a restricciones por tramos (Ver reporte)"
                elif "HABILITADO" in texto_upper or "ABIERTO" in texto_upper:
                    nuevo_estado = "HABILITADO"
                    vehiculos = "Todo tipo de vehículos habilitados"
                else:
                    nuevo_estado = "INFORME OFICIAL DISPONIBLE"
                    vehiculos = "Verificar detalle en el reporte"
            else:
                nuevo_estado = "SITIO EN LÍNEA"
                nuevo_resumen = "Conexión exitosa con Pasos Fronterizos. Esperando actualización del boletín diario."
                vehiculos = "Sin información de vehículos"
        else:
            nuevo_estado = "REVISAR FUENTE OFICIAL"
            nuevo_resumen = f"La plataforma gubernamental respondió con estado HTTP {response.status_code}."
            vehiculos = "No disponible"

    except Exception as e:
        print(f"Error en la extracción: {e}")
        # Si falla la red, mantenemos el último estado seguro conocido
        nuevo_estado = old_data.get('estado', 'ACTUALIZACIÓN PENDIENTE')
        nuevo_resumen = old_data.get('resumen', 'Reintentando conexión con servidores oficiales.')
        vehiculos = old_data.get('vehiculos_permitidos', 'Pendiente')

    # LÓGICA CLAVE: Si el texto del comunicado es exactamente igual al anterior, 
    # MANTENEMOS la hora del comunicado original. Solo cambia si la autoridad emite un texto nuevo.
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
    
    print(f"Verificación completada a las {hora_actual_str} (Comunicado emitido a las {hora_comunicado})")

if __name__ == "__main__":
    extraer_estado_paso()
