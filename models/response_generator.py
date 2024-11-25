from core.chains import create_query_chain

class ResponseGenerator:
    """
    A class to generator natural language output based on provided SQL Query
    """

    def __init__(self, query_template: str):
        """
        Initialize the SQLGenerator class by creating the SQL Generation chain

        Args:
            query_template (str): A prompt template to generate SQL queries
        """
        self.query_template = query_template

    async def initialize_chain(self):
        """
        Initialize the chain for SQL Generation
        """
        self.query_chain = await create_query_chain(
            self.query_template,
            input_variables=["history", "user_input", "graph_query_response"],
        )
        return self.query_chain

    async def response_generator(self, user_query, history, db_response):
        """
        Generate an SQL query corrector chain
        """

        response_generator_chain = await self.initialize_chain()
        final_response = await response_generator_chain.ainvoke(
            {
                "history": history,
                "user_input": user_query,
                "graph_query_response": db_response,
            }
        )
        return final_response
