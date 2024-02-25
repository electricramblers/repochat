from langchain_community.vectorstores import Chroma
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain import hub
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from .db import vector_db
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
        self.retriever = MultiQueryRetriever.from_llm(
            retriever=self.db.as_retriever(), llm=self.llm
        )
        self.prompt = hub.pull("defishguy/rag-prompt")
        if self.retriever is not None:
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
        else:
            self.rag_chain = None

    def question_and_answer(self, question):
        if self.rag_chain is not None:
            result = self.rag_chain.invoke(question)
            return result
        else:
            return (
                "Unable to process the question as the vector database does not exist."
            )
