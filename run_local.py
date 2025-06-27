"""
Script para ejecutar la aplicación localmente
"""
import subprocess
import sys
import os

def check_requirements():
    """Verifica que las dependencias estén instaladas"""
    try:
        import streamlit
        import pandas
        import numpy
        import plotly
        import scipy
        print("✅ Todas las dependencias están instaladas")
        return True
    except ImportError as e:
        print(f"❌ Falta dependencia: {e}")
        return False

def install_requirements():
    """Instala las dependencias necesarias"""
    print("📦 Instalando dependencias...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencias instaladas correctamente")
        return True
    except subprocess.CalledProcessError:
        print("❌ Error instalando dependencias")
        return False

def run_app():
    """Ejecuta la aplicación Streamlit"""
    print("🚀 Iniciando aplicación...")
    print("🌐 La aplicación se abrirá en: http://localhost:8501")
    print("⏹️  Para detener, presiona Ctrl+C")
    
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
    except KeyboardInterrupt:
        print("\n👋 Aplicación cerrada")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    print("📊 Analizador de Reglas de Asociación")
    print("=" * 40)
    
    # Verificar archivo principal
    if not os.path.exists("app.py"):
        print("❌ Archivo app.py no encontrado")
        return
    
    # Verificar dependencias
    if not check_requirements():
        if not install_requirements():
            return
    
    # Ejecutar aplicación
    run_app()

if __name__ == "__main__":
    main()

