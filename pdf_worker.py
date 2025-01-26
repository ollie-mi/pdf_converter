import os
import PyPDF2
from pdf2image import convert_from_path


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