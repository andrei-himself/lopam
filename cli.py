# cli.py
import argparse

from commands import *

def main():
    parser = argparse.ArgumentParser(
    prog="lopam",
    description = "Local password manager"
    )

    # Create subparsers - only one can be used per invocation
    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
        help="Choose one of the available commands"
    )

    # --- init ---
    parser_init = subparsers.add_parser("init", help="Initialize new vault")
    parser_init.add_argument("vault_name")

    # --- add ---
    parser_add = subparsers.add_parser("add", help="Add entry in a vault")
    parser_add.add_argument("vault_name")
    parser_add.add_argument("entry_name")


    # --- list ---
    parser_list = subparsers.add_parser("list", help="List vault entries")
    parser_list.add_argument("vault_name")
    parser_list.add_argument("keyword", nargs="?", default="")

    # --- show ---
    parser_show = subparsers.add_parser("show", help="Show an entry (username) and copy password to clipboard for 30 seconds")
    parser_show.add_argument("vault_name")
    parser_show.add_argument("entry_name")

    # Parse
    args = parser.parse_args()

    # Dispatch based on subcommand
    match args.command:
        case "init":
            init_vault(args.vault_name)
        case "add":
            add_entry(args.vault_name, args.entry_name)
        case "list":
            list_entries(args.vault_name, args.keyword)
        case "show":
            show_entry(args.vault_name, args.entry_name)
            