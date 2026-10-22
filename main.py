import os
import json
import feedparser
import google.generativeai as genai

# Configuración de la API de Gemini
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# URL del feed RSS
RSS_URL = "https://rss.app/feeds/GnQwSF23WseTfEtQ.xml"

def obtener_ultimo_comunicado():
    feed = feedparser.parse(RSS_URL)
    
    # Buscar el reporte más reciente sobre Cristo Redentor / Los Libertadores
    for entry in feed.entries:
        texto = entry.title + " " + getattr(entry, "summary", "")
        texto_lower = texto.lower()
        if "cristo redentor" in texto_lower or "los libertadores" in texto_lower:
            return texto.strip()
            
    # Si no hay uno específico en las últimas entradas, tomar la primera
    if feed.entries:
        return feed.entries[0].title
    return None

def analizar_con_gemini(comunicado):
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""
    Analiza el siguiente comunicado oficial sobre el Paso Internacional Cristo Redentor / Los Libertadores y devuelve ÚNICAMENTE un objeto JSON válido sin texto adicional ni formato Markdown (sin ```json):

    Comunicado: "{comunicado}"

    Estructura JSON requerida:
    {{
      "estado": "HABILITADO" o "CERRADO" o "HABILITADO POR ETAPAS",
      "resumen": "Resumen conciso y claro en máximo 3 viñetas o líneas cortas sobre los horarios, etapas o motivo del cierre.",
      "vehiculos_permitidos": "Especifica exactamente qué vehículos pueden circular (ej: 'Solo Camiones de Carga', 'Todo tipo de vehículos', 'Ninguno (Paso Cerrado)', 'Particulares y Buses')",
      "ultima_actualizacion": "Indica la fecha y hora o momento del reporte según el texto"
    }}
    """
    
    response = model.generate_content(prompt)
    
    # Limpiar respuesta por si incluye comillas de bloque de código
    cleaned_text = response.text.replace("```json", "").replace("```", "").strip()
    return json.loads(cleaned_text)

def main():
    comunicado = obtener_ultimo_comunicado()
    
    if not comunicado:
        print("No se encontraron comunicados recientes.")
        return

    print(f"Comunicado encontrado: {comunicado}")
    
    try:
        datos = analizar_con_gemini(comunicado)
        
        # Guardar resultado en status.json
        with open("status.json", "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
            
        print("status.json actualizado exitosamente:")
        print(json.dumps(datos, ensure_ascii=False, indent=2))
        
    except Exception as e:
        print(f"Error al procesar con Gemini: {e}")

if __name__ == "__main__":
    main()
