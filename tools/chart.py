import json
import os
from datetime import datetime
from typing import Literal, Union
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  
from langchain_core.tools import tool

try:
    from models.chart import Chart, Session
    DB_ENABLED = Session is not None
except ImportError:
    DB_ENABLED = False
    print("Warning: Chart database not available. Charts will only be saved as files.")


CHART_STORAGE_PATH = Path("static/charts")
CHART_STORAGE_PATH.mkdir(parents=True, exist_ok=True)


def _create_chart_image(
    chart_type: str,
    title: str,
    data: list[dict],
    x_label: str,
    y_label: str
) -> str:
    """Create actual chart image using matplotlib."""
    
    if not data:
        return None
    
    # Extract x and y values from data
    keys = list(data[0].keys())
    x_key = keys[0]
    y_key = keys[1] if len(keys) > 1 else keys[0]
    
    x_values = [item[x_key] for item in data]
    y_values = [item[y_key] for item in data]
    
    # Create figure
    plt.figure(figsize=(12, 6))
    
    # Create different chart types
    if chart_type == "line":
        plt.plot(x_values, y_values, marker='o', linewidth=2, markersize=6)
    elif chart_type == "bar":
        plt.bar(x_values, y_values)
    elif chart_type == "scatter":
        plt.scatter(x_values, y_values, s=100, alpha=0.6)
    elif chart_type == "area":
        plt.fill_between(range(len(x_values)), y_values, alpha=0.3)
        plt.plot(x_values, y_values, linewidth=2)
    elif chart_type == "pie":
        plt.pie(y_values, labels=x_values, autopct='%1.1f%%')
    
    # Styling
    plt.title(title, fontsize=16, fontweight='bold', pad=20)
    if chart_type != "pie":
        plt.xlabel(x_label, fontsize=12)
        plt.ylabel(y_label, fontsize=12)
        plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Rotate x-axis labels if too many
    if len(x_values) > 10 and chart_type != "pie":
        plt.xticks(rotation=45, ha='right')
    
    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"chart_{timestamp}.png"
    filepath = CHART_STORAGE_PATH / filename
    
    # Save chart
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()
    
    return str(filepath)


@tool(return_direct=True)
def generate_chart(
    chart_type: Literal["bar", "line", "pie", "scatter", "area"],
    title: str,
    data: Union[list[dict], str],
    x_label: str = "",
    y_label: str = "",
    description: str = "",
    thread_id: str = None  # Track which conversation
) -> str:
    """
    Generate a chart visualization from data and save as PNG image.
    Optionally saves metadata to database if available.
    
    Use this tool when:
    - User asks to visualize data
    - Showing trends over time (use "line")
    - Comparing categories (use "bar")
    - Showing proportions (use "pie")
    - Showing correlations (use "scatter")
    
    Args:
        chart_type: Type of chart - "bar", "line", "pie", "scatter", or "area"
        title: Clear, descriptive title for the chart
        data: List of dicts with data points OR JSON string. Example:
              [{"month": "Jan", "revenue": 1000}, {"month": "Feb", "revenue": 1200}]
        x_label: Label for x-axis (e.g., "Month", "Date", "Category")
        y_label: Label for y-axis (e.g., "Revenue ($M)", "Count", "Percentage")
        description: Brief description of what the chart shows
        thread_id: Optional conversation thread ID for tracking
    
    Returns:
        str: Message with chart file path and metadata
    """
    
    # Parse string input if needed
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError as e:
            return f"Chart Error: Invalid JSON data - {str(e)}"
    
    # Validation
    if not data:
        return "Chart Error: No data provided"
    
    if not isinstance(data, list):
        return f"Chart Error: Data must be a list, got {type(data)}"
    
    if not all(isinstance(item, dict) for item in data):
        return "Chart Error: All data items must be dictionaries"
    
    # Check for consistent keys
    if len(data) > 1:
        first_keys = set(data[0].keys())
        if not all(set(item.keys()) == first_keys for item in data):
            return " Chart Error: All data items must have the same keys"
    
    # Limit data points
    original_count = len(data)
    if len(data) > 100:
        data = data[:100]
        title += f" (showing first 100 of {original_count} points)"
    
    # Create chart image
    try:
        chart_path = _create_chart_image(
            chart_type=chart_type,
            title=title,
            data=data,
            x_label=x_label or "X-Axis",
            y_label=y_label or "Y-Axis"
        )
        
        if not chart_path:
            return " Chart Error: Failed to create chart image"
        
        chart_filename = Path(chart_path).name
        chart_url = f"/charts/{chart_filename}"
        
        # Save to database if available
        chart_info = {
            'chart_type': chart_type,
            'title': title,
            'file_path': chart_path,
            'file_url': chart_url,
            'x_label': x_label or "X-Axis",
            'y_label': y_label or "Y-Axis",
            'description': description or f"{chart_type.capitalize()} chart showing {title}",
            'data_points': len(data),
            'created_at': datetime.now().isoformat(),
            'thread_id': thread_id
        }
        
        if DB_ENABLED:
            try:
                session = Session()
                chart_record = Chart(
                    chart_type=chart_type,
                    title=title,
                    file_path=chart_path,
                    file_url=chart_url,
                    x_label=x_label or "X-Axis",
                    y_label=y_label or "Y-Axis",
                    description=description or f"{chart_type.capitalize()} chart showing {title}",
                    data_points=len(data),
                    thread_id=thread_id
                )
                session.add(chart_record)
                session.commit()
                
                chart_info['id'] = chart_record.id
                session.close()
            except Exception as db_error:
                print(f"Warning: Could not save chart to database: {db_error}")
        
        # Return success message
        return f""" Chart created successfully!

    **{title}**
- Type: {chart_type.capitalize()}
- Data points: {len(data)}
- File: `{chart_path}`
- URL: `{chart_url}`

The chart has been saved and is ready to view."""
    
    except Exception as e:
        return f"Chart Error: Failed to generate chart - {str(e)}"


@tool
def prepare_chart_data(
    sql_result: str,
    x_column: str,
    y_column: str,
    limit: int = 50
) -> str:
    """
    Helper tool to transform SQL results into chart-ready JSON format.
    
    Use this BEFORE generate_chart when you have SQL query results.
    
    Args:
        sql_result: The formatted SQL result string from sql_query tool
        x_column: Name of column to use for x-axis
        y_column: Name of column to use for y-axis
        limit: Maximum number of data points (default 50)
    
    Returns:
        str: JSON string of formatted data ready for generate_chart
    """
    try:
        lines = sql_result.strip().split('\n')
        
        # Find header line
        header_line = None
        for i, line in enumerate(lines):
            if '|' in line and not line.strip().startswith('-'):
                header_line = i
                break
        
        if header_line is None:
            return json.dumps([])
        
        # Parse headers
        headers = [h.strip() for h in lines[header_line].split('|')]
        
        # Find data start (after separator line)
        data_start = header_line + 2
        
        # Parse data rows
        data = []
        for line in lines[data_start:]:
            if line.strip() and '|' in line and not line.strip().startswith('...'):
                values = [v.strip() for v in line.split('|')]
                if len(values) == len(headers):
                    row_dict = dict(zip(headers, values))
                    
                    # Extract only x and y columns
                    if x_column in row_dict and y_column in row_dict:
                        data.append({
                            x_column: row_dict[x_column],
                            y_column: _parse_number(row_dict[y_column])
                        })
            
            if len(data) >= limit:
                break
        
        return json.dumps(data)
    
    except Exception as e:
        return json.dumps([])


def _parse_number(value: str) -> float:
    """Helper to parse numeric strings."""
    try:
        # Remove common formatting
        cleaned = value.replace(',', '').replace('$', '').replace('%', '').strip()
        return float(cleaned)
    except:
        return value  # Return as-is if not numeric


@tool
def list_charts(thread_id: str = None, limit: int = 10) -> str:
    """
    List recently created charts, optionally filtered by conversation thread.
    
    Args:
        thread_id: Optional thread ID to filter charts
        limit: Maximum number of charts to return (default 10)
    
    Returns:
        str: JSON list of chart metadata
    """
    if not DB_ENABLED:
        return "Chart database not available. Charts are saved as files only."
    
    try:
        session = Session()
        query = session.query(Chart)
        
        if thread_id:
            query = query.filter(Chart.thread_id == thread_id)
        
        charts = query.order_by(Chart.created_at.desc()).limit(limit).all()
        
        chart_list = [chart.to_dict() for chart in charts]
        session.close()
        
        if not chart_list:
            return "No charts found."
        
        return json.dumps(chart_list, indent=2)
    
    except Exception as e:
        return f"Error listing charts: {str(e)}"