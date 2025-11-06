"""
IRIS v6.0 - Model Manager CLI
Kommandoradsverktyg för att hantera AI-modeller
"""

import argparse
import sys
from typing import Optional
from tabulate import tabulate
from src.core.model_config import get_model_config_manager


def list_models(provider: Optional[str] = None, streaming: Optional[bool] = None):
    """Lista alla tillgängliga modeller"""
    manager = get_model_config_manager()
    
    if provider or streaming is not None:
        models = manager.filter_models(provider=provider, streaming=streaming)
    else:
        models = list(manager.models.keys())
    
    if not models:
        print("❌ Inga modeller hittades med de valda kriterierna")
        return
    
    # Skapa tabell
    headers = ["Nyckel", "Namn", "Provider", "Hastighet", "Kostnad", "Streaming"]
    rows = []
    
    for model_key in models:
        model = manager.get_model(model_key)
        if model:
            rows.append([
                model_key,
                model.namn,
                model.provider,
                model.hastighet,
                model.kostnad,
                "✅" if model.supports_streaming else "❌"
            ])
    
    print("\n🤖 Tillgängliga AI-modeller:")
    print(tabulate(rows, headers=headers, tablefmt="grid"))
    print(f"\nTotalt: {len(rows)} modeller\n")


def show_model_info(model_key: str):
    """Visa detaljerad information om en modell"""
    manager = get_model_config_manager()
    model = manager.get_model(model_key)
    
    if not model:
        print(f"❌ Modellen '{model_key}' hittades inte")
        return
    
    print(f"\n{'='*60}")
    print(f"🤖 {model.namn}")
    print(f"{'='*60}")
    print(f"Nyckel:           {model_key}")
    print(f"Provider:         {model.provider}")
    print(f"Model ID:         {model.model_id}")
    print(f"Beskrivning:      {model.beskrivning}")
    print(f"Max Tokens:       {model.max_tokens}")
    print(f"Default Temp:     {model.default_temperature}")
    print(f"Streaming:        {'✅ Ja' if model.supports_streaming else '❌ Nej'}")
    print(f"Vision:           {'✅ Ja' if model.supports_vision else '❌ Nej'}")
    print(f"Hastighet:        {model.hastighet}")
    print(f"Kostnad:          {model.kostnad}")
    print(f"Privat:           {'✅ Ja' if model.privat else '❌ Nej'}")
    print(f"\nRekommenderad för:")
    for item in model.rekommenderad_för:
        print(f"  • {item}")
    print(f"{'='*60}\n")


def show_profile_models(profile_name: str):
    """Visa modeller för en profil"""
    manager = get_model_config_manager()
    
    primary = manager.get_model_for_profile(profile_name)
    fallbacks = manager.get_fallback_models(profile_name)
    
    if not primary:
        print(f"❌ Profilen '{profile_name}' hittades inte")
        return
    
    print(f"\n📋 Modeller för profil: {profile_name}")
    print(f"{'='*60}")
    print(f"Primär modell:    {primary}")
    if fallbacks:
        print(f"Fallback-modeller:")
        for fb in fallbacks:
            print(f"  • {fb}")
    else:
        print(f"Fallback-modeller: Inga")
    print(f"{'='*60}\n")


def show_use_case(use_case: str):
    """Visa rekommenderade modeller för ett användningsfall"""
    manager = get_model_config_manager()
    models = manager.get_recommended_models(use_case)
    
    if not models:
        print(f"❌ Användningsfallet '{use_case}' hittades inte")
        return
    
    case_config = manager.användningsfall.get(use_case, {})
    beskrivning = case_config.get('beskrivning', 'Ingen beskrivning')
    
    print(f"\n💡 Användningsfall: {use_case}")
    print(f"{'='*60}")
    print(f"Beskrivning: {beskrivning}")
    print(f"\nRekommenderade modeller:")
    for model_key in models:
        model = manager.get_model(model_key)
        if model:
            print(f"  • {model_key} - {model.namn} ({model.hastighet}, {model.kostnad})")
    print(f"{'='*60}\n")


def list_profiles():
    """Lista alla profiler"""
    manager = get_model_config_manager()
    
    print(f"\n📋 Tillgängliga profiler:")
    print(f"{'='*60}")
    
    for profile_name in manager.profil_modeller.keys():
        primary = manager.get_model_for_profile(profile_name)
        print(f"• {profile_name:<15} → {primary}")
    
    print(f"{'='*60}\n")


def list_use_cases():
    """Lista alla användningsfall"""
    manager = get_model_config_manager()
    
    print(f"\n💡 Tillgängliga användningsfall:")
    print(f"{'='*60}")
    
    for use_case, config in manager.användningsfall.items():
        beskrivning = config.get('beskrivning', 'Ingen beskrivning')
        print(f"• {use_case:<25} - {beskrivning}")
    
    print(f"{'='*60}\n")


def main():
    """Main CLI funktion"""
    parser = argparse.ArgumentParser(
        description="IRIS Model Manager - Hantera AI-modeller",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exempel:
  python -m src.utils.model_manager_cli list
  python -m src.utils.model_manager_cli list --provider groq
  python -m src.utils.model_manager_cli info kimi-k2
  python -m src.utils.model_manager_cli profile snabb
  python -m src.utils.model_manager_cli usecase snabba_svar
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Kommandon')
    
    # List command
    list_parser = subparsers.add_parser('list', help='Lista modeller')
    list_parser.add_argument('--provider', help='Filtrera på provider')
    list_parser.add_argument('--streaming', action='store_true', help='Endast streaming-modeller')
    
    # Info command
    info_parser = subparsers.add_parser('info', help='Visa modellinformation')
    info_parser.add_argument('model_key', help='Modellnyckel')
    
    # Profile command
    profile_parser = subparsers.add_parser('profile', help='Visa profilmodeller')
    profile_parser.add_argument('profile_name', help='Profilnamn')
    
    # Use case command
    usecase_parser = subparsers.add_parser('usecase', help='Visa användningsfall')
    usecase_parser.add_argument('use_case', help='Användningsfall')
    
    # Profiles command
    subparsers.add_parser('profiles', help='Lista alla profiler')
    
    # Use cases command
    subparsers.add_parser('usecases', help='Lista alla användningsfall')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'list':
            list_models(
                provider=args.provider,
                streaming=args.streaming if hasattr(args, 'streaming') else None
            )
        elif args.command == 'info':
            show_model_info(args.model_key)
        elif args.command == 'profile':
            show_profile_models(args.profile_name)
        elif args.command == 'usecase':
            show_use_case(args.use_case)
        elif args.command == 'profiles':
            list_profiles()
        elif args.command == 'usecases':
            list_use_cases()
    except Exception as e:
        print(f"❌ Fel: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
