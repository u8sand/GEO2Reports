import pandas as pd 
import numpy as np
import json
import requests
import matplotlib.pyplot as plt
import seaborn as sns
import time
from matplotlib.ticker import MaxNLocator
from IPython.display import display,FileLink, Markdown

annot_dict = {}

# Function to get Enrichr Results 
# Takes a gene list and Enrichr libraries as input 
def Enrichr_API(enrichr_gene_list, all_libraries):


    all_terms = []
    all_pvalues =[] 
    all_adjusted_pvalues = []
    library_success = []
    short_id = ''

    for library_name in all_libraries : 
        ENRICHR_URL = 'http://amp.pharm.mssm.edu/Enrichr/addList'
        genes_str = '\n'.join(enrichr_gene_list)
        description = 'Example gene list'
        payload = {
            'list': (None, genes_str),
            'description': (None, description)
        }

        response = requests.post(ENRICHR_URL, files=payload)
        if not response.ok:
            raise Exception('Error analyzing gene list')

        data = json.loads(response.text)
        time.sleep(0.5)
        ENRICHR_URL = 'http://amp.pharm.mssm.edu/Enrichr/enrich'
        query_string = '?userListId=%s&backgroundType=%s'
        user_list_id = data['userListId']
        short_id = data["shortId"]
        gene_set_library = library_name
        response = requests.get(
            ENRICHR_URL + query_string % (user_list_id, gene_set_library)
         )
        if not response.ok:
            raise Exception('Error fetching enrichment results')
        try:
            data = json.loads(response.text)
            results_df  = pd.DataFrame(data[library_name][0:5])
            all_terms.append(list(results_df[1]))
            all_pvalues.append(list(results_df[2]))
            all_adjusted_pvalues.append(list(results_df[6]))
            library_success.append(library_name)
        except:
            print('Error for ' + library_name + ' library')

    return([all_terms,all_pvalues,all_adjusted_pvalues,str(short_id),library_success])



def enrichr_figure(all_terms,all_pvalues, all_adjusted_pvalues, plot_names, all_libraries, fig_format, bar_color, show_plot=True): 
    
    # rows and columns depend on number of Enrichr libraries submitted 
    rows = []
    cols = []
    
    # Bar colors
    if bar_color!= 'lightgrey':
        bar_color_not_sig = 'lightgrey'
        edgecolor=None
        linewidth=0
    else:
        bar_color_not_sig = 'white'
        edgecolor='black'
        linewidth=1
    
    # If only 1 Enrichr library selected, make simple plot 
    if len(all_libraries)==1:
        #fig,axes = plt.subplots(1, 1,figsize=[8.5,6])
        rows = [0]
        cols = [0]
        i = 0 
        bar_colors = [bar_color if (x < 0.05) else bar_color_not_sig for x in all_pvalues[i]]
        print(type(bar_colors))
        fig = sns.barplot(x=np.log10(all_pvalues[i])*-1, y=all_terms[i], palette=bar_colors, edgecolor=edgecolor, linewidth=linewidth)
        fig.axes.get_yaxis().set_visible(False)
        fig.set_title(all_libraries[i].replace('_',' '),fontsize=26)
        fig.set_xlabel('-Log10(p-value)',fontsize=25)
        fig.xaxis.set_major_locator(MaxNLocator(integer=True))
        fig.tick_params(axis='x', which='major', labelsize=20)
        if max(np.log10(all_pvalues[i])*-1)<1:
            fig.xaxis.set_ticks(np.arange(0, max(np.log10(all_pvalues[i])*-1), 0.1))
        for ii,annot in enumerate(all_terms[i]):
            if annot in annot_dict.keys():
                annot = annot_dict[annot]
            if all_adjusted_pvalues[i][ii] < 0.05:
                annot = '  *'.join([annot, str(str(np.format_float_scientific(all_pvalues[i][ii],precision=2)))]) 
            else:
                annot = '  '.join([annot, str(str(np.format_float_scientific(all_pvalues[i][ii],precision=2)))])

            title_start= max(fig.axes.get_xlim())/200
            fig.text(title_start,ii,annot,ha='left',wrap = True, fontsize = 26) #adjust font size
            fig.patch.set_edgecolor('black')  
            fig.patch.set_linewidth('2')
        
    
    # If there are an even number of Enrichr libraries below 6
    # Plots 1x2 or 2x2
    else:
        if len(all_libraries) % 2 == 0 and len(all_libraries) < 5:
                for i in range(0,int(len(all_libraries)/2)):    
                    rows = rows + [i]*2
                    cols = list(range(0,2))*int(len(all_libraries)/2)    
                fig, axes = plt.subplots(len(np.unique(rows)), len(np.unique(cols)),figsize=[7,int(2* len(np.unique(rows)))]) 
    
        
        # All other # of libraries 6 and above will have 3 columns and a flexible number of rows to accomodate all plots
        else:
            for i in range(0,int(np.ceil(len(all_libraries)/2))):
                rows = rows + [i]*2
                cols = list(range(0,2))*int(np.ceil(len(all_libraries)/2))
            fig, axes = plt.subplots(len(np.unique(rows)), len(np.unique(cols)),figsize=[8,int(2* len(np.unique(rows)))])
           
        # If final figure only has one row...
        if len(np.unique(rows))==1:
            for i,library_name in enumerate(all_libraries):
                bar_colors = [bar_color if (x < 0.05) else bar_color_not_sig for x in all_pvalues[i]]
                sns.barplot(x=np.log10(all_pvalues[i])*-1, y=all_terms[i],ax=axes[i], palette=bar_colors, edgecolor=edgecolor, linewidth=linewidth)
                axes[i].axes.get_yaxis().set_visible(False)
                axes[i].set_title(library_name.replace('_',' '),fontsize=36)
                axes[i].set_xlabel('-Log10(p-value)',fontsize=35)
                axes[i].xaxis.set_major_locator(MaxNLocator(integer=True))
                axes[i].tick_params(axis='x', which='major', labelsize=30)
                if max(np.log10(all_pvalues[i])*-1)<1:
                    axes[i].xaxis.set_ticks(np.arange(0, max(np.log10(all_pvalues[i])*-1), 0.1))
                for ii,annot in enumerate(all_terms[i]):
                    if annot in annot_dict.keys():
                        annot = annot_dict[annot]
                    if all_adjusted_pvalues[i][ii] < 0.05:
                        annot = '  *'.join([annot, str(str(np.format_float_scientific(all_pvalues[i][ii],precision=2)))]) 
                    else:
                        annot = '  '.join([annot, str(str(np.format_float_scientific(all_pvalues[i][ii],precision=2)))])

                    title_start= max(axes[i].axes.get_xlim())/200
                    axes[i].text(title_start,ii,annot,ha='left',wrap = True, fontsize = 36)
                    axes[i].patch.set_edgecolor('black')  
                    axes[i].patch.set_linewidth('2')

            plt.subplots_adjust(top=4.5, right = 4.7,wspace = 0.03,hspace = 0.2)


        # If the final figure has more than one row...
        else:


            for i,library_name in enumerate(all_libraries):
                bar_colors = [bar_color if (x < 0.05) else bar_color_not_sig for x in all_pvalues[i]]
                sns.barplot(x=np.log10(all_pvalues[i])*-1, y=all_terms[i],ax=axes[rows[i],cols[i]], palette=bar_colors, edgecolor=edgecolor, linewidth=linewidth)
                axes[rows[i],cols[i]].axes.get_yaxis().set_visible(False)
                axes[rows[i],cols[i]].set_title(library_name.replace('_',' '),fontsize=36)
                axes[rows[i],cols[i]].set_xlabel('-Log10(p-value)',fontsize=35)
                axes[rows[i],cols[i]].xaxis.set_major_locator(MaxNLocator(integer=True))
                axes[rows[i],cols[i]].tick_params(axis='x', which='major', labelsize=30)
                if max(np.log10(all_pvalues[i])*-1)<1:
                    axes[rows[i],cols[i]].xaxis.set_ticks(np.arange(0, max(np.log10(all_pvalues[i])*-1), 0.1))
                for ii,annot in enumerate(all_terms[i]):
                    if annot in annot_dict.keys():
                        annot = annot_dict[annot]
                    if all_adjusted_pvalues[i][ii] < 0.05:
                        annot = '  *'.join([annot, str(str(np.format_float_scientific(all_pvalues[i][ii],precision=2)))]) 
                    else:
                        annot = '  '.join([annot, str(str(np.format_float_scientific(all_pvalues[i][ii],precision=2)))])

                    title_start= max(axes[rows[i],cols[i]].axes.get_xlim())/200
                    axes[rows[i],cols[i]].text(title_start,ii,annot,ha='left',wrap = True, fontsize = 30) #control bar text font size here
                    axes[rows[i],cols[i]].patch.set_edgecolor('black')  
                    axes[rows[i],cols[i]].patch.set_linewidth('2')

            plt.subplots_adjust(top=4.8, right = 4.7,wspace = 0.03,hspace = 0.2)

        # If >6 libraries are chosen and is not a multiple of 2, delete empty plots
        if len(np.unique(rows))*len(np.unique(cols)) != len(all_libraries):
            diff = (len(np.unique(rows))*len(np.unique(cols))) - len(all_libraries)
            for i in range (1,int(diff+1)):
                fig.delaxes(axes[rows[-i]][cols[-i]])
    
    # Save results 
    for plot_name in plot_names: 
        plt.savefig(plot_name,bbox_inches = 'tight')

    # Show plot 
    if show_plot:
        plt.show()
    else:
        plt.close()

 
