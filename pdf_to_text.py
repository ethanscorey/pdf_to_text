import os
from glob import glob
from typing import AnyStr, Union, Iterable
import sys
import random

import pdftk
from utils import check_output, concat
from magick import magick
from tesseract import tesseract


def main():

    (in_file,
     out_file,
     file_format) = sys.argv[1:4]
    pages = burst_pdf(in_file)
    tiffed = tiff_pages(pages)
    tessed = tess_pages(tiffed, file_format, out_file)
    clean_up(tessed)
    return 0


def burst_pdf(pdf: str) -> str:
    # create unique signature to ensure no name collisions
    signature = int(random.random() * 100000000)
    check_output(pdftk.burst(pdf, f"tmp{signature}_%04d.pdf"))
    return f"tmp{signature}*.pdf"


def tiff_pages(pages: str) -> str:
    tiff_file = f"{pages[:-5]}_%04d.tiff"
    check_output(magick(pages,
                        tiff_file,
                        density=300,
                        type_="Grayscale",
                        compress="lzw",
                        background="white",
                        alpha="off",
                        depth=8))
    return f"{pages[:-5]}*.tiff"


def tess_pages(tiffs: str,
               file_format: str,
               output) -> str:
    fname_file = f"{tiffs[:-6]}.txt"
    make_tess_list(tiffs, fname_file)
    check_output(tesseract(fname_file, output, format=file_format))
    return f"{tiffs[:-10]}*"


def make_tess_list(files_glob: str, list_file: str) -> None:
    with open(list_file, "w") as f:
        for fname in glob(files_glob):
            f.write(fname)
            f.write("\n")


def clean_up(files: Union[AnyStr, os.PathLike]):
    try:
        for f in glob(files):
            os.remove(f)
    except TypeError:
        raise TypeError(f"Expected str, bytes or os.Pathlike, not {files}")

if __name__ == "__main__":
    main()
