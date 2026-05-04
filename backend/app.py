from fastapi.responses import FileResponse
import os
import sqlite3
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = os.getenv('DB_PATH', './app.db')

class ThinClient(BaseModel):
    modelo: str
    marca: str
    categoria: str
    rendimiento_cpu: str
    ram: str
    almacenamiento: str
    precio_usd: float
    descripcion: str

class Waitlist(BaseModel):
    email: str

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS thin_clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            modelo TEXT,
            marca TEXT,
            categoria TEXT,
            rendimiento_cpu TEXT,
            ram TEXT,
            almacenamiento TEXT,
            precio_usd REAL,
            descripcion TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS waitlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    seed_data = [
        {"modelo": "Dell Wyse 5070", "marca": "Dell", "categoria": "Thin Client", "rendimiento_cpu": "Intel Celeron J4105", "ram": "4GB", "almacenamiento": "16GB eMMC", "precio_usd": 299, "descripcion": "Ideal para entornos de trabajo remoto con soporte para múltiples monitores."},
        {"modelo": "HP t640", "marca": "HP", "categoria": "Thin Client", "rendimiento_cpu": "AMD Ryzen 3", "ram": "8GB", "almacenamiento": "32GB SSD", "precio_usd": 399, "descripcion": "Ofrece un rendimiento potente y es compatible con aplicaciones de virtualización."},
        {"modelo": "IGEL UD3", "marca": "IGEL", "categoria": "Thin Client", "rendimiento_cpu": "Intel Celeron N3350", "ram": "4GB", "almacenamiento": "8GB Flash", "precio_usd": 249, "descripcion": "Diseñado para una fácil gestión y seguridad en la nube."},
        {"modelo": "Lenovo ThinkCentre M625", "marca": "Lenovo", "categoria": "Thin Client", "rendimiento_cpu": "AMD A6", "ram": "4GB", "almacenamiento": "16GB SSD", "precio_usd": 279, "descripcion": "Compacto y eficiente, ideal para espacios reducidos."},
        {"modelo": "NComputing RX300", "marca": "NComputing", "categoria": "Thin Client", "rendimiento_cpu": "ARM Cortex-A53", "ram": "2GB", "almacenamiento": "8GB", "precio_usd": 199, "descripcion": "Perfecto para entornos educativos y de bajo costo."},
        {"modelo": "Citrix HDX", "marca": "Citrix", "categoria": "Thin Client", "rendimiento_cpu": "Varía según el dispositivo", "ram": "4GB", "almacenamiento": "32GB", "precio_usd": 350, "descripcion": "Optimizado para Citrix, ideal para aplicaciones empresariales."},
        {"modelo": "Acer Chromebox CXI3", "marca": "Acer", "categoria": "Thin Client", "rendimiento_cpu": "Intel Core i3", "ram": "4GB", "almacenamiento": "32GB", "precio_usd": 329, "descripcion": "Versátil y fácil de usar, ideal para aplicaciones basadas en la web."},
        {"modelo": "ViewSonic SC-T25", "marca": "ViewSonic", "categoria": "Thin Client", "rendimiento_cpu": "ARM Cortex-A72", "ram": "4GB", "almacenamiento": "16GB", "precio_usd": 220, "descripcion": "Diseñado para entornos de trabajo colaborativo."},
        {"modelo": "Microsoft Surface Hub 2S", "marca": "Microsoft", "categoria": "Thin Client", "rendimiento_cpu": "Intel Core i5", "ram": "8GB", "almacenamiento": "128GB", "precio_usd": 899, "descripcion": "Ideal para reuniones y colaboración en equipo."},
        {"modelo": "ASUS Chromebox 3", "marca": "ASUS", "categoria": "Thin Client", "rendimiento_cpu": "Intel Celeron 3865U", "ram": "4GB", "almacenamiento": "32GB", "precio_usd": 249, "descripcion": "Compacto y eficiente, ideal para entornos de oficina."},
        {"modelo": "ZOTAC ZBOX CI329 Nano", "marca": "ZOTAC", "categoria": "Thin Client", "rendimiento_cpu": "Intel Celeron N4100", "ram": "4GB", "almacenamiento": "32GB eMMC", "precio_usd": 299, "descripcion": "Silencioso y de bajo consumo, ideal para aplicaciones ligeras."},
        {"modelo": "Terra 2000", "marca": "Terra", "categoria": "Thin Client", "rendimiento_cpu": "Intel Atom", "ram": "2GB", "almacenamiento": "8GB", "precio_usd": 199, "descripcion": "Ideal para entornos educativos y de bajo costo."}
    ]
    for item in seed_data:
        cursor.execute('''
            INSERT OR IGNORE INTO thin_clients (modelo, marca, categoria, rendimiento_cpu, ram, almacenamiento, precio_usd, descripcion)
            VALUES (:modelo, :marca, :categoria, :rendimiento_cpu, :ram, :almacenamiento, :precio_usd, :descripcion)
        ''', item)
    conn.commit()
    conn.close()

@app.on_event("startup")
def startup():
    init_db()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/waitlist")
def add_to_waitlist(waitlist: Waitlist):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('INSERT INTO waitlist (email) VALUES (?)', (waitlist.email,))
    conn.commit()
    total = cursor.execute('SELECT COUNT(*) FROM waitlist').fetchone()[0]
    conn.close()
    return {"ok": True, "total": total}

@app.get("/waitlist/count")
def waitlist_count():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    count = cursor.execute('SELECT COUNT(*) FROM waitlist').fetchone()[0]
    conn.close()
    return {"count": count}

@app.get("/thin_clients")
def get_thin_clients():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    clients = cursor.execute('SELECT * FROM thin_clients').fetchall()
    conn.close()
    return [dict(client) for client in clients]

@app.get("/thin_clients/{client_id}")
def get_thin_client(client_id: int):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    client = cursor.execute('SELECT * FROM thin_clients WHERE id = ?', (client_id,)).fetchone()
    conn.close()
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    return dict(client)

@app.post("/thin_clients")
def create_thin_client(client: ThinClient):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO thin_clients (modelo, marca, categoria, rendimiento_cpu, ram, almacenamiento, precio_usd, descripcion)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (client.modelo, client.marca, client.categoria, client.rendimiento_cpu, client.ram, client.almacenamiento, client.precio_usd, client.descripcion))
    conn.commit()
    conn.close()
    return {"ok": True}

@app.put("/thin_clients/{client_id}")
def update_thin_client(client_id: int, client: ThinClient):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE thin_clients SET modelo = ?, marca = ?, categoria = ?, rendimiento_cpu = ?, ram = ?, almacenamiento = ?, precio_usd = ?, descripcion = ?
        WHERE id = ?
    ''', (client.modelo, client.marca, client.categoria, client.rendimiento_cpu, client.ram, client.almacenamiento, client.precio_usd, client.descripcion, client_id))
    conn.commit()
    conn.close()
    return {"ok": True}

@app.delete("/thin_clients/{client_id}")
def delete_thin_client(client_id: int):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('DELETE FROM thin_clients WHERE id = ?', (client_id,))
    conn.commit()
    conn.close()
    return {"ok": True}

port = int(os.getenv('PORT', 8001))
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)

@app.get("/", include_in_schema=False)
@app.get("/{_spa_path:path}", include_in_schema=False)
async def _serve_spa(_spa_path: str = ""):
    import os as _os
    _idx = _os.path.join(_os.path.dirname(__file__), "..", "frontend", "index.html")
    if not _os.path.exists(_idx):
        _idx = "frontend/index.html"
    if _os.path.exists(_idx):
        return FileResponse(_idx, media_type="text/html")
    from fastapi.responses import JSONResponse
    return JSONResponse({"error": "frontend not found"}, status_code=404)
