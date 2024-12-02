from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from observers.observers.models.docling import wrap_docling
from observers.stores import ArgillaStore

api_url = "<your-api-url>"
api_key = "<your-api-key>"

store = ArgillaStore(api_url=api_url, api_key=api_key)

pipeline_options = PdfPipelineOptions(
    images_scale=2.0,
    generate_page_images=True,
    generate_picture_images=True,
    generate_table_images=True,
)
format_options = {InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)}

converter = DocumentConverter(format_options=format_options)
converter = wrap_docling(converter, store=store)

source = "https://arxiv.org/pdf/2408.09869"  # document per local path or URL
result = converter.convert(source)
result = converter.convert_all([source])
# output: ## Docling Technical Report [...]"
