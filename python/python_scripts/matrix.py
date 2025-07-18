import xalign
import archs4py as a4
import pandas as pd
from python_scripts.utils import get_metadata
from maayanlab_bioinformatics.normalization.log import log2_normalize
from maayanlab_bioinformatics.normalization.zscore import zscore_normalize 
from maayanlab_bioinformatics.normalization.quantile_legacy import quantile_normalize
from maayanlab_bioinformatics.dge.limma_voom import limma_voom_differential_expression


def load_and_align_data(path, gse, species, aligner="kallisto"):
    '''
    Loads SRA data into the specified path and then aligns with with the specified aligner.

    Args:
        path (str): Path to the directory where SRA files will be downloaded.
        gse (str): GSE accession number.
        species (str): Species name for alignment.
        aligner (str): Aligner to use, e.g., "kallisto" or "star".

    Returns:
        tuple: Gene and transcript count matrices as pandas DataFrames.
    '''
    srr_ids = get_metadata(gse)['run_accession'].tolist()
    xalign.sra.load_sras(srr_ids, path) #download FastQ files 
    gene_count, transcript_count = xalign.align_folder(species, path, aligner, t=8, overwrite=False)
    return gene_count, transcript_count

def filter_low_exp(gene_counts):
    '''
    Filters gene with low expression based on read and sample thresholds.

    Args:
        gene_counts (DataFrame): DataFrame containing gene expression counts to be filtered.

    Returns:
        DataFrame: Filtered gene expression count matrix.
    '''

    filtered_exp = a4.utils.filter_genes(gene_counts, readThreshold=50, sampleThreshold=0.02, deterministic=True, aggregate=True)
    return filtered_exp

#tbd: add z-score normalization features.
def normalize(gene_counts):
    '''
    Normalizes gene expression matrix using log, quantile and z-score normalization.

    Args: 
        gene_counts (DataFrame): Gene expression matrix to be normalized.

    Returns:
        DataFrame: Normalized gene expression matrix.
    '''

    norm_exp = quantile_normalize(gene_counts)
    norm_exp = log2_normalize(norm_exp)
    norm_exp = zscore_normalize(norm_exp)
    return norm_exp



#depreciated
def deg_limma(anndict):
    '''
    Computes differentially expressed genes using Limma Voom.

    Args:
        anndict (dict): a dictionary composed of a gene expression and an annotations matrix
    
    Returns:
        DataFrame: Differential Gene Expression calculation results
    '''
    
    gene_counts = anndict['count']
    annotations = anndict['annotations']
    dge_table = limma_voom_differential_expression(
        gene_counts.loc[:, annotations['group']=='control'],
        gene_counts.loc[:, annotations['group']=='perturbation'],
        gene_counts
    )
    return dge_table