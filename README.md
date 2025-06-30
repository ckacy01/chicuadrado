# 📊 Analizador de Reglas de Asociación

Una aplicación web moderna y completa para análisis de reglas de asociación desarrollada con Streamlit. Implementa algoritmos estadísticos avanzados para el análisis de patrones de compra y asociaciones entre items.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://chicuadrado.streamlit.app)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## 🚀 Características Principales

### 📥 **Carga de Datos Flexible**
- **Archivos Excel**: Soporte para .xlsx y .xls con validación automática
- **Generación Aleatoria**: Datos sintéticos con correlaciones realistas
- **Entrada Manual**: Interfaz interactiva para crear datasets personalizados
- **Validación Automática**: Verificación de datos binarios y formato correcto

### 🔍 **Análisis Estadístico Completo**
- **Tablas de Contingencia**: Generación automática con totales marginales
- **8 Reglas de Asociación**: Análisis exhaustivo de todas las combinaciones posibles
- **Factores de Dependencia**: Implementación de la fórmula FD = P(A∩B) / (P(A) × P(B))
- **Prueba Chi-Cuadrado**: Significancia estadística con múltiples niveles de confianza
- **Métricas Avanzadas**: Confianza, cobertura, soporte y lift

### 📊 **Visualizaciones Interactivas**
- **Heatmaps**: Representación visual de tablas de contingencia
- **Gráficos de Barras**: Comparación de métricas y factores de dependencia
- **Dispersión con Jitter**: Distribución de datos con categorización por colores
- **Distribución Chi-Cuadrado**: Visualización de significancia estadística
- **Gráficos Comparativos**: Análisis visual de todas las reglas

### 📋 **Reportes Detallados**
- **Resumen Ejecutivo**: Métricas clave y conclusiones principales
- **Análisis Paso a Paso**: Cálculos detallados con fórmulas explicadas
- **Interpretaciones Contextuales**: Recomendaciones automáticas basadas en resultados
- **Documentación Completa**: Explicación de metodología y métricas

## 📊 Uso de la Aplicación

### 1. Carga de Datos
- **Excel**: Sube archivos .xlsx/.xls con datos binarios
- **Aleatorio**: Genera datos de ejemplo con correlaciones
- **Manual**: Crea tabla personalizada

### 2. Análisis
- Selecciona 2 items para analizar
- Obtén tabla de contingencia automáticamente
- Revisa métricas: confianza, cobertura, factor de dependencia
- Verifica significancia estadística (Chi-cuadrado)

### 3. Visualizaciones
- Heatmap de tabla de contingencia
- Gráfico de métricas comparativas
- Dispersión de datos con jitter
- Distribución Chi-cuadrado

### 4. Reporte
- Resumen ejecutivo completo
- Interpretación automática de resultados
- Recomendaciones basadas en análisis

## 🎯 Casos de Uso

- Análisis de cesta de mercado
- Recomendaciones de productos
- Estudios de correlación
- Investigación de patrones de comportamiento

## 🛠️ Tecnologías

- **Streamlit**: Framework web para Python
- **Pandas**: Manipulación de datos
- **NumPy**: Cálculos numéricos
- **Plotly**: Visualizaciones interactivas
- **SciPy**: Estadísticas y pruebas

## 🧑‍💻 Explicaciones técnicas (Funciones en app.py)
### 1. generate_sample_data

#### Propósito:
Genera un DataFrame de datos binarios (0 y 1) para simular compras de productos. Introduce correlaciones realistas entre ciertos ítems.

#### Parámetros:
- **n_items**: Número de ítems (columnas).
- **n_instances**: Número de transacciones (filas).
- **seed**: Semilla para reproducibilidad.

**Devuelve:**
DataFrame de pandas con los datos generados.

### 2. validate_data

#### **Propósito**:
Valida que los datos de entrada sean adecuados para el análisis (mínimo de columnas y filas, solo valores binarios).

#### Parámetros:
- **data**: DataFrame a validar.

#### Devuelve:
Tupla (bool, str) indicando si los datos son válidos y un mensaje de error o éxito.
### 3. calculate_dependency_factors

#### Propósito:
Calcula los cuatro factores de dependencia (FD) para cada combinación de presencia/ausencia de dos ítems usando la fórmula: FD = P(A∩B) / [P(A) × P(B)]

#### Parámetros:
- **a, b, c, d**: Conteos de la tabla de contingencia.
- **n**: Total de transacciones.

#### Devuelve:
Diccionario con los 4 factores, probabilidades involucradas, fórmulas, mapeo de la tabla y ejemplo de verificación.
### 4. interpret_dependency_factors

#### Propósito:
Genera explicaciones automáticas y contextuales sobre el significado de los factores de dependencia calculados entre dos ítems.

#### Parámetros:

- **fd_results**: Diccionario de factores de dependencia.
- **item1, item2**: Nombres de los ítems.

#### Devuelve:
Lista de interpretaciones en texto.
### 5. calculate_metrics

#### **Propósito**:
Calcula todas las métricas de asociación entre dos ítems:

- **Tabla de contingencia**.
- **Confianza, cobertura**.
- **Factores de dependencia**.
- **Prueba chi-cuadrado**.
- **Reglas de asociación**.
- **Interpretaciones**.

#### Parámetros:
- **data**: DataFrame de datos.
- i**tem1, item2**: Ítems a analizar.

#### Devuelve:
Diccionario con todas las métricas y tablas generadas.
### 6. calculate_all_association_rules

#### Propósito:
Construye las 8 reglas de asociación posibles entre dos ítems (todas las combinaciones de presencia y ausencia, en ambos sentidos) y calcula sus métricas: cobertura, confianza, soporte y la fórmula usada.

#### Parámetros:

- **a, b, c, d, n**: Valores de la tabla de contingencia y total.
- **item1, item2**: Nombres de los ítems.

#### Devuelve:
Lista de diccionarios, uno por cada regla generada.
### 7. create_contingency_heatmap

#### Propósito:
Genera un heatmap (gráfico de calor) usando Plotly, visualizando la tabla de contingencia entre dos ítems.

#### Parámetros:
- **contingency_table**: Tabla de contingencia.
- **item1, item2**: Nombres de los ítems.

#### Devuelve:
Objeto Figure de Plotly.
### 8. create_metrics_chart

#### Propósito:
Crea un gráfico de barras para visualizar confianza y cobertura de los dos ítems seleccionados.

#### Parámetros:
- **metrics**: Diccionario de métricas calculadas.
- **item1, item2**: Nombres de los ítems.

#### Devuelve:
Objeto Figure de Plotly.
### 9. create_dependency_factors_chart

#### Propósito:
Visualiza en barras los 4 factores de dependencia entre los dos ítems, coloreando según tipo de asociación (positiva, negativa, independencia).

#### Parámetros:
- **dependency_factors**: Diccionario de factores de dependencia.
- **item1**, **item2**: Nombres de los ítems.

#### Devuelve:
Objeto Figure de Plotly.
### 10.  create_all_rules_chart

#### Propósito:
Grafica todas las reglas de asociación (confianza y cobertura) en un gráfico de barras agrupadas.

#### Parámetros:
- **all_rules**: Lista de reglas calculadas.

#### Devuelve:
Objeto Figure de Plotly.
### 11. create_scatter_plot

#### Propósito:
Genera un gráfico de dispersión (scatter plot) tipo "jitter" para visualizar la distribución conjunta de los valores de los dos ítems seleccionados en las transacciones.

#### Parámetros:
- **data**: DataFrame de datos.
- **item1, item2**: Nombres de los ítems.

#### Devuelve:
Objeto Figure de Plotly.
### 12. create_chi_square_visualization

#### Propósito:
Visualiza la distribución teórica χ² y marca el valor calculado y los valores críticos en la gráfica.

#### Parámetros:
- **chi2_stat**: Valor calculado de chi-cuadrado.
- **critical_values**: Diccionario con los valores críticos.

#### Devuelve:
Objeto Figure de Plotly.
### 13. create_frequency_chart

#### Propósito:
Grafica la frecuencia de aparición (número de compras) de cada ítem en el dataset.

#### Parámetros:
- **data**: DataFrame de datos.

#### Devuelve:
Objeto Figure de Plotly.
### 14. main

#### Propósito:
Es la función principal. Organiza la estructura de toda la aplicación:
- **Configura la interfaz Streamlit.**
- **Controla la carga/generación/edición de datos.**
- **Permite seleccionar ítems para el análisis.**
- **Ejecuta y muestra resultados, visualizaciones e interpretaciones**
- **Presenta un reporte completo.**

## Para correr local

- Debes tener previamente instalado python3, lo puedes descargar desde su página oficial. [Python](https://www.python.org/downloads/)

- **Previamente debes tener creada un entorno virtual** de python o usar el ya creado dentro de esta carpeta con el comando: ```source rulesvenv/bin/activate ```
  - Para crear un entorno virtual usa: ```python3 -m venv rulesvenv  ```. Donde **rulwsvenv** es el nombre de nuestro entorno
  - Y ya despues usa el comando ```source ulesvenv/bin/activate```

- Una vez con el entorno virtual activo **Ejecutar el siguiente comando desde terminal:** ``` python3 run_local.py ```

Created by **Equipo 2 - 9-2 **
Universidad Politécnica de Sinaloa
