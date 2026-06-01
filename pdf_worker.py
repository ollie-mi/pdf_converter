import os
from io import BytesIO

import PyPDF2
from PyPDF2.filters import _xobj_to_image
from PyPDF2.generic import NameObject, NumberObject
from pdf2image import convert_from_path
from PIL import Image


def delete_last_two_pages(input_pdf, output_pdf):
    # Open the input PDF file
    with open(input_pdf, 'rb') as infile:
        reader = PyPDF2.PdfReader(infile)

        # Create a writer object for the output file
        writer = PyPDF2.PdfWriter()

        # Add all pages except the last two to the writer
        for page_num in range(len(reader.pages) - 2):
            writer.add_page(reader.pages[page_num])

        # Write the new PDF to the output file
        with open(output_pdf, 'wb') as outfile:
            writer.write(outfile)


# Example usage:
# input_pdf = 'input.pdf'  # Path to your input PDF file
# output_pdf = 'output.pdf'  # Path to the output PDF file
#
# delete_last_two_pages(input_pdf, output_pdf)
# print(f"Last two pages have been deleted and saved to {output_pdf}")


def merge_pdfs(pdf1, pdf2, output_pdf):
    # Open the two input PDF files
    with open(pdf1, 'rb') as file1, open(pdf2, 'rb') as file2:
        reader1 = PyPDF2.PdfReader(file1)
        reader2 = PyPDF2.PdfReader(file2)

        # Create a writer object for the output file
        writer = PyPDF2.PdfWriter()

        # Add pages from the first PDF
        for page in range(len(reader1.pages)):
            writer.add_page(reader1.pages[page])

        # Add pages from the second PDF
        for page in range(len(reader2.pages)):
            writer.add_page(reader2.pages[page])

        # Write the merged PDF to the output file
        with open(output_pdf, 'wb') as outfile:
            writer.write(outfile)


# Example usage:
# pdf1 = 'pdf1.pdf'  # Path to the first PDF file
# pdf2 = 'pdf2.pdf'  # Path to the second PDF file
# output_pdf = 'output.pdf'  # Path to the output merged PDF
#
# merge_pdfs(pdf1, pdf2, output_pdf)
# print(f"PDFs merged successfully into {output_pdf}")


def pdf_to_jpg(pdf_path, output_folder):
    # Create the output folder if it does not exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Folder '{output_folder}' created.")

    # Convert PDF to a list of image objects (one per page)
    images = convert_from_path(pdf_path)

    # Save each page as a separate JPG file
    for i, image in enumerate(images):
        jpg_path = f"{output_folder}/page_{i + 1}.jpg"
        image.save(jpg_path, 'JPEG')
        print(f"Page {i + 1} saved as {jpg_path}")


# Example usage:
# pdf_path = 'input.pdf'  # Path to the input PDF file
# output_folder = 'output_images'  # Folder to save JPG files
#
# pdf_to_jpg(pdf_path, output_folder)

def swap_pages(pdf_path, output_path, swaps):
    reader = PyPDF2.PdfReader(pdf_path)
    writer = PyPDF2.PdfWriter()

    num_pages = len(reader.pages)
    pages = list(reader.pages)

    for i, j in swaps:
        if i < num_pages and j < num_pages:
            pages[i], pages[j] = pages[j], pages[i]

    for page in pages:
        writer.add_page(page)

    with open(output_path, "wb") as output_pdf:
        writer.write(output_pdf)


# Example usage:
# pdf_file = "input.pdf" # Path to the input PDF file
# output_file = "output.pdf"  # Path to the output PDF
# swap_pairs = [(6, 12), (7, 13)]
#
# swap_pages(pdf_file, output_file, swap_pairs)


def _recompress_page_images(page, quality):
    """Re-encode every image XObject on a page as JPEG at the given quality.

    PyPDF2 3.0.1 has no high-level image replacement API, so the image
    streams are rewritten in place. Returns the number of images touched.
    """
    resources = page.get("/Resources")
    if resources is None:
        return 0

    x_objects = resources.get_object().get("/XObject")
    if x_objects is None:
        return 0
    x_objects = x_objects.get_object()

    recompressed = 0
    for name in list(x_objects.keys()):
        x_object = x_objects[name].get_object()
        if x_object.get("/Subtype") != "/Image":
            continue
        try:
            _extension, raw = _xobj_to_image(x_object)
            image = Image.open(BytesIO(raw))
            if image.mode not in ("RGB", "L"):
                image = image.convert("RGB")

            buffer = BytesIO()
            image.save(buffer, format="JPEG", quality=quality, optimize=True)

            x_object._data = buffer.getvalue()
            x_object[NameObject("/Filter")] = NameObject("/DCTDecode")
            x_object[NameObject("/ColorSpace")] = NameObject(
                "/DeviceRGB" if image.mode == "RGB" else "/DeviceGray"
            )
            x_object[NameObject("/BitsPerComponent")] = NumberObject(8)
            x_object[NameObject("/Width")] = NumberObject(image.width)
            x_object[NameObject("/Height")] = NumberObject(image.height)
            for key in ("/DecodeParms", "/SMask", "/Decode"):
                if key in x_object:
                    del x_object[key]
            recompressed += 1
        except Exception:
            # Skip images that cannot be decoded or re-encoded (e.g.
            # unsupported color spaces) and leave them untouched.
            continue
    return recompressed


def compress_pdf(input_pdf, output_pdf, image_quality=60):
    """Compress a PDF by re-encoding its embedded images as JPEG.

    Image re-encoding is the main source of size reduction for scanned or
    image-heavy PDFs. Content-stream packing (``compress_content_streams``)
    is intentionally not used: in PyPDF2 3.0.1 it can produce streams that
    some viewers fail to open, while giving almost no size benefit on PDFs
    whose streams are already compressed.

    Args:
        input_pdf: Path to the source PDF file.
        output_pdf: Path where the compressed PDF is written.
        image_quality: JPEG quality (1-95) used to re-encode embedded images.
            Lower values give smaller files at the cost of image quality.
    """
    with open(input_pdf, 'rb') as infile:
        reader = PyPDF2.PdfReader(infile)
        writer = PyPDF2.PdfWriter()

        for page in reader.pages:
            writer.add_page(page)

        for page in writer.pages:
            _recompress_page_images(page, image_quality)

        with open(output_pdf, 'wb') as outfile:
            writer.write(outfile)


# Example usage:
input_pdf = 'Contrato_de_arrendamento.pdf'  # Path to the input PDF file
output_pdf = 'compressed.pdf'  # Path to the compressed output PDF

compress_pdf(input_pdf, output_pdf, image_quality=60)
original = os.path.getsize(input_pdf)
compressed = os.path.getsize(output_pdf)
print(f"Size reduced from {original} to {compressed} bytes")
