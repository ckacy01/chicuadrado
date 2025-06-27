import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import chi2
import random

# Configuración de la página
st.set_page_config(
    page_title="Analizador de Reglas de Asociación",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS mejorado SIN los divs problemáticos
st.markdown("""
<style>
    /* Estilos base */
    .main-header {
        font-size: 3rem;
        color: #1f77b4 !important;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    /* Tarjetas de métricas - MODO CLARO */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        padding: 1rem !important;
        border-radius: 10px !important;
        color: white !important;
        text-align: center !important;
        margin: 0.5rem 0 !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
    }
    
    .metric-card h1, 
    .metric-card h2, 
    .metric-card h3,
    .metric-card * {
        color: white !important;
        margin: 0.2rem 0 !important;
    }
    
    /* Cajas de éxito - MODO CLARO */
    .success-box {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%) !important;
        padding: 1rem !important;
        border-radius: 10px !important;
        color: white !important;
        margin: 1rem 0 !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
    }
    
    .success-box *,
    .success-box strong {
        color: white !important;
    }
    
    /* Cajas de advertencia - MODO CLARO */
    .warning-box {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%) !important;
        padding: 1rem !important;
        border-radius: 10px !important;
        color: white !important;
        margin: 1rem 0 !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
    }
    
    .warning-box *,
    .warning-box strong {
        color: white !important;
    }
    
    /* MODO OSCURO - Detección automática */
    @media (prefers-color-scheme: dark) {
        .main-header {
            color: #4fc3f7 !important;
        }
    }
    
    /* Pestañas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px !important;
        padding-left: 20px !important;
        padding-right: 20px !important;
        border-radius: 10px 10px 0px 0px !important;
        transition: all 0.3s ease !important;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #1f77b4 !important;
        color: white !important;
    }
    
    /* Asegurar que los gráficos tengan fondo transparente */
    .js-plotly-plot {
        background: transparent !important;
    }
    
    .plotly {
        background: transparent !important;
    }
</style>
""", unsafe_allow_html=True)

# Funciones auxiliares (mantener las mismas)
@st.cache_data
def generate_sample_data(n_items=6, n_instances=100, seed=42):
    """Genera datos de ejemplo con correlaciones realistas"""
    np.random.seed(seed)
    random.seed(seed)
    
    items = ['Pan', 'Leche', 'Huevos', 'Mantequilla', 'Queso', 'Jamón', 'Yogurt', 'Cereal'][:n_items]
    data = []
    
    # Probabilidades base para cada item
    base_probs = [0.7, 0.6, 0.4, 0.4, 0.3, 0.3, 0.35, 0.25][:n_items]
    
    for i in range(n_instances):
        transaction = []
        for j, item in enumerate(items):
            prob = base_probs[j]
            
            # Añadir correlaciones realistas
            if item == 'Mantequilla' and len(transaction) > 0 and transaction[0] == 1:  # Pan
                prob += 0.3
            elif item == 'Jamón' and len(transaction) > 4 and len(transaction) > 4 and transaction[4] == 1:  # Queso
                prob += 0.4
            elif item == 'Yogurt' and len(transaction) > 1 and transaction[1] == 1:  # Leche
                prob += 0.2
            
            prob = min(prob, 0.95)  # Limitar probabilidad máxima
            transaction.append(1 if random.random() < prob else 0)
        
        data.append(transaction)
    
    return pd.DataFrame(data, columns=items)

def validate_data(data):
    """Valida que los datos sean correctos"""
    if data is None or data.empty:
        return False, "No hay datos para validar"
    
    # Verificar que hay al menos 2 columnas
    if len(data.columns) < 2:
        return False, "Se necesitan al menos 2 items para el análisis"
    
    # Verificar que hay al menos 5 filas
    if len(data) < 5:
        return False, "Se necesitan al menos 5 instancias para el análisis"
    
    # Verificar valores binarios
    for col in data.columns:
        unique_vals = data[col].dropna().unique()
        if not all(val in [0, 1] for val in unique_vals):
            return False, f"La columna '{col}' contiene valores no binarios"
    
    return True, "Datos válidos"

def calculate_dependency_factors(a, b, c, d, n):
    """
    Calcula los 4 factores de dependencia usando la fórmula: FD = P(A∩B) / (P(A) × P(B))
    
    Tabla de contingencia:
                Item2=0    Item2=1    Total
    Item1=0        d         c        c+d
    Item1=1        b         a        a+b
    Total        b+d       a+c        n
    
    Donde:
    - a = Item1=1 ∩ Item2=1
    - b = Item1=1 ∩ Item2=0  
    - c = Item1=0 ∩ Item2=1
    - d = Item1=0 ∩ Item2=0
    """
    
    if n == 0:
        return {
            'fd_1_1': 0, 'fd_1_0': 0, 'fd_0_1': 0, 'fd_0_0': 0,
            'probabilities': {}, 'formulas': {}, 'contingency_mapping': {}
        }
    
    # Calcular probabilidades marginales
    p_item1_1 = (a + b) / n  # P(Item1=1)
    p_item1_0 = (c + d) / n  # P(Item1=0)
    p_item2_1 = (a + c) / n  # P(Item2=1)
    p_item2_0 = (b + d) / n  # P(Item2=0)
    
    # Calcular probabilidades conjuntas
    p_both_1_1 = a / n  # P(Item1=1 ∩ Item2=1)
    p_1_0 = b / n        # P(Item1=1 ∩ Item2=0)
    p_0_1 = c / n        # P(Item1=0 ∩ Item2=1)
    p_both_0_0 = d / n   # P(Item1=0 ∩ Item2=0)
    
    # Calcular factores de dependencia: FD = P(A∩B) / (P(A) × P(B))
    # CORRECCIÓN: Usar exactamente la fórmula de la imagen
    fd_1_1 = p_both_1_1 / (p_item1_1 * p_item2_1) if (p_item1_1 * p_item2_1) > 0 else 0
    fd_1_0 = p_1_0 / (p_item1_1 * p_item2_0) if (p_item1_1 * p_item2_0) > 0 else 0
    fd_0_1 = p_0_1 / (p_item1_0 * p_item2_1) if (p_item1_0 * p_item2_1) > 0 else 0
    fd_0_0 = p_both_0_0 / (p_item1_0 * p_item2_0) if (p_item1_0 * p_item2_0) > 0 else 0
    
    return {
        'fd_1_1': fd_1_1,  # Item1=1, Item2=1
        'fd_1_0': fd_1_0,  # Item1=1, Item2=0
        'fd_0_1': fd_0_1,  # Item1=0, Item2=1
        'fd_0_0': fd_0_0,  # Item1=0, Item2=0
        'probabilities': {
            'p_item1_1': p_item1_1,
            'p_item1_0': p_item1_0,
            'p_item2_1': p_item2_1,
            'p_item2_0': p_item2_0,
            'p_both_1_1': p_both_1_1,
            'p_1_0': p_1_0,
            'p_0_1': p_0_1,
            'p_both_0_0': p_both_0_0
        },
        'formulas': {
            'fd_1_1_formula': f"{p_both_1_1:.3f} / ({p_item1_1:.3f} × {p_item2_1:.3f})",
            'fd_1_0_formula': f"{p_1_0:.3f} / ({p_item1_1:.3f} × {p_item2_0:.3f})",
            'fd_0_1_formula': f"{p_0_1:.3f} / ({p_item1_0:.3f} × {p_item2_1:.3f})",
            'fd_0_0_formula': f"{p_both_0_0:.3f} / ({p_item1_0:.3f} × {p_item2_0:.3f})"
        },
        'contingency_mapping': {
            'a': a,  # Item1=1, Item2=1
            'b': b,  # Item1=1, Item2=0
            'c': c,  # Item1=0, Item2=1
            'd': d   # Item1=0, Item2=0
        },
        'verification': {
            'example_calculation': f"FD(1,1) = P(1∩1)/[P(1)×P(1)] = ({a}/{n}) / [({a+b}/{n}) × ({a+c}/{n})] = {p_both_1_1:.3f} / ({p_item1_1:.3f} × {p_item2_1:.3f}) = {fd_1_1:.3f}"
        }
    }

def interpret_dependency_factors(fd_results, item1, item2):
    """Genera interpretaciones contextuales de los factores de dependencia"""
    interpretations = []
    
    fd_1_1 = fd_results['fd_1_1']
    fd_1_0 = fd_results['fd_1_0']
    fd_0_1 = fd_results['fd_0_1']
    fd_0_0 = fd_results['fd_0_0']
    
    # Interpretación principal
    if fd_0_1 > fd_1_1:
        if fd_0_1 > 1.2:
            interpretations.append(f"📈 **Comprar {item2} disminuye la compra de {item1}** (FD(~{item1}|{item2}) = {fd_0_1:.3f} > FD({item1}|{item2}) = {fd_1_1:.3f})")
        else:
            interpretations.append(f"⚠️ **Comprar {item2} tiende a disminuir la compra de {item1}** (FD(~{item1}|{item2}) = {fd_0_1:.3f})")
    elif fd_1_1 > fd_0_1:
        if fd_1_1 > 1.2:
            interpretations.append(f"📈 **Comprar {item2} aumenta la compra de {item1}** (FD({item1}|{item2}) = {fd_1_1:.3f} > FD(~{item1}|{item2}) = {fd_0_1:.3f})")
        else:
            interpretations.append(f"✅ **Comprar {item2} tiende a aumentar la compra de {item1}** (FD({item1}|{item2}) = {fd_1_1:.3f})")
    else:
        interpretations.append(f"⚪ **Comprar {item2} no afecta significativamente la compra de {item1}** (FD ≈ {fd_1_1:.3f})")
    
    # Interpretación secundaria
    if fd_0_0 > fd_1_0:
        interpretations.append(f"📉 **NO comprar {item2} disminuye la compra de {item1}** (FD(~{item1}|~{item2}) = {fd_0_0:.3f} > FD({item1}|~{item2}) = {fd_1_0:.3f})")
    elif fd_1_0 > fd_0_0:
        interpretations.append(f"📈 **NO comprar {item2} aumenta la compra de {item1}** (FD({item1}|~{item2}) = {fd_1_0:.3f} > FD(~{item1}|~{item2}) = {fd_0_0:.3f})")
    
    # Análisis detallado
    interpretations.append("---")
    interpretations.append("**Análisis detallado por celda:**")
    
    if fd_1_1 > 1.2:
        interpretations.append(f"✅ **Fuerte asociación positiva** entre {item1}=1 y {item2}=1 (FD = {fd_1_1:.3f})")
    elif fd_1_1 < 0.8:
        interpretations.append(f"❌ **Asociación negativa** entre {item1}=1 y {item2}=1 (FD = {fd_1_1:.3f})")
    else:
        interpretations.append(f"⚪ **Independencia** entre {item1}=1 y {item2}=1 (FD = {fd_1_1:.3f})")
    
    if fd_0_1 > 1.2:
        interpretations.append(f"⚠️ **Cuando se compra {item2}, es más probable NO comprar {item1}** (FD = {fd_0_1:.3f})")
    elif fd_0_1 < 0.8:
        interpretations.append(f"✅ **Cuando se compra {item2}, es menos probable NO comprar {item1}** (FD = {fd_0_1:.3f})")
    
    return interpretations

def calculate_metrics(data, item1, item2):
    """Calcula todas las métricas de asociación con manejo de errores"""
    try:
        # Crear tabla de contingencia
        contingency = pd.crosstab(data[item1], data[item2], margins=True)
        
        # Verificar que la tabla tiene el formato esperado
        if contingency.shape[0] < 3 or contingency.shape[1] < 3:
            # Crear tabla completa con ceros si faltan categorías
            full_contingency = pd.DataFrame(
                [[0, 0, 0], [0, 0, 0], [0, 0, 0]], 
                index=[0, 1, 'All'], 
                columns=[0, 1, 'All']
            )
            
            for i in contingency.index:
                for j in contingency.columns:
                    if i in full_contingency.index and j in full_contingency.columns:
                        full_contingency.loc[i, j] = contingency.loc[i, j]
            
            contingency = full_contingency
        
        # Extraer valores de forma segura
        a = contingency.iloc[1, 1] if contingency.shape[0] > 1 and contingency.shape[1] > 1 else 0
        b = contingency.iloc[1, 0] if contingency.shape[0] > 1 else 0
        c = contingency.iloc[0, 1] if contingency.shape[1] > 1 else 0
        d = contingency.iloc[0, 0] if contingency.shape[0] > 0 else 0
        n = contingency.iloc[-1, -1]
        
        # Calcular métricas básicas
        conf_1_to_2 = a / (a + b) if (a + b) > 0 else 0
        conf_2_to_1 = a / (a + c) if (a + c) > 0 else 0
        cov_1 = (a + b) / n if n > 0 else 0
        cov_2 = (a + c) / n if n > 0 else 0
        
        # Factor de dependencia ANTIGUO
        expected_a = (a + b) * (a + c) / n if n > 0 else 0
        dependency_factor_old = (a - expected_a) / expected_a if expected_a > 0 else 0
        
        # NUEVOS Factores de dependencia
        dependency_factors = calculate_dependency_factors(a, b, c, d, n)
        
        # Interpretaciones contextuales
        interpretations = interpret_dependency_factors(dependency_factors, item1, item2)
        
        # Chi-cuadrado
        denominator = (a + b) * (c + d) * (a + c) * (b + d)
        chi2_stat = n * (a * d - b * c) ** 2 / denominator if denominator > 0 else 0
        
        # Valores críticos
        critical_values = {
            '95%': 3.841,
            '99%': 6.635,
            '99.99%': 10.828
        }
        
        # Determinar significancia
        significance = []
        for level, critical in critical_values.items():
            if chi2_stat > critical:
                significance.append(level)
        
        # Todas las reglas de asociación
        all_rules = calculate_all_association_rules(a, b, c, d, n, item1, item2)
        
        return {
            'contingency': contingency,
            'a': int(a), 'b': int(b), 'c': int(c), 'd': int(d), 'n': int(n),
            'conf_1_to_2': float(conf_1_to_2),
            'conf_2_to_1': float(conf_2_to_1),
            'cov_1': float(cov_1),
            'cov_2': float(cov_2),
            'dependency_factor': float(dependency_factor_old),
            'dependency_factors': dependency_factors,
            'dependency_interpretations': interpretations,
            'chi2_stat': float(chi2_stat),
            'critical_values': critical_values,
            'significance': significance,
            'all_rules': all_rules
        }
    
    except Exception as e:
        st.error(f"Error calculando métricas: {str(e)}")
        return None

def calculate_all_association_rules(a, b, c, d, n, item1, item2):
    """Calcula todas las 8 reglas de asociación posibles"""
    
    rules = []
    
    # Reglas para item1 → item2
    cb_1_1 = a / n if n > 0 else 0
    cf_1_1 = a / (a + b) if (a + b) > 0 else 0
    rules.append({
        'rule': f'Si ({item1}=1) Entonces {item2}=1',
        'coverage': cb_1_1,
        'confidence': cf_1_1,
        'support': a,
        'total': a + b,
        'formula': f'({a}/{a + b})' if (a + b) > 0 else '(0/0)'
    })
    
    cb_1_0 = b / n if n > 0 else 0
    cf_1_0 = b / (a + b) if (a + b) > 0 else 0
    rules.append({
        'rule': f'Si ({item1}=1) Entonces {item2}=0',
        'coverage': cb_1_0,
        'confidence': cf_1_0,
        'support': b,
        'total': a + b,
        'formula': f'({b}/{a + b})' if (a + b) > 0 else '(0/0)'
    })
    
    cb_0_1 = c / n if n > 0 else 0
    cf_0_1 = c / (c + d) if (c + d) > 0 else 0
    rules.append({
        'rule': f'Si ({item1}=0) Entonces {item2}=1',
        'coverage': cb_0_1,
        'confidence': cf_0_1,
        'support': c,
        'total': c + d,
        'formula': f'({c}/{c + d})' if (c + d) > 0 else '(0/0)'
    })
    
    cb_0_0 = d / n if n > 0 else 0
    cf_0_0 = d / (c + d) if (c + d) > 0 else 0
    rules.append({
        'rule': f'Si ({item1}=0) Entonces {item2}=0',
        'coverage': cb_0_0,
        'confidence': cf_0_0,
        'support': d,
        'total': c + d,
        'formula': f'({d}/{c + d})' if (c + d) > 0 else '(0/0)'
    })
    
    # Reglas para item2 → item1
    cb_2_1 = a / n if n > 0 else 0
    cf_2_1 = a / (a + c) if (a + c) > 0 else 0
    rules.append({
        'rule': f'Si ({item2}=1) Entonces {item1}=1',
        'coverage': cb_2_1,
        'confidence': cf_2_1,
        'support': a,
        'total': a + c,
        'formula': f'({a}/{a + c})' if (a + c) > 0 else '(0/0)'
    })
    
    cb_2_0 = c / n if n > 0 else 0
    cf_2_0 = c / (a + c) if (a + c) > 0 else 0
    rules.append({
        'rule': f'Si ({item2}=1) Entonces {item1}=0',
        'coverage': cb_2_0,
        'confidence': cf_2_0,
        'support': c,
        'total': a + c,
        'formula': f'({c}/{a + c})' if (a + c) > 0 else '(0/0)'
    })
    
    cb_0_2 = b / n if n > 0 else 0
    cf_0_2 = b / (b + d) if (b + d) > 0 else 0
    rules.append({
        'rule': f'Si ({item2}=0) Entonces {item1}=1',
        'coverage': cb_0_2,
        'confidence': cf_0_2,
        'support': b,
        'total': b + d,
        'formula': f'({b}/{b + d})' if (b + d) > 0 else '(0/0)'
    })
    
    cb_0_0_2 = d / n if n > 0 else 0
    cf_0_0_2 = d / (b + d) if (b + d) > 0 else 0
    rules.append({
        'rule': f'Si ({item2}=0) Entonces {item1}=0',
        'coverage': cb_0_0_2,
        'confidence': cf_0_0_2,
        'support': d,
        'total': b + d,
        'formula': f'({d}/{b + d})' if (b + d) > 0 else '(0/0)'
    })
    
    return rules

def create_contingency_heatmap(contingency_table, item1, item2):
    """Crea heatmap de la tabla de contingencia"""
    try:
        data_matrix = contingency_table.iloc[:-1, :-1].values
        
        fig = go.Figure(data=go.Heatmap(
            z=data_matrix,
            x=[f'{item2}=0', f'{item2}=1'],
            y=[f'{item1}=0', f'{item1}=1'],
            colorscale='Blues',
            text=data_matrix,
            texttemplate="%{text}",
            textfont={"size": 20},
            hoverongaps=False,
            showscale=True
        ))
        
        fig.update_layout(
            title=f'Tabla de Contingencia: {item1} vs {item2}',
            xaxis_title=item2,
            yaxis_title=item1,
            font=dict(size=14),
            height=400,
            width=500,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        return fig
    
    except Exception as e:
        st.error(f"Error creando heatmap: {str(e)}")
        return go.Figure()

def create_metrics_chart(metrics, item1, item2):
    """Crea gráfico de métricas"""
    try:
        categories = [
            f'Confianza<br>{item1}→{item2}',
            f'Confianza<br>{item2}→{item1}',
            f'Cobertura<br>{item1}',
            f'Cobertura<br>{item2}'
        ]
        
        values = [
            metrics['conf_1_to_2'],
            metrics['conf_2_to_1'],
            metrics['cov_1'],
            metrics['cov_2']
        ]
        
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
        
        fig = go.Figure(data=[
            go.Bar(
                x=categories,
                y=values,
                marker_color=colors,
                text=[f'{v:.3f}' for v in values],
                textposition='auto',
            )
        ])
        
        fig.update_layout(
            title='Métricas de Asociación',
            yaxis_title='Valor',
            yaxis=dict(range=[0, 1]),
            font=dict(size=12),
            height=400,
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        return fig
    
    except Exception as e:
        st.error(f"Error creando gráfico de métricas: {str(e)}")
        return go.Figure()

def create_dependency_factors_chart(dependency_factors, item1, item2):
    """Crea gráfico con los 4 factores de dependencia - CORREGIDO"""
    try:
        # CORRECCIÓN: Organizar según la tabla de contingencia estándar
        categories = [
            f'{item1}=1<br>{item2}=1',  # a
            f'{item1}=1<br>{item2}=0',  # b
            f'{item1}=0<br>{item2}=1',  # c
            f'{item1}=0<br>{item2}=0'   # d
        ]
        
        values = [
            dependency_factors['fd_1_1'],  # a: Item1=1, Item2=1
            dependency_factors['fd_1_0'],  # b: Item1=1, Item2=0
            dependency_factors['fd_0_1'],  # c: Item1=0, Item2=1
            dependency_factors['fd_0_0']   # d: Item1=0, Item2=0
        ]
        
        colors = []
        for val in values:
            if val > 1.2:
                colors.append('#4CAF50')  # Verde - Asociación positiva fuerte
            elif val < 0.8:
                colors.append('#F44336')  # Rojo - Asociación negativa fuerte
            else:
                colors.append('#9E9E9E')  # Gris - Independencia
        
        fig = go.Figure(data=[
            go.Bar(
                x=categories,
                y=values,
                marker_color=colors,
                text=[f'{v:.3f}' for v in values],
                textposition='auto',
            )
        ])
        
        fig.add_hline(y=1, line_dash="dash", line_color="black", 
                      annotation_text="Independencia (FD = 1)")
        
        fig.update_layout(
            title=f'Factores de Dependencia: {item1} vs {item2}',
            yaxis_title='Factor de Dependencia',
            font=dict(size=12),
            height=400,
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        return fig
    
    except Exception as e:
        st.error(f"Error creando gráfico de factores de dependencia: {str(e)}")
        return go.Figure()

def create_all_rules_chart(all_rules):
    """Crea gráfico con todas las reglas de asociación"""
    try:
        rule_names = [rule['rule'].replace(' Entonces ', '→').replace('Si (', '').replace(')', '') for rule in all_rules]
        confidences = [rule['confidence'] for rule in all_rules]
        coverages = [rule['coverage'] for rule in all_rules]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Confianza',
            x=rule_names,
            y=confidences,
            marker_color='#FF6B6B',
            text=[f'{v:.1%}' for v in confidences],
            textposition='auto',
        ))
        
        fig.add_trace(go.Bar(
            name='Cobertura',
            x=rule_names,
            y=coverages,
            marker_color='#4ECDC4',
            text=[f'{v:.1%}' for v in coverages],
            textposition='auto',
        ))
        
        fig.update_layout(
            title='Todas las Reglas de Asociación',
            xaxis_title='Reglas',
            yaxis_title='Valor',
            yaxis=dict(range=[0, 1]),
            barmode='group',
            font=dict(size=10),
            height=500,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis_tickangle=-45
        )
        
        return fig
    
    except Exception as e:
        st.error(f"Error creando gráfico de todas las reglas: {str(e)}")
        return go.Figure()

def create_scatter_plot(data, item1, item2):
    """Crea gráfico de dispersión con jitter"""
    try:
        np.random.seed(42)
        x_jitter = data[item1] + np.random.normal(0, 0.05, len(data))
        y_jitter = data[item2] + np.random.normal(0, 0.05, len(data))
        
        colors = []
        for _, row in data.iterrows():
            if row[item1] == 1 and row[item2] == 1:
                colors.append('Ambos=1')
            elif row[item1] == 1 and row[item2] == 0:
                colors.append(f'{item1}=1, {item2}=0')
            elif row[item1] == 0 and row[item2] == 1:
                colors.append(f'{item1}=0, {item2}=1')
            else:
                colors.append('Ambos=0')
        
        fig = px.scatter(
            x=x_jitter, y=y_jitter,
            color=colors,
            title=f'Distribución de Datos: {item1} vs {item2}',
            labels={'x': item1, 'y': item2},
            color_discrete_map={
                'Ambos=1': '#FF6B6B',
                f'{item1}=1, {item2}=0': '#4ECDC4',
                f'{item1}=0, {item2}=1': '#45B7D1',
                'Ambos=0': '#96CEB4'
            }
        )
        
        fig.update_layout(
            height=400,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        fig.update_xaxes(range=[-0.3, 1.3], tickvals=[0, 1])
        fig.update_yaxes(range=[-0.3, 1.3], tickvals=[0, 1])
        
        return fig
    
    except Exception as e:
        st.error(f"Error creando gráfico de dispersión: {str(e)}")
        return go.Figure()

def create_chi_square_visualization(chi2_stat, critical_values):
    """Crea visualización de la prueba Chi-cuadrado"""
    try:
        x = np.linspace(0, max(15, chi2_stat + 2), 1000)
        y = chi2.pdf(x, df=1)
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=x, y=y,
            mode='lines',
            name='Distribución χ²',
            line=dict(color='blue', width=2)
        ))
        
        if chi2_stat > 0:
            fig.add_vline(
                x=chi2_stat,
                line_dash="dash",
                line_color="red",
                annotation_text=f"χ² calculado = {chi2_stat:.3f}",
                annotation_position="top"
            )
        
        colors = ['orange', 'purple', 'green']
        for i, (level, critical) in enumerate(critical_values.items()):
            fig.add_vline(
                x=critical,
                line_dash="dot",
                line_color=colors[i],
                annotation_text=f"{level}: {critical}",
                annotation_position="top"
            )
        
        fig.update_layout(
            title='Prueba Chi-Cuadrado',
            xaxis_title='Valor χ²',
            yaxis_title='Densidad',
            height=400,
            showlegend=True,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        return fig
    
    except Exception as e:
        st.error(f"Error creando visualización Chi-cuadrado: {str(e)}")
        return go.Figure()

def create_frequency_chart(data):
    """Crea gráfico de frecuencias por item"""
    try:
        freq_data = data.sum().sort_values(ascending=False)
        
        fig = px.bar(
            x=freq_data.index,
            y=freq_data.values,
            title="Frecuencia de cada Item",
            labels={'x': 'Items', 'y': 'Frecuencia'},
            color=freq_data.values,
            color_continuous_scale='viridis'
        )
        fig.update_layout(
            height=400,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        return fig
    
    except Exception as e:
        st.error(f"Error creando gráfico de frecuencias: {str(e)}")
        return go.Figure()

# Interfaz principal
def main():
    # Título principal
    st.markdown('<h1 class="main-header">📊 Analizador de Reglas de Asociación</h1>', unsafe_allow_html=True)
    
    # Inicializar session state
    if 'data' not in st.session_state:
        st.session_state.data = None
    if 'current_metrics' not in st.session_state:
        st.session_state.current_metrics = None
    if 'current_items' not in st.session_state:
        st.session_state.current_items = None
    
    # Sidebar para configuración
    with st.sidebar:
        st.header("⚙️ Configuración")
        
        data_option = st.radio(
            "Selecciona el método de carga:",
            ["📁 Cargar archivo Excel", "🎲 Generar datos aleatorios", "✏️ Entrada manual"]
        )
        
        if st.button("🗑️ Limpiar Datos"):
            st.session_state.data = None
            st.session_state.current_metrics = None
            st.session_state.current_items = None
            st.rerun()
    
    # Pestañas principales
    tab1, tab2, tab3, tab4 = st.tabs(["📥 Carga de Datos", "🔍 Análisis", "📊 Visualizaciones", "📋 Reporte"])
    
    with tab1:
        st.header("Carga de Datos")
        
        if data_option == "📁 Cargar archivo Excel":
            uploaded_file = st.file_uploader(
                "Selecciona un archivo Excel",
                type=['xlsx', 'xls'],
                help="El archivo debe contener datos binarios (0 y 1)"
            )
            
            if uploaded_file is not None:
                try:
                    data = pd.read_excel(uploaded_file)
                    
                    is_valid, message = validate_data(data)
                    if not is_valid:
                        st.error(f"Error en los datos: {message}")
                        return
                    
                    non_binary_cols = []
                    for col in data.columns:
                        unique_vals = data[col].dropna().unique()
                        if not all(val in [0, 1] for val in unique_vals):
                            non_binary_cols.append(col)
                    
                    if non_binary_cols:
                        st.warning(f"Las siguientes columnas contienen valores no binarios y serán convertidas: {', '.join(non_binary_cols)}")
                        for col in non_binary_cols:
                            data[col] = (data[col] > 0).astype(int)
                    
                    st.session_state.data = data
                    st.markdown('<div class="success-box"><strong>✅ Datos cargados correctamente</strong></div>', unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"Error al cargar el archivo: {str(e)}")
        
        elif data_option == "🎲 Generar datos aleatorios":
            col1, col2 = st.columns(2)
            
            with col1:
                n_items = st.slider("Número de items", 2, 8, 6)
            with col2:
                n_instances = st.slider("Número de instancias", 10, 500, 100)
            
            if st.button("🎲 Generar Datos", type="primary"):
                try:
                    st.session_state.data = generate_sample_data(n_items, n_instances)
                    st.markdown('<div class="success-box"><strong>✅ Datos generados correctamente</strong></div>', unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Error generando datos: {str(e)}")
        
        elif data_option == "✏️ Entrada manual":
            col1, col2 = st.columns(2)
            
            with col1:
                n_items = st.slider("Número de items", 2, 8, 4, key="manual_items")
            with col2:
                n_instances = st.slider("Número de instancias", 5, 50, 10, key="manual_instances")
            
            if 'manual_data_initialized' not in st.session_state:
                st.session_state.manual_data_initialized = False
                st.session_state.manual_data = None
            
            if st.button("📝 Crear Tabla Manual", key="create_manual_table"):
                items = [f"Item_{i+1}" for i in range(n_items)]
                
                manual_data = []
                for i in range(n_instances):
                    row = [0] * n_items
                    manual_data.append(row)
                
                st.session_state.manual_data = {
                    'data': manual_data,
                    'items': items,
                    'n_items': n_items,
                    'n_instances': n_instances
                }
                st.session_state.manual_data_initialized = True
                st.rerun()
            
            if st.session_state.manual_data_initialized and st.session_state.manual_data:
                st.subheader("✏️ Editar Datos")
                
                manual_info = st.session_state.manual_data
                items = manual_info['items']
                n_items = manual_info['n_items']
                n_instances = manual_info['n_instances']
                
                with st.form("manual_data_form", clear_on_submit=False):
                    st.write("**Instrucciones:** Selecciona 0 o 1 para cada celda")
                    
                    updated_data = []
                    
                    header_cols = st.columns([1] + [1] * n_items)
                    header_cols[0].write("**Instancia**")
                    for j, item in enumerate(items):
                        header_cols[j+1].write(f"**{item}**")
                    
                    for i in range(n_instances):
                        cols = st.columns([1] + [1] * n_items)
                        cols[0].write(f"Inst {i+1}")
                        
                        row = []
                        for j in range(n_items):
                            current_value = manual_info['data'][i][j] if i < len(manual_info['data']) and j < len(manual_info['data'][i]) else 0
                            
                            value = cols[j+1].selectbox(
                                f"",
                                options=[0, 1],
                                index=current_value,
                                key=f"manual_item_{i}_{j}",
                                label_visibility="collapsed"
                            )
                            row.append(value)
                        updated_data.append(row)
                    
                    col1, col2, col3 = st.columns([1, 1, 1])
                    
                    with col1:
                        if st.form_submit_button("💾 Guardar Datos", type="primary"):
                            try:
                                df = pd.DataFrame(updated_data, columns=items)
                                st.session_state.data = df
                                
                                st.session_state.manual_data_initialized = False
                                st.session_state.manual_data = None
                                
                                st.success("✅ Datos guardados correctamente")
                                st.rerun()
                                
                            except Exception as e:
                                st.error(f"Error guardando datos: {str(e)}")
                    
                    with col2:
                        if st.form_submit_button("🎲 Llenar Aleatoriamente"):
                            try:
                                random_data = []
                                for i in range(n_instances):
                                    row = [random.choice([0, 1]) for _ in range(n_items)]
                                    random_data.append(row)
                                
                                st.session_state.manual_data['data'] = random_data
                                st.success("🎲 Datos llenados aleatoriamente")
                                st.rerun()
                                
                            except Exception as e:
                                st.error(f"Error llenando datos: {str(e)}")
                    
                    with col3:
                        if st.form_submit_button("🗑️ Cancelar"):
                            st.session_state.manual_data_initialized = False
                            st.session_state.manual_data = None
                            st.rerun()
                
                if st.session_state.manual_data:
                    st.subheader("👀 Vista Previa")
                    preview_df = pd.DataFrame(
                        st.session_state.manual_data['data'], 
                        columns=st.session_state.manual_data['items']
                    )
                    st.dataframe(preview_df, use_container_width=True)
        
        # Mostrar datos cargados
        if st.session_state.data is not None:
            st.subheader("📋 Datos Cargados")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📊 Instancias", len(st.session_state.data))
            with col2:
                st.metric("🏷️ Items", len(st.session_state.data.columns))
            with col3:
                total_cells = len(st.session_state.data) * len(st.session_state.data.columns)
                density = st.session_state.data.sum().sum() / total_cells if total_cells > 0 else 0
                st.metric("🎯 Densidad", f"{density:.2%}")
            
            st.dataframe(st.session_state.data, use_container_width=True)
            
            st.subheader("📈 Frecuencias por Item")
            fig = create_frequency_chart(st.session_state.data)
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.header("Análisis de Asociación")
        
        if st.session_state.data is None:
            st.markdown('<div class="warning-box"><strong>⚠️ Primero debes cargar datos en la pestaña "Carga de Datos"</strong></div>', unsafe_allow_html=True)
        else:
            is_valid, message = validate_data(st.session_state.data)
            if not is_valid:
                st.error(f"Error en los datos: {message}")
                return
            
            col1, col2 = st.columns(2)
            
            with col1:
                item1 = st.selectbox("Selecciona Item 1", st.session_state.data.columns)
            with col2:
                available_items = [col for col in st.session_state.data.columns if col != item1]
                if available_items:
                    item2 = st.selectbox("Selecciona Item 2", available_items)
                else:
                    st.error("Se necesitan al menos 2 items diferentes")
                    return
            
            if st.button("🔍 Analizar Asociación", type="primary"):
                metrics = calculate_metrics(st.session_state.data, item1, item2)
                
                if metrics is None:
                    st.error("Error calculando métricas. Verifica los datos.")
                    return
                
                # Tabla de contingencia
                st.subheader("📋 Tabla de Contingencia")
                
                cont_display = metrics['contingency'].copy()
                cont_display.index = [f'{item1}=0', f'{item1}=1', 'Total']
                cont_display.columns = [f'{item2}=0', f'{item2}=1', 'Total']
                
                st.dataframe(cont_display, use_container_width=True)
                
                # Métricas principales
                st.subheader("📊 Métricas de Asociación Básicas")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>Confianza</h3>
                        <h2>{item1} → {item2}</h2>
                        <h1>{metrics['conf_1_to_2']:.3f}</h1>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>Confianza</h3>
                        <h2>{item2} → {item1}</h2>
                        <h1>{metrics['conf_2_to_1']:.3f}</h1>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>Cobertura</h3>
                        <h2>{item1}</h2>
                        <h1>{metrics['cov_1']:.3f}</h1>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>Cobertura</h3>
                        <h2>{item2}</h2>
                        <h1>{metrics['cov_2']:.3f}</h1>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Todas las reglas de asociación
                st.subheader("🔍 Todas las Reglas de Asociación")
                
                rules_data = []
                for rule in metrics['all_rules']:
                    rules_data.append({
                        'Regla': rule['rule'],
                        'Cobertura (Cb)': f"{rule['coverage']:.1%}",
                        'Confianza (Cf)': f"{rule['confidence']:.1%}",
                        'Fórmula': rule['formula']
                    })
                
                rules_df = pd.DataFrame(rules_data)
                st.dataframe(rules_df, use_container_width=True, hide_index=True)
                
                # Factor de dependencia mejorado
                st.subheader("🔗 Factores de Dependencia")
                
                dep_factors = metrics['dependency_factors']
                
                # En la sección de Factor de dependencia mejorado, reemplazar la tabla markdown con:

                st.markdown(f"""
### Tabla de Dependencia

| | **{item2}=1** | **{item2}=0** |
|---|---|---|
| **{item1}=1** | {dep_factors['fd_1_1']:.3f} | {dep_factors['fd_1_0']:.3f} |
| **{item1}=0** | {dep_factors['fd_0_1']:.3f} | {dep_factors['fd_0_0']:.3f} |

**Verificación de cálculos (siguiendo la fórmula de la imagen):**

**FD({item1}=1, {item2}=1):**
- P({item1}=1 ∩ {item2}=1) = {metrics['a']}/{metrics['n']} = {dep_factors['probabilities']['p_both_1_1']:.3f}
- P({item1}=1) = {metrics['a']+metrics['b']}/{metrics['n']} = {dep_factors['probabilities']['p_item1_1']:.3f}
- P({item2}=1) = {metrics['a']+metrics['c']}/{metrics['n']} = {dep_factors['probabilities']['p_item2_1']:.3f}
- FD = {dep_factors['probabilities']['p_both_1_1']:.3f} / ({dep_factors['probabilities']['p_item1_1']:.3f} × {dep_factors['probabilities']['p_item2_1']:.3f}) = **{dep_factors['fd_1_1']:.3f}**

**FD({item1}=1, {item2}=0):**
- P({item1}=1 ∩ {item2}=0) = {metrics['b']}/{metrics['n']} = {dep_factors['probabilities']['p_1_0']:.3f}
- P({item1}=1) = {dep_factors['probabilities']['p_item1_1']:.3f}
- P({item2}=0) = {dep_factors['probabilities']['p_item2_0']:.3f}
- FD = {dep_factors['probabilities']['p_1_0']:.3f} / ({dep_factors['probabilities']['p_item1_1']:.3f} × {dep_factors['probabilities']['p_item2_0']:.3f}) = **{dep_factors['fd_1_0']:.3f}**

**FD({item1}=0, {item2}=1):**
- P({item1}=0 ∩ {item2}=1) = {metrics['c']}/{metrics['n']} = {dep_factors['probabilities']['p_0_1']:.3f}
- P({item1}=0) = {dep_factors['probabilities']['p_item1_0']:.3f}
- P({item2}=1) = {dep_factors['probabilities']['p_item2_1']:.3f}
- FD = {dep_factors['probabilities']['p_0_1']:.3f} / ({dep_factors['probabilities']['p_item1_0']:.3f} × {dep_factors['probabilities']['p_item2_1']:.3f}) = **{dep_factors['fd_0_1']:.3f}**

**FD({item1}=0, {item2}=0):**
- P({item1}=0 ∩ {item2}=0) = {metrics['d']}/{metrics['n']} = {dep_factors['probabilities']['p_both_0_0']:.3f}
- P({item1}=0) = {dep_factors['probabilities']['p_item1_0']:.3f}
- P({item2}=0) = {dep_factors['probabilities']['p_item2_0']:.3f}
- FD = {dep_factors['probabilities']['p_both_0_0']:.3f} / ({dep_factors['probabilities']['p_item1_0']:.3f} × {dep_factors['probabilities']['p_item2_0']:.3f}) = **{dep_factors['fd_0_0']:.3f}**

**Fórmula general:** FD = P(A∩B) / (P(A) × P(B))
""")
                
                # Interpretaciones contextuales - CORREGIDAS
                st.subheader("💬 Interpretaciones")
                
                for interpretation in metrics['dependency_interpretations']:
                    st.write(interpretation)
                
                # Información sobre factores de dependencia - LIMPIA
                st.info("""
                **Cómo interpretar los Factores de Dependencia:**
                
                • FD > 1: Asociación positiva (aumenta la probabilidad)
                • FD < 1: Asociación negativa (disminuye la probabilidad)  
                • FD ≈ 1: Independencia (no hay asociación)
                
                **Ejemplo de interpretación:**
                Si FD(Pan=1, Mantequilla=0) > 1, significa que "Comprar Pan aumenta la probabilidad de NO comprar Mantequilla"
                """)
                
                # Prueba Chi-cuadrado
                st.subheader("🧮 Prueba Chi-Cuadrado")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Chi-cuadrado calculado", f"{metrics['chi2_stat']:.4f}")
                    
                    st.write("**Valores Críticos:**")
                    for level, critical in metrics['critical_values'].items():
                        is_significant = metrics['chi2_stat'] > critical
                        icon = "✅" if is_significant else "❌"
                        st.write(f"{icon} {level}: {critical}")
                
                with col2:
                    if metrics['significance']:
                        st.markdown(f"""
                        <div class="success-box">
                            <strong>🎉 ASOCIACIÓN SIGNIFICATIVA</strong><br>
                            Niveles de confianza: {', '.join(metrics['significance'])}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="warning-box">
                            <strong>⚠️ ASOCIACIÓN NO SIGNIFICATIVA</strong><br>
                            No hay evidencia estadística de asociación
                        </div>
                        """, unsafe_allow_html=True)
                
                # Guardar métricas
                st.session_state.current_metrics = metrics
                st.session_state.current_items = (item1, item2)
    
    with tab3:
        st.header("Visualizaciones")
        
        if st.session_state.current_metrics is None:
            st.markdown('<div class="warning-box"><strong>⚠️ Primero debes realizar un análisis en la pestaña "Análisis"</strong></div>', unsafe_allow_html=True)
        else:
            metrics = st.session_state.current_metrics
            item1, item2 = st.session_state.current_items
            
            # Gráfico de factores de dependencia
            st.subheader("🔗 Factores de Dependencia")
            fig_dependency = create_dependency_factors_chart(metrics['dependency_factors'], item1, item2)
            st.plotly_chart(fig_dependency, use_container_width=True)
            
            # Gráfico de todas las reglas
            st.subheader("📊 Todas las Reglas de Asociación")
            fig_all_rules = create_all_rules_chart(metrics['all_rules'])
            st.plotly_chart(fig_all_rules, use_container_width=True)
            
            # Gráficos en dos columnas
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🔥 Tabla de Contingencia")
                fig1 = create_contingency_heatmap(metrics['contingency'], item1, item2)
                st.plotly_chart(fig1, use_container_width=True)
                
                st.subheader("📊 Métricas Básicas")
                fig2 = create_metrics_chart(metrics, item1, item2)
                st.plotly_chart(fig2, use_container_width=True)
            
            with col2:
                st.subheader("🎯 Distribución")
                fig3 = create_scatter_plot(st.session_state.data, item1, item2)
                st.plotly_chart(fig3, use_container_width=True)
                
                st.subheader("📈 Chi-Cuadrado")
                fig4 = create_chi_square_visualization(metrics['chi2_stat'], metrics['critical_values'])
                st.plotly_chart(fig4, use_container_width=True)
    
    with tab4:
        st.header("Reporte Completo")
        
        if st.session_state.current_metrics is None:
            st.markdown('<div class="warning-box"><strong>⚠️ Primero debes realizar un análisis en la pestaña "Análisis"</strong></div>', unsafe_allow_html=True)
        else:
            metrics = st.session_state.current_metrics
            item1, item2 = st.session_state.current_items
            
            st.subheader(f"📄 Reporte de Análisis: {item1} vs {item2}")
            
            # Resumen ejecutivo
            st.markdown("### 📋 Resumen Ejecutivo")
            
            summary = f"""
            **Items Analizados:** {item1} y {item2}
            
            **Tamaño de la Muestra:** {metrics['n']} transacciones
            
            **Reglas de Asociación Principales:**
            - {item1} → {item2}: Confianza = {metrics['conf_1_to_2']:.3f}, Cobertura = {metrics['cov_1']:.3f}
            - {item2} → {item1}: Confianza = {metrics['conf_2_to_1']:.3f}, Cobertura = {metrics['cov_2']:.3f}
            
            **Factores de Dependencia:**
            - FD({item1}=1, {item2}=1) = {metrics['dependency_factors']['fd_1_1']:.3f}
            - FD({item1}=1, {item2}=0) = {metrics['dependency_factors']['fd_1_0']:.3f}
            - FD({item1}=0, {item2}=1) = {metrics['dependency_factors']['fd_0_1']:.3f}
            - FD({item1}=0, {item2}=0) = {metrics['dependency_factors']['fd_0_0']:.3f}
            
            **Significancia Estadística:** {'Sí' if metrics['significance'] else 'No'}
            {f"(Niveles: {', '.join(metrics['significance'])})" if metrics['significance'] else ""}
            """
            
            st.markdown(summary)
            
            # Tabla de contingencia detallada
            st.markdown("### 📊 Tabla de Contingencia Detallada")
            
            detailed_table = f"""
            |               | {item2}=0 | {item2}=1 | Total |
            |---------------|-----------|-----------|-------|
            | **{item1}=0** | {metrics['d']}        | {metrics['c']}        | {metrics['c']+metrics['d']}    |
            | **{item1}=1** | {metrics['b']}        | {metrics['a']}        | {metrics['a']+metrics['b']}    |
            | **Total**     | {metrics['b']+metrics['d']}        | {metrics['a']+metrics['c']}        | {metrics['n']}    |
            """
            
            st.markdown(detailed_table)
            
            # Análisis completo de factores de dependencia
            st.markdown("### 🔗 Análisis Completo de Factores de Dependencia")
            
            st.markdown("**Fórmula utilizada:** FD = P(A∩B) / (P(A) × P(B))")
            
            dep_factors = metrics['dependency_factors']
            
            st.markdown(f"""
            **Cálculos detallados:**
            
            1. **FD({item1}=1, {item2}=1)** = {dep_factors['formulas']['fd_1_1_formula']} = **{dep_factors['fd_1_1']:.3f}**
            2. **FD({item1}=1, {item2}=0)** = {dep_factors['formulas']['fd_1_0_formula']} = **{dep_factors['fd_1_0']:.3f}**
            3. **FD({item1}=0, {item2}=1)** = {dep_factors['formulas']['fd_0_1_formula']} = **{dep_factors['fd_0_1']:.3f}**
            4. **FD({item1}=0, {item2}=0)** = {dep_factors['formulas']['fd_0_0_formula']} = **{dep_factors['fd_0_0']:.3f}**
            """)
            
            # Análisis completo de reglas
            st.markdown("### 🔍 Análisis Completo de Reglas")
            
            st.markdown("**Todas las reglas de asociación calculadas:**")
            
            for i, rule in enumerate(metrics['all_rules'], 1):
                st.markdown(f"""
                **{i}.** {rule['rule']}
                - Cobertura = {rule['coverage']:.1%}
                - Confianza = {rule['confidence']:.1%} {rule['formula']}
                """)
            
            # Interpretación
            st.markdown("### 🔍 Interpretación de Resultados")
            
            st.markdown("**Interpretaciones de los Factores de Dependencia:**")
            for interpretation in metrics['dependency_interpretations']:
                st.markdown(interpretation)
            
            interpretation = []
            
            if metrics['conf_1_to_2'] > 0.7:
                interpretation.append(f"✅ **Alta confianza** en la regla {item1} → {item2} ({metrics['conf_1_to_2']:.1%})")
            elif metrics['conf_1_to_2'] > 0.5:
                interpretation.append(f"⚠️ **Confianza moderada** en la regla {item1} → {item2} ({metrics['conf_1_to_2']:.1%})")
            else:
                interpretation.append(f"❌ **Baja confianza** en la regla {item1} → {item2} ({metrics['conf_1_to_2']:.1%})")
            
            # Cobertura
            if metrics['cov_1'] > 0.3:
                interpretation.append(f"✅ **Alta cobertura** del item {item1} ({metrics['cov_1']:.1%})")
            elif metrics['cov_1'] > 0.1:
                interpretation.append(f"⚠️ **Cobertura moderada** del item {item1} ({metrics['cov_1']:.1%})")
            else:
                interpretation.append(f"❌ **Baja cobertura** del item {item1} ({metrics['cov_1']:.1%})")
            
            st.markdown("**Interpretaciones adicionales:**")
            for interp in interpretation:
                st.markdown(interp)
            
            # Recomendaciones
            st.markdown("### 💡 Recomendaciones")
            
            recommendations = []
            
            if metrics['conf_1_to_2'] > 0.6 and metrics['significance']:
                recommendations.append(f"🎯 Considerar promociones cruzadas: cuando los clientes compren {item1}, ofrecer {item2}")
            
            if metrics['cov_1'] > 0.3 and metrics['cov_2'] > 0.3:
                recommendations.append(f"📦 Crear paquetes combinados de {item1} y {item2}")
            
            if not metrics['significance']:
                recommendations.append(f"🔍 Los items {item1} y {item2} parecen ser independientes, considerar otros pares de items")
            
            # Recomendaciones basadas en factores de dependencia
            if dep_factors['fd_1_1'] > 1.2:
                recommendations.append(f"✅ **Estrategia de venta cruzada:** Promover {item2} cuando se compre {item1}")
            
            if dep_factors['fd_1_0'] > 1.2:
                recommendations.append(f"⚠️ **Productos sustitutos:** {item1} y {item2} pueden ser sustitutos, considerar estrategias diferenciadas")
            
            if not recommendations:
                recommendations.append("📝 Analizar más pares de items para encontrar asociaciones significativas")
            
            for rec in recommendations:
                st.markdown(rec)
            
            # Información adicional
            st.markdown("### ℹ️ Información Adicional")
            st.markdown("""
            **Cómo interpretar las métricas:**
            - **Confianza**: Probabilidad de que ocurra B dado que ocurrió A
            - **Cobertura**: Frecuencia relativa del item en el dataset
            - **Factor de Dependencia**: FD = P(A∩B) / (P(A) × P(B))
              - FD > 1: Asociación positiva
              - FD < 1: Asociación negativa  
              - FD ≈ 1: Independencia
            - **Chi-cuadrado**: Prueba de independencia estadística
            
            **Interpretación de las 8 reglas:**
            - Las reglas muestran todas las combinaciones posibles entre los items
            - Cada regla tiene su propia cobertura y confianza
            - Las reglas complementarias suman 100% en confianza para cada antecedente
            
            **Interpretación de los 4 Factores de Dependencia:**
            - Muestran cómo cada combinación de valores afecta la probabilidad
            - Permiten identificar patrones de compra y sustitución
            - Son útiles para estrategias de marketing y gestión de inventario
            """)

if __name__ == "__main__":
    main()
