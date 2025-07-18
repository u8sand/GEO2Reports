import pandas as pd
import plotly.express as px
import dash_bio
import sklearn
from umap import UMAP
import numpy as np
import os
import kaleido

# import plotly.io as pio
# from IPython.display import Image, display

def plot(gene_counts, annotations, save_formats, n_components=2, decomp="pca", save_html=False, save_path=""):
    """
    Plots a dimensionality reduction (PCA, t-SNE, or UMAP) of gene counts.

    Args:
        gene_counts (pd.DataFrame): A normalized gene counts matrix.
        annotations (pd.DataFrame): Maps samples to its experimental group.
        n_components (int): Number of components to plot (2 or 3).
        decomp (str): Which decomposition to use: "pca", "tsne", or "umap".

    Returns:
        None
    """
    decomp = decomp.lower()
    gene_counts = gene_counts.T  # Ensure samples are rows

    if(n_components not in [2, 3]):
        raise ValueError("n_components must be either 2 or 3.")

    # Align annotations to gene_counts
    annotations = annotations.reindex(gene_counts.index)

    decomp = decomp.lower()
    if decomp == "pca":
        model = sklearn.decomposition.PCA(n_components=n_components)
        projections = model.fit_transform(gene_counts)
        total_variance = model.explained_variance_ratio_.sum() * 100
        title = f'PCA of Gene Expression (Total Variance explained: {total_variance:.2f}%)'
        labels = {str(i): f'PC{i+1} (variance explained: {model.explained_variance_ratio_[i]*100:.2f}%)' for i in range(n_components)}

    elif decomp == "tsne":
        perplexity = min(30, gene_counts.shape[0] - 1)
        model = sklearn.manifold.TSNE(n_components=n_components, random_state=42, perplexity=perplexity)
        projections = model.fit_transform(gene_counts.values)
        title = 't-SNE of Gene Expression'
        labels = {str(i): f't-SNE {i+1}' for i in range(n_components)}

    elif decomp == "umap":
        model = UMAP(n_components=n_components, random_state=42)
        projections = model.fit_transform(gene_counts.values)
        title = 'UMAP of Gene Expression'
        labels = {str(i): f'UMAP {i+1}' for i in range(n_components)}

    else:
        raise ValueError("decomp must be one of: 'pca', 'tsne', or 'umap'.")

    if n_components == 2:
        fig = px.scatter(
            projections, x=0, y=1, color=annotations["group"],
            #title=title,
            labels=labels, 
            hover_name=gene_counts.index,
        )
        fig.update_layout(
            width=700,
            height=500,
            plot_bgcolor="rgba(0,0,0,0)",
            showlegend=True,
            legend=dict(
                title="",
                font=dict(
                    size=14,
                    family='Arial'
                )
            ),
            # title=dict(
            #     font=dict(
            #         size=20
            #     ),
            #     x=0.5,
            #     xanchor="center"
            # )
        )
        fig.update_xaxes(
            showline=True,           
            linecolor="black",       
            linewidth=2,             
            showgrid=False,          
            zeroline=False,
            title=dict(
                font=dict(
                    size=20,
                    family='Arial'
                )
            )       
        )
        fig.update_yaxes(
            scaleanchor="x",
            scaleratio=1,
            showline=True,
            linecolor="black",
            linewidth=2,
            showgrid=False,
            zeroline=False,
            title=dict(
                font=dict(
                    size=20,
                    family='Arial'
                ),
                standoff=5
            )
        )
    else: #support for 3D plots
        fig = px.scatter_3d(
            projections, x=0, y=1, z=2, color=annotations["group"],
            title=title, labels=labels, width=600, height=600
        )
        fig.update_scenes(
            aspectmode="cube",
            xaxis=dict(
                showline=True,
                linecolor='lightgrey',
                showbackground=False,
                gridcolor='lightgrey',
                zerolinecolor='black'
            ),
            yaxis=dict(
                showline=True,
                linecolor='lightgrey',
                showbackground=False,
                gridcolor='lightgrey',
                zerolinecolor='black'
            ),
            zaxis=dict(
                showline=True,
                linecolor='lightgrey',
                showbackground=False,
                gridcolor='lightgrey',
                zerolinecolor='black'
            ),
        )

    fig.update_traces(marker=dict(size=20))
    
    for f in save_formats:
        fig_name = decomp + '.' + f
        fig.write_image(os.path.join(save_path, fig_name), scale=2)

    if save_html:
        fig_name = decomp + ".html"
        fig.write_html(os.path.join(save_path, fig_name))
    else:
        fig.show()

def plot_clustergram(gene_counts):
    '''
    Creates a reuasable Plotly Figure object that can be displayed in a Jupyter notebook.

    Args: 
        gene_counts (DataFrame): a normalized, filtered gene count matrix.
    
    Returns:
        plotly.graph_objs._figure.Figure: A clustergram in the form of a Plotly Figure
    '''
    
    clustergram = dash_bio.Clustergram(
        data = gene_counts,
        column_labels = list(gene_counts.columns.values),
        row_labels = list(gene_counts.index),
        color_threshold={
            'row': 250,
            'col': 700
        },
        hidden_labels='row',
        height = 800,
        width = 600,
        color_map= [
            [0.0, '#636EFA'],
            #[0.25, '#AB63FA'],
            [0.5, '#FFFFFF'],
            #[0.75, '#E763FA'],
            [1.0, '#EF553B']
        ],
        row_dist = "cosine",
        col_dist = "cosine",
        link_method="average",
        paper_bg_color='#FFFFFF'
    )
    return clustergram

def plot_volcano(deg, threshold, save_formats, save_name = "volcano", save_html=False, save_path=""):
    
    deg['significance'] = "insignificant"
    deg.loc[(deg['P.Value']<0.05) & (deg['logFC']<-threshold), 'significance'] = "downregulated"
    deg.loc[(deg['P.Value']<0.05) & (deg['logFC']>threshold), 'significance'] = "upregulated"
    
    deg['-log10p'] = -np.log10(deg['P.Value'])

    fig = px.scatter(
        deg,
        x='logFC',
        y='-log10p',
        color='significance',
        color_discrete_map={
            'insignificant': 'black',
            'upregulated': 'red',
            'downregulated': 'blue'
        },
        hover_name=deg.index,
        #title="Control vs. Perturbation Signatures-Volcano Plot",
    )
    #hide insignificant from the legend.
    for trace in fig['data']:
        if trace['name'] == 'insignificant':
            trace['showlegend']=False

    fig.update_layout(
        width=700,
        height=450,
        plot_bgcolor="rgba(0,0,0,0)",
        # title=dict(
        #     font=dict(
        #         size=20
        #     ),
        #     x=0.5,
        #     xanchor='center'
        # ),
        legend=dict(
            title="",
            font=dict(
                size=14,
                family='Arial'
            )
        ),
        font=dict(
            family='Arial'
        )
    )

    max_abs_x = max(abs(deg['logFC'].min()), abs(deg['logFC'].max()))+0.5
    max_y = deg['-log10p'].max()

    fig.update_xaxes(
        range=[-max_abs_x, max_abs_x],
        zerolinecolor="black",
        zerolinewidth=1,
        gridcolor="lightgrey",
        gridwidth=1,
        title=dict(
            font=dict(
                size=20,
            )
        )
    )
    fig.update_yaxes(
        range=[0, max_y * 1.05],
        zerolinecolor="black",
        zerolinewidth=1,
        gridcolor="lightgrey",
        gridwidth=1,
        title=dict(
            font=dict(
                size=20,
            )
        )
    )
    
    for fmt in save_formats:
        fig_name = f"{save_name}.{fmt}"
        fig.write_image(os.path.join(save_path, fig_name))

    if save_html:
        fig.write_html(os.path.join(save_path, f"{save_name}.html"))
    else:
        fig.show()
