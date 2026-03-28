import json
from langchain_core.tools import tool


@tool(return_direct=True)
def generate_chart(
    chart_type: str,
    title: str,
    data: list,
    x_label: str = "",
    y_label: str = "",
) -> str:
    
    """
    Generate a chart based on the provided data and parameters.

    Args:
        chart_type (str): The type of chart to generate (e.g., "bar", "line", "pie").
        title (str): The title of the chart.
        data (list): A list of dictionaries containing the data points for the chart.
        x_label (str, optional): The label for the x-axis. Defaults to "".
        y_label (str, optional): The label for the y-axis. Defaults to "".

    Returns:
        str: A JSON string representing the generated chart.
    """
    # For demonstration purposes, we'll return a JSON representation of the chart parameters.
    # In a real implementation, you would generate an actual chart image or URL here.
    chart_info = {
        "chart_type": chart_type,
        "title": title,
        "data": data,
        "x_label": x_label,
        "y_label": y_label
    }
    return f"CHART_DATA:{json.dumps(chart_info)}"