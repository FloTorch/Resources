from flotorch.strands.agent import FlotorchStrandsAgent
from strands_tools import file_write
from tools.medical_coder_tools import search_codes_icd10cm, search_codes_hcpcs
from utils.config import settings

def build_medical_coder_agents():
    
    # --- Build Agent from Flotorch Gateway config ---
    diagnosis_extractor_client = FlotorchStrandsAgent(
        agent_name="diagnosis-extractor",
        api_key=settings.flotorch_api_key,
        base_url=settings.flotorch_base_url,
        # custom_tools=[]
    )
    # Get the Strands Agent from Flotorch Gateway
    diagnosis_extractor = diagnosis_extractor_client._get_synced_agent()


    procedure_extractor_client = FlotorchStrandsAgent(
        agent_name="procedure-extractor",
        api_key=settings.flotorch_api_key,
        base_url=settings.flotorch_base_url,
        # custom_tools=[]
    )
    procedure_extractor = procedure_extractor_client._get_synced_agent()


    diagnosis_code_retriever_client = FlotorchStrandsAgent(
        agent_name="diagnosis-code-retriever",
        api_key=settings.flotorch_api_key,
        base_url=settings.flotorch_base_url,
        custom_tools=[file_write, search_codes_icd10cm]
    )
    diagnosis_code_retriever = diagnosis_code_retriever_client._get_synced_agent()


    procedure_code_retriever_client = FlotorchStrandsAgent(
        agent_name="procedure-code-retriever",
        api_key=settings.flotorch_api_key,
        base_url=settings.flotorch_base_url,
        custom_tools=[file_write, search_codes_hcpcs]
    )
    procedure_code_retriever = procedure_code_retriever_client._get_synced_agent()

    patient_summary_generator_client = FlotorchStrandsAgent(
        agent_name="patient-report-generator",
        api_key=settings.flotorch_api_key,
        base_url=settings.flotorch_base_url,
        custom_tools=[file_write]
    )
    patient_summary_generator = patient_summary_generator_client._get_synced_agent()
    
    return diagnosis_extractor, procedure_extractor, diagnosis_code_retriever, procedure_code_retriever, patient_summary_generator