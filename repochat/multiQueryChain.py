from langchain_community.vectorstores import Chroma
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain import hub
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from .db import vector_db, get_first_true_embedding, embedding_chooser
from .models import ai_agent

from .constants import (
    UUID,
    absolute_path_to_config,
    configuration,
    absolute_path_to_repo_directory,
    absolute_path_to_database_directory,
    repository_name_only,
    database_name_only,
    get_current_time_date,
)


class multiQuery:
    def __init__(self):
        self.database_name = f"db_{database_name_only()}"
        self.llm = ai_agent()[0]
        self.prompt = hub.pull("defishguy/rag-prompt")
        self.persist_dir = absolute_path_to_database_directory()
        self.db = vector_db()
        self.retriever = self.db.as_retriever()

        self.prompt = hub.pull("defishguy/rag-prompt")
        self.rag_chain = (
            {
                "context": self.retriever
                | (lambda docs: "\n\n".join(doc.page_content for doc in docs)),
                "question": RunnablePassthrough(),
            }
            | self.prompt
            | self.llm
            | StrOutputParser()
        )

    def question_and_answer(self, question):
        result = self.rag_chain.invoke(question)
        return result


# Streamlit application to take user input and display answers
# def main():
#    st.title("Question Answering System")
#    question = st.text_input("Ask a question:")
#    if question:
#        qa_system = QuestionAnsweringSystem()
#        answer = qa_system.answer_question(question)
#        st.text(answer)
