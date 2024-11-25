from config.config import settings
from src.langchain_custom.graph_qa.cypher import GraphCypherQAChain
from langchain_community.graphs import Neo4jGraph
from langchain_community.chat_models.azure_openai import AzureChatOpenAI
from langchain_core.prompts.prompt import PromptTemplate

async def initialize_graph() -> Neo4jGraph:
    """Initialize and return the Neo4j graph."""
    return Neo4jGraph(
        url=settings.neo4j.NEO4J_URI,
        username=settings.neo4j.NEO4J_USERNAME,
        password=settings.neo4j.NEO4J_PASSWORD
    )

def get_azure_api_kwargs() -> dict:
    """Return the Azure API configuration."""
    return {
        "model": settings.azure.AZURE_MODEL_NAME,
        "api_key": settings.azure.MODEL_API_KEY,
        "azure_endpoint": settings.azure.MODEL_ENDPOINT,
        "api_version": settings.azure.AZURE_API_VERSION
    }

async def create_cypher_chain(graph: Neo4jGraph) -> GraphCypherQAChain:
    """Create and return a GraphCypherQAChain."""
    cypher_prompt = PromptTemplate(
        input_variables=["schema", "question"],
        template=settings.cypher.CYPHER_GENERATION_TEMPLATE
    )
    graph.refresh_schema()
    chain = GraphCypherQAChain.from_llm(
        cypher_prompt=cypher_prompt,
        llm=AzureChatOpenAI(temperature=0, **get_azure_api_kwargs()),
        graph=graph,
        return_intermediate_steps = True,
        verbose=True
    )
    return chain

async def cypher_chain(chain: GraphCypherQAChain, query: str) -> dict:
    """Invoke the chain with the given query and return the output."""
    return chain.invoke(query)
