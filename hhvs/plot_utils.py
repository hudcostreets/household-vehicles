from functools import partial
from os.path import join

import plotly.express as px
import plotly.graph_objects as go
from IPython.core.display import Image
import ire
from ire import export


plotly_default_colors = px.colors.qualitative.Plotly
colors = default_colors = [ plotly_default_colors[i] for i in [2, 0, 3, 4, 1] ]


W, H = 700, 500
# W, H = 1200, 800


def plot(
        df,
        title,
        subtitle=None,
        subtitle_size='0.7em',
        y=None,
        colors=None,
        melt=None,
        name=None,
        w=W, h=H,
        pct=False,
        bg='white',
        x_tickangle=-45,
        xgrid=None,
        ygrid='#bbb',
        legend=None,
        layout=None,
        xaxis=None,
        export_kwargs=None,
        **kwargs
):
    """Plotly bar graph wrapper exposing default settings and data transforms used in this project."""
    if melt:
        # Convert input `df` from "wide" to "long" format, set plot {x,y,color} kwargs appropriately
        x = df.index.name
        y = melt
        color = df.columns.name
        df = df.reset_index().melt(id_vars=x, value_name=melt)
        kwargs['x'] = x
        kwargs['color'] = color

    colors = colors or default_colors
    if y or 'value' not in kwargs.get('labels', {}):
        y = y or df.columns.name
        if 'labels' not in kwargs:
            kwargs['labels'] = {}
        kwargs['labels']['value'] = y

    if 'yrange' in kwargs:
        yrange = kwargs.pop('yrange')
    else:
        # "Stacked percentage" graph range
        yrange = [0, 1] if pct else None

    yaxis_kwargs = dict(
        yaxis=dict(
            tickformat=',.0%',
            range=yrange,
        )
    ) if pct else dict()

    # Optionally disable iRe export
    do_export = kwargs.pop('export') if 'export' in kwargs else True

    if 'text' not in kwargs:
        # Label each bar with its y-axis value
        kwargs['text'] = y

    # Configure text-label properties
    traces_kwargs = {
        k: kwargs.pop(k) if k in kwargs else default
        for k, default in {
            'textposition': 'inside',
            'textangle': 0,
            'texttemplate': '%{y:.0%}' if pct else '%{y:.2s}',
        }.items()
    }

    fig = px.bar(df, **kwargs, y=y, color_discrete_sequence=colors)
    fig.update_layout(
        xaxis=xaxis,
        hovermode='x',
        **yaxis_kwargs,
        legend=legend,
        plot_bgcolor=bg,
        width=w,
        height=h,
        **(layout or {}),
    )

    fig.update_xaxes(tickangle=x_tickangle, gridcolor=xgrid)
    fig.update_yaxes(gridcolor=ygrid)
    fig.update_traces(hovertemplate=None, **traces_kwargs)

    # Save 2 copies of the plot, as PNG:
    # - one with title text "burned in" to the image
    # - one without the title text
    # The latter is used in e.g. the README, where the title is included in Markdown above each image.
    titled_fig = go.Figure(fig)
    full_subtitle = f'<br><span style="font-size: {subtitle_size}">{subtitle}</span>' if subtitle else ''
    full_title = f'{title}{full_subtitle}'
    titled_fig.update_layout(
        title=dict(text=full_title, x=0.5, y=.95),
        margin_t=fig.layout.margin.t + 50,
    )

    # Save PNGs (with and without "title")
    if name:
        fig.write_image(f'{name}.png', width=w, height=h)
        titled_fig.write_image(f'{name}_title.png', width=w, height=h)

    # Optionally export plot JSON to iRe
    if do_export:
        return export(titled_fig, name=name, show='png', **(export_kwargs or {}))
    else:
        return Image(titled_fig.to_image(width=w, height=h))


def ur_legend(title):
    """Plotly "layout" properties for a legend in the upper right corner, with given text."""
    return dict(
        yanchor="top",
        y=0.96,
        xanchor="right",
        x=0.98,
        title=title,
    )


# Layout properties for stacked bar graphs
abs_margin = dict(t=10, l=0, r=10, b=10)
abs_layout = dict(margin=abs_margin)
abs_plot = partial(plot, layout=abs_layout)

# Layout properties for stacked "percentage" graphs
pct_legend = dict(
    orientation="h",
    yanchor="bottom",
    y=1.01,
    xanchor="center",
    x=0.5,
    title='Vehicles per household:',
)
pct_margin = dict(t=40, l=0, r=10, b=10)
pct_layout = dict(margin=pct_margin)
pct_plot = partial(plot, legend=pct_legend, layout=pct_layout, pct=True)
