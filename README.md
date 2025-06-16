# PDF OCR App

A small command line tool to convert PDF files to images and extract text. The default OCR engine is Tesseract but two Hugging Face models are also supported.

## Requirements

- Python 3.8+
- [pdf2image](https://pypi.org/project/pdf2image/)
- [Pillow](https://pypi.org/project/Pillow/)
- [pytesseract](https://pypi.org/project/pytesseract/)
- [transformers](https://pypi.org/project/transformers/) and [torch](https://pypi.org/project/torch/) for the optional Hugging Face models
- Tesseract OCR installed on your system
- Poppler utilities for PDF rendering

Install the Python dependencies via pip:

```bash
pip install -r requirements.txt
```

## Usage

```bash
python pdf_ocr.py <file.pdf> --out-dir output --lang deu --engine tesseract
```

All pages of the PDF will be saved as JPG images in the output folder. The recognized text is printed to the console and written to `output/output.txt`.

## Notes

This repository contains only a minimal example. Make sure `tesseract` and the language data you need are installed on your system.
