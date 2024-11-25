"""
In this module, we define the llm chains to be used
"""

from .llm_service import LLMService
from langchain.prompts.prompt import PromptTemplate
from langchain_core.output_parsers import StrOutputParser


async def create_query_chain(query_template, input_variables):
    try:
        llm = LLMService()
        
        query_prompt = PromptTemplate(
            template=query_template, input_variables=input_variables
        )
        query_chain = query_prompt | llm | StrOutputParser()
        return query_chain
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
