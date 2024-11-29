from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from observers.observers.models.docling import wrap_docling

pipeline_options = PdfPipelineOptions(
    images_scale=2.0,
    generate_page_images=True,
    generate_picture_images=True,
    generate_table_images=True,
)
format_options = {InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)}

converter = DocumentConverter(format_options=format_options)
converter = wrap_docling(converter, media_types=["pictures", "tables"])

source = "https://arxiv.org/pdf/2406.04467"  # document per local path or URL
result = converter.convert(source)
# output: ## Docling Technical Report [...]"
