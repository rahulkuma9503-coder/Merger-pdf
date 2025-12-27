import shutil
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import Color
from io import BytesIO
import math

class PDFHandler:
    """Handle all PDF operations"""
    
    def merge_pdfs(self, pdf_files, output_path):
        """
        Merge multiple PDF files into one
        
        Args:
            pdf_files: List of PDF file paths to merge
            output_path: Output file path for merged PDF
        """
        writer = PdfWriter()
        
        for pdf_file in pdf_files:
            reader = PdfReader(pdf_file)
            for page in reader.pages:
                writer.add_page(page)
        
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
    
    def rename_pdf(self, input_path, output_path):
        """
        Rename a PDF file (essentially copy with new name)
        
        Args:
            input_path: Original PDF file path
            output_path: New PDF file path with desired name
        """
        shutil.copy2(input_path, output_path)
    
    def add_watermark(self, input_path, output_path, watermark_text, position='center', opacity=0.3):
        """
        Add text watermark to all pages of a PDF
        
        Args:
            input_path: Input PDF file path
            output_path: Output PDF file path
            watermark_text: Text to use as watermark
            position: Watermark position ('center', 'top', 'bottom', 'diagonal')
            opacity: Watermark opacity (0.0 to 1.0)
        """
        reader = PdfReader(input_path)
        writer = PdfWriter()
        
        for page in reader.pages:
            # Create watermark
            watermark = self._create_watermark(
                watermark_text, 
                position, 
                opacity,
                float(page.mediabox.width),
                float(page.mediabox.height)
            )
            
            # Merge watermark with page
            page.merge_page(watermark.pages[0])
            writer.add_page(page)
        
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
    
    def _create_watermark(self, text, position, opacity, page_width, page_height):
        """
        Create a watermark PDF
        
        Args:
            text: Watermark text
            position: Position of watermark
            opacity: Opacity value
            page_width: Width of the page
            page_height: Height of the page
        
        Returns:
            PdfReader object with watermark
        """
        packet = BytesIO()
        c = canvas.Canvas(packet, pagesize=(page_width, page_height))
        
        # Set font and size
        font_size = 50
        c.setFont("Helvetica-Bold", font_size)
        
        # Set color with opacity
        c.setFillColor(Color(0.5, 0.5, 0.5, alpha=opacity))
        
        # Calculate text dimensions
        text_width = c.stringWidth(text, "Helvetica-Bold", font_size)
        
        # Position watermark based on user selection
        if position == 'center':
            x = (page_width - text_width) / 2
            y = page_height / 2
            c.drawString(x, y, text)
        
        elif position == 'top':
            x = (page_width - text_width) / 2
            y = page_height - 100
            c.drawString(x, y, text)
        
        elif position == 'bottom':
            x = (page_width - text_width) / 2
            y = 50
            c.drawString(x, y, text)
        
        elif position == 'diagonal':
            # Rotate text diagonally
            c.saveState()
            c.translate(page_width / 2, page_height / 2)
            c.rotate(45)
            c.drawString(-text_width / 2, 0, text)
            c.restoreState()
        
        c.save()
        
        # Move to the beginning of the BytesIO buffer
        packet.seek(0)
        
        return PdfReader(packet)
