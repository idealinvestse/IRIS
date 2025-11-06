"""
IRIS v6.0 - Model Configuration Examples
Exempel på hur man använder modellkonfigurationssystemet
"""

from src.core.model_config import get_model_config_manager
from src.core.config import get_settings


def exempel_1_lista_modeller():
    """Exempel 1: Lista alla tillgängliga modeller"""
    print("\n" + "="*60)
    print("EXEMPEL 1: Lista alla modeller")
    print("="*60)
    
    manager = get_model_config_manager()
    models = manager.list_all_models()
    
    for key, beskrivning in models.items():
        print(f"• {key:20} - {beskrivning}")


def exempel_2_hämta_modell_info():
    """Exempel 2: Hämta detaljerad information om en modell"""
    print("\n" + "="*60)
    print("EXEMPEL 2: Hämta modellinformation")
    print("="*60)
    
    manager = get_model_config_manager()
    model = manager.get_model("kimi-k2")
    
    if model:
        print(f"Namn: {model.namn}")
        print(f"Provider: {model.provider}")
        print(f"Model ID: {model.model_id}")
        print(f"Max tokens: {model.max_tokens}")
        print(f"Temperature: {model.default_temperature}")
        print(f"Streaming: {'✅' if model.supports_streaming else '❌'}")
        print(f"Hastighet: {model.hastighet}")
        print(f"Kostnad: {model.kostnad}")
        print(f"Rekommenderad för: {', '.join(model.rekommenderad_för)}")


def exempel_3_filtrera_modeller():
    """Exempel 3: Filtrera modeller baserat på kriterier"""
    print("\n" + "="*60)
    print("EXEMPEL 3: Filtrera modeller")
    print("="*60)
    
    manager = get_model_config_manager()
    
    # Hämta alla Groq-modeller med streaming
    filtered = manager.filter_models(
        provider="groq",
        streaming=True
    )
    
    print(f"Groq-modeller med streaming: {', '.join(filtered)}")
    
    # Hämta billiga modeller
    cheap = manager.filter_models(max_kostnad="låg")
    print(f"Billiga modeller: {', '.join(cheap)}")
    
    # Hämta privata modeller
    private = manager.filter_models(privat=True)
    print(f"Privata modeller: {', '.join(private)}")


def exempel_4_profil_modeller():
    """Exempel 4: Hämta modeller för profiler"""
    print("\n" + "="*60)
    print("EXEMPEL 4: Profil-modeller")
    print("="*60)
    
    manager = get_model_config_manager()
    
    profiler = ["snabb", "smart", "privat"]
    for profil in profiler:
        primary = manager.get_model_for_profile(profil)
        fallbacks = manager.get_fallback_models(profil)
        print(f"\nProfil '{profil}':")
        print(f"  Primär: {primary}")
        print(f"  Fallbacks: {', '.join(fallbacks)}")


def exempel_5_användningsfall():
    """Exempel 5: Rekommenderade modeller för användningsfall"""
    print("\n" + "="*60)
    print("EXEMPEL 5: Användningsfall")
    print("="*60)
    
    manager = get_model_config_manager()
    
    användningsfall = ["snabba_svar", "komplexa_analyser", "privat_känslig_data"]
    for case in användningsfall:
        models = manager.get_recommended_models(case)
        print(f"\n{case}:")
        for model_key in models:
            model = manager.get_model(model_key)
            if model:
                print(f"  • {model.namn} ({model.hastighet}, {model.kostnad})")


def exempel_6_settings_integration():
    """Exempel 6: Använda med Settings"""
    print("\n" + "="*60)
    print("EXEMPEL 6: Settings Integration")
    print("="*60)
    
    settings = get_settings()
    
    # Hämta modell för en profil
    model_id = settings.get_model_for_profile("snabb")
    print(f"Modell för 'snabb' profil: {model_id}")
    
    # Hämta manager från settings
    manager = settings.get_model_config_manager()
    model = manager.get_model_by_id(model_id)
    if model:
        print(f"Modell namn: {model.namn}")
        print(f"Beskrivning: {model.beskrivning}")


def exempel_7_välj_bästa_modell():
    """Exempel 7: Dynamiskt välja bästa modell"""
    print("\n" + "="*60)
    print("EXEMPEL 7: Välj bästa modell dynamiskt")
    print("="*60)
    
    def välj_modell(användningsfall: str, max_kostnad: str = "medel"):
        """Välj bästa modellen för ett användningsfall"""
        manager = get_model_config_manager()
        
        # Få rekommendationer
        rekommenderade = manager.get_recommended_models(användningsfall)
        
        if not rekommenderade:
            return "lokal"
        
        # Filtrera på kostnad
        kostnad_ordning = {"gratis": 0, "låg": 1, "medel": 2, "hög": 3}
        max_värde = kostnad_ordning.get(max_kostnad, 999)
        
        for model_key in rekommenderade:
            model = manager.get_model(model_key)
            if model:
                modell_värde = kostnad_ordning.get(model.kostnad, 999)
                if modell_värde <= max_värde:
                    return model_key
        
        return rekommenderade[0]
    
    # Test med olika användningsfall
    cases = [
        ("snabba_svar", "låg"),
        ("komplexa_analyser", "medel"),
        ("privat_känslig_data", "gratis")
    ]
    
    for case, max_cost in cases:
        vald = välj_modell(case, max_cost)
        model = get_model_config_manager().get_model(vald)
        print(f"\n{case} (max: {max_cost}):")
        print(f"  Vald modell: {vald}")
        if model:
            print(f"  Kostnad: {model.kostnad}, Hastighet: {model.hastighet}")


def exempel_8_modell_jämförelse():
    """Exempel 8: Jämföra modeller"""
    print("\n" + "="*60)
    print("EXEMPEL 8: Jämför modeller")
    print("="*60)
    
    manager = get_model_config_manager()
    
    # Jämför Groq-modeller
    groq_models = manager.get_models_by_provider("groq")
    
    print("\nGroq Modeller Jämförelse:")
    print(f"{'Namn':<25} {'Max Tokens':<12} {'Streaming':<10} {'Hastighet':<15} {'Kostnad'}")
    print("-" * 80)
    
    for model in groq_models:
        streaming = "✅" if model.supports_streaming else "❌"
        print(f"{model.namn:<25} {model.max_tokens:<12} {streaming:<10} {model.hastighet:<15} {model.kostnad}")


def main():
    """Kör alla exempel"""
    exempel_1_lista_modeller()
    exempel_2_hämta_modell_info()
    exempel_3_filtrera_modeller()
    exempel_4_profil_modeller()
    exempel_5_användningsfall()
    exempel_6_settings_integration()
    exempel_7_välj_bästa_modell()
    exempel_8_modell_jämförelse()
    
    print("\n" + "="*60)
    print("✅ Alla exempel slutförda!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
