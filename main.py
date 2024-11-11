import asyncio
import pandas as pd
from typing import List, Tuple
from time import perf_counter
from src.chains.boundoschain import initialize_graph, create_cypher_chain, cypher_chain


queries = [
    "Which is the latest OS version to use for E5760?",
    "Please generate a complete list of platform controllers with the initial version of ONTAP each was released on.",
    "The data team is enquired for this. How many NetApp systems have upgraded to ONTAP 9.15.1 and beyond?",
    "Provide me all the major versions of operating system for ONTAP after 9.10.1.",
    "My team needs information on all the patch releases for 9.14.1 and 9.15.1 and 9.16.1. List all of their patch releases with support states.",
    "Provide me the temperature details for the AFF-A90 controller.",
    "Which platform controllers are available under the E2800 family? Could you provide the platform configurations for each as well.",
    "Provide me the physical details for AFF A150A UTA2 Single Chassis HA Pair.",
    
    "Can you tell me the various port counts for E2812 Simplex 8GB FC?",
    "I was told to install the latest patch of ONTAP 9.14.1 for FAS9000. Could you check what the latest patch release is?",
    "What is the advised OS release for 9.15.1 for AFF A1K?",
    "My configuration is using AFF A150 with either 9.14.1. Which version of OS do you suggest to use?",
    
    "My team is asking for all the recommended ONTAP releases for AFF A220 platform.",
    "What are the recommended OS version for E2624?",
    # "I need a list of ONTAP versions that I can run on my AFF C250 system. Beginning with the most recent version, list every single version that is supported. Make this a descending list, ending with the very first version that was supported on the system.",
    "Can you tell me the latest P release of FAS2620 and FAS6280 for every support state?",
    "What are the overlapping OS versions for AFF A200 and AFF A150?",
    "What are RC releases and are they ever recommended in platform controller configuration?",
    "What are all supports and milestone dates for 9.14.1P1?"
]

async def execute_query(chain, query: str) -> Tuple[str, str, str, float]:
    """
    Executes a single Cypher query and returns its details.

    Parameters:
        chain: The Cypher chain object.
        query (str): The query string to execute.

    Returns:
        Tuple[str, str, str, float]: Query, result, Cypher query, and execution time.
    """
    start_time = perf_counter()
    output = await cypher_chain(chain, query)
    exec_time = perf_counter() - start_time

    result = output.get("result", None)
    cypher_query = output.get("intermediate_steps", [{}])[0].get("query", "").replace("cypher\n", "", 1)
    return query, result, cypher_query, exec_time

async def executor_csv(user_queries: List[str]) -> pd.DataFrame:
    """
    Main function to execute multiple graph queries asynchronously and store their performance metrics.

    Parameters:
        user_queries (List[str]): List of queries to execute.

    Returns:
        pd.DataFrame: DataFrame with query results and performance metrics.
    """
    graph = await initialize_graph()
    chain = await create_cypher_chain(graph)

    # Asynchronously execute all queries and gather results
    tasks = [execute_query(chain, query) for query in user_queries]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Prepare data for DataFrame, filtering out any failed queries
    data = [
        {"Query": query, "Result": result, "Cypher Query": cypher_query, "Execution Time (s)": round(exec_time,3)}
        for query, result, cypher_query, exec_time in results
        if not isinstance(result, Exception)
    ]

    # Convert to DataFrame
    df = pd.DataFrame(data)
    return df

async def main():
    graph = await initialize_graph()
    chain = await create_cypher_chain(graph)
    while True:
        query = input("Enter your query (type 'exit' or 'bye' to stop.): ")
        
        if query.lower() in {"exit", "bye"}:
            print("Have a nice day.. BYE.......")
            break
        
        query_text, result, cypher_query, exec_time = await execute_query(chain=chain, query=query)
        print(f"Query: {query_text}\nResult: {result}\nCypher Query: {cypher_query}\nExecution Time: {exec_time} seconds\n")

if __name__ == "__main__":
    asyncio.run(main())