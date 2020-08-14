from typing import (List, Optional, Sequence, Collection,
                    Mapping, Any, Tuple, Iterable, Callable)
from subprocess import CompletedProcess
import re
from os.path import isfile

from cli import CLI, Input, OperatorMap
from exceptions import ValidationError


PDFTKOperators = Tuple[List[str], List[str], List[str],
                       List[str], List[str], List[str]]
PDFTKOptions = Tuple[List[str], List[str], List[str],
                     List[str], List[str], List[str],
                     List[str], List[str], List[str],
                     List[str]]


class PDFTK(CLI):
    empty_command = ["pdftk", "--version"]

    __slots__ = ("input",
                 "output",
                 "input_pw",
                 "operation",
                 "operation_arguments",
                 "allow",
                 "owner_pw",
                 "user_pw",
                 "encrypt",
                 "flatten",
                 "need_appearances",
                 "compress",
                 "uncompress",
                 "keep_first_id",
                 "keep_final_id",
                 "drop_xfa",
                 "verbose",
                 "ask")

    def __init__(self,
                 input_: Optional[Input] = None,
                 output: Optional[str] = None,
                 operators: Optional[OperatorMap] = None,
                 options: Optional[Mapping[str, Any]] = None,
                 windows: bool = False):
        super().__init__(input_,
                         output,
                         operators,
                         options,
                         windows)
        self.input = self.assign_input(input_)
        self.output = self.assign_output(output)
        (self.input_pw,
         self.operation,
         self.operation_arguments,
         self.allow,
         self.owner_pw,
         self.user_pw) = self.assign_operators(operators)
        (self.encrypt,
         self.flatten,
         self.need_appearances,
         self.compress,
         self.uncompress,
         self.keep_first_id,
         self.keep_final_id,
         self.drop_xfa,
         self.verbose,
         self.ask) = self.assign_options(options)

    def assign_input(self, input_: Optional[Input]) -> List[str]:
        if input_ is not None:
            return self.format_input_vars(input_)
        else:
            return []

    def assign_output(self, output: Optional[str]) -> List[str]:
        if output is not None:
            return self.format_op_args("output", output)
        else:
            return []

    def assign_operators(self,
                         operators: Optional[OperatorMap]) -> PDFTKOperators:
        if operators is None:
            return ([], [], [],
                    [], [], [])
        return (self.format_input_vars(operators.get("input_pw")),
                self.default_var(operators.get("operation"), []),
                self.default_var(
                    operators.get("operation_arguments"), []),
                self.format_op_args("allow", operators.get("allow")),
                self.format_op_args("owner_pw",
                                    operators.get("owner_pw")),
                self.format_op_args("user_pw",
                                    operators.get("user_pw")))

    def assign_options(self,
                       options: Optional[Mapping[str, Any]]) -> PDFTKOptions:
        if options is None:
            return ([], [], [],
                    [], [], [],
                    [], [], [],
                    [])
        return (self.format_encrypt(options.get("encrypt")),
                self.format_option(options, "flatten", []),
                self.format_option(options, "need_appearances", []),
                self.format_option(options, "compress", []),
                self.format_option(options, "uncompress", []),
                self.format_option(options, "drop_xfa", []),
                self.format_option(options, "keep_first_id", []),
                self.format_option(options, "keep_final_id", []),
                self.format_option(options, "verbose", []),
                self.format_ask(options.get("ask")))

    def validate_input(self):
        i = None
        try:
            for i in self.input:
                assert isinstance(i, str)
                assert isfile(i) or (i == "PROMPT")
        except AssertionError:
            raise ValidationError(f"Invalid input value: {i}")

    def validate_output(self):
        i = None
        if self.output:
            try:
                for i in self.output[1:]:
                    assert re.search(r'.+\.pdf|PROMPT', i)
                    assert i not in self.input
            except AssertionError:
                raise ValidationError(f"Invalid output value: {i}")

    def validate_operators(self):
        self.validate_operation()
        self.validate_operation_args()
        self.validate_permissions()
        self.validate_pws()

    def validate_options(self):
        self.validate_option(self.encrypt, ["encrypt_40bit", "encrypt_128bit"])
        self.validate_option(self.flatten, ["flatten"])
        self.validate_option(self.need_appearances, ["need_appearances"])
        self.validate_option(self.compress, ["compress"])
        self.validate_option(self.uncompress, ["uncompress"])
        self.validate_option(self.keep_first_id, ["keep_first_id"])
        self.validate_option(self.keep_final_id, ["keep_final_id"])
        self.validate_option(self.drop_xfa, ["drop_xfa"])
        self.validate_option(self.ask, ["ask", "dont_ask"])

    def validate_operation(self):
        allowable_ops = [
            "cat",
            "shuffle",
            "burst",
            "rotate",
            "generate_fdf",
            "fill_form",
            "background",
            "multibackground",
            "stamp",
            "multistamp",
            "dump_data",
            "dump_data_utf8",
            "dump_data_fields",
            "dump_data_fields_utf8",
            "dump_data_anots",
            "update_info",
            "update_info_utf8",
            "attach_files",
            "unpack_files",
        ]
        try:
            if self.operation:
                assert len(self.operation) == 1
                assert self.operation[0] in allowable_ops

        except AssertionError:
            raise ValidationError(f"Invalid operation: {self.operation}\n"
                                  f"Operation must be in {allowable_ops}")

    def validate_operation_args(self):
        ...

    def validate_permissions(self):
        allowable = [
            "allow",
            "Printing",
            "DegradedPrinting",
            "ModifyContents",
            "Assembly",
            "CopyContents",
            "ScreenReaders",
            "ModifyAnnotations",
            "FillIn",
            "AllFeatures"
        ]
        not_in_allowable = [i for i in self.allow
                            if i not in allowable]
        try:
            assert len(not_in_allowable) == 0
        except AssertionError:
            raise ValidationError(
                f"Invalid permission(s): {not_in_allowable}\n"
                f"Permission must be in {allowable}")

    def validate_pws(self):
        self.validate_pw("input_pw", self.input_pw)
        self.validate_pw("owner_pw", self.owner_pw)
        self.validate_pw("user_pw", self.user_pw)

    @staticmethod
    def validate_pw(pw_type: str, pw: Sequence[str]):
        try:
            if pw:
                assert re.search(r'\S+', pw[0])
        except AssertionError:
            raise ValidationError(f"Invalid {pw_type}: {pw}")

    @staticmethod
    def validate_option(option: List[str], valid: Collection[str]):
        try:
            if option:
                assert option[0] in valid
        except AssertionError:
            raise ValidationError(f"Invalid option {option}")

    def format_input_vars(self, var: Any) -> List[str]:
        default_mapping = {str: lambda x: [x],
                           Iterable: lambda x: list(x),
                           dict: lambda x: [f"{k}={v}"
                                            for k, v in x.items()],
                           None: lambda x: [],
                           object: lambda x: [str(x)]}
        return self.default_vars(var, default_mapping)

    @staticmethod
    def format_ask(ask: bool) -> List[str]:
        if ask:
            return ["ask"]
        else:
            return ["dont_ask"]

    @staticmethod
    def format_encrypt(encrypt: int) -> List[str]:
        if encrypt is None:
            return []
        elif encrypt == 40:
            return ["encrypt_40bit"]
        elif encrypt == 128:
            return ["encrypt_128bit"]
        else:
            raise Exception(f"Invalid encrypt option {encrypt}. "
                            "Value must be 40 or 128")

    def test_args_empty(self) -> bool:
        return ((self.input == [])
                and (self.output == [])
                and (self.operation == []))

    def prepare_command(self) -> List[str]:
        command = (
                ["pdftk"]
                + self.input
                + self.input_pw
                + self.operation
                + self.operation_arguments
                + self.output
                + self.encrypt
                + self.allow
                + self.owner_pw
                + self.user_pw
                + self.flatten
                + self.need_appearances
                + self.compress
                + self.uncompress
                + self.keep_first_id
                + self.keep_final_id
                + self.drop_xfa
                + self.verbose
                + self.ask
        )
        return command


def make_command(command: str) -> Callable[[Input,
                                            str,
                                            Optional[OperatorMap],
                                            Optional[Mapping[str, str]],
                                            Optional[Sequence[str]]],
                                           CompletedProcess]:
    def inner(input_: Input,
              output: str,
              operators: Optional[OperatorMap] = None,
              options: Optional[Mapping[str, str]] = None,
              command_args: Optional[Sequence[str]] = None):
        if operators is None:
            operators = {}
        operators["operation"] = command
        operators["operation_arguments"] = command_args
        return PDFTK(input_,
                     output,
                     operators,
                     options).run()
    return inner


cat = make_command("cat")
shuffle = make_command("shuffle")
burst = make_command("burst")
rotate = make_command("rotate")
fill_form = make_command("fill_form")
background = make_command("background")
multibackground = make_command("multibackground")
stamp = make_command("stamp")
multistamp = make_command("multistamp")
update_info = make_command("update_info")
update_info_utf8 = make_command("update_info_utf8")
attach_files = make_command("attach_files")

generate_fdf = make_command("generate_fdf")
dump_data = make_command("dump_data")
dump_data_utf8 = make_command("dump_data_utf8")
dump_data_fields = make_command("dump_data_fields")
dump_data_fields_utf8 = make_command("dump_data_fields_utf8")
dump_data_annots = make_command("dump_data_annots")
unpack_files = make_command("unpack_files")


if __name__ == "__main__":
    print(burst("C:/Users/ethan/2020-07-09-fdny-foil.pdf", "foiled_%04d.pdf"))
