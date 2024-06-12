import click
from paths_cli.compiling._gendocs import DocsGenerator, load_config
from paths_cli.compiling.root_compiler import _COMPILERS
from paths_cli.commands.compile import register_installed_plugins


@click.command()
@click.argument("config_file")
@click.option("--stdout", type=bool, is_flag=True, default=False)
def main(config_file, stdout):
    """Generate documentation for installed compiling plugins."""
    do_main(config_file, stdout)


def do_main(config_file, stdout=False):
    """Separate method so this can be imported and run"""
    register_installed_plugins()
    config = load_config(config_file)
    generator = DocsGenerator(config)
    generator.generate(_COMPILERS.values(), stdout)


if __name__ == "__main__":
    main()
