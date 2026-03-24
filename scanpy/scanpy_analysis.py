import scanpy as sc
import matplotlib.pyplot as plt
import os

# ==============================
# Setup
# ==============================

os.makedirs("./results/figures", exist_ok=True)
os.makedirs("./results", exist_ok=True)

sc.settings.figdir = "./results/figures"
sc.settings.set_figure_params(dpi=100, facecolor='white')

# ==============================
# Load Dataset
# ==============================

adata = sc.datasets.pbmc3k()

# ==============================
# Quality Control
# ==============================

adata.var_names_make_unique()
adata.var['mt'] = adata.var_names.str.startswith('MT-')

sc.pp.calculate_qc_metrics(adata, qc_vars=['mt'], inplace=True)

sc.pl.violin(
    adata,
    ['n_genes_by_counts', 'total_counts', 'pct_counts_mt'],
    multi_panel=True,
    save="_qc.png"
)

# ==============================
# Filtering
# ==============================

adata = adata[adata.obs.n_genes_by_counts < 2500, :]
adata = adata[adata.obs.pct_counts_mt < 5, :]

# ==============================
# Normalization
# ==============================

sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)

# ==============================
# PCA
# ==============================

sc.pp.scale(adata, max_value=10)
sc.tl.pca(adata)

sc.pl.pca(adata, save="_pca.png")

# ==============================
# Neighbors + Clustering
# ==============================

sc.pp.neighbors(adata, n_neighbors=10, n_pcs=40)

# VERY IMPORTANT: create clusters BEFORE plotting
sc.tl.leiden(adata)

# Save cluster counts
adata.obs['leiden'].value_counts().to_csv("results/cluster_counts.csv")

# ==============================
# UMAP
# ==============================

sc.tl.umap(adata)

# UMAP clusters
sc.pl.umap(adata, color=['leiden'], save="_umap_clusters.png")

# UMAP marker genes
sc.pl.umap(
    adata,
    color=['CD3D', 'MS4A1', 'NKG7', 'LYZ'],
    save="_umap_markers.png"
)

# ==============================
# Marker Genes
# ==============================

sc.tl.rank_genes_groups(adata, 'leiden', method='t-test')

sc.pl.rank_genes_groups(adata, save="_markers.png")

# ==============================
# Save Data
# ==============================

adata.write("results/pbmc_processed.h5ad")

print("✅ Analysis complete. Results saved in 'results/' folder.")
