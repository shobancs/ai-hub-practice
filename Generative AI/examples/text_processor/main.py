"""
main.py - Single entry point for the Text Processor app.

Usage:
    # Interactive menu
    python main.py

    # Direct commands
    python main.py summarize --text "Your text here"
    python main.py summarize --file notes.md --style key_takeaways
    python main.py summarize --url https://en.wikipedia.org/wiki/Python_(programming_language)
    python main.py sentiment --text "I love this product but the price is too high."
    python main.py action-items --file meeting_notes.txt
    python main.py history
    python main.py stats

    # Start web UI
    python main.py --web

    # Start REST API
    python main.py --api
"""
import sys
import os
from pathlib import Path

# Ensure the *parent* of the text_processor package is on the path so that
# `import text_processor` works regardless of the working directory.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def _interactive_menu() -> None:
    """Interactive menu — loops until the user quits."""
    while True:
        print("\n========================================")
        print("       AI Text Processor  v1.0")
        print("========================================\n")
        print("  1. Summarize text / file / URL")
        print("  2. Sentiment analysis")
        print("  3. Extract action items")
        print("  4. Improve writing")
        print("  5. View history")
        print("  6. View usage stats")
        print("  7. Launch web UI  (requires: pip install gradio)")
        print("  8. Launch REST API (requires: pip install fastapi uvicorn)")
        print("  q. Quit\n")

        choice = input("Choose an option: ").strip()

        try:
            if choice == "1":
                src = input("Enter text, file path, or URL: ").strip()
                style = input("Style [bullet_points/paragraph/key_takeaways/tldr]: ").strip() or "bullet_points"
                length = input("Length [short/medium/long]: ").strip() or "medium"
                from text_processor.interfaces.cli import cmd_summarize
                import argparse
                args = argparse.Namespace(
                    text=src if not (src.startswith("http") or Path(src).exists()) else None,
                    file=src if Path(src).exists() else None,
                    url=src if src.startswith("http") else None,
                    style=style, length=length, audience="general",
                    model="gpt-4o-mini", budget=5.0,
                )
                cmd_summarize(args)

            elif choice == "2":
                text = input("Enter text: ").strip()
                from text_processor.interfaces.cli import cmd_sentiment
                import argparse
                args = argparse.Namespace(text=text, file=None, url=None, model="gpt-4o-mini")
                cmd_sentiment(args)

            elif choice == "3":
                text = input("Paste meeting notes / email:\n")
                from text_processor.interfaces.cli import cmd_action_items
                import argparse
                args = argparse.Namespace(text=text, file=None, url=None, model="gpt-4o-mini")
                cmd_action_items(args)

            elif choice == "4":
                text = input("Enter text to improve: ").strip()
                goal = input("Goal [clarity/conciseness/formal/casual/persuasive]: ").strip() or "clarity"
                from text_processor.core import AppConfig, LLMClient, PromptTemplates
                config = AppConfig()
                config.validate()
                client = LLMClient(config)
                templates = PromptTemplates()
                pair = templates.improve_writing(text, goal=goal)
                response = client.chat(pair.user, system_message=pair.system)
                print(f"\n── Improved Text ──────────────────────────────")
                print(response.content)
                print(f"\nCost: ${response.cost_usd:.4f}")

            elif choice == "5":
                from text_processor.interfaces.cli import cmd_history
                import argparse
                cmd_history(argparse.Namespace(limit=20))

            elif choice == "6":
                from text_processor.interfaces.cli import cmd_stats
                import argparse
                cmd_stats(argparse.Namespace())

            elif choice == "7":
                try:
                    import gradio  # noqa: F401
                except ImportError:
                    print("\nGradio is not installed. Run:  pip install gradio")
                    continue
                from text_processor.interfaces.web_ui import main as web_main
                print("Starting web UI at http://localhost:7860  (Ctrl+C to stop)")
                web_main()

            elif choice == "8":
                try:
                    import uvicorn  # noqa: F401
                except ImportError:
                    print("\nuvicorn is not installed. Run:  pip install fastapi uvicorn")
                    continue
                import subprocess
                print("Starting REST API at http://localhost:8000/docs  (Ctrl+C to stop)")
                subprocess.run([
                    sys.executable, "-m", "uvicorn",
                    "text_processor.interfaces.api:app",
                    "--reload", "--port", "8000"
                ])

            elif choice in ("q", "Q", "quit", "exit"):
                print("Goodbye!")
                sys.exit(0)

            else:
                print(f"  Invalid option '{choice}'. Enter a number 1-8 or q.")

        except KeyboardInterrupt:
            print("\nCancelled. Returning to menu.")
        except Exception as exc:
            print(f"\n  Error: {exc}")
            print("  (Check your .env file has OPENAI_API_KEY set)")


def main() -> None:
    # Pass-through to CLI if arguments are provided
    if len(sys.argv) > 1:
        if sys.argv[1] == "--web":
            from text_processor.interfaces.web_ui import main as web_main
            web_main()
        elif sys.argv[1] == "--api":
            import subprocess
            subprocess.run([
                sys.executable, "-m", "uvicorn",
                "text_processor.interfaces.api:app",
                "--reload", "--port", "8000"
            ])
        else:
            from text_processor.interfaces.cli import main as cli_main
            cli_main()
    else:
        _interactive_menu()


if __name__ == "__main__":
    main()
