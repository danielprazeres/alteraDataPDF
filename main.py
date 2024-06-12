import fitz  # PyMuPDF
import os

def replace_date_in_pdfs(source_folder, target_folder, old_dates, new_date):
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    for filename in os.listdir(source_folder):
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(source_folder, filename)
            new_pdf_path = os.path.join(target_folder, filename)

            doc = fitz.open(pdf_path)

            for page in doc:
                for old_date in old_dates:
                    text_instances = page.search_for(old_date)
                    for inst in text_instances:
                        rect = fitz.Rect(inst)
                        # Cobrir a data antiga com uma caixa branca
                        page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))
                        # Inserir a nova data em preto, diretamente nas coordenadas especificadas
                        # Ajustar a posição do texto para melhor visibilidade
                        page.insert_text((rect.x0 + 2, rect.y1 - 14), new_date, fontsize=12, color=(0, 0, 0))

            doc.save(new_pdf_path)
            doc.close()

source_folder = '/Users/danielprazeres/Desktop/arquivosPDF'
target_folder = '/Users/danielprazeres/Desktop/modificado'
old_dates = ['23/11/2023', '26/11/2023']
new_date = '10/06/2024'

replace_date_in_pdfs(source_folder, target_folder, old_dates, new_date)
