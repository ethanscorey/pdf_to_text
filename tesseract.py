from typing import Any, Tuple, List, Mapping, Optional, Union, Iterable

from cli import CLI, OperatorMap, Input
from utils import flatten


def tesseract(input, output, format):
    return Tesseract(input, output, {"l": "eng"}, format).run()


class Tesseract(CLI):
    empty_command = ["tesseract", "--version"]

    __slots__ = ("input",
                 "output",
                 "options",
                 "config_file")

    def __init__(self,
                 input_: Input = None,
                 output: Optional[str] = None,
                 operators: Optional[OperatorMap] = None,
                 options: Iterable[str] = None,
                 windows: bool = False):
        super().__init__(input_,
                         output,
                         operators,
                         options,
                         windows)
        self.input = self.assign_input(input_)
        self.output = self.assign_output(output)
        self.options = self.assign_operators(operators)
        self.config_file = self.assign_options(options)

    def assign_input(self, input_: str) -> List[str]:
        return self.default_var(input_, [])

    def assign_output(self, output: Optional[str]) -> List[str]:
        if output is not None:
            return [output]
        return []

    def assign_operators(self,
                         operators: Optional[Mapping[str, str]]) -> List[str]:
        return self.default_var(flatten(operators), [])

    def assign_options(self,
                       options: Optional[Mapping[str, Any]]) -> List[str]:
        return self.default_var(options, [])

    def prepare_command(self) -> List[str]:
        return (["tesseract"]
                + self.input
                + self.output
                + self.options
                + self.config_file)

    def validate_input(self):
        ...

    def validate_output(self):
        ...

    def validate_operators(self):
        ...

    def validate_options(self):
        ...

    def validate_operation(self):
        ...

    def test_args_empty(self) -> bool:
        return ((self.input == [])
                and (self.output == [])
                and (self.options == [])
                and (self.config_file == []))


if __name__ == "__main__":
    print(Tesseract("to_ocr.txt",
                    "more_garbage",
                    {"l": "eng"}, "pdf").run())
