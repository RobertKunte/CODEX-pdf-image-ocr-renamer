import argparse
import os
from pdf2image import convert_from_path
from PIL import Image
import pytesseract

def pdf_to_images(pdf_path, out_dir):
    images = convert_from_path(pdf_path)
    os.makedirs(out_dir, exist_ok=True)
    image_paths = []
    for i, image in enumerate(images, 1):
        path = os.path.join(out_dir, f"page_{i}.jpg")
        image.save(path, "JPEG")
        image_paths.append(path)
    return image_paths


def images_to_text(image_paths, lang="deu"):
    text_parts = []
    for path in image_paths:
        image = Image.open(path)
        text = pytesseract.image_to_string(image, lang=lang)
        text_parts.append(text)
    return "\n".join(text_parts)


def main():
    parser = argparse.ArgumentParser(description="PDF OCR extractor")
    parser.add_argument("pdf", help="Input PDF file")
    parser.add_argument("--out-dir", default="output", help="Directory for images and text")
    parser.add_argument("--lang", default="deu", help="Tesseract language code")
    args = parser.parse_args()

    image_paths = pdf_to_images(args.pdf, args.out_dir)
    text = images_to_text(image_paths, args.lang)
    text_file = os.path.join(args.out_dir, "output.txt")
    with open(text_file, "w", encoding="utf-8") as f:
        f.write(text)
    print(text)
    print(f"Text saved to {text_file}")


if __name__ == "__main__":
    main()
