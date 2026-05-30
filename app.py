import streamlit as st
import urllib.parse
from src.topic_extractor import extract_topics
from src.video_recommender import recommend_videos
from src.document_loader import load_document, split_text
from src.embeddings import create_vector_store
from src.rag_pipeline import create_qa_chain
from src.question_generator import (
    generate_questions,
    generate_mock_test,
    generate_notes,
)

st.set_page_config(page_title="AI Exam Prep Assistant", layout="wide")
st.title("🎓 AI Exam Prep Assistant")
st.markdown("Upload your notes or syllabus and get predicted exam questions, answers and mock tests!")
st.divider()

# Session state
if "vector_store" not in st.session_state:
    st.session_state.vector_store = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Sidebar
with st.sidebar:
    st.header("📄 Upload Documents")
    uploaded_files = st.file_uploader(
        "Upload PDF files",
        type=["pdf","docx","pptx"],
        accept_multiple_files=True
    )

    if uploaded_files:
        if st.button("⚙️ Process Documents", use_container_width=True):
            with st.spinner("Reading and indexing your documents..."):
                all_chunks = []
                all_text = ""
                for file in uploaded_files:
                    text = load_document(file)
                    all_text += text + "\n"
                    chunks = split_text(text)
                    all_chunks.extend(chunks)

                st.session_state.vector_store = create_vector_store(all_chunks)
                st.session_state.topics = extract_topics(all_text)
                st.success(f"✅ Processed {len(uploaded_files)} document(s) — {len(all_chunks)} chunks indexed!")

    st.divider()
    st.markdown("### How to use")
    st.markdown("1. Upload PDF, DOCX or PPTX files")
    st.markdown("2. Click Process Documents")
    st.markdown("3. Use any tab to interact with your material")

# Main content
if st.session_state.vector_store is None:
    st.info("👈 Upload and process your documents from the sidebar to get started!")
else:
    tab1, tab2, tab3, tab4,tab5 = st.tabs(["💬 Ask Questions", "📝 Generate Exam Questions", "📋 Mock Test", "📒 Generate Notes","🎥 Video Recommendations"])

    # Tab 1 - Q&A
    with tab1:
        st.subheader("Ask anything from your documents")
        st.markdown("Type your question below and click **Get Answer**")

        question = st.text_input("Enter your question:", placeholder="e.g. What is backpropagation?")
        ask_button = st.button("🔍 Get Answer", use_container_width=True)

        if ask_button and question:
            with st.spinner("Finding answer from your documents..."):
                qa_chain = create_qa_chain(st.session_state.vector_store)
                answer = qa_chain.invoke(question)
                st.session_state.chat_history.append({
                    "question": question,
                    "answer": answer
                })

        if ask_button and not question:
            st.warning("Please enter a question first!")

        if st.session_state.chat_history:
            st.divider()
            st.markdown("### Chat History")
            for chat in reversed(st.session_state.chat_history):
                st.markdown(f"**🙋 Q: {chat['question']}**")
                st.markdown(f"🤖 **A:** {chat['answer']}")
                st.divider()

    # Tab 2 - Question Generator
    with tab2:
        st.subheader("Generate Predicted Exam Questions")
        st.markdown("Select your preferences and click **Generate Questions**")

        col1, col2, col3 = st.columns(3)
        with col1:
            topic = st.text_input("Topic (optional)", placeholder="e.g. Neural Networks")
        with col2:
            difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
        with col3:
            num_questions = st.slider("Number of Questions", 3, 15, 5)

        if st.button("📝 Generate Questions", use_container_width=True):
            with st.spinner("Generating exam questions from your material..."):
                questions = generate_questions(
                    st.session_state.vector_store,
                    topic=topic,
                    difficulty=difficulty,
                    num_questions=num_questions
                )
                st.divider()
                st.markdown(questions)

                st.download_button(
                    label="⬇️ Download Questions",
                    data=questions,
                    file_name="exam_questions.txt",
                    mime="text/plain",
                    use_container_width=True
                )

    # Tab 3 - Mock Test
    with tab3:
        st.subheader("Generate a Full Mock Test")
        st.markdown("Get a complete exam with mixed difficulty questions and full answer key")

        num_mock = st.slider("Number of Questions", 5, 20, 10)

        if st.button("📋 Generate Mock Test", use_container_width=True):
            with st.spinner("Creating your mock test..."):
                mock_test = generate_mock_test(
                    st.session_state.vector_store,
                    num_questions=num_mock
                )
                st.divider()
                st.markdown(mock_test)

                st.download_button(
                    label="⬇️ Download Mock Test",
                    data=mock_test,
                    file_name="mock_test.txt",
                    mime="text/plain",
                    use_container_width=True
                )

    # Tab 4 - Generate Notes
    with tab4:
        st.subheader("Generate Study Notes")
        st.markdown("AI will read your uploaded material and create clean structured notes")

        if st.button("📒 Generate Notes", use_container_width=True):
            with st.spinner("Generating structured notes from your material..."):
                notes = generate_notes(st.session_state.vector_store)
                st.divider()
                st.markdown(notes)

                st.download_button(
                    label="⬇️ Download Notes",
                    data=notes,
                    file_name="study_notes.txt",
                    mime="text/plain",
                    use_container_width=True
                )

    # Tab 5 - Video Recommendations
    with tab5:
        st.subheader("🎥 Recommended Learning Videos")

        if "topics" not in st.session_state:
            st.info("Upload and process documents first.")
        else:
            for topic in st.session_state.topics:
                st.markdown(f"### 📚 {topic}")

                queries = recommend_videos(topic)

                for query in queries:
                    youtube_url = (
                        "https://www.youtube.com/results?search_query="
                        + urllib.parse.quote(query)
                    )

                    st.markdown(f"▶ [{query}]({youtube_url})")

                st.divider()