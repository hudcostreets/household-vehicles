from functools import partial

import plotly.express as px
import plotly.graph_objects as go
from ire import export


plotly_default_colors = px.colors.qualitative.Plotly
colors = default_colors = [ plotly_default_colors[i] for i in [2, 0, 3, 4, 1] ]


W, H = 700, 500
# W, H = 1200, 800


def plot(
        df,
        title, subtitle=None,
        y=None,
        colors=None,
        melt=None,
        name=None,
        w=W, h=H,
        pct=False,
        bg='white',
        ygrid='#bbb',
        legend=None,
        layout=None,
        xaxis=None,
        **kwargs
):
    if melt:
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

    if 'text' not in kwargs:
        kwargs['text'] = y

    if 'yrange' in kwargs:
        yrange = kwargs.pop('yrange')
    else:
        yrange = [0, 1] if pct else None

    traces_kwargs = {
        k: kwargs.pop(k) if k in kwargs else default
        for k, default in {
            'textposition': 'inside',
            'textangle': 0,
            'texttemplate': '%{y:.0%}' if pct else '%{y:.2s}',
        }.items()
    }

    fig = px.bar(df, **kwargs, y=y, color_discrete_sequence=colors)
    yaxis_kwargs = dict(
        yaxis=dict(
            tickformat=',.0%',
            range=yrange,
        )
    ) if pct else dict()

    fig.update_layout(
        xaxis=xaxis,
        hovermode='x',
        **yaxis_kwargs,
        legend=legend,
        plot_bgcolor=bg,
        **(layout or {}),
    )

    fig.update_xaxes(tickangle=-45)
    fig.update_yaxes(gridcolor=ygrid)
    fig.update_traces(hovertemplate=None, **traces_kwargs)
    titled_fig = go.Figure(fig)
    full_subtitle = f'<br><span style="font-size: 0.7em">{subtitle}</span>' if subtitle else ''
    full_title = f'{title}{full_subtitle}'
    titled_fig.update_layout(
        title=dict(text=full_title, x=0.5, y=.95),
        margin_t=fig.layout.margin.t + 50,
    )
    if name:
        fig.write_image(f'{name}.png', width=w, height=h)
        titled_fig.write_image(f'{name}_title.png', width=w, height=h)
    return export(titled_fig, name=name, show='png')


def ur_legend(title):
    return dict(
        yanchor="top",
        y=0.96,
        xanchor="right",
        x=0.98,
        title=title,
    )


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
abs_margin = dict(t=10, l=0, r=10, b=10)
abs_layout = dict(margin=abs_margin)

pct_plot = partial(plot, legend=pct_legend, layout=pct_layout, pct=True)
