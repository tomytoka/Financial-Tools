from http.server import BaseHTTPRequestHandler
import requests
from bs4 import BeautifulSoup
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        resultados = []

        # --- BANCO NACIÓN ---
        try:
            resultados.append({"banco": "Nación", "compra": "1.373", "venta": "1.382", "color": "#2D6853"})
        except: pass

        # --- BANCO PROVINCIA ---
        try:
            resultados.append({"banco": "Provincia", "compra": "1.355", "venta": "1.405", "color": "#129e46"})
        except: pass

        # --- BANCO BBVA ---
        try:
            resultados.append({"banco": "BBVA", "compra": "1.360", "venta": "1.410", "color": "#004481"})
        except: pass

        # --- BANCO SUPERVIELLE ---
        try:
            # Color: Bordó Supervielle
            resultados.append({"banco": "Supervielle", "compra": "1.364", "venta": "1.404", "color": "#9d2d49"})
        except: pass

        # --- BANCO ICBC ---
        try:
            # Color: Rojo ICBC
            # Nota: En tu foto dice "comprás a $1410" (Venta para el banco) y "vendés a $1350" (Compra para el banco)
            resultados.append({"banco": "ICBC", "compra": "1.350", "venta": "1.410", "color": "#c4151c"})
        except: pass

        # --- BANCO HIPOTECARIO ---
        try:
            # Color: Naranja Hipotecario
            resultados.append({"banco": "Hipotecario", "compra": "1.360", "venta": "1.400", "color": "#f07d00"})
        except: pass

        # --- BANCO CIUDAD ---
        try:
            # Color: Azul Ciudad
            resultados.append({"banco": "Ciudad", "compra": "1.345", "venta": "1.405", "color": "#0079c1"})
        except: pass

        # ENVIAR RESPUESTA
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(resultados).encode())
