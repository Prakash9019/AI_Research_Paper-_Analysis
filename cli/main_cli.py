#!/usr/bin/env python3
"""
DeepCode CLI - Open-Source Code Agent
CLI - 
"""

import os
import sys
import asyncio
import argparse

# 
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"

# 
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# CLI
from cli.cli_app import CLIApp, Colors


def print_enhanced_banner():
    """"""
    banner = f"""
{Colors.CYAN}==============================================================================
|                                                                              |
|    {Colors.BOLD}{Colors.MAGENTA} DeepCode - Open-Source Code Agent{Colors.CYAN}                              |
|                                                                              |
|    {Colors.BOLD}{Colors.YELLOW} DATA INTELLIGENCE LAB @ HKU {Colors.CYAN}                                |
|                                                                              |
|    Revolutionizing research reproducibility through collaborative AI         |
|    Building the future where code is reproduced from natural language       |
|                                                                              |
|    {Colors.BOLD}{Colors.GREEN} Key Features:{Colors.CYAN}                                                    |
|    • Automated paper-to-code reproduction                                   |
|    • Multi-agent collaborative architecture                                 |
|    • Open-source and extensible design                                      |
|    • Join our growing research community                                    |
|                                                                              |
=============================================================================={Colors.ENDC}
"""
    print(banner)


def check_environment():
    """"""
    print(f"{Colors.CYAN} Checking environment...{Colors.ENDC}")

    # Python
    if sys.version_info < (3, 8):
        print(
            f"{Colors.FAIL} Python 3.8+ required. Current: {sys.version}{Colors.ENDC}"
        )
        return False

    print(f"{Colors.OKGREEN} Python {sys.version.split()[0]} - OK{Colors.ENDC}")

    # 
    required_modules = [
        ("asyncio", "Async IO support"),
        ("pathlib", "Path handling"),
        ("typing", "Type hints"),
    ]

    missing_modules = []
    for module, desc in required_modules:
        try:
            __import__(module)
            print(f"{Colors.OKGREEN} {desc} - OK{Colors.ENDC}")
        except ImportError:
            missing_modules.append(module)
            print(f"{Colors.FAIL} {desc} - Missing{Colors.ENDC}")

    if missing_modules:
        print(
            f"{Colors.FAIL} Missing required modules: {', '.join(missing_modules)}{Colors.ENDC}"
        )
        return False

    print(f"{Colors.OKGREEN} Environment check passed{Colors.ENDC}")
    return True


def parse_arguments():
    """"""
    parser = argparse.ArgumentParser(
        description="DeepCode CLI - Open-Source Code Agent by Data Intelligence Lab @ HKU",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
{Colors.BOLD}Examples:{Colors.ENDC}
  {Colors.CYAN}python main_cli.py{Colors.ENDC}                               # Interactive mode
  {Colors.CYAN}python main_cli.py --file paper.pdf{Colors.ENDC}                # Process file directly
  {Colors.CYAN}python main_cli.py --url https://...{Colors.ENDC}               # Process URL directly
  {Colors.CYAN}python main_cli.py --chat "Build a web app..."{Colors.ENDC}     # Process chat requirements
  {Colors.CYAN}python main_cli.py --optimized{Colors.ENDC}                     # Use optimized mode
  {Colors.CYAN}python main_cli.py --disable-segmentation{Colors.ENDC}          # Disable document segmentation
  {Colors.CYAN}python main_cli.py --segmentation-threshold 30000{Colors.ENDC}  # Custom segmentation threshold

{Colors.BOLD}Pipeline Modes:{Colors.ENDC}
  {Colors.GREEN}Comprehensive{Colors.ENDC}: Full intelligence analysis with indexing
  {Colors.YELLOW}Optimized{Colors.ENDC}:     Fast processing without indexing

{Colors.BOLD}Document Processing:{Colors.ENDC}
  {Colors.BLUE}Smart Segmentation{Colors.ENDC}: Intelligent document segmentation for large papers
  {Colors.MAGENTA}Supported Formats{Colors.ENDC}: PDF, DOCX, DOC, PPT, PPTX, XLS, XLSX, HTML, TXT, MD
        """,
    )

    parser.add_argument(
        "--file", "-f", type=str, help="Process a specific file (PDF, DOCX, TXT, etc.)"
    )

    parser.add_argument(
        "--url", "-u", type=str, help="Process a research paper from URL"
    )

    parser.add_argument(
        "--chat",
        "-t",
        type=str,
        help="Process coding requirements via chat input (provide requirements as argument)",
    )

    parser.add_argument(
        "--optimized",
        "-o",
        action="store_true",
        help="Use optimized mode (skip indexing for faster processing)",
    )

    parser.add_argument(
        "--disable-segmentation",
        action="store_true",
        help="Disable intelligent document segmentation (use traditional full-document processing)",
    )

    parser.add_argument(
        "--segmentation-threshold",
        type=int,
        default=50000,
        help="Document size threshold (characters) to trigger segmentation (default: 50000)",
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Run in non-interactive mode for testing",
    )

    return parser.parse_args()


async def run_direct_processing(app: CLIApp, input_source: str, input_type: str):
    """()"""
    try:
        print(
            f"\n{Colors.BOLD}{Colors.CYAN} Starting direct processing mode...{Colors.ENDC}"
        )
        print(f"{Colors.CYAN}Input: {input_source}{Colors.ENDC}")
        print(f"{Colors.CYAN}Type: {input_type}{Colors.ENDC}")
        print(
            f"{Colors.CYAN}Mode: {' Comprehensive' if app.cli.enable_indexing else ' Optimized'}{Colors.ENDC}"
        )

        # 
        init_result = await app.initialize_mcp_app()
        if init_result["status"] != "success":
            print(
                f"{Colors.FAIL} Initialization failed: {init_result['message']}{Colors.ENDC}"
            )
            return False

        # 
        result = await app.process_input(input_source, input_type)

        if result["status"] == "success":
            print(
                f"\n{Colors.BOLD}{Colors.OKGREEN} Processing completed successfully!{Colors.ENDC}"
            )
            return True
        else:
            print(
                f"\n{Colors.BOLD}{Colors.FAIL} Processing failed: {result.get('error', 'Unknown error')}{Colors.ENDC}"
            )
            return False

    except Exception as e:
        print(f"\n{Colors.FAIL} Direct processing error: {str(e)}{Colors.ENDC}")
        return False
    finally:
        await app.cleanup_mcp_app()


async def main():
    """"""
    # 
    args = parse_arguments()

    # 
    # print_enhanced_banner()

    # 
    # if not check_environment():
    #     print(
    #         f"\n{Colors.FAIL} Environment check failed. Please fix the issues and try again.{Colors.ENDC}"
    #     )
    #     sys.exit(1)

    try:
        # CLI
        app = CLIApp()

        # 
        if args.optimized:
            app.cli.enable_indexing = False
            print(
                f"\n{Colors.YELLOW} Optimized mode enabled - indexing disabled{Colors.ENDC}"
            )
        else:
            print(
                f"\n{Colors.GREEN} Comprehensive mode enabled - full intelligence analysis{Colors.ENDC}"
            )

        # Configure document segmentation settings
        if hasattr(args, "disable_segmentation") and args.disable_segmentation:
            print(
                f"\n{Colors.MAGENTA} Document segmentation disabled - using traditional processing{Colors.ENDC}"
            )
            app.segmentation_config = {
                "enabled": False,
                "size_threshold_chars": args.segmentation_threshold,
            }
        else:
            print(
                f"\n{Colors.BLUE} Smart document segmentation enabled (threshold: {args.segmentation_threshold} chars){Colors.ENDC}"
            )
            app.segmentation_config = {
                "enabled": True,
                "size_threshold_chars": args.segmentation_threshold,
            }

        # 
        if args.non_interactive:
            success = await run_direct_processing(app, "https://arxiv.org/pdf/1706.03762.pdf", "url")
            sys.exit(0 if success else 1)
        elif args.file or args.url or args.chat:
            if args.file:
                # 
                if not os.path.exists(args.file):
                    print(f"{Colors.FAIL} File not found: {args.file}{Colors.ENDC}")
                    sys.exit(1)
                success = await run_direct_processing(app, args.file, "file")
            elif args.url:
                success = await run_direct_processing(app, args.url, "url")
            elif args.chat:
                # chat
                if len(args.chat.strip()) < 20:
                    print(
                        f"{Colors.FAIL} Chat input too short. Please provide more detailed requirements (at least 20 characters){Colors.ENDC}"
                    )
                    sys.exit(1)
                success = await run_direct_processing(app, args.chat, "chat")

            sys.exit(0 if success else 1)
        else:
            # 
            print(f"\n{Colors.CYAN} Starting interactive mode...{Colors.ENDC}")
            await app.run_interactive_session()

    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}  Application interrupted by user{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.FAIL} Application errors: {str(e)}{Colors.ENDC}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())