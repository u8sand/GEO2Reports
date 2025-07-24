import json
import time
import requests
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
# from matplotlib_venn import venn2
from matplotlib.ticker import MaxNLocator
import seaborn as sns
# from scipy.stats import fisher_exact
from IPython.display import HTML, display, Markdown, FileLink, Image
import os
pd.set_option('display.float_format', '{:.2e}'.format)

class druganalysis:
    def __init__(self, geneset, geneset_dn, save_path, save_name="", direction="down-regulators", tab_num=1, fig_num=1):
        self.direction=direction
        self.save_path=save_path
        self.save_name = save_name
        self.fig_num=fig_num
        self.tab_num=tab_num
        if self.direction == 'up-regulators' or self.direction == 'mimickers':
            self.direction_str = 'up'
        else:
            self.direction_str = 'down'

        self.geneset = self.get_l2s2_valid_genes(geneset)
        self.geneset_dn = self.get_l2s2_valid_genes(geneset_dn)

        if len(geneset) == 0 or len(geneset_dn) == 0:
            raise ValueError("Insufficient genes in the input gene sets that overlap with the L2S2 database.")
        
        self.l2s2_geneset_up_id, self.l2s2_geneset_dn_id = self.add_user_geneset(self.geneset, geneset_dn=self.geneset_dn)
        self.drugseqr_geneset_up_id, self.drugseqr_geneset_dn_id = self.add_user_geneset(self.geneset, geneset_dn=self.geneset_dn, url="http://drugseqr.maayanlab.cloud/graphql")
        
        self.l2s2_df = self.enrich_up_down(self.geneset, self.geneset_dn, first=500).dropna()
        self.drugseqr_df = self.enrich_up_down(self.geneset, self.geneset_dn, url="http://drugseqr.maayanlab.cloud/graphql", first=500).dropna()

        self.l2s2_df_nofda = self.enrich_up_down(self.geneset, self.geneset_dn, first=500, fda_approved=False).dropna()
        self.drugseqr_df_nofda = self.enrich_up_down(self.geneset, self.geneset_dn, url="http://drugseqr.maayanlab.cloud/graphql", first=500, fda_approved=False).dropna()
        
        # if self.l2s2_df.empty and self.drugseqr_df.empty:
        #     raise ValueError("No results found for the provided gene set(s).")

        # self.l2s2_df['perturbation'] =self.l2s2_df['term'].apply(lambda x: x.split('_')[4].lower() if len(x.split('_')) > 4 else None)
        # self.drugseqr_df['perturbation'] = self.drugseqr_df['term'].apply(lambda x: x.split('_')[0].lower() if len(x.split('_')) > 0 else None)
        # self.l2s2_df_nofda['perturbation'] = self.l2s2_df_nofda['term'].apply(lambda x: x.split('_')[4] if len(x.split('_')) > 4 else None)
        # self.drugseqr_df_nofda['perturbation'] = self.drugseqr_df_nofda['term'].apply(lambda x: x.split('_')[0].lower() if len(x.split('_')) > 0 else None)

        if not self.l2s2_df.empty:
            self.l2s2_df['perturbation'] =self.l2s2_df['term'].apply(lambda x: x.split('_')[4].lower() if len(x.split('_')) > 4 else None)
        # else:
        #     print("no FDA-approved L2S2 drugs.")

        if not self.l2s2_df_nofda.empty:
            self.l2s2_df_nofda['perturbation'] = self.l2s2_df_nofda['term'].apply(lambda x: x.split('_')[4] if len(x.split('_')) > 4 else None)
        # else:
        #     print("no L2S2 drugs.")

        if not self.drugseqr_df.empty:
            self.drugseqr_df['perturbation'] = self.drugseqr_df['term'].apply(lambda x: x.split('_')[0].lower() if len(x.split('_')) > 0 else None)
        # else:
        #     print("no FDA-approved DRUG-seqr drugs.")

        if not self.drugseqr_df_nofda.empty:
            self.drugseqr_df_nofda['perturbation'] = self.drugseqr_df_nofda['term'].apply(lambda x: x.split('_')[0].lower() if len(x.split('_')) > 0 else None)
        # else:
        #     print("no DRUG-seqr drugs.")
        


    def enrich_single_set(self, geneset: list, first=500, url="http://l2s2.maayanlab.cloud/graphql", fda_approved=True):
        query = {
        "operationName": "EnrichmentQuery",
        "variables": {
            "filterTerm": f" {self.direction_str}",
            "offset": 0,
            "first": first,
            "filterFda": fda_approved,
            "sortBy": "pvalue",
            "genes": geneset,
        },
        "query": """query EnrichmentQuery(
                        $genes: [String]!
                        $filterTerm: String = ""
                        $offset: Int = 0
                        $first: Int = 10
                        $filterFda: Boolean = false
                        $sortBy: String = ""
                        ) {
                        currentBackground {
                            enrich(
                            genes: $genes
                            filterTerm: $filterTerm
                            offset: $offset
                            first: $first
                            filterFda: $filterFda
                            sortby: $sortBy
                            ) {
                            nodes {
                                geneSetHash
                                pvalue
                                adjPvalue
                                oddsRatio
                                nOverlap
                                geneSets {
                                nodes {
                                    term
                                    id
                                    nGeneIds
                                    geneSetFdaCountsById {
                                    nodes {
                                        approved
                                        count
                                    }
                                    }
                                }
                                totalCount
                                }
                            }
                            totalCount
                            }
                        }
                        }
                        """,
        }

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        response = requests.post(url, data=json.dumps(query), headers=headers)
        response.raise_for_status()
        res = response.json()

        enrichment = res['data']['currentBackground']['enrich']['nodes']# %%

        df_enrichment = pd.json_normalize(
            enrichment, 
            record_path=['geneSets', 'nodes'], 
            meta=['geneSetHash', 'pvalue', 'adjPvalue', 'oddsRatio', 'nOverlap']
        )

        if df_enrichment.empty:
            return pd.DataFrame()
        
        df_enrichment["approved"] = df_enrichment["geneSetFdaCountsById.nodes"].map(lambda x: x[0]['approved'] if len(x) > 0 else False)
        df_enrichment["count"] = df_enrichment["geneSetFdaCountsById.nodes"].map(lambda x: x[0]['count'] if len(x) > 0 else 0)
        df_enrichment.drop(columns=['geneSetFdaCountsById.nodes'], inplace=True)

        return df_enrichment

    def enrich_up_down(self, genes_up: list[str], genes_down: list[str], first=500, url="http://l2s2.maayanlab.cloud/graphql", fda_approved=True):
        query = {
            "operationName": "PairEnrichmentQuery",
            "variables": {
            "filterTerm": f" {self.direction_str}",
            "offset": 0,
            "first": first,
            "filterFda": fda_approved,
            "sortBy": "pvalue_mimic" if self.direction_str == "up" else "pvalue_reverse",
            "pvalueLe": 0.05,
            "genesUp": genes_up,
            "genesDown": genes_down
            },
            "query": """query PairEnrichmentQuery($genesUp: [String]!, $genesDown: [String]!, $filterTerm: String = "", $offset: Int = 0, $first: Int = 10, $filterFda: Boolean = false, $sortBy: String = "", $pvalueLe: Float = 0.05) {{
                            currentBackground {{
                                {}(
                                filterTerm: $filterTerm
                                offset: $offset
                                first: $first
                                filterFda: $filterFda
                                sortby: $sortBy
                                pvalueLe: $pvalueLe
                                genesDown: $genesDown
                                genesUp: $genesUp
                                ) {{
                                totalCount
                                nodes {{
                                    adjPvalueMimic
                                    adjPvalueReverse
                                    mimickerOverlap
                                    oddsRatioMimic
                                    oddsRatioReverse
                                    pvalueMimic
                                    pvalueReverse
                                    reverserOverlap
                                    geneSet {{
                                    nodes {{
                                        id
                                        nGeneIds
                                        term
                                        geneSetFdaCountsById {{
                                        nodes {{
                                            count
                                            approved
                                        }}
                                        }}
                                    }}
                                    }}
                                }}
                                }}
                            }}
                            }}""".format("pairedEnrich" if 'l2s2' in url else "pairEnrich")
        }

        headers = {
                "Accept": "application/json",
                "Content-Type": "application/json"
        }

        response = requests.post(url, data=json.dumps(query), headers=headers)

        response.raise_for_status()
        res = response.json()
        if 'pairEnrich' in res['data']['currentBackground']:
            enrichment = res['data']['currentBackground']['pairEnrich']['nodes']
        else: 
            enrichment = res['data']['currentBackground']['pairedEnrich']['nodes']
        
        df_enrichment_pair = pd.DataFrame(enrichment)

        if df_enrichment_pair.empty:
            return pd.DataFrame()
        
        df_enrichment_pair["geneSetIdUp"] = df_enrichment_pair["geneSet"].map(
            lambda t: next((node['id'] for node in t['nodes'] if ' up' in node['term']), None)
        )

        df_enrichment_pair["geneSetIdDown"] = df_enrichment_pair["geneSet"].map(
            lambda t: next((node['id'] for node in t['nodes'] if ' down' in node['term']), None)
        )
        
        df_enrichment_pair["term"] = df_enrichment_pair["geneSet"].map(
            lambda t: t['nodes'][0]['term']
        )
        
        def try_or_else_factory(fn, other):
            def try_or_else(*args, **kwargs):
                try: return fn(*args, **kwargs)
                except: return other
            return try_or_else
        
        df_enrichment_pair["approved"] = df_enrichment_pair["geneSet"].map(
            try_or_else_factory(lambda t: t['nodes'][0]['geneSetFdaCountsById']['nodes'][0]['approved'], False)
        )
        
        df_enrichment_pair["count"] = df_enrichment_pair["geneSet"].map(
            try_or_else_factory(lambda t: t['nodes'][0]['geneSetFdaCountsById']['nodes'][0]['count'], 0)
        )
        
        df_enrichment_pair = df_enrichment_pair.drop(columns=['geneSet']).reset_index(drop=True)
        
        return df_enrichment_pair

    def get_overlap(self, genes, id, url="http://l2s2.maayanlab.cloud/graphql"):
        query = {
        "operationName": "OverlapQuery",
        "variables": {
            "id": id,
            "genes": genes
        },
        "query": """query OverlapQuery($id: UUID!, $genes: [String]!) {geneSet(id: $id) {
        overlap(genes: $genes) {
        nodes {
            symbol
            ncbiGeneId
            description
            summary
        }   }}}"""
        }
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        response = requests.post(url, data=json.dumps(query), headers=headers)
        
        response.raise_for_status()
        res = response.json()
        return [item['symbol'] for item in res['data']['geneSet']['overlap']['nodes']]

    def get_up_dn_overlap(self, genes_up: list[str], genes_down: list[str], id_up: str, id_down: str, overlap_type: str,  url="http://l2s2.maayanlab.cloud/graphql"):
        if overlap_type == 'mimickers':
            up_up_overlap = self.get_overlap(genes_up, id_up, url)
            dn_dn_overlap = self.get_overlap(genes_down, id_down, url)
            return list(set(up_up_overlap) | set(dn_dn_overlap))
        elif overlap_type == 'reversers':
            up_dn_overlap = self.get_overlap(genes_up, id_down, url)
            dn_up_overlap = self.get_overlap(genes_down, id_up, url)
            return list(set(up_dn_overlap) | set(dn_up_overlap))
        
    def add_user_geneset(self, geneset, geneset_dn = None, url="http://l2s2.maayanlab.cloud/graphql"):
        query = {
                "query": "mutation AddUserGeneSet($genes: [String] = [\"AKT1\"], $description: String = \"\") {\n  addUserGeneSet(input: {genes: $genes, description: $description}) {\n    userGeneSet {\n      id\n    }\n  }\n}",
                "variables": {
                    "genes": geneset,
                    "description": "User gene set" if geneset_dn is not None else "User gene set (up)"
                },
                "operationName": "AddUserGeneSet"
        }
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        response = requests.post(url, data=json.dumps(query), headers=headers)
        
        response.raise_for_status()
        res = response.json()
        
        if geneset_dn is not None:
            query = {
                "query": "mutation AddUserGeneSet($genes: [String] = [\"AKT1\"], $description: String = \"\") {\n  addUserGeneSet(input: {genes: $genes, description: $description}) {\n    userGeneSet {\n      id\n    }\n  }\n}",
                "variables": {
                    "genes": geneset_dn,
                    "description": "User gene set (down)"
                },
                "operationName": "AddUserGeneSet"
            }
            
            response = requests.post(url, data=json.dumps(query), headers=headers)
            
            response.raise_for_status()
            res_dn = response.json()
            return res['data']['addUserGeneSet']['userGeneSet']['id'], res_dn['data']['addUserGeneSet']['userGeneSet']['id']
        
        return res['data']['addUserGeneSet']['userGeneSet']['id']

    def get_l2s2_valid_genes(self, genes: list[str], url="http://l2s2.maayanlab.cloud/graphql"):
        query = {
        "query": """query GenesQuery($genes: [String]!) {
            geneMap2(genes: $genes) {
                nodes {
                    gene
                    geneInfo {
                        symbol
                        }
                    }
                }
            }""",
        "variables": {"genes": genes},
        "operationName": "GenesQuery"
        }
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        response = requests.post(url, data=json.dumps(query), headers=headers)

        response.raise_for_status()
        res = response.json()
        return [g['geneInfo']['symbol'] for g in res['data']['geneMap2']['nodes'] if g['geneInfo'] != None]

         
    def display_table(self, db):
        if db=="l2s2_fda":
            approval = "FDA-approved"
            library = "LINCS L1000"
            df = self.l2s2_df
            up_id = self.l2s2_geneset_up_id
            down_id = self.l2s2_geneset_dn_id

        elif db=="l2s2_all":
            approval = ""
            library = "LINCS L1000"
            df = self.l2s2_df_nofda
            up_id = self.l2s2_geneset_up_id
            down_id = self.l2s2_geneset_dn_id

        elif db=="drugseqr_fda":
            approval = "FDA-approved"
            library = "DRUG-seq"
            df = self.drugseqr_df
            up_id = self.drugseqr_geneset_up_id
            down_id = self.drugseqr_geneset_dn_id

        elif db=="drugseqr_all":
            approval = ""
            library = "DRUG-seq"
            df = self.drugseqr_df_nofda
            up_id = self.drugseqr_geneset_up_id
            down_id = self.drugseqr_geneset_dn_id

        else:
            raise ValueError("Choose a valid dataset.")

        termdict = {
            "mimickers": "mimic",
            "reversers": "reverse"
        }

        if df.empty:
            raise ValueError(f"No Results for {db}")

        df_t20 = df.iloc[:20]
        
        # print(df_t20.columns)
        # print(df_t20.empty)
        
        columns = ['perturbation', 'term']
        if self.direction == "mimickers":
            columns.extend(['pvalueMimic', 'adjPvalueMimic', 'oddsRatioMimic', 'mimickerOverlap'])
        else:
            columns.extend(['pvalueReverse', 'adjPvalueReverse', 'oddsRatioReverse','reverserOverlap'])

        columns.extend(['approved', 'count'])

        display(df_t20[columns])

        # display(df_t20)
        
        display(Markdown(f"Table {self.tab_num}: Ranked {approval} {library} signatures predicted to {termdict[self.direction]} the uploaded geneset."))
        display(HTML(f"<a href=\"https://l2s2.maayanlab.cloud/enrichpair?dataset={up_id}&dataset={down_id}&fda=true&dir={self.direction_str.strip()}&sort={'pvalue_reverse' if self.direction_str == 'down' else 'pvalue_mimic'}\" target=\"_blank\">View in L2S2</a>"))
        self.tab_num += 1

        filename = os.path.join(self.save_path, f"{self.save_name}_{self.direction}_{db}.tsv")
        df[:200].to_csv(filename, sep='\t')
        display(FileLink(filename, result_html_prefix="Download table: "))

    def display_barplot(self, db, save_formats, color='tomato'): 
        if db == "l2s2_fda":
            df = self.l2s2_df
            approval = "FDA-approved"
        elif db == "l2s2_all":
            df = self.l2s2_df_nofda
            approval = ""
        elif db == "drugseqr_fda":
            df = self.drugseqr_df
            approval = "FDA-approved"
        elif db == "drugseqr_all":
            df = self.drugseqr_df_nofda
            approval = ""
        else:
            raise ValueError("Choose a valid dataset.")
        
        if df.empty:
            raise ValueError(f"No Results for {db}")
        df_t20 = df.iloc[:20]
        bar_color_not_sig = "lightgrey"
        bar_color = color
        edgecolor=None

        if self.direction == 'mimickers':
            pvalcol = 'pvalueMimic'
        else:
            pvalcol = 'pvalueReverse'
        

        
        df_t20['-log10(pvalue)'] = np.log10(df_t20[pvalcol])*-1
        df_t20 = df_t20.groupby(by="perturbation", level=None, sort=False).mean().reset_index()
        df_t20.sort_values(by='-log10(pvalue)', ascending=True)
        bar_colors = [bar_color if (x < 0.05) else bar_color_not_sig for x in df_t20[pvalcol].tolist()]
        
        fig=sns.barplot(
            data=df_t20,
            x="-log10(pvalue)", 
            y="perturbation",
            palette=bar_colors,
            legend=False,
            edgecolor=edgecolor,
            linewidth=1,
            orient='y',
            errorbar=None,
            #ax=ax
        )

        fig.xaxis.set_major_locator(MaxNLocator(integer=True))
        fig.tick_params(axis='x', which='major', labelsize=10)

        fig.axes.get_yaxis().set_visible(False)
        for i in range(len(df_t20)):
            if df_t20[pvalcol].iloc[i] < 0.05:
                annot = f" *{df_t20['perturbation'].iloc[i]} {np.format_float_scientific(df_t20[pvalcol].iloc[i],precision=2)}"
            else:
                annot = f" {df_t20['perturbation'].iloc[i]} {np.format_float_scientific(df_t20[pvalcol].iloc[i],precision=2)}"
            
            title_start= max(fig.axes.get_xlim())/200
            fig.text(title_start,i,annot,ha='left', va='center', wrap = True, fontsize = 8)

        for fmt in save_formats:
            file_path = os.path.join(self.save_path, f"{self.save_name}_{self.direction}_{db}.{fmt}")
            plt.savefig(file_path, bbox_inches="tight", dpi=300)
        
        #plt.show()

        display(Image(os.path.join(self.save_path, f"{self.save_name}_{self.direction}_{db}.png"), width=600))
        display(Markdown(f"Figure {self.fig_num}: barplot representation depicting the -log10p values of the top {approval} {db} {self.direction}. Red bars represent statistically significant results; otherwise gray."))
        self.fig_num += 1

        for fmt in save_formats:
            file_path = os.path.join(self.save_path, f"{self.save_name}_{self.direction}_{db}.{fmt}")
            display(FileLink(file_path, result_html_prefix=f"Download bar plot as {fmt}"))
        
        plt.close()