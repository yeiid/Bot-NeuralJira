import sys
import os

def print_help():
    print("🚀 NeuralJira - Marketing Engine")
    print("=" * 30)
    print("Opciones:")
    print("  dashboard    : Lanza la interfaz visual (Streamlit)")
    print("  news         : Genera y publica post de noticias automático")
    print("  tutorial     : Genera y publica tutorial (requiere tema)")
    print("  test         : Valida conexión Facebook")
    print("=" * 30)

def main():
    if len(sys.argv) < 2:
        print_help()
        return

    cmd = sys.argv[1].lower()
    
    if cmd == "dashboard":
        print("Lanzando Dashboard...")
        os.system("streamlit run marketing_engine/dashboard.py")
    elif cmd == "news":
        from marketing_engine.orchestrator import MarketingOrchestrator
        orch = MarketingOrchestrator()
        orch.run_news_cycle()
    elif cmd == "tutorial":
        from marketing_engine.orchestrator import MarketingOrchestrator
        orch = MarketingOrchestrator()
        topic = sys.argv[2] if len(sys.argv) > 2 else "NeuralJira Bot"
        orch.run_tutorial_cycle(topic)
    elif cmd == "test":
        from marketing_engine.core.facebook_api import FacebookAPI
        api = FacebookAPI()
        success, msg = api.validate_connection()
        print(f"Facebook: {msg}")
    else:
        print_help()

if __name__ == "__main__":
    main()
