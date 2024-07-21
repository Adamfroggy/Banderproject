from altair import Chart
import altair as alt
from pandas import DataFrame


def chart(df: DataFrame, x: str, y: str,  target: str) -> alt.Chart:
    """
    Create a visually enhanced Altair chart based on the provided DataFrame.

    This function generates a scatter plot using Altair with customizable features such as color scheme,
    interactivity, and theming to match the dark mode of the web application.

    :param df: DataFrame containing the data to visualize. It must include columns corresponding to `x`, `y`, and `target`.
    :param x: Name of the column to be used for the x-axis.
    :param y: Name of the column to be used for the y-axis.
    :param target: Name of the column to be used for color encoding.
    :return: An Altair Chart object that represents the scatter plot.
    """

    # Define chart properties such as dimensions and background color
    properties = {
        'width': 800,
        'height': 400,
        'background': '2e2e2e',  # Dark background to match the web app theme
        'padding': 5
    }
    # Create an Altair chart with a scatter plot (circle marks)
    chart = alt.Chart(df, title="Enhanced Rank Chart").mark_circle(size=60).encode(
        # Encode the x-axis with the specified column and title
        x=alt.X(x, title=x, axis=alt.Axis(labelColor='white', titleColor='white')),
        # Encode the y-axis with the specified column and title
        y=alt.Y(y, title=y, axis=alt.Axis(labelColor='white', titleColor='white')),
        # Encode the color based on the target column with a color scale
        color=alt.Color(target, scale=alt.Scale(scheme='viridis'),
                        legend=alt.Legend(labelColor='white', titleColor='white')),
        # Add tooltips to display detailed information on hover
        tooltip=[x, y, target]
    ).properties(
        # Set the chart dimensions and background color
        width=properties['width'],
        height=properties['height'],
        background=properties['background'],
        padding=properties['padding']
    ).configure_title(
        # Configure the chart title's color
        color='white'
    ).configure_legend(
        # Configure the legend's label and title colors
        labelColor='white',
        titleColor='white'
    ).interactive() # Enable interactivity (zoom and pan)

    return chart

