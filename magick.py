"""Partial CLI implementation for ImageMagick. The full suite is too complex
to warrant providing full support, given that my primary goal is OCR.

The following options and operations are implemented:
  -density (Image Setting, goes before image)
  -type (Image Setting, goes after image)
  -compress (Image Setting, goes after image)
  -background (Image Setting, goes after image)
  -alpha (Image Setting, goes after image)
  -depth (Image Setting, goes after image)
"""

from typing import Any, Tuple, List, Mapping, Optional, Union, Iterable

from cli import CLI, Input, OperatorMap
from exceptions import ValidationError
from utils import flatten


MagickOperatorMap = Optional[Mapping[str, Mapping[str, str]]]


def magick(input_: Union[str, Iterable[str]],
           output: str,
           density: int,
           type_: str,
           compress: str,
           background: str,
           alpha: str,
           depth: int):
    operators = {
        "density": {"type": "setting",
                    "position": "pre",
                    "value": density},
        "type": {"type": "setting",
                 "position": "post",
                 "value": type_},
        "compress": {"type": "setting",
                     "position": "post",
                     "value": compress},
        "background": {"type": "setting",
                       "position": "post",
                       "value": background},
        "alpha": {"type": "setting",
                  "position": "post",
                  "value": alpha},
        "depth": {"type": "setting",
                  "position": "post",
                  "value": depth}
    }
    return Magick(input_,
                  output,
                  operators).run()


class Magick(CLI):
    empty_command = ["magick", "-version"]

    __slots__ = ("input",
                 "output",
                 "density",
                 "type",
                 "compress",
                 "background",
                 "alpha",
                 "depth")

    def __init__(self,
                 input_: Input = None,
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
        (self.pre_image_settings,
         self.post_image_settings) = self.assign_operators(operators)

    def assign_input(self, input_: str) -> List[str]:
        return self.default_var(input_, [])

    def assign_output(self, output: Optional[str]) -> List[str]:
        if output is not None:
            return [output]
        return []

    def assign_operators(self,
                         operators: Optional[MagickOperatorMap]) -> Tuple:
        if operators is not None:
            pre_image_settings = self.get_settings(operators, "pre")
            post_image_settings = self.get_settings(operators, "post")
            return flatten(pre_image_settings), flatten(post_image_settings)
        return [], []

    def assign_options(self,
                       options: Optional[Mapping[str, Any]]) -> Tuple:
        pass

    def prepare_command(self) -> List[str]:
        return (["magick"]
                + self.pre_image_settings
                + self.input
                + self.post_image_settings
                + self.output)

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
        return ((self.pre_image_settings == [])
                and (self.input == [])
                and (self.post_image_settings == [])
                and (self.output == [])
                )

    @staticmethod
    def get_settings(operators, position):
        """Returns all operators with type 'setting' and position :position:"""
        return dict((k, str(v["value"])) for k, v in operators.items()
                    if (v["type"] == "setting"
                        and v["position"] == position))


if __name__ == "__main__":
    operators = {
        "density": {"type": "setting",
                    "position": "pre",
                    "value": 300},
        "type": {"type": "setting",
                 "position": "post",
                 "value": "Grayscale"},
        "compress": {"type": "setting",
                     "position": "post",
                     "value": "lzw"},
        "background": {"type": "setting",
                       "position": "post",
                       "value": "white"},
        "alpha": {"type": "setting",
                  "position": "post",
                  "value": "off"},
        "depth": {"type": "setting",
                  "position": "post",
                  "value": 8}
    }
    print(magick("foiled_*.pdf",
                 "foiled_%04d.tiff",
                 density=300,
                 type_="Grayscale",
                 compress="lzw",
                 background="white",
                 alpha="off",
                 depth=8))
