import os
import json
import feedparser
import google.generativeai as genai

# Enlace RSS puente de @UPFronterizos
URL_RSS = "https://rss.app/feeds/GnQwSF23WseTfEtQ.xml"

# Clave de la Inteligencia Artificial (se configurará en los permisos de GitHub)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

def obtener_ultimo_reporte():
    try:
        feed = feedparser.parse(URL_RSS)
        # Toma la última publicación
        ultimo_informe = feed.entries[0].summary
        return ultimo_informe
    except Exception as e:
        print(f"Error al leer el feed: {e}")
        return None

def procesar_con_gemini(texto_informe):
    model = genai.GenerativeModel("gemini-2.5-flash")
    
    prompt = f"""
    Analiza este reporte de Pasos Fronterizos y extrae la información sobre el Paso Cristo Redentor / Los Libertadores.
    Texto del reporte: "{texto_informe}"

    Devuelve ÚNICAMENTE un JSON válido con esta estructura:
    {{
      "estado": "Abierto" o "Cerrado",
      "motivo": "Explicación breve de la causa o estado",
      "horario": "Horario de atención o apertura",
      "vehiculos": "Todos", "Solo camiones", "Solo particulares" o "Ninguno",
      "resumen": "Resumen ejecutivo en máximo 10 palabras"
    }}
    """

    respuesta = model.generate_content(
        prompt,
        generation_config={"response_mime_type": "application/json"}
    )
    return json.loads(respuesta.text)

def main():
    print("Leyendo último reporte...")
    texto = obtener_ultimo_reporte()
    if texto:
        datos = procesar_con_gemini(texto)
        print("Datos procesados por IA:", datos)
        
        # Guarda el resultado en un archivo status.json
        with open("status.json", "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
