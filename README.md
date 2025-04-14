# Análisis de Portafolio Bancario - Bancolombia

Este proyecto fue desarrollado como parte de una prueba técnica y tiene como objetivo analizar y visualizar datos financieros de clientes de Bancolombia, con foco en los activos bajo administración (ABA), distribución de portafolios, perfiles de riesgo y evolución temporal.

## 📊 Funcionalidades

El script permite generar múltiples visualizaciones a partir de los datos almacenados en una base de datos PostgreSQL. Estas son las gráficas disponibles:

1. **Portafolio por Cliente**  
   Visualiza cómo se distribuye el portafolio de cada cliente entre macroactivos y activos específicos.

2. **Portafolio por Banca**  
   Muestra la distribución de activos según los diferentes segmentos de banca (Empresarial, Personal, etc.).

3. **Portafolio por Perfil de Riesgo**  
   Compara la asignación de activos entre clientes con perfiles conservador, moderado o arriesgado.

4. **Evolución del ABA Promedio Mensual**  
   Traza la evolución en el tiempo del promedio de ABA de todos los clientes del banco.

5. **Eficiencia de carga de datos en plantilla**  
   Compara la cantidad de datos originales vs. los cargados exitosamente mediante plantilla (gráfico de torta).

6. **Top Clientes (Pirámide Invertida)**  
   Lista los 10 clientes con mayores montos invertidos, en una pirámide descendente mostrando solo el ID.

7. **Activo más y menos invertido (Global)**  
   Identifica cuál activo tiene mayor y menor participación entre todas las categorías.

8. **Activo más y menos invertido (solo FICs)**  
   Filtro especializado para mostrar solo activos de tipo FIC y comparar su volumen relativo de inversión.

---

## 🛠️ Requisitos

- Python 3.8+
- PostgreSQL (con la base de datos `db_bancolombia` cargada)
- Bibliotecas de Python:
  - pandas
  - matplotlib
  - seaborn
  - psycopg2

Instala los requisitos con:

```bash
pip install pandas matplotlib seaborn psycopg2
