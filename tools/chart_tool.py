import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import pandas as pd

def generate_chart_tool(rows, columns, chart_type, x_col, y_col, title):
    """
    Generates a matplotlib chart and returns the base64 encoded PNG string.
    """
    try:
        if not rows or not columns:
            return None

        df = pd.DataFrame(rows, columns=columns)
        
        # Basic data validation
        if x_col not in df.columns or y_col not in df.columns:
            print(f"[Chart Tool] Error: Columns {x_col} or {y_col} not found in data.")
            return None

        plt.figure(figsize=(10, 6))
        
        if chart_type == "bar":
            plt.bar(df[x_col], df[y_col], color='skyblue')
        elif chart_type == "line":
            plt.plot(df[x_col], df[y_col], marker='o', linestyle='-', color='green')
        elif chart_type == "scatter":
            plt.scatter(df[x_col], df[y_col], color='red')
        elif chart_type == "pie":
            plt.pie(df[y_col], labels=df[x_col], autopct='%1.1f%%')
        else:
            # Default to line
            plt.plot(df[x_col], df[y_col])

        plt.title(title)
        plt.xlabel(x_col)
        plt.ylabel(y_col)
        plt.tight_layout()

        # Save to buffer
        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        plt.close()
        buf.seek(0)
        
        # Encode to base64
        img_base64 = base64.b64encode(buf.read()).decode("utf-8")
        return img_base64

    except Exception as e:
        print(f"[Chart Tool] Generation Failed: {e}")
        return None