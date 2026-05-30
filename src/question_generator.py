import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

def generate_questions(vector_store, topic="", difficulty="Medium", num_questions=5):
    llm = ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model_name="llama-3.3-70b-versatile",
        temperature=0.7
    )

    if topic:
        docs = vector_store.similarity_search(topic, k=5)
    else:
        docs = vector_store.similarity_search("main topics concepts", k=5)
    
    context = "\n".join([doc.page_content for doc in docs])
    topic_instruction = f"Focus on the topic: {topic}" if topic else "Cover the main topics from the material."

    prompt = f"""
    You are an expert exam question generator.
    Based on the following study material, generate {num_questions} {difficulty} level exam questions.
    {topic_instruction}
    
    Study Material:
    {context}
    
    Generate exactly {num_questions} questions in this format with each on a NEW LINE:
    
    **Q1.** [Question]
    
    **Q2.** [Question]
    
    Then provide answers:
    
    ## ANSWERS
    
    **A1.** [Answer]
    
    **A2.** [Answer]
    """

    response = llm.invoke(prompt)
    return response.content


def generate_mock_test(vector_store, num_questions=10):
    llm = ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model_name="llama-3.3-70b-versatile",
        temperature=0.7
    )

    docs = vector_store.similarity_search("important topics exam", k=8)
    context = "\n".join([doc.page_content for doc in docs])

    prompt = f"""
    Based on this study material, create a complete mock exam with {num_questions} questions.
    Include a mix of easy, medium and hard questions.
    Each question and answer MUST be on its own separate line.
    
    Study Material:
    {context}
    
    Use this exact format:
    
    ## MOCK EXAM
    
    **Q1.** [Question] *(Easy)*
    
    **Q2.** [Question] *(Medium)*
    
    ## ANSWER KEY
    
    **A1.** [Answer]
    
    **A2.** [Answer]
    """

    response = llm.invoke(prompt)
    return response.content
def generate_notes(vector_store):
    llm = ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model_name="llama-3.3-70b-versatile",
        temperature=0.3
    )

    docs = vector_store.similarity_search("main concepts topics summary", k=8)
    context = "\n".join([doc.page_content for doc in docs])

    prompt = f"""
    Based on the following study material, create clean and well structured study notes.
    
    Study Material:
    {context}
    
    Format the notes like this:
    
    ## 📚 Study Notes
    
    ### Topic 1: [Topic Name]
    - Key point 1
    - Key point 2
    - Key point 3
    
    ### Topic 2: [Topic Name]
    - Key point 1
    - Key point 2
    
    ### Key Definitions
    - **Term 1**: Definition
    - **Term 2**: Definition
    
    ### Important Formulas / Concepts
    - Formula or concept 1
    - Formula or concept 2
    
    ### Quick Summary
    2-3 sentences summarizing the entire material.
    """

    response = llm.invoke(prompt)
    return response.content