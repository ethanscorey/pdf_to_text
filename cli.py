"""
This module defines a base class for accessing the command-line
interfaces for pdftk, ImageMagick, and Tesseract OCR. The CLI
class defined in this module takes an input file, an output file,
and optional mappings of options, operators, and arguments in order
to output and run a valid command to one of these command-line tools.
"""


from typing import (Union, Mapping, Optional, Type, Iterable,
                    List, Callable, Any, Tuple, Sequence)
from subprocess import run, CompletedProcess
from abc import ABC, abstractmethod

Input = Union[str, Sequence[str], Mapping[str, str]]
OperatorMap = Optional[Mapping[str, Any]]
DefaultMapping = Mapping[Optional[Type], Callable[[Any], List[str]]]
DefaultVar = Union[List[str], Callable[[Any], List[str]]]


class CLI(ABC):
    empty_command = []

    @abstractmethod
    def __init__(self,
                 input_: Optional[Input] = None,
                 output: Optional[str] = None,
                 operators: Optional[OperatorMap] = None,
                 options: Optional[Mapping[str, Any]] = None,
                 windows: bool = False):
        """Subclasses will override to assign input, output,
        operators, and options to valid attributes.
        """
        self.windows = windows

    @abstractmethod
    def assign_input(self, input_: Input) -> List[str]:
        """Converts :input_: to properly formatted list."""
        pass

    @abstractmethod
    def assign_output(self, output: Optional[str]) -> List[str]:
        """Converts :output: to properly formatted list."""
        pass

    @abstractmethod
    def assign_operators(self,
                         operators: OperatorMap) -> Tuple[List[str], ...]:
        """Converts :operators: mapping to tuple of lists to assign to each
        operator attribute during __init__.
        """
        pass

    @abstractmethod
    def assign_options(self,
                       options: Mapping[str, Any]) -> Tuple[List[str], ...]:
        """Converts :options: mapping to tuple of lists to assign to each
        option attribute during __init__.
        """
        pass

    @staticmethod
    def default_vars(var: Any,
                     default_mapping: DefaultMapping) -> List[str]:
        """Converts :var: to default value according to :default_mapping:"""
        for type_ in default_mapping:
            if type_ is not None and isinstance(var, type_):
                return default_mapping[type_](var)
            if (type_ is None) and (var is None):
                return default_mapping[None](var)
        raise Exception(f"Default not defined for type {type(var)}")

    @classmethod
    def default_var(cls,
                    var: Any,
                    default: DefaultVar) -> List[str]:
        """Converts :var: to list or replaces with :default:
        if :var: is None.
        """
        default_mapping = {str: lambda x: [x],
                           Iterable: lambda x: list(x),
                           None: lambda x: default,
                           object: lambda x: [str(x)]}
        return cls.default_vars(var, default_mapping)

    @staticmethod
    def format_op_args(op: str, arg: Any) -> List[str]:
        """Converts :op: and :arg: to list of format
        [:op:, :arg:] or [:op:] + list(:arg:) if :arg: is a list.
        """
        if arg is None:
            return []
        elif isinstance(arg, str):
            return [op, arg]
        elif isinstance(arg, Iterable):
            return [op] + list(arg)
        else:
            return [op, str(arg)]

    @staticmethod
    def format_option(options: Mapping[str, Any],
                      option: str,
                      default: List[str]) -> List[str]:
        """Converts :option: to list if :option: in :options:, else returns
        :default:.
        """
        return [option] if options.get(option) else default

    @abstractmethod
    def prepare_command(self) -> List[str]:
        """Combines attributes into valid command."""
        pass

    @abstractmethod
    def validate_input(self) -> None:
        """Ensures input in correct format and input files, if any exist."""
        pass

    @abstractmethod
    def validate_output(self) -> None:
        """Ensures output in correct format."""
        pass

    @abstractmethod
    def validate_operators(self) -> None:
        """Ensures operators are valid and have valid arguments."""
        pass

    @abstractmethod
    def validate_options(self) -> None:
        """Ensures options are valid."""
        pass

    @abstractmethod
    def test_args_empty(self) -> bool:
        """Checks if all arguments to CLI are empty"""
        pass

    def run(self) -> CompletedProcess:
        """Validates, creates, and runs command."""
        if self.test_args_empty():
            return run(self.empty_command)
        self.validate_input()
        self.validate_output()
        self.validate_operators()
        self.validate_options()
        command = self.prepare_command()
        return run(command)
