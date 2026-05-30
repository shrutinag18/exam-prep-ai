from src.rag_pipeline import get_llm

def recommend_videos(topic):

    llm = get_llm()

    prompt = f"""
    Suggest 3 YouTube search queries for learning:

    {topic}

    Return only the search queries.
    One per line.
    """

    response = llm.invoke(prompt)

    return [
        query.strip()
        for query in response.content.split("\n")
        if query.strip()
    ]