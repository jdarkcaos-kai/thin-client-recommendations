from fastapi.responses import FileResponse
import os
import sqlite3
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict

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
    nombre: str
    marca: str
    categoria: str
    precio: float
    rendimiento: str
    procesador: str
    ram: str
    almacenamiento: str
    sistema_operativo: str
    descripcion: str

class WaitlistItem(BaseModel):
    email: str

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS thin_clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            marca TEXT,
            categoria TEXT,
            precio REAL,
            rendimiento TEXT,
            procesador TEXT,
            ram TEXT,
            almacenamiento TEXT,
            sistema_operativo TEXT,
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
    cursor.execute('''
        INSERT INTO thin_clients (nombre, marca, categoria, precio, rendimiento, procesador, ram, almacenamiento, sistema_operativo, descripcion)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', ("HP t640", "HP", "Thin Client", 299.99, "Alto", "AMD Ryzen 3", "4GB", "32GB eMMC", "Windows 10 IoT", "Ideal para entornos de trabajo colaborativos con alta demanda gráfica."))
    cursor.execute('''
        INSERT INTO thin_clients (nombre, marca, categoria, precio, rendimiento, procesador, ram, almacenamiento, sistema_operativo, descripcion)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', ("Dell Wyse 5070", "Dell", "Thin Client", 329.00, "Medio", "Intel Celeron", "8GB", "16GB Flash", "ThinOS", "Versátil y seguro, adecuado para diversas aplicaciones empresariales."))
    cursor.execute('''
        INSERT INTO thin_clients (nombre, marca, categoria, precio, rendimiento, procesador, ram, almacenamiento, sistema_operativo, descripcion)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', ("Lenovo ThinkCentre M625", "Lenovo", "Thin Client", 249.99, "Bajo", "AMD A6", "4GB", "500GB HDD", "Windows 10 Pro", "Compacto y eficiente para tareas básicas."))
    conn.commit()
    conn.close()

@app.on_event("startup")
def startup_event():
    init_db()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/waitlist")
def add_to_waitlist(item: WaitlistItem):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('INSERT INTO waitlist (email) VALUES (?)', (item.email,))
    conn.commit()
    total = cursor.lastrowid
    conn.close()
    return {"ok": True, "total": total}

@app.get("/waitlist/count")
def waitlist_count():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) as count FROM waitlist')
    count = cursor.fetchone()['count']
    conn.close()
    return {"count": count}

@app.get("/thin_clients", response_model=List[ThinClient])
def get_thin_clients():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM thin_clients')
    clients = cursor.fetchall()
    conn.close()
    return [dict(client) for client in clients]

@app.get("/thin_clients/{client_id}", response_model=ThinClient)
def get_thin_client(client_id: int):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM thin_clients WHERE id = ?', (client_id,))
    client = cursor.fetchone()
    conn.close()
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    return dict(client)

@app.post("/thin_clients", response_model=ThinClient)
def create_thin_client(client: ThinClient):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO thin_clients (nombre, marca, categoria, precio, rendimiento, procesador, ram, almacenamiento, sistema_operativo, descripcion)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (client.nombre, client.marca, client.categoria, client.precio, client.rendimiento, client.procesador, client.ram, client.almacenamiento, client.sistema_operativo, client.descripcion))
    conn.commit()
    client_id = cursor.lastrowid
    conn.close()
    client.id = client_id
    return client

@app.put("/thin_clients/{client_id}", response_model=ThinClient)
def update_thin_client(client_id: int, client: ThinClient):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE thin_clients SET nombre = ?, marca = ?, categoria = ?, precio = ?, rendimiento = ?, procesador = ?, ram = ?, almacenamiento = ?, sistema_operativo = ?, descripcion = ?
        WHERE id = ?
    ''', (client.nombre, client.marca, client.categoria, client.precio, client.rendimiento, client.procesador, client.ram, client.almacenamiento, client.sistema_operativo, client.descripcion, client_id))
    conn.commit()
    conn.close()
    return client

@app.delete("/thin_clients/{client_id}")
def delete_thin_client(client_id: int):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('DELETE FROM thin_clients WHERE id = ?', (client_id,))
    conn.commit()
    conn.close()
    return {"ok": True}

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
