from collections import namedtuple

from paths_cli.compiling.root_compiler import _CategoryCompilerProxy
from paths_cli.wizard.standard_categories import get_category_info

NO_DEFAULT = object()

NO_PARAMETER_LOADED = object()

ProxyParameter = namedtuple(
    'ProxyParameter',
    ['name', 'ask', 'helper', 'default', 'autohelp', 'summarize'],
    defaults=[None, NO_DEFAULT, False, None]
)


class WizardParameter:
    """Load a single parameter from the wizard.

    Parameters
    ----------
    name : str
        name of this parameter
    ask : List[str]
        list of strings that the wizard should use to ask the user for
        input. These can be formatted with a provided ``context`` dict.
    loader : Callable
        method to create parameter from user input string
    helper : Union[`:class:.Helper`, str]
        method to provide help for this parameter
    default : Any
        default value of this parameter; ``NO_DEFAULT`` if no default exists
    autohelp : bool
        if True, bad input automatically causes the help information to be
        shown. Default False.
    summarize : Callable
        method to provide summary of created output.
    """
    def __init__(self, name, ask, loader, *, helper=None, default=NO_DEFAULT,
                 autohelp=False, summarize=None):
        self.name = name
        self.ask = ask
        self.loader = loader
        self.helper = helper
        self.default = default
        self.autohelp = autohelp
        if summarize is None:
            summarize = str
        self.summarize = summarize

    @classmethod
    def from_proxy(cls, proxy, compiler_plugin):
        """Create a parameter from a proxy parameter a compiler plugin.

        Parameters
        ----------
        proxy : :class:`.ProxyParameter`
            proxy with wizard-specific information for user interaction
        compiler_plugin : :class:`.InstanceCompilerPlugin`
            the compiler plugin to make objects of this type
        """
        loader_dict = {p.name: p.loader for p in compiler_plugin.parameters}
        dct = proxy._asdict()
        loader = loader_dict[proxy.name]
        if isinstance(loader, _CategoryCompilerProxy):
            # TODO: can this import now be moved to top of file?
            from paths_cli.wizard.plugin_registration import \
                    get_category_wizard
            category = loader.category
            dct['loader'] = get_category_wizard(category)
            dct['ask'] = get_category_info(category).singular
            dct['store_name'] = get_category_info(category).storage
            cls_ = _ExistingObjectParameter
        else:
            cls_ = cls
            dct['loader'] = loader
        return cls_(**dct)

    def __call__(self, wizard, context):
        """Load the parameter.

        Parameters
        ----------
        wizard : :class:`.Wizard`
            wizard for interacting with the user
        context : dict
            context dic

        Returns
        -------
        Any :
            the result of converting user string input to a parsed parameter
        """
        obj = NO_PARAMETER_LOADED
        ask = self.ask.format(**context)
        while obj is NO_PARAMETER_LOADED:
            obj = wizard.ask_load(ask, self.loader, self.helper,
                                  autohelp=self.autohelp)
        return obj


class _ExistingObjectParameter(WizardParameter):
    """Special parameter type for parameters created by wizards.

    This should only be created as part of the
    :method:`.WizardParameter.from_proxy` method; client code should not use
    this directly.
    """
    def __init__(self, name, ask, loader, store_name, *, helper=None,
                 default=NO_DEFAULT, autohelp=False, summarize=None):
        super().__init__(name=name, ask=ask, loader=loader, helper=helper,
                         default=default, autohelp=autohelp,
                         summarize=summarize)
        self.store_name = store_name

    @classmethod
    def from_proxy(cls, proxy, compiler_plugin):
        raise NotImplementedError()

    def __call__(self, wizard, context):
        ask = self.ask.format(**context)
        obj = wizard.obj_selector(self.store_name, ask, self.loader)
        return obj


class FromWizardPrerequisite:
    """Load prerequisites from the wizard.

    WARNING: This should be considered very experimental and may be removed
    or substantially changed in future versions.

    Parameters
    ----------
    name : str
        the name of this prerequisite
    create_func : Callable[:class:`.Wizard] -> Any
        method to create a relevant object, using the given wizard for user
        interaction. Note that the specific return object can be extracted
        from the results of this method by using load_func
    category : str
        category of object this creates
    n_required : int
        number of instances that must be created
    obj_name : str
        singular version of object name in order to refer to it in user
        interactions
    store_name : str
        name of the store in which this object would be found if it has
        already been created for this Wizard
    say_create : List[str]
        user interaction statement prior to creating this object. Each
        element in the list makes a separate statement from the wizard.
    say_finish : List[str]
        user interaction statment upon completing this object. Each element
        in the list makes a separate statment from the wizard.
    load_func : Callable
        method to extract specific return object from the create_func.
        Default is to return the result of create_func.
    """
    def __init__(self, name, create_func, category, n_required, *,
                 obj_name=None, store_name=None, say_create=None,
                 say_finish=None, load_func=None):
        self.name = name
        self.create_func = create_func
        self.category = category
        if obj_name is None:
            obj_name = get_category_info(category).singular
        if store_name is None:
            store_name = get_category_info(category).storage

        self.obj_name = obj_name
        self.store_name = store_name
        self.n_required = n_required
        self.say_create = say_create
        self.say_finish = say_finish
        if load_func is None:
            load_func = lambda x: x

        self.load_func = load_func

    def _create_new(self, wizard):
        """Create a new instance of this prereq.

        Invoked if more objects of this type are needed than have already
        been created for the wizard.

        Parameters
        ----------
        wizard : :class:`.Wizard`
            the wizard to use for user interaction

        Returns
        -------
        Any :
            single instance of the required class
        """
        if self.say_create:
            wizard.say(self.say_create)
        obj = self.create_func(wizard)
        wizard.register(obj, self.obj_name, self.store_name)
        result = self.load_func(obj)
        return result

    def _get_existing(self, wizard):
        """Get existing instances of the desired object.

        This is invoked either when there are the exact right number of
        objects already created, or to get the initial objects when there
        aren't enough objects created yet.

        Parameters
        ----------
        wizard : :class:`.Wizard`
            the wizard to use for user interaction

        Returns
        -------
        List[Any] :
            list of existing instances
        """
        all_objs = list(getattr(wizard, self.store_name).values())
        results = [self.load_func(obj) for obj in all_objs]
        return results

    def _select_single_existing(self, wizard):
        """Ask the user to select an instance from the saved instances.

        This is invoked if there are more instances already created than are
        required. This is called once for each instance required.

        Parameters
        ----------
        wizard : :class:`.Wizard`
            the wizard to use for user interaction

        Returns
        -------
        Any :
            single instance of the required class
        """
        obj = wizard.obj_selector(self.store_name, self.obj_name,
                                  self.create_func)
        return self.load_func(obj)

    def __call__(self, wizard, context=None):
        """Obtain the correct number of instances of the desired type.

        This will either take the existing object(s) in the wizard (if the
        exact correct number have been created in the wizard), create new
        objects (if there are not enough) or ask the user to select the
        existing instances (if there are more than enough).

        Parameters
        ----------
        wizard : :class:`.Wizard`
            the wizard to use for user interaction
        context : dict
            context dictionary

        Returns
        -------
        Dict[str, List[Any]] :
            mapping ``self.name`` to a list of objects of the correct type.
            Note that this always maps to a list; receiving code may need to
            handle that fact.
        """
        n_existing = len(getattr(wizard, self.store_name))
        if n_existing == self.n_required:
            # early return in this case (return silently)
            return {self.name: self._get_existing(wizard)}

        if n_existing > self.n_required:
            sel = [self._select_single_existing(wizard)
                   for _ in range(self.n_required)]
            dct = {self.name: sel}
        else:
            objs = self._get_existing(wizard)
            while len(getattr(wizard, self.store_name)) < self.n_required:
                objs.append(self._create_new(wizard))
            dct = {self.name: objs}

        if self.say_finish:
            wizard.say(self.say_finish)
        return dct
