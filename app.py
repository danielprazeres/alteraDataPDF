import fitz  # PyMuPDF
import os
import logging
import zipfile
from io import BytesIO
import streamlit as st

# Configurar logging
logging.basicConfig(level=logging.DEBUG)

# Configuração de pastas
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'

def replace_date_in_pdf(file_path, old_dates, new_date):
    logging.info(f'Substituindo datas no arquivo: {file_path}')
    try:
        doc = fitz.open(file_path)
        for page in doc:
            for old_date in old_dates:
                text_instances = page.search_for(old_date)
                for inst in text_instances:
                    rect = fitz.Rect(inst)
                    page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))
                    page.insert_text((rect.x0 + 2, rect.y1 - 14), new_date, fontsize=12, color=(0, 0, 0))
        processed_path = os.path.join(PROCESSED_FOLDER, os.path.basename(file_path))
        doc.save(processed_path)
        doc.close()
        logging.info(f'Arquivo processado salvo em: {processed_path}')
        return processed_path
    except Exception as e:
        logging.error(f'Erro ao processar arquivo: {e}')
        raise

def main():
    st.title("Substituir Datas em PDF")
    st.write("Faça upload de arquivos PDF, especifique as datas antigas e a nova data para substituí-las.")

    uploaded_files = st.file_uploader("Envie os arquivos PDF", type="pdf", accept_multiple_files=True)
    old_dates_str = st.text_input("Insira as datas antigas (separadas por vírgula)", placeholder="ex: 23/11/2023,26/11/2023")
    new_date = st.text_input("Insira a nova data", placeholder="ex: 20/11/2024")
    
    if st.button("Processar Arquivos"):
        if not uploaded_files:
            st.error("Por favor, envie pelo menos um arquivo PDF.")
            return
        
        if not old_dates_str or not new_date:
            st.error("Por favor, insira datas antigas e a nova data corretamente.")
            return
        
        # Convertendo datas antigas para uma lista
        old_dates = [date.strip() for date in old_dates_str.split(',') if date.strip()]
        
        processed_files = []
        for uploaded_file in uploaded_files:
            if allowed_file(uploaded_file.name):
                file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
                with open(file_path, 'wb') as f:
                    f.write(uploaded_file.read())
                logging.info(f'Arquivo enviado para: {file_path}')

                try:
                    processed_file_path = replace_date_in_pdf(file_path, old_dates, new_date)
                    processed_files.append(processed_file_path)
                except Exception as e:
                    logging.error(f'Erro no processamento: {e}')
                    st.error(f"Erro ao processar o arquivo {uploaded_file.name}. Verifique os logs para mais detalhes.")
                    return

        # Criando arquivo ZIP com PDFs processados
        if processed_files:
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
                for file_path in processed_files:
                    zf.write(file_path, os.path.basename(file_path))
            zip_buffer.seek(0)
            
            st.success("Arquivos processados com sucesso!")
            st.download_button(
                label="Baixar Arquivos Processados (ZIP)",
                data=zip_buffer,
                file_name="arquivos_processados.zip",
                mime="application/zip"
            )
        else:
            st.error("Nenhum arquivo foi processado.")

if __name__ == '__main__':
    main()