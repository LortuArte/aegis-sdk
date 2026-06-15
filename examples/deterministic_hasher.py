import json
import hashlib

def generate_deterministic_hash(data: dict) -> str:
    """
    Genera un hash SHA-256 determinista para un diccionario.
    
    El mercado exige determinismo: para que el hash sea el mismo siempre,
    debemos ordenar las claves del JSON antes de realizar el hashing.
    """
    
    # 1. Serialización determinista:
    # 'sort_keys=True' es vital. Sin esto, un cambio en el orden de las
    # claves en el diccionario resultaría en un hash diferente.
    # 'separators' elimina espacios innecesarios para mayor eficiencia.
    serialized_data = json.dumps(data, sort_keys=True, separators=(',', ':'))
    
    # 2. Hashing:
    # Usamos SHA-256, el estándar actual para integridad de datos.
    # Encodeamos a UTF-8 antes de pasar al objeto de hash.
    hash_object = hashlib.sha256(serialized_data.encode('utf-8'))
    
    # Retornamos el hash en formato hexadecimal.
    return hash_object.hexdigest()

# --- Ejemplo de uso ---
if __name__ == "__main__":
    # Dos diccionarios con el mismo contenido pero diferente orden
    objeto_1 = {"id": 1, "nombre": "Proyecto Alpha", "status": "activo"}
    objeto_2 = {"nombre": "Proyecto Alpha", "status": "activo", "id": 1}
    
    hash_1 = generate_deterministic_hash(objeto_1)
    hash_2 = generate_deterministic_hash(objeto_2)
    
    print(f"Hash 1: {hash_1}")
    print(f"Hash 2: {hash_2}")
    
    # Verificación de determinismo
    if hash_1 == hash_2:
        print("\nResultado: Éxito. El hash es idéntico independientemente del orden.")
    else:
        print("\nResultado: Error. El hash es diferente.")