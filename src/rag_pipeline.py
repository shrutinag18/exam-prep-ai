import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

def get_llm():
    return ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model_name="llama-3.3-70b-versatile",
        temperature=0.3
    )

def create_qa_chain(vector_store):
    llm = get_llm()
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})

    prompt = PromptTemplate.from_template("""
    You are a helpful study assistant. Use the following context from the 
    student's notes or syllabus to answer the question.
    Always base your answer on the provided context.
    If the answer is not in the context, say "I couldn't find this in your documents."
    
    Context: {context}
    Question: {question}
    
    Answer:
    """)

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return chain