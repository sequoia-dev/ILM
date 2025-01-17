#! /usr/bin/env python3
"""Dimension reduction for faster analysis MSM"""

import pyemma
import tools
from load_feat import *
import numpy as np
import matplotlib.pyplot as plt


def pca_reduction(data, dim):
    """Do a PCA dimension reduction and plot it

    Parameters
    ----------
    data : pyemma.load
        Data loaded from pyemma loader

    Returns
    -------
    pca : pyemma.pca
        Data reduced using PCA
    """
    # Dimension reduction
    pca = pyemma.coordinates.pca(data, dim=dim)

    return pca


def plot_pca(pca, T, dim, save=False, outdir="", display=False,ij=(0,1)):
    """Plot the PCA dimension reduction

    Parameters
    ----------
    pca : pyemma.pca
        Data reduced using PCA
    T : float
        Temperature of the system
    dim : int
        Number of dimension to project the reduction
    save : bool, optional
        Save or not the plot, by default False
    display : bool, optional
        Display or not the plot, by default False
    outdir : str, optional
        Output directory to save the plot, by default ''
    ij : tuple, optional
        Index to project the representation, by default (0,1)

    Raises
    ------
    Exception
        Provide a directory to save the file
    """
    # Concatenate
    pca_concatenated = np.concatenate(pca.get_output())

    # Histogramm plot of the new dimension
    fig, ax = pyemma.plots.plot_feature_histograms(
        pca_concatenated, ignore_dim_warning=True
    )

    if save:
        if outdir == "":
            raise Exception("Please provide a directory to save the file")
        else:
            plt.savefig(f"{outdir}/pca_histogram.pdf", dpi=300, bbox_inches="tight")
    if display:
        plt.show()

    # Free energy plot of the new dimension
    if dim >= 2:
        fig, axes = plt.subplots(1, 1, figsize=(5, 4))
        i,j = ij
        kT = tools.get_kT(T)
        pyemma.plots.plot_free_energy(
            *pca_concatenated.T[[i,j]],
            ax=axes,
            kT=kT,
            cbar_label="free energy / kJ.mol-1",
        )
        axes.set_xlabel(f"PC {i+1}")
        axes.set_ylabel(f"PC {j+1}")
        if save:
            if outdir == "":
                raise Exception("Please provide a directory to save the file")
            else:
                plt.savefig(
                    f"{outdir}/pca_free_energy_direct_from_density.pdf",
                    dpi=300,
                    bbox_inches="tight",
                )
        if display:
            plt.show()


def tica_reduction(data, lag, dim):
    """Do a TICA dimension reduction

    Parameters
    ----------
    data : pyemma.load
        Data loaded from pyemma loader
    lag : int
        Lag time
    dim : int
        Number of dimension to project the reduction

    Returns
    -------
    tica : pyemma.tica
        Data reduced using TICA
    """

    # TICA reduction
    tica = pyemma.coordinates.tica(data, dim=dim, lag=lag)

    return tica


def plot_tica(tica, T, dim, display=False, save=False, outdir="",ij=(0,1)):
    """Plot a TICA dimension reduction

    Parameters
    ----------
    tica : pyemma.tica
        Data reduced using TICA
    T : float
        Temperature of the system
    dim : int
        Number of dimension to project the reduction
    save : bool, optional
        Save or not the plot, by default False
    display : bool, optional
        Display or not the plot, by default False
    outdir : str, optional
        Output directory to save the plot, by default ''
    ij : tuple, optional
        Index to project the representation, by default (0,1)

    Raises
    ------
    Exception
        Provide a directory to save the file
    """
    tica_concatenated = np.concatenate(tica.get_output())

    # Histogramm plot
    fig, axes = plt.subplots(1, 1, figsize=(5, 4))
    pyemma.plots.plot_feature_histograms(
        tica_concatenated,
        ["TICA {}".format(i + 1) for i in range(tica.dimension())],
        ax=axes,
        ignore_dim_warning=True,
    )
    if save:
        if outdir == "":
            raise Exception("Please provide a directory to save the file")
        else:
            plt.savefig(f"{outdir}/tica_histogram.pdf", dpi=300, bbox_inches="tight")
    if display:
        plt.show()

    # Free energy plot
    if dim >= 2:
        fig, axes = plt.subplots(1, 1, figsize=(5, 4))
        i,j = ij
        kT = tools.get_kT(T)
        pyemma.plots.plot_free_energy(
            *tica_concatenated.T[[i,j]],
            ax=axes,
            kT=kT,
            cbar_label="free energy / kJ.mol-1",
        )
        axes.set_xlabel(f"TIC {i+1}")
        axes.set_ylabel(f"TIC {j+1}")
        if save:
            if outdir == "":
                raise Exception("Please provide a directory to save the file")
            else:
                plt.savefig(
                    f"{outdir}/tica_free_energy_direct_from_density.pdf",
                    dpi=300,
                    bbox_inches="tight",
                )
        if display:
            plt.show()


def clustering(reduction, method, k, stride):
    """Clustering of the data

    Parameters
    ----------
    reduction : pyemma.data
        Data from pyemma loader or from PCA, TICA reduction
    method : str
        Method to use, 'kmeans' and 'regspace' are implemented
    k : int
        Number of cluster
    stride : int
        Stride

    Returns
    -------
    cluster : pyemma.cluster
        Data clustered
    """
    if method == "kmeans":
        cluster = pyemma.coordinates.cluster_kmeans(
            reduction, k=k, stride=stride, max_iter=200
        )
    if method == "regspace":
        cluster = pyemma.coordinates.cluster_regspace(reduction, k=k, stride=stride)

    return cluster


def clustering_plot(reduction, cluster, save=False, outdir="", display=False,ij=(0,1)):
    """Plot of the clustering

    Parameters
    ----------
    reduction : pyemma.data
        Data from pyemma loader or from PCA, TICA reduction
    cluster : pyemma.cluster
        Data clustered
    save : bool, optional
        Save or not the plot, by default False
    display : bool, optional
        Display or not the plot, by default False
    outdir : str, optional
        Output directory to save the plot, by default ''
    ij : tuple, optional
        Index to project the representation, by default (0,1)
    
    Raises
    ------
    Exception
        Provide a directory to save the file
    """

    # If no reduction has been performed
    if type(reduction) == list:
        reduction_concatenated = np.concatenate(reduction)
        dimension = len(reduction)
    # Dimension reduction
    else:
        reduction_concatenated = np.concatenate(reduction.get_output())
        dimension = reduction.dimension()

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    # Histogram plot
    pyemma.plots.plot_feature_histograms(
        reduction_concatenated,
        ["IC {}".format(i + 1) for i in range(dimension)],
        ax=axes[0],
    )
    # Density plot
    i,j = ij
    pyemma.plots.plot_density(
        *reduction_concatenated.T[[i,j]], ax=axes[1], cbar=False, alpha=0.1, logscale=True
    )
    axes[1].scatter(*cluster.clustercenters.T[[i,j]], s=15, c="C1")
    axes[1].set_xlabel(f"IC {i+1}")
    axes[1].set_ylabel(f"IC {j+1}")

    if save:
        if outdir == "":
            raise Exception("Please provide a directory to save the file")
        else:
            plt.savefig(f"{outdir}/cluster.pdf", dpi=300, bbox_inches="tight")
    if display:
        plt.show()


def vamp_reduction(data, dim, lag):
    """Do a VAMP dimension reduction

    Parameters
    ----------
    data : pyemma.load
        Data loaded from pyemma loader
    lag : int
        Lag time
    dim : int
        Number of dimension to project the reduction

    Returns
    -------
    vamp : pyemma.vamp
        Data reduced using vamp
    """

    vamp = pyemma.coordinates.vamp(data=data, dim=dim, lag=lag)

    return vamp


def plot_vamp(vamp, T, dim, save=False, display=False, outdir="",ij=(0,1)):
    """Plot a VAMP dimension reduction

    Parameters
    ----------
    vamp : pyemma.vamp
        Data reduced using VAMP
    T : float
        Temperature of the system
    dim : int
        Number of dimension to project the reduction
    save : bool, optional
        Save or not the plot, by default False
    display : bool, optional
        Display or not the plot, by default False
    outdir : str, optional
        Output directory to save the plot, by default ''
    ij : tuple, optional
        Index to project the representation, by default (0,1)

    Raises
    ------
    Exception
        Provide a directory to save the file
    """

    vamp_concatenated = np.concatenate(vamp.get_output())

    # Histogramm plot
    fig, axes = plt.subplots(1, 1, figsize=(5, 4))
    pyemma.plots.plot_feature_histograms(
        vamp_concatenated,
        ["VAMP {}".format(i + 1) for i in range(vamp.dimension())],
        ax=axes,
        ignore_dim_warning=True,
    )
    if save:
        if outdir == "":
            raise Exception("Please provide a directory to save the file")
        else:
            plt.savefig(f"{outdir}/vamp_histogram.pdf", dpi=300, bbox_inches="tight")
    if display:
        plt.show()

    # Free energy plot
    if dim >= 2:
        fig, axes = plt.subplots(1, 1, figsize=(5, 4))
        i,j = ij
        kT = tools.get_kT(T)
        pyemma.plots.plot_free_energy(
            *vamp_concatenated.T[[i,j]],
            ax=axes,
            kT=kT,
            cbar_label="free energy / kJ.mol-1",
        )
        axes.set_xlabel(f"VAMP {i+1}")
        axes.set_ylabel(f"VAMP {j+1}")
        if save:
            if outdir == "":
                raise Exception("Please provide a directory to save the file")
            else:
                plt.savefig(
                    f"{outdir}/vamp_free_energy_direct_from_density.pdf",
                    dpi=300,
                    bbox_inches="tight",
                )
        if display:
            plt.show()


def plot_lag_dim_vamp(lags,data,dim,save=False,outdir='',display=False):
    """Plot the VAMP2 score as a function of the number of dimension and the lag time

    Parameters
    ----------
    lags : list
        List containing the different lag times to test
    data : pyemma.load
        Data loaded from pyemma loader
    dim : int
        Maximum number of dimension to test
    save : bool, optional
        Save or not the plot, by default False
    display : bool, optional
        Display or not the plot, by default False
    outdir : str, optional
        Output directory to save the plot, by default ''

    Raises
    ------
    Exception
        Provide a directory to save the file
    """
    # Get the dimensions
    dims = np.arange(1,dim+1)
    
    fig, ax = plt.subplots()
    
    # Get a line plot for each lag
    for i, lag in enumerate(lags):
        scores_ = np.array(
            [score_cv(data=data,dim=d,lag=lag,number_of_splits=3) for d in dims]
        )
        # Score and associated error
        scores = np.mean(scores_, axis=1)
        errors = np.std(scores_, axis=1, ddof=1)
        color = 'C{}'.format(i)
        # Plot
        ax.fill_between(dims, scores - errors, scores + errors, alpha=0.3, facecolor=color)
        ax.plot(dims, scores, '--o', color=color, label='lag={:.1f} steps'.format(lag))
    
    ax.legend()
    ax.set_xlabel('Number of dimension')
    ax.set_ylabel('VAMP-2 score')
    
    if save:
        if outdir == "":
            raise Exception("Please provide a directory to save the file")
        else:
            plt.savefig(
                f"{outdir}/vamp_lag_dim.pdf",
                dpi=300,
                bbox_inches="tight",
            )
    if display:
        plt.show()

def plot_vamp_cluster(
        n_clustercenters,
        lag,
        data,
        save=False,
        outdir='',
        display=False
    ):
    """Plot the VAMP2 score as a function of the number of cluster

    Parameters
    ----------
    n_clustercenters : list
        List of the number of cluster to test
    lag : int
        Lag time of the MSM
    data : pyemma.load
        Data loaded from pyemma loader
    save : bool, optional
        Save or not the plot, by default False
    display : bool, optional
        Display or not the plot, by default False
    outdir : str, optional
        Output directory to save the plot, by default ''

    Raises
    ------
    Exception
        Provide a directory to save the file
    """
    # At this point the MSM lag time has to be guessed...
    scores = np.zeros((len(n_clustercenters), 5))
    for n, k in enumerate(n_clustercenters):
        # Multiple round of discretization
        for m in range(5):
            # Clusters
            _cl = pyemma.coordinates.cluster_kmeans(
                data, k=k, max_iter=500, stride=1)
            # MSM
            _msm = pyemma.msm.estimate_markov_model(_cl.dtrajs, lag)
            # Score
            scores[n, m] = _msm.score_cv(
                _cl.dtrajs, n=1, score_method='VAMP2', score_k=min(10, k))

    fig, ax = plt.subplots()
    
    lower, upper = pyemma.util.statistics.confidence_interval(scores.T.tolist(), conf=0.9)
    
    ax.fill_between(n_clustercenters, lower, upper, alpha=0.3)
    ax.plot(n_clustercenters, np.mean(scores, axis=1), '-o')
    ax.semilogx()
    ax.set_xlabel('Number of cluster centers')
    ax.set_ylabel('VAMP-2 score')
    
    if save:
        if outdir == "":
            raise Exception("Please provide a directory to save the file")
        else:
            plt.savefig(
                f"{outdir}/vamp_kcluster.pdf",
                dpi=300,
                bbox_inches="tight",
            )
    if display:
        plt.show()


if __name__ == "__main__":
    # Path
    pdb = "/data/cloison/Simulations/HSP90-NT/SIMULATIONS_TRAJECTORIES/AMBER19SB_OPC/GS_cluster1.pdb"
    traj = [
        "/data/cloison/Simulations/HSP90-NT/SIMULATIONS_TRAJECTORIES/AMBER19SB_OPC/GS01_md_all_fitBB_protonly.xtc",
        "/data/cloison/Simulations/HSP90-NT/SIMULATIONS_TRAJECTORIES/AMBER19SB_OPC/GS02_md_all_fitBB_protonly.xtc",
    ]
    outdir = "/home/ccattin/Documents/Code/outputs"
    # Feat
    pairNames = ["64_CA-130_CA", "119_CA-24_CA","123_CA-24_CA","119_CA-27_CA"]
    # Parameters
    save = True
    display = True
    T = 300
    lag = 300
    dim = 3
    ij = (0,2)

    pair_indices = tools.create_pairIndices_from_pairNames(pdb, pairNames)
    feat = create_feat(pdb)
    feat = feat_atom_distances(feat,pair_indices)
    data = load_data(traj, feat, stride=5, ram=True)

    plot_feat_hist(data, feat, display=display, save=save, outdir=outdir)
    plot_density_energy(
        data=data, T=T, pairNames=pairNames, display=display, save=save, outdir=outdir,ij=ij
    )
    pca = pca_reduction(data=data, dim=dim)

    plot_pca(pca=pca, T=T, dim=dim, save=save, outdir=outdir, display=display,ij=ij)

    tica = tica_reduction(data=data, lag=lag, dim=dim)

    plot_tica(tica=tica, T=T, dim=dim, save=save, display=display, outdir=outdir,ij=ij)

    cluster = clustering(reduction=tica, method="kmeans", k=200, stride=1)

    clustering_plot(
        reduction=tica, cluster=cluster, save=save, outdir=outdir, display=display,ij=ij
    )

    vamp = vamp_reduction(data=data, dim=dim, lag=lag)

    plot_vamp(vamp=vamp, T=T, dim=dim, save=save, display=display, outdir=outdir,ij=ij)

    plot_lag_dim_vamp(
        lags=[1,2,5,10,20],
        data=data,
        dim=2
    )

    plot_vamp_cluster(
        n_clustercenters=[10,50,100,200,400,1000],
        lag=300,
        data=tica
    )
