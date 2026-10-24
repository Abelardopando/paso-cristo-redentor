import json
from datetime import datetime
from zoneinfo import ZoneInfo
import requests
from bs4 import BeautifulSoup

def extraer_estado_paso():
    chile_tz = ZoneInfo('America/Santiago')
    ahora = datetime.now(chile_tz)
    hora_formateada = ahora.strftime('%d/%m/%Y %I:%M %p').replace('AM', 'a. m.').replace('PM', 'p. m.')

    # URL oficial de la Unidad de Pasos Fronterizos
    url = "https://pasosfronterizos.mininterior.cl/"
    
    estado_data = {
        "estado": "VERIFICANDO...",
        "resumen": "Sincronizando y analizando el último reporte oficial del complejo...",
        "vehiculos_permitidos": "Consultando...",
        "ultima_actualizacion": hora_formateada
    }

    try:
        # Simulamos un navegador real para evitar bloqueos del servidor gubernamental
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            texto_encontrado = ""
            # Buscamos en los contenedores habituales de la web oficial
            elementos = soup.find_all(['div', 'article', 'section', 'p', 'li', 'span'])
            
            for el in elementos:
                texto = el.get_text(strip=True)
                # Buscamos menciones al paso internacional
                if "CRISTO REDENTOR" in texto.upper() or "LIBERTADORES" in texto.upper():
                    if len(texto) > 40: # Evitamos títulos cortos sueltos
                        texto_encontrado = texto
                        break
            
            if texto_encontrado:
                estado_data["resumen"] = texto_encontrado[:500] # Guardamos el comunicado oficial real
                
                # Lógica de interpretación automática de estado según el texto oficial
                texto_upper = texto_encontrado.upper()
                if "CERRADO" in texto_upper or "SUSPENDIDO" in texto_upper:
                    estado_data["estado"] = "CERRADO"
                    estado_data["vehiculos_permitidos"] = "Tránsito suspendido temporalmente"
                elif "ETAPAS" in texto_upper or "PARCIAL" in texto_upper or "RESTRICCIÓN" in texto_upper:
                    estado_data["estado"] = "ABIERTO - ETAPAS"
                    estado_data["vehiculos_permitidos"
                    ] = "Sujeto a restricciones por tramos (Ver reporte)"
                elif "HABILITADO" in texto_upper or "ABIERTO" in texto_upper:
                    estado_data["estado"] = "HABILITADO"
                    estado_data["vehiculos_permitidos"] = "Todo tipo de vehículos habilitados"
                else:
                    estado_data["estado"] = "INFORME OFICIAL DISPONIBLE"
                    estado_data["vehiculos_permitidos"] = "Verificar detalle en el reporte"
            else:
                estado_data["estado"] = "SITIO EN LÍNEA"
                estado_data["resumen"] = "Conexión exitosa con Pasos Fronterizos. Esperando actualización del boletín diario del complejo."
                estado_data["vehiculos_permitidos"] = "Sin información de vehículos aún"
                
        else:
            estado_data["estado"] = "REVISAR FUENTE OFICIAL"
            estado_data["resumen"] = f"La plataforma gubernamental respondió con estado HTTP {response.status_code}. El sistema reintentará."
            estado_data["vehiculos_permitidos"] = "No disponible"

    except Exception as e:
        print(f"Error en la extracción: {e}")
        estado_data["estado"] = "ACTUALIZACIÓN PENDIENTE"
        estado_data["resumen"] = "El bot está reintentando la conexión con los servidores oficiales de la cordillera."
        estado_data["vehiculos_permitidos"] = "Pendiente de lectura"

    # Guardar en status.json para que la web lo lea al instante
    with open('status.json', 'w', encoding='utf-8') as f:
        json.dump(estado_data, f, ensure_ascii=False, indent=4)
    
    print(f"Scraping inteligente completado a las {hora_formateada}")

if __name__ == "__main__":
    extraer_estado_paso()
