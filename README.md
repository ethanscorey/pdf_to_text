# pdf_to_text
Python project integrating pdftk, ImageMagick, and Tesseract OCR into a PDF OCR stack.

This project uses Python to link together the command-line interfaces for pdftk (TK), ImageMagick (TK), and Tesseract OCR (TK) as part of a command-line tool for performing OCR on a PDF file. 

Command syntax: This project uses a simplified version of the syntax for Tesseract commands. 

`python pdf_to_text.py [INPUT_FILE] [OUTPUT_FILE] [OUTPUT_FILE_FORMAT]`

As with the Tesseract CLI, `[OUTPUT_FILE]` should only include the file name, not the file extension (e.g., "output," not "output.pdf" or "output.txt"). 

Example:

`python pdf_to_text.py example.pdf example_ocr pdf` yields `example_ocr.pdf` as output.

This tool can output the OCRed document in any file format supported by Tesseract. See Tesseract documentation for more details.

In order for this tool to function, pdftk, ImageMagick, and Tesseract must all be installed. See documentation for installation instructions. 

This tool is free software, and may be used or redistributed for any purpose in accordance with the licenses for pdftk, ImageMagick, and Tesseract. 
