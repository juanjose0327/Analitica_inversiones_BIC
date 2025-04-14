import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

def connect_to_database():
    return psycopg2.connect(
        host="localhost",
        user="postgres",
        password="password",
        port="5432",
        database="db_bancolombia"
    )

def obtener_datos_portafolio():
    conn = connect_to_database()
    query = """
        SELECT h.*, c.banca, p.perfil_riesgo, a.activo
        FROM historico_aba_macroactivos h
        LEFT JOIN cat_banca c ON h.cod_banca = c.cod_banca
        LEFT JOIN cat_perfil_riesgo p ON h.cod_perfil_riesgo = p.cod_perfil_riesgo
        LEFT JOIN catalogo_activos a ON h.cod_activo = a.cod_activo
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def grafico_portafolio_cliente(df):
    ultima_fecha = df[['year', 'month']].dropna().astype(int).sort_values(['year', 'month']).drop_duplicates().iloc[-1]
    df_ultima = df[(df['year'].astype(int) == ultima_fecha['year']) & (df['month'].astype(int) == ultima_fecha['month'])]

    clientes = df_ultima['id_sistema_cliente'].unique()
    for cliente in clientes:
        df_cliente = df_ultima[df_ultima['id_sistema_cliente'] == cliente]
        df_grouped = df_cliente.groupby(['macroactivo', 'activo'])['aba'].sum().reset_index()
        df_grouped['porcentaje'] = df_grouped['aba'] / df_grouped['aba'].sum() * 100

        plt.figure(figsize=(10, 6))
        bars = sns.barplot(data=df_grouped, x='porcentaje', y='activo', hue='macroactivo')
        plt.title(f"Portafolio del Cliente {cliente}")
        plt.xlabel('% del Portafolio')
        plt.ylabel('Activo')
        plt.legend(title='Macroactivo')

        # Etiquetas con porcentaje
        for bar in bars.patches:
            width = bar.get_width()
            if width > 0:
                plt.text(width + 0.5, bar.get_y() + bar.get_height() / 2,
                         f'{width:.1f}%', va='center')

        plt.tight_layout()
        plt.show()

def grafico_portafolio_banca(df):
    ultima_fecha = df[['year', 'month']].dropna().astype(int).sort_values(['year', 'month']).drop_duplicates().iloc[-1]
    df_ultima = df[(df['year'].astype(int) == ultima_fecha['year']) & (df['month'].astype(int) == ultima_fecha['month'])]

    df_grouped = df_ultima.groupby(['banca', 'macroactivo'])['aba'].sum().reset_index()
    df_total = df_grouped.groupby('banca')['aba'].sum().reset_index().rename(columns={'aba': 'total'})
    df_grouped = df_grouped.merge(df_total, on='banca')
    df_grouped['porcentaje'] = df_grouped['aba'] / df_grouped['total'] * 100

    plt.figure(figsize=(12, 6))
    bars = sns.barplot(data=df_grouped, x='banca', y='porcentaje', hue='macroactivo')
    plt.title('Distribución del Portafolio por Banca')
    plt.ylabel('% del Portafolio')

    # Etiquetas con porcentaje
    for bar in bars.patches:
        height = bar.get_height()
        if height > 0:
            plt.text(bar.get_x() + bar.get_width() / 2,
                     height + 0.5,
                     f'{height:.1f}%',
                     ha='center', va='bottom')

    plt.tight_layout()
    plt.show()

def grafico_portafolio_perfil_riesgo(df):
    ultima_fecha = df[['year', 'month']].dropna().astype(int).sort_values(['year', 'month']).drop_duplicates().iloc[-1]
    df_ultima = df[(df['year'].astype(int) == ultima_fecha['year']) & (df['month'].astype(int) == ultima_fecha['month'])]

    df_grouped = df_ultima.groupby(['perfil_riesgo', 'macroactivo'])['aba'].sum().reset_index()
    df_total = df_grouped.groupby('perfil_riesgo')['aba'].sum().reset_index().rename(columns={'aba': 'total'})
    df_grouped = df_grouped.merge(df_total, on='perfil_riesgo')
    df_grouped['porcentaje'] = df_grouped['aba'] / df_grouped['total'] * 100

    plt.figure(figsize=(12, 6))
    bars = sns.barplot(data=df_grouped, x='perfil_riesgo', y='porcentaje', hue='macroactivo')
    plt.title('Distribución del Portafolio por Perfil de Riesgo')
    plt.ylabel('% del Portafolio')

    # Etiquetas con porcentaje
    for bar in bars.patches:
        height = bar.get_height()
        if height > 0:
            plt.text(bar.get_x() + bar.get_width() / 2,
                     height + 0.5,
                     f'{height:.1f}%',
                     ha='center', va='bottom')

    plt.tight_layout()
    plt.show()

def grafico_evolucion_ABA(df, fecha_inicio=None, fecha_fin=None):
    df['fecha'] = pd.to_datetime(df['year'].astype(str) + '-' + df['month'].astype(int).astype(str) + '-01')
    
    if fecha_inicio:
        df = df[df['fecha'] >= pd.to_datetime(fecha_inicio)]
    if fecha_fin:
        df = df[df['fecha'] <= pd.to_datetime(fecha_fin)]

    # 🔁 Promedio del ABA por mes
    df_grouped = df.groupby('fecha')['aba'].mean().reset_index()  # Usar .mean() en lugar de .sum()

    plt.figure(figsize=(12, 6))
    sns.lineplot(data=df_grouped, x='fecha', y='aba', marker='o')
    plt.title('Evolución Mensual del ABA Promedio del Banco')
    plt.xlabel('Fecha')
    plt.ylabel('ABA Promedio')
    plt.xticks(rotation=45)  # Rota las fechas para mejorar la legibilidad
    plt.tight_layout()
    plt.show()
    
    
def grafico_eficiencia_carga():
    datos_originales = 6694
    datos_limpios = 4077
    datos_descartados = datos_originales - datos_limpios

    labels = ['Datos conservados', 'Datos descartados']
    sizes = [datos_limpios, datos_descartados]
    colors = ['#4CAF50', '#F44336']

    plt.figure(figsize=(6, 6))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
    plt.title('Eficiencia de Carga de Datos a Plantilla')
    plt.axis('equal')  # Círculo perfecto
    plt.show()
    

def grafico_top_clientes_piramide(df, top_n=10):
    # Agrupar y ordenar por ABA total
    df_top = df.groupby('id_sistema_cliente')['aba'].sum().reset_index()
    df_top = df_top.sort_values('aba', ascending=True).head(top_n)

    # Invertir el orden para que el mayor quede arriba
    df_top = df_top[::-1]

    plt.figure(figsize=(8, 6))
    bars = plt.barh(y=df_top['id_sistema_cliente'], width=df_top['aba'], color='#2E86AB')

    # Eliminar valores numéricos en el eje x
    plt.xticks([])
    plt.xlabel('')
    plt.ylabel('ID Cliente')
    plt.title(f'Top {top_n} Clientes con Mayor ABA (Pirámide Invertida)')
    plt.gca().invert_yaxis()  # Esto hace la pirámide: pone el mayor arriba

    plt.tight_layout()
    plt.show()


def grafico_activo_mas_menos_inversion_fics(df):
    # Filtramos solo FICs
    df_fics = df[df['macroactivo'] == 'FICs']

    # Agrupamos por activo y sumamos ABA
    df_grouped = df_fics.groupby('activo')['aba'].sum().reset_index()

    # Identificamos el activo más y el menos invertido
    activo_max = df_grouped.loc[df_grouped['aba'].idxmax()]
    activo_min = df_grouped.loc[df_grouped['aba'].idxmin()]

    resumen = pd.DataFrame([activo_max, activo_min])
    resumen['tipo'] = ['Más Invertido', 'Menos Invertido']

    # Gráfico
    plt.figure(figsize=(8, 6))
    sns.barplot(data=resumen, x='activo', y='aba', hue='tipo', palette='coolwarm')

    # Añadir etiquetas
    for i, row in resumen.iterrows():
        plt.text(i, row['aba'] + row['aba']*0.01, f"{row['tipo']}", ha='center')

    plt.title('Activos con Más y Menos Inversión dentro de FICs')
    plt.xlabel('Activo')
    plt.ylabel('Total ABA')
    plt.tight_layout()
    plt.show()
    
def grafico_activo_mas_menos_inversion_RentaVariable(df):
    # Filtramos solo Renta Varibale
    df_fics = df[df['macroactivo'] == 'Renta Variable']

    # Agrupamos por activo y sumamos ABA
    df_grouped = df_fics.groupby('activo')['aba'].sum().reset_index()

    # Identificamos el activo más y el menos invertido
    activo_max = df_grouped.loc[df_grouped['aba'].idxmax()]
    activo_min = df_grouped.loc[df_grouped['aba'].idxmin()]

    resumen = pd.DataFrame([activo_max, activo_min])
    resumen['tipo'] = ['Más Invertido', 'Menos Invertido']

    # Gráfico
    plt.figure(figsize=(4, 3))
    sns.barplot(data=resumen, x='activo', y='aba', hue='tipo', palette='coolwarm')

    # Añadir etiquetas
    for i, row in resumen.iterrows():
        plt.text(i, row['aba'] + row['aba']*0.01, f"{row['tipo']}", ha='center')

    plt.title('Activos con Más y Menos Inversión dentro de Renta Variable')
    plt.xlabel('Activo')
    plt.ylabel('Total ABA')
    plt.tight_layout()
    plt.show()





if __name__ == "__main__":
    df = obtener_datos_portafolio()

    print("\n--- Gráficas disponibles ---")
    print("1. Portafolio por cliente")
    print("2. Portafolio por banca")
    print("3. Portafolio por perfil de riesgo")
    print("4. Evolución ABA promedio")
    print("5. Eficiencia de carga de datos")
    print("6. Top 10 clientes con mayor ABA total")
    print("7. Activo más y menos invertido dentro de FICs")
    print("8. Activo más y menos invertido dentro de Renta Variable")


    opcion = input("Seleccione una opción (1-8): ")
    if opcion == '1':
        grafico_portafolio_cliente(df)
    elif opcion == '2':
        grafico_portafolio_banca(df)
    elif opcion == '3':
        grafico_portafolio_perfil_riesgo(df)
    elif opcion == '4':
        fecha_inicio = input("Ingrese fecha de inicio (YYYY-MM) o presione Enter para omitir: ") or None
        fecha_fin = input("Ingrese fecha de fin (YYYY-MM) o presione Enter para omitir: ") or None
        grafico_evolucion_ABA(df, fecha_inicio, fecha_fin)
    elif opcion == '5':
        grafico_eficiencia_carga()  
    elif opcion == '6':
        grafico_top_clientes_piramide(df)
    elif opcion == '7':
        grafico_activo_mas_menos_inversion_fics(df)
    elif opcion == '8':
        grafico_activo_mas_menos_inversion_RentaVariable(df)



    else:
        print("⚠️ Opción no válida.")
        
        
