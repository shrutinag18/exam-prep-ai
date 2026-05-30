import streamlit as st
from src.document_loader import load_pdf, split_text
from src.embeddings import create_vector_store
from src.rag_pipeline import create_qa_chain
from src.question_generator import generate_questions, generate_mock_test

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
        type=["pdf"],
        accept_multiple_files=True
    )

    if uploaded_files:
        if st.button("Process Documents"):
            with st.spinner("Reading and indexing your documents..."):
                all_chunks = []
                for file in uploaded_files:
                    text = load_pdf(file)
                    chunks = split_text(text)
                    all_chunks.extend(chunks)

                st.session_state.vector_store = create_vector_store(all_chunks)
                st.success(f"Processed {len(uploaded_files)} document(s) — {len(all_chunks)} chunks indexed!")

    st.divider()
    st.markdown("### How to use")
    st.markdown("1. Upload your PDF notes or syllabus")
    st.markdown("2. Click Process Documents")
    st.markdown("3. Ask questions or generate exam questions")

# Main content
if st.session_state.vector_store is None:
    st.info("Upload and process your documents from the sidebar to get started!")
else:
    tab1, tab2, tab3 = st.tabs(["💬 Ask Questions", "📝 Generate Exam Questions", "📋 Mock Test"])

    # Tab 1 - Q&A
    with tab1:
        st.subheader("Ask anything from your documents")
        question = st.text_input("Enter your question:")

        if question:
            with st.spinner("Finding answer..."):
                qa_chain = create_qa_chain(st.session_state.vector_store)
                answer = qa_chain.invoke(question)

                st.session_state.chat_history.append({
                    "question": question,
                    "answer": answer
                })

        if st.session_state.chat_history:
            for chat in reversed(st.session_state.chat_history):
                st.markdown(f"**Q: {chat['question']}**")
                st.markdown(f"A: {chat['answer']}")
                st.divider()

    # Tab 2 - Question Generator
    with tab2:
        st.subheader("Generate Predicted Exam Questions")

        col1, col2, col3 = st.columns(3)
        with col1:
            topic = st.text_input("Topic (optional)", placeholder="e.g. Neural Networks")
        with col2:
            difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
        with col3:
            num_questions = st.slider("Number of Questions", 3, 15, 5)

        if st.button("Generate Questions"):
            with st.spinner("Generating exam questions..."):
                questions = generate_questions(
                    st.session_state.vector_store,
                    topic=topic,
                    difficulty=difficulty,
                    num_questions=num_questions
                )
                st.markdown(questions)

    # Tab 3 - Mock Test
    with tab3:
        st.subheader("Generate a Full Mock Test")

        num_mock = st.slider("Number of Questions", 5, 20, 10)

        if st.button("Generate Mock Test"):
            with st.spinner("Creating your mock test..."):
                mock_test = generate_mock_test(
                    st.session_state.vector_store,
                    num_questions=num_mock
                )
                st.markdown(mock_test)

                st.download_button(
                    label="Download Mock Test",
                    data=mock_test,
                    file_name="mock_test.txt",
                    mime="text/plain"
                )