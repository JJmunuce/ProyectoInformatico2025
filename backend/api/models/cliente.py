from api import mysql

class Cliente:
    def __init__(self, row):
        self._id = row.get('id_cliente')
        self._nombre = row.get('nombre')
        self._dni = row.get('dni')
        self._telefono = row.get('telefono')
        self._id_negocio = row.get('id_negocio')

    def to_json(self):
        return {
            "id_cliente": self._id,
            "nombre": self._nombre,
            "dni": self._dni,
            "telefono": self._telefono,
            "id_negocio": self._id_negocio
        }

    @classmethod
    def get_all(cls, id_negocio): # <--- Recibe id_negocio
        cur = mysql.connection.cursor()
        # Filtrado
        cur.execute("SELECT * FROM cliente WHERE id_negocio = %s", (id_negocio,))
        rows = cur.fetchall()
        cur.close()
        return [cls(row).to_json() for row in rows]

    @classmethod
    def create(cls, data):
        nombre = data['nombre']
        dni = data.get('dni')
        telefono = data.get('telefono')
        id_negocio = data.get('id_negocio')

        if not dni:
            raise Exception("El DNI es obligatorio")

        cur = mysql.connection.cursor()
        
        # Validación de duplicados EN ESTE NEGOCIO
        cur.execute("SELECT id_cliente FROM cliente WHERE dni = %s AND id_negocio = %s", (dni, id_negocio))
        if cur.fetchone():
            cur.close()
            raise Exception(f"Ya existe un cliente con el DNI {dni}")

        try:
            cur.execute(
                "INSERT INTO cliente (nombre, dni, telefono, id_negocio) VALUES (%s, %s, %s, %s)",
                (nombre, dni, telefono, id_negocio)
            )
            mysql.connection.commit()
            inserted_id = getattr(cur, 'lastrowid', None)
            cur.close()
            return {"mensaje": "Cliente creado exitosamente", "id_cliente": inserted_id}
        except Exception as ex:
            try: cur.close()
            except: pass
            raise ex