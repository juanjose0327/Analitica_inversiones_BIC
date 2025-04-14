# Sistema de Análisis de Datos Bancolombia

Este proyecto implementa un sistema completo para el procesamiento, limpieza, almacenamiento y visualización de datos financieros en una base de datos PostgreSQL. El sistema está diseñado para analizar activos bajo administración (ABA) clasificados por diferentes categorías como tipo de banca, perfil de riesgo y tipo de activo.

## Requisitos

### Librerías Python
```bash
pip install psycopg2-binary pandas matplotlib seaborn
```

### Base de Datos
- PostgreSQL (versión 10 o superior)
- Credenciales por defecto:
  - Host: localhost
  - Usuario: postgres
  - Contraseña: password
  - Puerto: 5432

## Estructura del Proyecto

El proyecto se compone de dos scripts principales:

1. **ETL (Extract, Transform, Load)**: `CÓDIGOBIC.py` o `paste.txt`
   - Crea la base de datos y tablas
   - Procesa y limpia datos de archivos CSV
   - Gestiona datos problemáticos
   - Realiza correcciones específicas

2. **Visualización**: `Gráficas Bancolombia.py`
   - Genera diferentes visualizaciones de los datos almacenados
   - Ofrece un menú interactivo para seleccionar gráficas

### Estructura de la Base de Datos

#### Tablas Principales
- `cat_perfil_riesgo`: Catálogo de perfiles de riesgo
- `catalogo_activos`: Catálogo de tipos de activos
- `cat_banca`: Catálogo de tipos de banca
- `historico_aba_macroactivos`: Datos históricos de activos bajo administración

#### Tablas de Control de Calidad
- `pendientes_idCliente`: Registros con problemas en ID de cliente
- `pendientes_month`: Registros con problemas en el mes
- `pendientes_codActivo`: Registros con problemas en código de activo
- `pendientes_aba`: Registros con valores ABA nulos
- `pendientes_perfil_riesgo`: Registros con problemas en perfil de riesgo
- `pendientes_codbanca`: Registros con problemas en código de banca

## Configuración

### PostgreSQL
1. Instalar PostgreSQL
2. Crear un usuario `postgres` con contraseña `password`
3. Asegurarse que PostgreSQL esté corriendo en el puerto 5432

### Datos de Entrada
Preparar los siguientes archivos CSV en la carpeta `/Users/juanjose/Downloads/`:
- `cat_perfil_riesgo.csv`: Catálogo de perfiles de riesgo
- `catalogo_activos.csv`: Catálogo de activos
- `catalogo_banca.csv`: Catálogo de bancas
- `historico_aba_macroactivos.csv`: Datos históricos

Los archivos deben estar en formato CSV con separador punto y coma (;).

## Ejecución

### 1. Procesamiento ETL
```bash
python CÓDIGOBIC.py
```

Este script realizará:
- Creación de la base de datos `db_bancolombia`
- Creación de las tablas
- Importación de datos desde los archivos CSV
- Limpieza y tratamiento de datos
- Corrección de filas desalineadas

### 2. Visualización de Datos
```bash
python "Gráficas Bancolombia.py"
```

Mostrará un menú con las siguientes opciones:
1. Portafolio por cliente
2. Portafolio por banca
3. Portafolio por perfil de riesgo
4. Evolución ABA promedio
5. Eficiencia de carga de datos
6. Top 10 clientes con mayor ABA total
7. Activo más y menos invertido dentro de FICs
8. Activo más y menos invertido dentro de Renta Variable

## Flujo del Proceso

1. **ETL**:
   - Conexión a PostgreSQL
   - Creación de base de datos y tablas
   - Importación de datos desde CSV
   - Limpieza y transformación de datos
   - Clasificación de activos en macroactivos
   - Separación de registros con problemas
   - Corrección de casos específicos

2. **Análisis**:
   - Consulta de datos desde la base de datos
   - Unión de tablas para información completa
   - Generación de visualizaciones según el tipo de análisis
   - Presentación de resultados gráficos

## Acerca del Procesamiento de Datos

- Los datos se clasifican en tres categorías principales de macroactivos:
  - **Renta Fija**: Códigos 1000, 1001
  - **Renta Variable**: Códigos 1002-1005, 1011-1017
  - **FICs** (Fondos de Inversión Colectiva): Códigos 1007-1010, 1018-1020

- Los registros con datos problemáticos se almacenan en tablas separadas para su revisión.

## Notas Adicionales

- Todos los montos ABA se convierten a formato decimal con punto como separador decimal.
- Se realizan correcciones específicas para códigos de activo conocidos (10007→1007, 1015→1115).
- Se verifica que los IDs de cliente tengan exactamente 11 caracteres.
- Se implementan múltiples validaciones para asegurar la calidad de los datos.
