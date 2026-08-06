import sqlite3
import numpy as np
import faiss
import pickle
import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

DB_FILE = "products.db"
FAISS_INDEX_FILE = "products.index"
METADATA_FILE = "products_meta.pkl"

# 🌟 FIXED: Correct Mesh API URL
client = OpenAI(
    base_url="https://meshapi.ai",
    api_key=os.getenv("MESH_API_KEY")
)

def init_sql_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            action TEXT NOT NULL,
            item_title TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def get_embedding(text: str):
    try:
        response = client.embeddings.create(
            model="openai/text-embedding-3-small",
            input=[text]
        )
        if isinstance(response, str):
            try:
                response = json.loads(response)
            except:
                pass

        if hasattr(response, 'data') and len(response.data) > 0:
            if hasattr(response.data[0], 'embedding'):
                return response.data[0].embedding
            return response.data
        elif isinstance(response, dict) and 'data' in response:
            if isinstance(response['data'], list) and len(response['data']) > 0:
                if isinstance(response['data'][0], dict) and 'embedding' in response['data'][0]:
                    return response['data'][0]['embedding']
                return response['data']
        
        if hasattr(response, 'embedding'):
            return response.embedding
        return None
    except Exception as e:
        print(f"Embedding generation failed: {e}")
        return None

def db_add_product(title: str, description: str, category: str, price: float):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM products WHERE title = ?", (title,))
    exists = cursor.fetchone()
    if exists:
        conn.close()
        return exists[0]

    cursor.execute(
        "INSERT INTO products (title, description, category, price) VALUES (?, ?, ?, ?)",
        (title, description, category, price)
    )
    product_id = cursor.lastrowid
    conn.commit()
    conn.close()

    # 🌟 FIXED: Removed the early exit bug so subsequent products update correctly
    combined_text = f"Title: {title}. Description: {description}. Category: {category}."
    embedding = get_embedding(combined_text)
    
    if embedding is not None:
        embedding_np = np.array([embedding], dtype=np.float32)
        
        if os.path.exists(FAISS_INDEX_FILE) and os.path.exists(METADATA_FILE):
            index = faiss.read_index(FAISS_INDEX_FILE)
            with open(METADATA_FILE, 'rb') as f:
                metadata = pickle.load(f)
        else:
            index = faiss.IndexFlatL2(len(embedding))
            metadata = []

        index.add(embedding_np)
        metadata.append({"sql_id": product_id, "title": title, "category": category})

        faiss.write_index(index, FAISS_INDEX_FILE)
        with open(METADATA_FILE, 'wb') as f:
            pickle.dump(metadata, f)
            
    return product_id

def db_semantic_search(query: str, top_k=2):
    results = []
    
    if os.path.exists(FAISS_INDEX_FILE) and os.path.exists(METADATA_FILE):
        query_embedding = get_embedding(query)
        if query_embedding is not None:
            try:
                index = faiss.read_index(FAISS_INDEX_FILE)
                with open(METADATA_FILE, 'rb') as f:
                    metadata = pickle.load(f)

                query_np = np.array([query_embedding], dtype=np.float32)
                distances, indices = index.search(query_np, top_k)

                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                for idx in indices[0]:
                    if idx == -1 or idx >= len(metadata):
                        continue
                    sql_id = metadata[idx]["sql_id"]
                    cursor.execute("SELECT id, title, description, category, price FROM products WHERE id = ?", (sql_id,))
                    row = cursor.fetchone()
                    if row:
                        results.append({
                            "id": row[0], 
                            "title": row[1], 
                            "description": row[2], 
                            "category": row[3], 
                            "price": row[4]
                        })
                conn.close()
                if results:
                    return results
            except Exception as e:
                print(f"FAISS search fell back: {e}")

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, description, category, price FROM products LIMIT ?", (top_k,))
    rows = cursor.fetchall()
    conn.close()
    return [{
        "id": r[0], 
        "title": r[1], 
        "description": r[2], 
        "category": r[3], 
        "price": r[4]
    } for r in rows]

def db_log_event(user_id: str, action: str, item_title: str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO user_events (user_id, action, item_title) VALUES (?, ?, ?)",
        (user_id, action, item_title)
    )
    conn.commit()
    conn.close()

def db_get_user_history(user_id: str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT action, item_title FROM user_events WHERE user_id = ? AND item_title != 'Home Marketplace Page' ORDER BY timestamp DESC LIMIT 5", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [f"{row[0]}ed '{row[1]}'" for row in rows]
