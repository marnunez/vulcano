# -* coding: utf-8 *-
"""
:py:mod:`vulcano.command.models`
--------------------------------
Vulcano models
"""
# System imports
import inspect

# Third-party imports
from pynspector.func_inspections import get_func_inspect_result
from cached_property import cached_property

# Local imports


__all__ = ["Command"]


class Command(object):
    """
    Vulcano Command

    This represents a Command registered for Vulcano

    :param str name: Name for this command
    :param str description: Description of this command
    :param function func: Function that has been registered to be executed
    :param function show_if: Determines when you should display a function or not
    :param dict args_opts: A dictionary that provides a list of posibilities for each argument
    """

    def __init__(self, func, name=None, description=None, show_if=True, args_opts=None):
        self.show_if = show_if
        self.func = func  # type: callable
        func_inspect = get_func_inspect_result(func)
        self.name = name or func_inspect.name  # type: str
        self.short_description = description or func_inspect.short_description
        self.long_description = func_inspect.long_description
        self.args = func_inspect.arguments
        self.args_opts = args_opts if args_opts else {}  # type: callable

    @property
    def visible(self):
        if isinstance(self.show_if, bool):
            return self.show_if
        return self.show_if()

    @property
    def source_code(self):
        return inspect.getsource(self.func)

    @property
    def help(self):
        """ Returns the help for this command

        There should be 2 kind of helps, one for args and another one for REPL mode.

        :return: Help to print
        :rtype: str
        """
        description_item = "{}: \t{}".format(self.name, self.short_description)
        if self.long_description:
            description_item += "\n{}".format(self.long_description)
        if self.args:
            description_item += "\n\t Args:"
            for arg in self.args:
                arg_description = "\n\t\t"
                if arg.is_mandatory:
                    arg_description += "*"
                arg_description += "{arg.name}"
                if arg.kind:
                    arg_description += "({arg.kind})"
                if arg.is_kwarg and arg.default is not None:
                    arg_description += "(default: {arg.default})"
                if arg.name in self.args_opts:
                    if callable(self.args_opts[arg.name]):
                        arg_description += ": from_function"
                    else:
                        arg_description += u": {}".format(str(self.args_opts[arg.name]))
                else:
                    arg_description += ": {arg.description}"
                description_item += arg_description.format(arg=arg)
        return description_item + "\n"

    @cached_property
    def command_completer(self):
        return [(u"{}".format(self.name), u"{}".format(self.short_description or ""))]

    @cached_property
    def args_completion(self):
        completions = []
        for arg in self.args:
            if arg.name in self.args_opts.keys():
                name_opt = self.args_opts[arg.name]
                name_opt = name_opt() if callable(name_opt) else name_opt
                completions.append([(u"{}".format(opt), None) for opt in name_opt])
            else:
                completions.append(
                    [(u"{}".format(arg.name), u"{}".format(arg.description))]
                )
        return completions

    def run(self, *args, **kwargs):
        """
        Execute this command and return it's result

        :param args: Arguments to pass the function
        :param kwargs: Known arguments to pass the function
        :return: The result of the function execution
        """
        return self.func(*args, **kwargs)
