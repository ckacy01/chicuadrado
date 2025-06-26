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

# JavaScript para detectar modo oscuro y aplicar estilos
st.markdown("""
<script>
function applyThemeStyles() {
    // Detectar si estamos en modo oscuro
    const isDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    const streamlitDark = document.querySelector('[data-theme="dark"]') !== null;
    const bodyDark = document.body.classList.contains('dark') || 
                     getComputedStyle(document.body).backgroundColor === 'rgb(14, 17, 23)';
    
    const isActuallyDark = isDark || streamlitDark || bodyDark;
    
    // Aplicar clase al body
    if (isActuallyDark) {
        document.body.classList.add('dark-mode');
    } else {
        document.body.classList.remove('dark-mode');
    }
}

// Ejecutar al cargar y cuando cambie el tema
document.addEventListener('DOMContentLoaded', applyThemeStyles);
if (window.matchMedia) {
    window.matchMedia('(prefers-color-scheme: dark)').addListener(applyThemeStyles);
}

// Ejecutar periódicamente para detectar cambios de Streamlit
setInterval(applyThemeStyles, 1000);
</script>
""", unsafe_allow_html=True)

# CSS mejorado con detección de modo oscuro
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
    
    /* Cajas de información - MODO CLARO */
    .info-box {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%) !important;
        padding: 1rem !important;
        border-radius: 10px !important;
        margin: 1rem 0 !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
        color: #262730 !important;
    }
    
    .info-box * {
        color: #262730 !important;
    }
    
    /* MODO OSCURO - Detectado por JavaScript */
    .dark-mode .info-box {
        background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%) !important;
        color: #ffffff !important;
    }
    
    .dark-mode .info-box * {
        color: #ffffff !important;
    }
    
    /* Detección alternativa de modo oscuro por CSS */
    @media (prefers-color-scheme: dark) {
        .info-box {
            background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%) !important;
            color: #ffffff !important;
        }
        
        .info-box * {
            color: #ffffff !important;
        }
    }
    
    /* Detección por atributo de Streamlit */
    [data-theme="dark"] .info-box {
        background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%) !important;
        color: #ffffff !important;
    }
    
    [data-theme="dark"] .info-box * {
        color: #ffffff !important;
    }
    
    /* Detección por color de fondo del body */
    body[style*="rgb(14, 17, 23)"] .info-box,
    body[style*="background-color: rgb(14, 17, 23)"] .info-box {
        background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%) !important;
        color: #ffffff !important;
    }
    
    body[style*="rgb(14, 17, 23)"] .info-box *,
    body[style*="background-color: rgb(14, 17, 23)"] .info-box * {
        color: #ffffff !important;
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
    
    /* Forzar estilos en elementos específicos de Streamlit */
    div[data-testid="metric-container"] {
        background: transparent !important;
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
        a = contingency.iloc[1, 1] if contingency.shape[0] > 1 and contingency.shape[1] > 1 else 0  # ambos = 1
        b = contingency.iloc[1, 0] if contingency.shape[0] > 1 else 0  # item1=1, item2=0
        c = contingency.iloc[0, 1] if contingency.shape[1] > 1 else 0  # item1=0, item2=1
        d = contingency.iloc[0, 0] if contingency.shape[0] > 0 else 0  # ambos = 0
        n = contingency.iloc[-1, -1]  # total
        
        # Calcular métricas con división segura
        conf_1_to_2 = a / (a + b) if (a + b) > 0 else 0
        conf_2_to_1 = a / (a + c) if (a + c) > 0 else 0
        cov_1 = (a + b) / n if n > 0 else 0
        cov_2 = (a + c) / n if n > 0 else 0
        
        # Factor de dependencia
        expected_a = (a + b) * (a + c) / n if n > 0 else 0
        dependency_factor = (a - expected_a) / expected_a if expected_a > 0 else 0
        
        # Chi-cuadrado con verificación de denominador
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
        
        return {
            'contingency': contingency,
            'a': int(a), 'b': int(b), 'c': int(c), 'd': int(d), 'n': int(n),
            'conf_1_to_2': float(conf_1_to_2),
            'conf_2_to_1': float(conf_2_to_1),
            'cov_1': float(cov_1),
            'cov_2': float(cov_2),
            'dependency_factor': float(dependency_factor),
            'chi2_stat': float(chi2_stat),
            'critical_values': critical_values,
            'significance': significance
        }
    
    except Exception as e:
        st.error(f"Error calculando métricas: {str(e)}")
        return None

def create_contingency_heatmap(contingency_table, item1, item2):
    """Crea heatmap de la tabla de contingencia"""
    try:
        # Preparar datos sin totales
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

def create_scatter_plot(data, item1, item2):
    """Crea gráfico de dispersión con jitter"""
    try:
        # Añadir jitter para mejor visualización
        np.random.seed(42)  # Para reproducibilidad
        x_jitter = data[item1] + np.random.normal(0, 0.05, len(data))
        y_jitter = data[item2] + np.random.normal(0, 0.05, len(data))
        
        # Crear colores basados en combinaciones
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
        
        # Curva de distribución
        fig.add_trace(go.Scatter(
            x=x, y=y,
            mode='lines',
            name='Distribución χ²',
            line=dict(color='blue', width=2)
        ))
        
        # Valor calculado
        if chi2_stat > 0:
            fig.add_vline(
                x=chi2_stat,
                line_dash="dash",
                line_color="red",
                annotation_text=f"χ² calculado = {chi2_stat:.3f}",
                annotation_position="top"
            )
        
        # Valores críticos
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
        
        # Opción de carga de datos
        data_option = st.radio(
            "Selecciona el método de carga:",
            ["📁 Cargar archivo Excel", "🎲 Generar datos aleatorios", "✏️ Entrada manual"]
        )
        
        # Botón para limpiar datos
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
                    
                    # Validar datos
                    is_valid, message = validate_data(data)
                    if not is_valid:
                        st.error(f"Error en los datos: {message}")
                        return
                    
                    # Convertir valores no binarios
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
                n_items = st.slider("Número de items", 2, 8, 4)
            with col2:
                n_instances = st.slider("Número de instancias", 5, 50, 10)
            
            if st.button("📝 Crear Tabla Manual"):
                items = [f"Item_{i+1}" for i in range(n_items)]
                
                # Crear formulario para entrada manual
                with st.form("manual_data_form"):
                    st.write("Ingresa los datos (0 o 1):")
                    
                    data = []
                    for i in range(n_instances):
                        cols = st.columns(n_items + 1)
                        cols[0].write(f"Inst {i+1}")
                        
                        row = []
                        for j in range(n_items):
                            value = cols[j+1].selectbox(
                                f"{items[j]}",
                                [0, 1],
                                key=f"item_{i}_{j}",
                                label_visibility="collapsed"
                            )
                            row.append(value)
                        data.append(row)
                    
                    if st.form_submit_button("💾 Guardar Datos", type="primary"):
                        try:
                            st.session_state.data = pd.DataFrame(data, columns=items)
                            st.success("Datos guardados correctamente")
                        except Exception as e:
                            st.error(f"Error guardando datos: {str(e)}")
        
        # Mostrar datos cargados
        if st.session_state.data is not None:
            st.subheader("📋 Datos Cargados")
            
            # Estadísticas básicas
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📊 Instancias", len(st.session_state.data))
            with col2:
                st.metric("🏷️ Items", len(st.session_state.data.columns))
            with col3:
                total_cells = len(st.session_state.data) * len(st.session_state.data.columns)
                density = st.session_state.data.sum().sum() / total_cells if total_cells > 0 else 0
                st.metric("🎯 Densidad", f"{density:.2%}")
            
            # Mostrar tabla
            st.dataframe(st.session_state.data, use_container_width=True)
            
            # Frecuencias por item
            st.subheader("📈 Frecuencias por Item")
            fig = create_frequency_chart(st.session_state.data)
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.header("Análisis de Asociación")
        
        if st.session_state.data is None:
            st.markdown('<div class="warning-box"><strong>⚠️ Primero debes cargar datos en la pestaña "Carga de Datos"</strong></div>', unsafe_allow_html=True)
        else:
            # Validar datos antes del análisis
            is_valid, message = validate_data(st.session_state.data)
            if not is_valid:
                st.error(f"Error en los datos: {message}")
                return
            
            # Selección de items
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
                # Calcular métricas
                metrics = calculate_metrics(st.session_state.data, item1, item2)
                
                if metrics is None:
                    st.error("Error calculando métricas. Verifica los datos.")
                    return
                
                # Mostrar tabla de contingencia
                st.subheader("📋 Tabla de Contingencia")
                
                # Crear tabla más visual
                cont_display = metrics['contingency'].copy()
                cont_display.index = [f'{item1}=0', f'{item1}=1', 'Total']
                cont_display.columns = [f'{item2}=0', f'{item2}=1', 'Total']
                
                st.dataframe(cont_display, use_container_width=True)
                
                # Métricas principales
                st.subheader("📊 Métricas de Asociación")
                
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
                
                # Factor de dependencia
                st.subheader("🔗 Factor de Dependencia")
                
                dep_text = "Asociación Positiva" if metrics['dependency_factor'] > 0 else "Asociación Negativa" if metrics['dependency_factor'] < 0 else "Sin Asociación"
                
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.metric(
                        "Factor de Dependencia",
                        f"{metrics['dependency_factor']:.4f}",
                        delta=dep_text
                    )
                
                with col2:
                    st.markdown(f"""
                    <div class="info-box">
                        <strong>Interpretación:</strong><br>
                        • Factor > 0: Los items tienden a aparecer juntos<br>
                        • Factor < 0: Los items tienden a excluirse mutuamente<br>
                        • Factor ≈ 0: Los items son independientes
                    </div>
                    """, unsafe_allow_html=True)
                
                # Prueba Chi-cuadrado
                st.subheader("🧮 Prueba Chi-Cuadrado")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Chi-cuadrado calculado", f"{metrics['chi2_stat']:.4f}")
                    
                    # Mostrar valores críticos
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
                
                # Guardar métricas en session_state
                st.session_state.current_metrics = metrics
                st.session_state.current_items = (item1, item2)
    
    with tab3:
        st.header("Visualizaciones")
        
        if st.session_state.current_metrics is None:
            st.markdown('<div class="warning-box"><strong>⚠️ Primero debes realizar un análisis en la pestaña "Análisis"</strong></div>', unsafe_allow_html=True)
        else:
            metrics = st.session_state.current_metrics
            item1, item2 = st.session_state.current_items
            
            # Gráficos en dos columnas
            col1, col2 = st.columns(2)
            
            with col1:
                # Heatmap de contingencia
                st.subheader("🔥 Tabla de Contingencia")
                fig1 = create_contingency_heatmap(metrics['contingency'], item1, item2)
                st.plotly_chart(fig1, use_container_width=True)
                
                # Gráfico de métricas
                st.subheader("📊 Métricas")
                fig2 = create_metrics_chart(metrics, item1, item2)
                st.plotly_chart(fig2, use_container_width=True)
            
            with col2:
                # Gráfico de dispersión
                st.subheader("🎯 Distribución")
                fig3 = create_scatter_plot(st.session_state.data, item1, item2)
                st.plotly_chart(fig3, use_container_width=True)
                
                # Visualización Chi-cuadrado
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
            
            # Generar reporte
            st.subheader(f"📄 Reporte de Análisis: {item1} vs {item2}")
            
            # Resumen ejecutivo
            st.markdown("### 📋 Resumen Ejecutivo")
            
            summary = f"""
            **Items Analizados:** {item1} y {item2}
            
            **Tamaño de la Muestra:** {metrics['n']} transacciones
            
            **Reglas de Asociación:**
            - {item1} → {item2}: Confianza = {metrics['conf_1_to_2']:.3f}, Cobertura = {metrics['cov_1']:.3f}
            - {item2} → {item1}: Confianza = {metrics['conf_2_to_1']:.3f}, Cobertura = {metrics['cov_2']:.3f}
            
            **Factor de Dependencia:** {metrics['dependency_factor']:.4f}
            
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
            
            # Interpretación
            st.markdown("### 🔍 Interpretación de Resultados")
            
            interpretation = []
            
            # Confianza
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
            
            # Dependencia
            if abs(metrics['dependency_factor']) > 0.5:
                dep_type = "fuerte" if metrics['dependency_factor'] > 0 else "fuerte negativa"
                interpretation.append(f"✅ **Dependencia {dep_type}** entre los items")
            elif abs(metrics['dependency_factor']) > 0.2:
                dep_type = "moderada" if metrics['dependency_factor'] > 0 else "moderada negativa"
                interpretation.append(f"⚠️ **Dependencia {dep_type}** entre los items")
            else:
                interpretation.append(f"❌ **Dependencia débil** entre los items")
            
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
            
            if metrics['dependency_factor'] < -0.3:
                recommendations.append(f"⚠️ Los items {item1} y {item2} tienden a excluirse mutuamente")
            
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
            - **Factor de Dependencia**: Medida de asociación entre items
            - **Chi-cuadrado**: Prueba de independencia estadística
            """)

if __name__ == "__main__":
    main()
