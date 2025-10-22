from strands.multiagent import GraphBuilder
from agents.medical_coder_agents import build_medical_coder_agents


def build_medical_coder_graph():
    
    # 1. Build agents
    diagnosis_extractor, procedure_extractor, diagnosis_code_retriever, procedure_code_retriever, patient_summary_generator = build_medical_coder_agents()
    
    # 2. Initialize graph builder
    medical_coder_builder = GraphBuilder()

    # 3, Add nodes (identify agents)
    medical_coder_builder.add_node(diagnosis_extractor, "diagnosis_extractor")
    medical_coder_builder.add_node(procedure_extractor, "procedure_extractor")
    medical_coder_builder.add_node(diagnosis_code_retriever, "diagnosis_code_retriever")
    medical_coder_builder.add_node(procedure_code_retriever, "procedure_code_retriever")
    medical_coder_builder.add_node(patient_summary_generator, "patient_report_generator")

    # medical_coder_builder.add_node(file_writer, "file_writer")

    # 4. Add edges (connect agent inputs and outputs)
    medical_coder_builder.add_edge("diagnosis_extractor", "diagnosis_code_retriever")
    medical_coder_builder.add_edge("procedure_extractor", "procedure_code_retriever")
    medical_coder_builder.add_edge("diagnosis_code_retriever", "patient_report_generator")
    medical_coder_builder.add_edge("procedure_code_retriever", "patient_report_generator")

    # medical_coder_builder.add_edge("diagnosis_code_retriever", "file_writer", condition=write_file)
    # medical_coder_builder.add_edge("procedure_code_retriever", "file_writer", condition=write_file)
    # medical_coder_builder.add_edge("patient_summary_generator", "file_writer", condition=write_file)

    # 5. Set starting points
    medical_coder_builder.set_entry_point("diagnosis_extractor")
    medical_coder_builder.set_entry_point("procedure_extractor")

    # 6. Set max node executions
    medical_coder_builder.set_max_node_executions(1000)

    # 7. Set execution time limit
    medical_coder_builder.set_execution_timeout(600)   # 10 minute timeout

    # 8. Build graph
    medical_coder_graph = medical_coder_builder.build()
    
    return medical_coder_graph