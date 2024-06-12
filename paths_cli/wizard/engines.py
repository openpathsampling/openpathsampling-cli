from paths_cli.wizard.plugin_classes import LoadFromOPS, WrapCategory

_ENGINE_HELP = "An engine describes how you'll do the actual dynamics."
ENGINE_PLUGIN = WrapCategory(
    name='engine',
    ask="What will you use for the underlying engine?",
    intro=("Let's make an engine. " + _ENGINE_HELP + " Most of the "
           "details are given in files that depend on the specific "
           "type of engine."),
    helper=_ENGINE_HELP
)

ENGINE_FROM_FILE = LoadFromOPS('engine')

if __name__ == "__main__":  # no-cov
    from paths_cli.wizard.run_module import run_category
    run_category('engine')
