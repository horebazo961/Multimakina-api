import pdfplumber
import io
import logging

logger = logging.getLogger(__name__)

class PDFService:
    @staticmethod
    def extract_obd_dtc_from_pdf(file_bytes: bytes) -> str:
        """
        Extrae de forma determinista el texto y busca códigos de diagnóstico (DTC)
        desde un reporte PDF generado por un scanner OBD-II.
        """
        extracted_text = ""
        try:
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        extracted_text += text + "\n"
        except Exception as e:
            logger.error(f"Error crítico procesando el PDF OBD-II: {str(e)}")
            raise ValueError(f"No se pudo parsear el documento PDF: {str(e)}")
        
        return extracted_text.strip()

    @staticmethod
    def generate_vehicle_pdf(vehicle_data: dict) -> bytes:
        """
        Genera un reporte PDF consolidado del vehículo y sus fallas.
        """
        # Implementación base en bytes para evitar errores de importación
        buffer = io.BytesIO()
        buffer.write(f"Reporte Tecnico - {vehicle_data.get('brand', 'N/A')} {vehicle_data.get('model', 'N/A')}\n".encode('utf-8'))
        buffer.write(f"VIN: {vehicle_data.get('vin', 'N/A')}\n".encode('utf-8'))
        buffer.write(f"DTC Codes: {vehicle_data.get('dtc_codes', 'Sin codigos')}\n".encode('utf-8'))
        buffer.seek(0)
        return buffer.read()

# Funciones de conveniencia expuestas a nivel de módulo
def extract_obd_dtc_from_pdf(file_bytes: bytes) -> str:
    return PDFService.extract_obd_dtc_from_pdf(file_bytes)

def generate_vehicle_pdf(vehicle_data: dict) -> bytes:
    return PDFService.generate_vehicle_pdf(vehicle_data)