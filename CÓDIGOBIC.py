import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns


def create_database(db_name):
    conn = psycopg2.connect(
        host="localhost",
        user="postgres",
        password="password",
        port="5432"
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    try:
        cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))
        print(f"📦 Base de datos '{db_name}' creada")
    except psycopg2.errors.DuplicateDatabase:
        print(f"⚠️ La base de datos '{db_name}' ya existe")
    cursor.close()
    conn.close()
    conn = psycopg2.connect(
        host="localhost",
        user="postgres",
        password="password",
        port="5432",
        database=db_name
    )
    return conn

def create_tables(conn):
    cursor = conn.cursor()
    cursor.execute("""
    DROP TABLE IF EXISTS pendientes_codbanca;
    DROP TABLE IF EXISTS pendientes_perfil_riesgo;
    DROP TABLE IF EXISTS pendientes_aba;
    DROP TABLE IF EXISTS pendientes_idCliente;
    DROP TABLE IF EXISTS pendientes_month;
    DROP TABLE IF EXISTS pendientes_codActivo;
    DROP TABLE IF EXISTS historico_aba_macroactivos;
    DROP TABLE IF EXISTS cat_banca;
    DROP TABLE IF EXISTS catalogo_activos;
    DROP TABLE IF EXISTS cat_perfil_riesgo;

    CREATE TABLE cat_perfil_riesgo (
      cod_perfil_riesgo VARCHAR(255),
      perfil_riesgo VARCHAR(255)
    );

    CREATE TABLE catalogo_activos (
      cod_activo VARCHAR(255),
      activo VARCHAR(255)
    );

    CREATE TABLE cat_banca (
      cod_banca VARCHAR(255),
      banca VARCHAR(255)
    );

    CREATE TABLE historico_aba_macroactivos (
      id_sistema_cliente VARCHAR(255),
      ingestion_year VARCHAR(255),
      ingestion_month NUMERIC(255),
      ingestion_day VARCHAR(255),
      macroactivo VARCHAR(255),
      cod_activo VARCHAR(255),
      aba NUMERIC(20,2),
      cod_perfil_riesgo VARCHAR(255),
      cod_banca VARCHAR(255),
      year VARCHAR(255),
      month NUMERIC(255)
    );

    CREATE TABLE pendientes_idCliente AS SELECT * FROM historico_aba_macroactivos WHERE 1=0;
    CREATE TABLE pendientes_month AS SELECT * FROM historico_aba_macroactivos WHERE 1=0;
    CREATE TABLE pendientes_codActivo AS SELECT * FROM historico_aba_macroactivos WHERE 1=0;
    CREATE TABLE pendientes_aba AS SELECT * FROM historico_aba_macroactivos WHERE 1=0;
    CREATE TABLE pendientes_perfil_riesgo AS SELECT * FROM historico_aba_macroactivos WHERE 1=0;
    CREATE TABLE pendientes_codbanca AS SELECT * FROM historico_aba_macroactivos WHERE 1=0;
    """)
    conn.commit()
    cursor.close()
    print("✅ Tablas creadas correctamente")

def limpiar_columnas(df):
    df['cod_activo'] = df['cod_activo'].replace('10007', '1007')
    df['cod_activo'] = df['cod_activo'].replace('1015', '1115')
    return df

def asignar_macroactivo(df):
    renta_fija = ['1000', '1001']
    renta_variable = ['1002', '1003', '1004', '1005', '1011', '1012', '1014','1115', '1016', '1017']
    fics = ['1009', '1010', '1007', '1008', '1018', '1019', '1020']

    def clasificar(codigo):
        if pd.isna(codigo):
            return None
        codigo = str(codigo).strip()
        if codigo in renta_fija:
            return 'Renta Fija'
        elif codigo in renta_variable:
            return 'Renta Variable'
        elif codigo in fics:
            return 'FICs'
        return None

    df['macroactivo'] = df['cod_activo'].apply(clasificar)
    return df

def exportar_a_pendientes_aba(conn, df):
    pendientes = df[df['aba'].isna()]
    if pendientes.empty:
        print("✅ No hay filas con 'aba' nulo para exportar")
        return

    cursor = conn.cursor()
    columns = list(pendientes.columns)
    placeholders = ', '.join(['%s'] * len(columns))
    insert_stmt = f"INSERT INTO pendientes_aba ({', '.join(columns)}) VALUES ({placeholders})"
    for _, row in pendientes.iterrows():
        cursor.execute(insert_stmt, tuple(row))
    conn.commit()
    cursor.close()
    print(f"📤 {len(pendientes)} fila(s) con 'aba' nulo exportadas a 'pendientes_aba'")

def ingest_csv_data(conn, csv_file, table_name):
    try:
        df = pd.read_csv(csv_file, sep=";", dtype=str)
        df.columns = [col.strip() for col in df.columns]

        if table_name == 'historico_aba_macroactivos':
            df = limpiar_columnas(df)
            df = asignar_macroactivo(df)

            df['aba'] = (
                df['aba']
                .str.replace(",", ".", regex=False)
                .str.replace(r"[^\d.]", "", regex=True)
                .replace('', pd.NA)
                .astype(float)
            )

            exportar_a_pendientes_aba(conn, df)
            df = df[df['aba'].notna()]

        df = df.where(pd.notna(df), None)

        cursor = conn.cursor()
        columns = list(df.columns)
        placeholders = ', '.join(['%s'] * len(columns))
        insert_stmt = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
        for _, row in df.iterrows():
            cursor.execute(insert_stmt, tuple(row))

        conn.commit()
        print(f"📥 Datos insertados en '{table_name}'")
        cursor.close()
        return True
    except Exception as e:
        conn.rollback()
        print(f"❌ Error al insertar en {table_name}: {e}")
        return False

def mover_nulls(conn):
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO pendientes_idCliente
        SELECT * FROM historico_aba_macroactivos
        WHERE id_sistema_cliente IS NULL OR LENGTH(id_sistema_cliente) != 11
    """)
    cursor.execute("""
        DELETE FROM historico_aba_macroactivos
        WHERE id_sistema_cliente IS NULL OR LENGTH(id_sistema_cliente) != 11
    """)
    
    cursor.execute("""
        INSERT INTO pendientes_perfil_riesgo
        SELECT * FROM historico_aba_macroactivos
        WHERE cod_perfil_riesgo IS NULL
    """)
    cursor.execute("""
        DELETE FROM historico_aba_macroactivos
        WHERE cod_perfil_riesgo IS NULL
    """)

    cursor.execute("""
        INSERT INTO pendientes_month
        SELECT * FROM historico_aba_macroactivos
        WHERE ingestion_month IS NULL
    """)
    cursor.execute("""
        DELETE FROM historico_aba_macroactivos
        WHERE ingestion_month IS NULL
    """)

    cursor.execute("""
        INSERT INTO pendientes_codActivo
        SELECT * FROM historico_aba_macroactivos
        WHERE cod_activo IS NULL
    """)
    cursor.execute("""
        DELETE FROM historico_aba_macroactivos
        WHERE cod_activo IS NULL
    """)
    
    cursor.execute("""
        INSERT INTO pendientes_codbanca
        SELECT * FROM historico_aba_macroactivos
        WHERE cod_banca IS NULL
    """)
    cursor.execute("""
        DELETE FROM historico_aba_macroactivos
        WHERE cod_banca IS NULL
    """)

    cursor.execute("""
        INSERT INTO pendientes_codActivo
        SELECT * FROM historico_aba_macroactivos
        WHERE cod_activo = '1022'
    """)
    cursor.execute("""
        DELETE FROM historico_aba_macroactivos
        WHERE cod_activo = '1022'
    """)

    cursor.execute("""
        UPDATE historico_aba_macroactivos
        SET year = ingestion_year
    """)

    cursor.execute("""
        UPDATE historico_aba_macroactivos
        SET ingestion_month = month
        WHERE ingestion_month = 'NaN'
    """)

    conn.commit()
    cursor.close()
    print("🔄 Limpieza y organización de datos completada")

def corregir_fila_desalineada(conn):
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM historico_aba_macroactivos
        WHERE LOWER(TRIM(cod_activo)) = 'renta variable'
    """)
    conn.commit()
    print("✅ Fila 'Renta Variable' eliminada")

    cursor.execute("""
        INSERT INTO historico_aba_macroactivos (
            id_sistema_cliente,
            ingestion_year,
            ingestion_month,
            ingestion_day,
            macroactivo,
            cod_activo,
            aba,
            cod_perfil_riesgo,
            cod_banca,
            year,
            month
        ) VALUES (
            '10032184607',
            '2024',
            '5',
            '10',
            'Renta Variable',
            '1002',
            12615000.00,
            '1468',
            'PN',
            '2024',
            '5'
        )
    """)
    conn.commit()
    print("✅ Fila corregida y actualizada correctamente")
    cursor.close()

def corregir_fila_desalineada_perfilRiesgo(conn):
    cursor = conn.cursor()
    print("🔍 Verificando filas antes de eliminar...")
    cursor.execute("""
        SELECT cod_perfil_riesgo, cod_banca, LENGTH(cod_perfil_riesgo) 
        FROM historico_aba_macroactivos
        WHERE LOWER(TRIM(cod_perfil_riesgo)) = 'pn'
    """)
    rows = cursor.fetchall()
    if rows:
        print("✅ Fila(s) encontrada(s) con 'PN':")
        for row in rows:
            print(f"  cod_perfil_riesgo: '{row[0]}' | cod_banca: {row[1]} | longitud: {row[2]}")
    else:
        print("⚠️ No se encontraron filas con 'PN' en 'cod_perfil_riesgo'")

    print("🗑️ Eliminando filas con 'cod_perfil_riesgo' = 'PN'...")
    cursor.execute("""
        DELETE FROM historico_aba_macroactivos
        WHERE LOWER(TRIM(cod_perfil_riesgo)) = 'pn'
    """)
    conn.commit()
    print("✅ Fila(s) 'PN' eliminada(s)")

    print("🧩 Insertando fila corregida...")
    cursor.execute("""
        INSERT INTO historico_aba_macroactivos (
            id_sistema_cliente,
            ingestion_year,
            ingestion_month,
            ingestion_day,
            macroactivo,
            cod_activo,
            aba,
            cod_perfil_riesgo,
            cod_banca,
            year,
            month
        ) VALUES (
            '10071747544',
            '2024',
            '3',
            '14',
            'FICs',
            '1007',
            369990.35,
            '1469',
            'PN',
            '2024',
            '3'
        )
    """)
    conn.commit()
    print("✅ Fila corregida insertada")
    cursor.close()

def main():
    db_name = "db_bancolombia"
    conn = create_database(db_name)
    create_tables(conn)

    csv_dir = "/Users/juanjose/Downloads/"
    file_table_mapping = {
        'cat_perfil_riesgo.csv': 'cat_perfil_riesgo',
        'catalogo_activos.csv': 'catalogo_activos',
        'catalogo_banca.csv': 'cat_banca',
        'historico_aba_macroactivos.csv': 'historico_aba_macroactivos'
    }

    table_order = ['cat_perfil_riesgo', 'catalogo_activos', 'cat_banca', 'historico_aba_macroactivos']
    for table in table_order:
        filename = next((f for f, t in file_table_mapping.items() if t == table), None)
        if filename:
            path = os.path.join(csv_dir, filename)
            if os.path.exists(path):
                print(f"📄 Procesando {filename}")
                ingest_csv_data(conn, path, table)
            else:
                print(f"⚠️ Archivo {filename} no encontrado")

    mover_nulls(conn)
    corregir_fila_desalineada(conn)
    corregir_fila_desalineada_perfilRiesgo(conn)
    conn.close()
    print("🎉 Proceso completo")

if __name__ == "__main__":
    main()
    
    


