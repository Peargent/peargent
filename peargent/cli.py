# peargent/cli.py

"""
Command-line interface for running .pear files.
Usage: peargent <path-to-pear-file>
"""

import sys
import argparse
import re
from pathlib import Path


def _format_error(e: Exception) -> str:
    """Format an exception into a user-friendly error message."""
    error_str = str(e)
    
    # Rate limit errors
    if "429" in error_str or "rate" in error_str.lower() or "quota" in error_str.lower():
        return "Rate limit exceeded. Please wait a moment and try again."
    
    # Authentication errors
    if "401" in error_str or "403" in error_str or "unauthorized" in error_str.lower():
        return "Authentication failed. Please check your API key."
    
    # API key missing
    if "api key" in error_str.lower() or "api_key" in error_str.lower():
        return "API key not found. Please set the required environment variable."
    
    # Network errors
    if "connection" in error_str.lower() or "network" in error_str.lower():
        return "Network error. Please check your internet connection."
    
    # Timeout
    if "timeout" in error_str.lower():
        return "Request timed out. Please try again."
    
    # Server errors
    if "500" in error_str or "502" in error_str or "503" in error_str:
        return "Server error. The API service may be temporarily unavailable."
    
    # Keep it short - just show first line or up to 100 chars
    first_line = error_str.split('\n')[0]
    if len(first_line) > 100:
        return first_line[:100] + "..."
    return first_line


def run_pear(args):
    """Handler for the 'run' command."""
    pear_file = args.pear_file
    verbose = args.verbose

    # Validate file exists
    pear_path = Path(pear_file)
    if not pear_path.exists():
        print(f"❌ Error: File not found: {pear_file}")
        sys.exit(1)
    
    if not pear_path.suffix == ".pear":
        print(f"⚠️  Warning: File does not have .pear extension: {pear_file}")
    
    # Load the .pear file
    try:
        from peargent.atlas.loader import load_pear
        from peargent._core.agent import Agent
        from peargent._core.pool import Pool
        
        print(f"📦 Loading {pear_path.name}...")
        obj = load_pear(str(pear_path))
        
        # Determine what was loaded
        if isinstance(obj, Pool):
            agent_names = obj.agents_names
            print(f"✅ Loaded pool with {len(agent_names)} agents: {', '.join(agent_names)}")
            run_interactive(obj, "pool")
        
        elif isinstance(obj, Agent):
            print(f"✅ Loaded agent: {obj.name}")
            run_interactive(obj, "agent")
        
        elif isinstance(obj, list):
            if len(obj) == 1:
                agent = obj[0]
                print(f"✅ Loaded agent: {agent.name}")
                run_interactive(agent, "agent")
            else:
                # Show selection menu
                print(f"✅ Loaded {len(obj)} agents:")
                for i, agent in enumerate(obj, 1):
                    desc = getattr(agent, 'description', '') or ''
                    if desc:
                        print(f"  [{i}] {agent.name} - {desc[:50]}")
                    else:
                        print(f"  [{i}] {agent.name}")
                print()
                
                # Get user selection
                while True:
                    try:
                        choice = input(f"Select agent (1-{len(obj)}): ").strip()
                        idx = int(choice) - 1
                        if 0 <= idx < len(obj):
                            selected = obj[idx]
                            print(f"\n💬 Chatting with {selected.name}...")
                            run_interactive(selected, "agent")
                            break
                        else:
                            print(f"Please enter a number between 1 and {len(obj)}")
                    except ValueError:
                        print(f"Please enter a number between 1 and {len(obj)}")
                    except (KeyboardInterrupt, EOFError):
                        print("\n👋 Goodbye!")
                        sys.exit(0)
        
        else:
            print(f"❌ Error: Unknown object type loaded: {type(obj)}")
            sys.exit(1)
            
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error loading .pear file: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def main():
    """Main entry point for the peargent CLI."""
    parser = argparse.ArgumentParser(
        prog="peargent",
        description="Peargent CLI - Run and manage AI agents"
    )
    
    # Add version argument
    parser.add_argument(
        "--version", "-V",
        action="store_true",
        help="Show version information"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Run command
    run_parser = subparsers.add_parser(
        "run", 
        help="Run a .pear file",
        description="Run AI agents and pools from .pear files"
    )
    run_parser.add_argument(
        "pear_file",
        type=str,
        help="Path to the .pear file to run"
    )
    run_parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    # If no arguments provided, print help
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
        
    args = parser.parse_args()
    
    if args.version:
        # Try to get version from package
        try:
            from importlib.metadata import version
            print(f"peargent {version('peargent')}")
        except ImportError:
            print("peargent (version unknown)")
        sys.exit(0)
    
    if args.command == "run":
        run_pear(args)
    else:
        # Fallback for backward compatibility or just show help
        # If the user provided a file directly without 'run', we could check if it exists
        # But for now let's enforce 'run' or show help
        parser.print_help()


def run_interactive(obj, obj_type: str):
    """
    Run an interactive REPL loop for the agent or pool.
    
    Args:
        obj: The Agent or Pool to run
        obj_type: "agent" or "pool"
    """
    print()
    print("─" * 50)
    print("Type your message and press Enter to chat.")
    print("Type 'exit' or 'quit' to stop.")
    print("─" * 50)
    print()
    
    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ("exit", "quit", "q"):
                print("\n👋 Goodbye!")
                break
            
            # Run the agent/pool
            print()
            try:
                response = obj.run(user_input)
                print(f"Assistant: {response}")
            except Exception as e:
                print(f"❌ {_format_error(e)}")
            
            print()
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except EOFError:
            print("\n\n👋 Goodbye!")
            break


if __name__ == "__main__":
    main()
