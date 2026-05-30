from src.rag_pipeline import get_llm

def extract_topics(text):

    llm = get_llm()

    prompt = f"""
    Extract the 5 most important study topics from this text.

    Return only topic names.
    One topic per line.

    TEXT:
    {text[:5000]}
    """

    response = llm.invoke(prompt)

    topics = [
        topic.strip()
        for topic in response.content.split("\n")
        if topic.strip()
    ]

    return topics