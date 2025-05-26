import sqlite3
import re
from datetime import datetime

def init_db():
    conn = sqlite3.connect("core_db.db")
    cursor = conn.cursor()

    # Mensagens (histórico IA)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            role TEXT,
            content TEXT
        )
    """)

    # Transações financeiras
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            tipo TEXT,
            descricao TEXT,
            categoria TEXT,
            valor REAL,
            data TEXT
        )
    """)

    conn.commit()
    conn.close()

def save_message(user_id, role, content):
    conn = sqlite3.connect("core_db.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (user_id, role, content) VALUES (?, ?, ?)", (user_id, role, content))
    conn.commit()
    conn.close()

def get_user_history(user_id, max_messages=10):
    conn = sqlite3.connect("core_db.db")
    cursor = conn.cursor()
    cursor.execute("SELECT role, content FROM messages WHERE user_id = ? ORDER BY id DESC LIMIT ?", (user_id, max_messages))
    rows = cursor.fetchall()
    conn.close()
    return [{"role": role, "content": content} for role, content in reversed(rows)]

def save_transaction(user_id, tipo, descricao, categoria, valor, data):
    conn = sqlite3.connect("core_db.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO transactions (user_id, tipo, descricao, categoria, valor, data)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, tipo, descricao, categoria, valor, data))
    conn.commit()
    conn.close()

def parse_transaction(response_text):
    # Regex para extrair dados do resumo
    try:
        tipo = re.search(r"💸 Tipo: (.+)", response_text).group(1).strip()
        descricao = re.search(r"🧾 Item: (.+)", response_text).group(1).strip()
        categoria = re.search(r"🗂️ Categoria: (.+)", response_text).group(1).strip()
        valor_str = re.search(r"💰 Valor: R\$ ([\d\.,]+)", response_text).group(1).replace(",", ".")
        valor = float(valor_str)
        data = datetime.now().strftime("%Y-%m-%d")
        return {
            "tipo": tipo,
            "descricao": descricao,
            "categoria": categoria,
            "valor": valor,
            "data": data
        }
    except Exception:
        return None
