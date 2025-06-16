import argparse
import os
from pdf2image import convert_from_path
from PIL import Image
import pytesseract
from typing import List

try:
    from transformers import AutoProcessor, Qwen2VLForConditionalGeneration, Qwen2_5_VLForConditionalGeneration
    import torch
except Exception:
    AutoProcessor = None  # type: ignore
    Qwen2VLForConditionalGeneration = None  # type: ignore
    Qwen2_5_VLForConditionalGeneration = None  # type: ignore
    torch = None  # type: ignore

def pdf_to_images(pdf_path, out_dir):
    images = convert_from_path(pdf_path)
    os.makedirs(out_dir, exist_ok=True)
    image_paths = []
    for i, image in enumerate(images, 1):
        path = os.path.join(out_dir, f"page_{i}.jpg")
        image.save(path, "JPEG")
        image_paths.append(path)
    return image_paths


def _images_to_text_tesseract(image_paths: List[str], lang: str = "deu") -> str:
    text_parts = []
    for path in image_paths:
        image = Image.open(path)
        text = pytesseract.image_to_string(image, lang=lang)
        text_parts.append(text)
    return "\n".join(text_parts)


_qwen_processor = None
_qwen_model = None


def _ensure_qwen_loaded():
    global _qwen_processor, _qwen_model
    if _qwen_model is None:
        if AutoProcessor is None:
            raise RuntimeError("transformers is required for Qwen2 model")
        QV_MODEL_ID = "prithivMLmods/Qwen2-VL-OCR-2B-Instruct"
        _qwen_processor = AutoProcessor.from_pretrained(QV_MODEL_ID, trust_remote_code=True)
        _qwen_model = Qwen2VLForConditionalGeneration.from_pretrained(
            QV_MODEL_ID,
            trust_remote_code=True,
            torch_dtype=torch.float16,
        ).to("cuda").eval()


def _images_to_text_qwen(image_paths: List[str]) -> str:
    _ensure_qwen_loaded()
    results = []
    for path in image_paths:
        image = Image.open(path)
        inputs = _qwen_processor(text="Recognize the text in the image", images=image, return_tensors="pt").to("cuda")
        ids = _qwen_model.generate(**inputs, max_new_tokens=512)
        text = _qwen_processor.batch_decode(ids, skip_special_tokens=True)[0]
        results.append(text.strip())
    return "\n".join(results)


_rolm_processor = None
_rolm_model = None


def _ensure_rolm_loaded():
    global _rolm_processor, _rolm_model
    if _rolm_model is None:
        if AutoProcessor is None:
            raise RuntimeError("transformers is required for RolmOCR model")
        ROLM_MODEL_ID = "reducto/RolmOCR"
        _rolm_processor = AutoProcessor.from_pretrained(ROLM_MODEL_ID, trust_remote_code=True)
        _rolm_model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
            ROLM_MODEL_ID,
            trust_remote_code=True,
            torch_dtype=torch.bfloat16,
        ).to("cuda").eval()


def _images_to_text_rolm(image_paths: List[str]) -> str:
    _ensure_rolm_loaded()
    results = []
    for path in image_paths:
        image = Image.open(path)
        inputs = _rolm_processor(text="Recognize the text in the image", images=image, return_tensors="pt").to("cuda")
        ids = _rolm_model.generate(**inputs, max_new_tokens=512)
        text = _rolm_processor.batch_decode(ids, skip_special_tokens=True)[0]
        results.append(text.strip())
    return "\n".join(results)


def images_to_text(image_paths: List[str], lang: str = "deu", engine: str = "tesseract") -> str:
    if engine == "tesseract":
        return _images_to_text_tesseract(image_paths, lang)
    if engine == "qwen2":
        return _images_to_text_qwen(image_paths)
    if engine == "rolmocr":
        return _images_to_text_rolm(image_paths)
    raise ValueError(f"Unknown OCR engine: {engine}")


def main():
    parser = argparse.ArgumentParser(description="PDF OCR extractor")
    parser.add_argument("pdf", help="Input PDF file")
    parser.add_argument("--out-dir", default="output", help="Directory for images and text")
    parser.add_argument("--lang", default="deu", help="Tesseract language code")
    parser.add_argument(
        "--engine",
        default="tesseract",
        choices=["tesseract", "qwen2", "rolmocr"],
        help="OCR engine to use",
    )
    args = parser.parse_args()

    image_paths = pdf_to_images(args.pdf, args.out_dir)
    text = images_to_text(image_paths, args.lang, args.engine)
    text_file = os.path.join(args.out_dir, "output.txt")
    with open(text_file, "w", encoding="utf-8") as f:
        f.write(text)
    print(text)
    print(f"Text saved to {text_file}")


if __name__ == "__main__":
    main()
