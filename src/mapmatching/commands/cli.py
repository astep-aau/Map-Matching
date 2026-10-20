import importlib
import pkgutil

import typer

from mapmatching import commands

app = typer.Typer(no_args_is_help = True)

@app.callback()
def main() -> None:
    """Map matching happens here."""


def register_commands() -> None:
    """This function scans all files in the commands folder and registers them as a CLI command on the app object"""
    for module_info in pkgutil.iter_modules(commands.__path__):
        name = module_info.name
        if name == "cli" or name.startswith("_"):
            continue
        
        module = importlib.import_module(f"{commands.__name__}.{name}")

        if hasattr(module, "app"):
            app.add_typer(module.app, name = name)
        elif hasattr(module, name):
            app.command(name)(getattr(module, name))
        else:
            raise RuntimeError(
                f"commands/{name}.py must define a function '{name}' or a Typer 'app'. Or else the command cannot be registered, to skip the file, rename to '_{name}.py'"
            )

register_commands()