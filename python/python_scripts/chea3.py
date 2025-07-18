import json
import requests
import numpy as np
from time import sleep
from tabulate import tabulate
from IPython.display import HTML, display, Image, FileLink, Markdown
import plotly.graph_objects as go
import kaleido
import os

num_tfs = 10
threshold =3

def get_chea3_results(gene_set, query_name):
    ADDLIST_URL = 'https://maayanlab.cloud/chea3/api/enrich/'
    payload = {
        'gene_set': gene_set,
        'query_name': query_name
    }
    response = requests.post(ADDLIST_URL, data=json.dumps(payload))
    if not response.ok: 
        # r.ok (where r is the object) returns whether the call to the url was successful
        raise Exception('Error analyzing gene list')
    sleep(1)
    return json.loads(response.text) # .text returns the content of response in unicode

# Function for displaying tables 
def display_tables(lib, description, results):
    
    for libname in lib:
        display(HTML(f'<h3>{libname}</h3>'))
        
        table = [0] * num_tfs
        tablecounter = 0
        for i in results[libname][0:num_tfs]:
            table[tablecounter] = [i['Rank'],
                                   i['TF'],
                                   f"{i['Intersect']}/{i['Set length']}", 
                                   i['FET p-value'], 
                                   i['FDR'], 
                                   i['Odds Ratio'],
                                   f"{', '.join(i['Overlapping_Genes'].split(',')[0:10])}, ..."]
            tablecounter += 1

        display(HTML(tabulate(table, 
                              ['Rank', 
                               'TF', 
                               'Overlap', 
                               'FET p-value', 
                               'FDR', 
                               'Odds Ratio', 
                               'Overlapping Genes'], 
                              tablefmt='html')))
        
        display(HTML(f'<h5>{description[libname]}</h5>'))
        
        tsv_name = f"{libname.replace(' ', '_')}.tsv"
        with open(tsv_name, 'w') as tsv_file:
            tsv_file.write(tabulate(table, ['Rank', 
                                            'TF',
                                            'Overlap', 
                                            'FET p-value', 
                                            'FDR', 
                                            'Odds Ratio', 
                                            'Overlapping Genes'], 
                                    tablefmt='tsv'))
        display(HTML(f'<a href="{tsv_name}">Download table in .tsv</a>'))
        
        
# Function for displaying the individual library bar charts 
def display_charts(libs, description, results): 
    for libname in libs:
        
        display(HTML(f'<h3>{libname}</h3>'))
        
        tfs = [i['TF'] for i in results[libname]][0:num_tfs]
        scores = [float(i['FET p-value']) for i in results[libname]][0:num_tfs]
        
        # reverse the order/ranking of the tfs (and their respective scores)
        tfs = tfs[::-1]
        scores = scores[::-1]

        # takes the -log of the scores
        scores = -np.log10(scores)

        
        score_range = max(scores) - min(scores)
        x_lowerbound = min(scores) - (score_range * 0.05)
        x_upperbound = max(scores) + (score_range * 0.05)
        
        libfig = go.Figure(data = go.Bar(name = libname, 
                                         x = scores, 
                                         y = tfs, 
                                         marker = go.bar.Marker(color = 'rgb(255,127,80)'), 
                                         orientation = 'h'))
        libfig.update_layout(
            title = {
                'text':'Bar Chart of Scores based on FET p-values',
                'y': 0.87,
                'x': 0.5,
                'xanchor':'center',
                'yanchor':'top'
            },
            xaxis_title = '-log\u2081\u2080(FET p-value)', 
            # \u208 unicode to get the subscript (need a subscript of "10")
            yaxis_title = 'Transcription Factors',
            font = dict(
                size = 16,
                color = 'black'
            )
        )
        
        libfig.update_xaxes(range = [x_lowerbound, x_upperbound])
        
        libfig.show()
        
        display(HTML(f'<h5>{description[libname]}</h5>'))
        
def indexfinder(lib_score_list, value):
    index = 1
    for num in lib_score_list:
        if num == value:
            return index
        elif num != 0:
            index += 1

def mean_rank_bar(results, save_name, save_formats, save_html=False, save_path=""):
    c_lib_palette = {'ARCHS4 Coexpression':'rgb(196, 8, 8)',
                 'ENCODE ChIP-seq':'rgb(244, 109, 67)',
                 'Enrichr Queries':'rgb(242, 172, 68)', 
                 'GTEx Coexpression':'rgb(236, 252, 68)',
                 'Literature ChIP-seq':'rgb(165, 242, 162)',
                 'ReMap ChIP-seq':'rgb(92, 217, 78)'}
    # this sets all the color values for all the libraries that will be displayed in the bar chart

    # NOTE: removed Integrated mean/topRank since those are compiled from the above 6 libraries 
    # afterwards and so none of the TFs will have Integrated mean/topRank as one of their libraries

    c_lib_means = {'ARCHS4 Coexpression': [0] * num_tfs, 'ENCODE ChIP-seq': [0] * num_tfs, 
                'Enrichr Queries': [0] * num_tfs, 'GTEx Coexpression': [0] * num_tfs,
                'Literature ChIP-seq': [0] * num_tfs, 'ReMap ChIP-seq': [0] * num_tfs}
    # creates a dictionary where each library is a key, and the values are empty lists with as
    # many indices/spaces as the user has requested transcription factors (ex: if the user
    # requests 15 TFs to be returned, the lists will have 15 spaces)


    libs_sorted = ['ARCHS4 Coexpression','ENCODE ChIP-seq','Enrichr Queries',
                'GTEx Coexpression','Literature ChIP-seq','ReMap ChIP-seq']



    mr_results = results['Integrated--meanRank']
    ###### NOTE: for meanRank, the TFs are already ranked by Score ######

    for i in range(len(mr_results)):
        for lib in libs_sorted:
            mr_results[i].update({lib:0})
            
    for i in range(len(mr_results)):
        thing = mr_results[i]['Library'].split(';')
        for a in range(len(thing)):
            library, value = thing[a].split(',')
            mr_results[i].update({library:int(value)})
        
    sortedARCHS4 = sorted(mr_results, key = lambda k: k['ARCHS4 Coexpression'])
    sortedGTEx = sorted(mr_results, key = lambda k: k['GTEx Coexpression']) 
    sortedEnrichr = sorted(mr_results, key = lambda k: k['Enrichr Queries']) 
    sortedENCODE = sorted(mr_results, key = lambda k: k['ENCODE ChIP-seq']) 
    sortedReMap = sorted(mr_results, key = lambda k: k['ReMap ChIP-seq']) 
    sortedLit = sorted(mr_results, key = lambda k: k['Literature ChIP-seq']) 

    rankedARCHS4 = [entry['ARCHS4 Coexpression'] for entry in sortedARCHS4]
    rankedENCODE = [entry['ENCODE ChIP-seq'] for entry in sortedENCODE]
    rankedEnrichr = [entry['Enrichr Queries'] for entry in sortedEnrichr] 
    rankedGTEx = [entry['GTEx Coexpression'] for entry in sortedGTEx]
    rankedLit = [entry['Literature ChIP-seq'] for entry in sortedLit]
    rankedReMap = [entry['ReMap ChIP-seq'] for entry in sortedReMap] 


    ranking_dict = {'ARCHS4 Coexpression':rankedARCHS4,
                    'ENCODE ChIP-seq':rankedENCODE,
                    'Enrichr Queries':rankedEnrichr,
                    'GTEx Coexpression':rankedGTEx,
                    'Literature ChIP-seq':rankedLit,
                    'ReMap ChIP-seq':rankedReMap}

    for tfentry in mr_results:
        tfentry.update( [('SumRank', 0), ('AvgRank', 0) ])
        library_scores = tfentry['Library'].split(';')
        lib_counter = 0
        for a in library_scores:
            l, v = a.split(',')
            v = int(v)
            #scorerank = ranking_dict[l].index(v) + 1
            scorerank = indexfinder(ranking_dict[l], int(v))
            tfentry['SumRank'] += int(scorerank)
            lib_counter += 1
        tfentry['AvgRank'] = (tfentry['SumRank'] / lib_counter)
        
    sorted_results = sorted(mr_results, key = lambda k: k['AvgRank'])

    sorted_top_results = []
    index = 0
    while (len(sorted_top_results) < num_tfs):
        if len(sorted_results[index]['Library'].split(';')) >= threshold:
            sorted_top_results.append(sorted_results[index])
        index += 1
        # moves on to the next index
        
    sorted_top_results = sorted_top_results[::-1]

    # set up a list with all the TFs, sorted by rank (lowest to highest, in line with top_results)
    sorted_tfs = []
    for i in range(0, len(sorted_top_results)):
        sorted_tfs.append(sorted_top_results[i].get('TF'))
        # this pulls only the TF name from top_results and adds it to sorted_tfs

    for i, tfentry in enumerate(sorted_top_results):
        libscores = tfentry['Library'].split(';')
        for a in libscores:
            lib, value = a.split(',')
            rank = indexfinder(ranking_dict[lib], int(value))
            avg = tfentry['AvgRank']
            tot = tfentry['SumRank']
            bar_length = (rank*avg)/tot
            c_lib_means[lib][i] = float(bar_length)

    fig = go.Figure(data = [go.Bar(name = c_lib, 
                                x = c_lib_means[c_lib], 
                                y = sorted_tfs,
                                marker = go.bar.Marker(color = c_lib_palette[c_lib]), 
                                orientation = 'h') 
                            for c_lib in libs_sorted])

    fig.update_layout(barmode = 'stack')
    fig.update_layout(
        title = {
            #'text': 'Stacked Bar Chart of Average Ranks in Different Libraries',
            'text': '',
            'y': 0.87,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
        },
        xaxis_title = 'Average of Ranks Across All Libraries',
        yaxis_title = 'Transcription Factors',
        font = dict(
            size = 13,
            color = 'black',
            family = 'Arial'
        ),
        width=700,
        margin=dict(
            t=30
        )
    )

    for fmt in save_formats: 
        file_name = save_name+'.'+fmt
        fig.write_image(os.path.join(save_path, file_name), scale=2)

    if save_html:
        fig.write_html(os.path.join(save_path, f"{save_name}.html"))
    else:
        fig.show()