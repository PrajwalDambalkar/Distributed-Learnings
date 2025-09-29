"""
MCP Server for TheMealDB Recipe API
Author: PrajwalD
Course: DATA-236 - Distributed Systems for Data Engineering
Assignment: Homework 4 - Part 3

This server implements the Model Context Protocol (MCP) to provide Claude
with tools for searching and retrieving recipe data from TheMealDB API.
"""

import asyncio
import logging
import sys
from typing import List, Dict, Any

import httpx
from mcp.server.fastmcp import FastMCP

# Configure logging to stderr only (stdout is reserved for JSON-RPC)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stderr,
)

# Initialize FastMCP server with name "meals"
mcp = FastMCP("meals")

# TheMealDB API base URL
API_BASE = "https://www.themealdb.com/api/json/v1/1"


def _clamp(n: int, lo: int, hi: int) -> int:
    """
    Clamp a value between minimum and maximum bounds.
    Ensures user-provided limits stay within valid API ranges.
    
    Args:
        n: The number to clamp
        lo: Minimum allowed value
        hi: Maximum allowed value
    
    Returns:
        Clamped value between lo and hi
    """
    try:
        n = int(n)
    except Exception:
        n = lo  # Default to minimum if conversion fails
    return max(lo, min(hi, n))


@mcp.tool()
async def search_meals_by_name(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Search for meals by name using TheMealDB search endpoint.
    
    Args:
        query: The meal name to search for (e.g., "pasta", "chicken")
        limit: Maximum number of results to return (1-25)
    
    Returns:
        List of meal dictionaries containing: id, name, area, category, thumb
    
    Example:
        search_meals_by_name("carbonara", limit=5)
    """
    q = (query or "").strip()
    if not q:
        logging.info("Empty search query received")
        return []

    logging.info(f"Searching for meals matching: '{q}' (limit: {limit})")
    limit = _clamp(limit, 1, 25)
    
    url = f"{API_BASE}/search.php"
    params = {"s": q}

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
    except (httpx.RequestError, httpx.HTTPStatusError) as e:
        logging.error(f"Network error during search: {e}")
        raise RuntimeError(f"Failed to connect to TheMealDB API: {e}") from e
    except ValueError as e:
        logging.error(f"Invalid JSON response: {e}")
        raise RuntimeError(f"Received malformed data from TheMealDB: {e}") from e

    meals = data.get("meals")
    if meals is None:
        logging.info(f"No meals found for query: '{q}'")
        return []

    # Extract relevant fields from each meal
    out: List[Dict[str, Any]] = []
    for m in meals:
        out.append({
            "id": m.get("idMeal"),
            "name": m.get("strMeal"),
            "area": m.get("strArea"),
            "category": m.get("strCategory"),
            "thumb": m.get("strMealThumb"),
        })
        if len(out) >= limit:
            break
    
    logging.info(f"Returning {len(out)} meals for '{q}'")
    return out


@mcp.tool()
async def meals_by_ingredient(ingredient: str, limit: int = 12) -> List[Dict[str, Any]]:
    """
    Filter meals by their main ingredient.
    
    Args:
        ingredient: Main ingredient to filter by (e.g., "chicken", "beef", "tomato")
        limit: Maximum number of results (1-50)
    
    Returns:
        List of meal dictionaries containing: id, name, thumb
    
    Example:
        meals_by_ingredient("chicken", limit=10)
    """
    ing = (ingredient or "").strip()
    if not ing:
        logging.info("Empty ingredient provided")
        return []
    
    logging.info(f"Filtering meals by ingredient: '{ing}' (limit: {limit})")
    limit = _clamp(limit, 1, 50)

    url = f"{API_BASE}/filter.php"
    params = {"i": ing}

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
    except (httpx.RequestError, httpx.HTTPStatusError) as e:
        logging.error(f"Network error filtering by ingredient: {e}")
        raise RuntimeError(f"Failed to fetch ingredient data from TheMealDB: {e}") from e
    except ValueError as e:
        logging.error(f"JSON parse error: {e}")
        raise RuntimeError(f"Invalid response format from TheMealDB: {e}") from e

    meals = data.get("meals")
    if meals is None:
        logging.info(f"No meals found with ingredient: '{ing}'")
        return []

    out = []
    for m in meals:
        out.append({
            "id": m.get("idMeal"),
            "name": m.get("strMeal"),
            "thumb": m.get("strMealThumb"),
        })
        if len(out) >= limit:
            break
    
    logging.info(f"Found {len(out)} meals with ingredient '{ing}'")
    return out


def _extract_ingredients(meal: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Extract ingredient-measure pairs from a meal object.
    TheMealDB stores ingredients as strIngredient1-20 and strMeasure1-20.
    
    Args:
        meal: Raw meal dictionary from API
    
    Returns:
        List of {name, measure} dictionaries for non-empty ingredients
    """
    items = []
    for i in range(1, 21):  # API has 20 ingredient slots
        name = (meal.get(f"strIngredient{i}") or "").strip()
        measure = (meal.get(f"strMeasure{i}") or "").strip()
        if name:  # Only include if ingredient name exists
            items.append({"name": name, "measure": measure})
    return items


@mcp.tool()
async def meal_details(id: str):
    """
    Lookup complete details for a specific meal by ID.
    
    Args:
        id: The meal ID (e.g., "52772")
    
    Returns:
        Dictionary with full meal information including:
        - Basic info: id, name, category, area
        - Media: image, youtube, source URL
        - Recipe: instructions, ingredients with measurements
    
    Example:
        meal_details("52772")
    """
    mid = (str(id) if id is not None else "").strip()
    if not mid:
        logging.error("meal_details called without ID")
        raise ValueError("Meal ID is required")

    logging.info(f"Fetching details for meal ID: {mid}")
    url = f"{API_BASE}/lookup.php"
    params = {"i": mid}

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
    except (httpx.RequestError, httpx.HTTPStatusError) as e:
        logging.error(f"Network error fetching meal details: {e}")
        raise RuntimeError(f"Failed to retrieve meal from TheMealDB: {e}") from e
    except ValueError as e:
        logging.error(f"JSON decode error: {e}")
        raise RuntimeError(f"Invalid data format from TheMealDB: {e}") from e

    meals = data.get("meals") or []
    if not meals:
        logging.warning(f"No meal found with ID: {mid}")
        return None

    m = meals[0]
    result = {
        "id": m.get("idMeal"),
        "name": m.get("strMeal"),
        "category": m.get("strCategory"),
        "area": m.get("strArea"),
        "instructions": m.get("strInstructions"),
        "image": m.get("strMealThumb"),
        "source": m.get("strSource"),
        "youtube": m.get("strYoutube"),
        "ingredients": _extract_ingredients(m),
    }
    
    logging.info(f"Successfully retrieved details for '{result['name']}'")
    return result


@mcp.tool()
async def random_meal() -> Dict[str, Any] | None:
    """
    Get a random meal from TheMealDB.
    Great for meal inspiration or discovering new recipes.
    
    Returns:
        Dictionary with same structure as meal_details
    
    Example:
        random_meal()
    """
    logging.info("Fetching random meal")
    url = f"{API_BASE}/random.php"

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()
    except (httpx.RequestError, httpx.HTTPStatusError) as e:
        logging.error(f"Network error getting random meal: {e}")
        raise RuntimeError(f"Failed to fetch random meal from TheMealDB: {e}") from e
    except ValueError as e:
        logging.error(f"JSON error: {e}")
        raise RuntimeError(f"Invalid response from TheMealDB: {e}") from e

    meals = data.get("meals") or []
    if not meals:
        logging.warning("Random meal endpoint returned no results")
        return None

    m = meals[0]
    result = {
        "id": m.get("idMeal"),
        "name": m.get("strMeal"),
        "category": m.get("strCategory"),
        "area": m.get("strArea"),
        "instructions": m.get("strInstructions"),
        "image": m.get("strMealThumb"),
        "source": m.get("strSource"),
        "youtube": m.get("strYoutube"),
        "ingredients": _extract_ingredients(m),
    }
    
    logging.info(f"Random meal selected: '{result['name']}'")
    return result


if __name__ == "__main__":
    # Run the MCP server
    asyncio.run(mcp.run())