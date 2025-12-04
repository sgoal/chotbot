from ddgs import DDGS
import logging

logger = logging.getLogger(__name__)

class SearchTool:
    """
    A tool for performing deep searches using DuckDuckGo.
    """

    def run(self, query: str, max_results: int = 3) -> dict:
        """
        Performs a search using DuckDuckGo and returns the results.

        Args:
            query (str): The search query.
            max_results (int): The maximum number of results to return.

        Returns:
            dict: A dictionary containing the search results or an error message.
        """
        logger.info(f"Performing search for: '{query}'")
        try:
            with DDGS(timeout=20) as ddgs:
                results = list(ddgs.text(
                    query,
                    max_results=max_results
                ))
            logger.info(f"Found {len(results)} results.")
            
            # 格式化结果，添加引用信息
            formatted_results = []
            for idx, result in enumerate(results, 1):
                formatted_results.append({
                    "id": idx,
                    "title": result.get("title", ""),
                    "body": result.get("body", ""),
                    "href": result.get("href", ""),
                    "source": "DuckDuckGo Search"
                })
            
            return {
                "result": formatted_results,
                "citations": formatted_results  # 添加引用信息
            }
        except Exception as e:
            logger.error(f"Search failed for query '{query}': {e}", exc_info=True)
            return {"error": "Search failed", "message": str(e)}