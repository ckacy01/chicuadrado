# 📊 Analizador de Reglas de Asociación

Una aplicación web moderna y completa para análisis de reglas de asociación desarrollada con Streamlit. Implementa algoritmos estadísticos avanzados para el análisis de patrones de compra y asociaciones entre items.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://chicuadrado.streamlit.app)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

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
