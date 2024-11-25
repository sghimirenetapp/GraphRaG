from core.chains import create_query_chain


class QueryCorrector:
    """
    A class to handle Query generation from natural language input
    """

    def __init__(self, query_template: str):
        """
        Initialize the SQLGenerator class by creating the SQL Generation chain

        Args:
            query_template (str): A prompt template to generate SQL queries
        """
        self.query_template = query_template
        self.query_chain = None

    async def initialize_chain(self):
        """
        Initialize the chain for SQL Generation
        """
        self.query_chain = await create_query_chain(
            self.query_template,
            input_variables=[
                "dialect",
                "question",
                "schema",
                "prev_query",
                "suggestions",
            ],
        )
        return self.query_chain

    async def graph_query_corrector(self):
        """
        Generate an SQL query corrector chain
        """

        await self.initialize_chain()
        return self.query_chain
