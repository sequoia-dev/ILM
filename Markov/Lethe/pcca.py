#! /usr/bin/env python3
"""Markov State Model PCCA++ and TPT analysis"""

import pyemma
import tools
from load_feat import *
from dimension_reduction import *
from validation import *
from markov_analysis import *

def stationary_prob(msm,nstate):
     """Display the stationary probabilities

     Parameters
     ----------
     msm : pyemma.msm
        MSM or bayesian MSM
     nstate : int
         Number of meta stable state to consider
     """

     msm.pcca(nstate)
     print('Sationary probabilities of the metastable sets')
     for i, s in enumerate(msm.metastable_sets):
          print('π_{} = {:f}'.format(i + 1, msm.pi[s].sum()))

def plot_metastable_membership(
          msm,
          nstate,
          data,
          cluster,
          display=False,
          save=False,
          outdir=''
          ):
     """Plot the metastable membership

     Parameters
     ----------
     msm : pyemma.msm
        MSM or bayesian MSM
     nstate : int
         Number of meta stable state to consider
     cluster : pyemma.cluster
        Cluster to make the analysis
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

     # Data without dimension reduction
     if type(data) == list:
          data_concatenated = np.concatenate(data)
     # Dimension reduction
     else:
          data_concatenated = np.concatenate(data.get_output())
          
     dtrajs_concatenated = np.concatenate(cluster.dtrajs)

     # Metastable distribution plot
     fig, axes = plt.subplots(1, nstate, figsize=(15, 3))
     for i, ax in enumerate(axes.flat):
          pyemma.plots.plot_contour(
               *data_concatenated.T,
               msm.metastable_distributions[i][dtrajs_concatenated],
               ax=ax,
               cmap='afmhot_r', 
               mask=True,
               cbar_label='Metastable distribution {}'.format(i + 1)
               )
          ax.set_xlabel('Feat 1')
     axes[0].set_ylabel('Feat 2')
     
     if save:
        if outdir=='':
            raise Exception('Please provide a directory to save the file')
        else:
            plt.savefig(f'{outdir}/metastable_membership.pdf',dpi=300,bbox_inches='tight')

     if display:
        plt.show()


def concatenate(msm,cluster):
     """Concatenate data for TPT analysis

     Parameters
     ----------
     msm : pyemma.msm
        MSM or bayesian MSM
     cluster : pyemma.cluster
        Cluster to make the analysis

     Returns
     -------
     metastable_traj : pyemma.msm.metastable_assignments
         Trajectories of metastable states
     highest_membership : int
          Indice of the highest membership
     coarse_state_centers : pyemma.cluster.clustercenters
          Coarse state centers
     """
     dtrajs_concatenated = np.concatenate(cluster.dtrajs)

     metastable_traj = msm.metastable_assignments[
         dtrajs_concatenated
         ]
     
     highest_membership = msm.metastable_distributions.argmax(1)
     
     coarse_state_centers = cluster.clustercenters[
         msm.active_set[highest_membership]
         ]
     
     return metastable_traj, highest_membership, coarse_state_centers


def get_mfpt(msm,nstates):
     """Mean First Passage Time and its inverse

     Parameters
     ----------
     msm : pyemma.msm
        MSM or bayesian MSM
     nstate : int
         Number of meta stable state to consider

     Returns
     -------
     mfpt : np.array
         Array containing the Mean First Passage Time
     inverse_mfpt : np.array
          Array containing the inverse of MFPT
     """
     # Init
     mfpt = np.zeros((nstates, nstates))
     # Loop over all the state in a square matrix
     for i in range(nstates):
          for j in range(nstates):
               mfpt[i, j] = msm.mfpt(
                    msm.metastable_sets[i],
                    msm.metastable_sets[j])
     # Compute the inverse
     inverse_mfpt = np.zeros_like(mfpt)
     nz = mfpt.nonzero()
     inverse_mfpt[nz] = 1.0 / mfpt[nz]
     return mfpt, inverse_mfpt

def plot_mftp(
          data,
          nstates,
          mfpt,
          inverse_mfpt,
          metastable_traj,
          coarse_state_centers,
          display=False,
          save=False,
          outdir=''
          ):
     """Plot the flux map with the MFPT

     Parameters
     ----------
     data : pyemma.load
        Data loaded from pyemma loader
     nstate : int
         Number of meta stable state to consider
     mfpt : np.array
         Array containing the Mean First Passage Time
     inverse_mfpt : np.array
          Array containing the inverse of MFPT
     metastable_traj : pyemma.msm.metastable_assignments
         Trajectories of metastable states
     coarse_state_centers : pyemma.cluster.clustercenters
          Coarse state centers
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

     # Data without dimension reduction
     if type(data) == list:
          data_concatenated = np.concatenate(data)
     # Dimension reduction
     else:
          data_concatenated = np.concatenate(data.get_output())

     fig, ax = plt.subplots(figsize=(10, 7))

     # Plot the state map under
     _, _, misc = pyemma.plots.plot_state_map(
          *data_concatenated.T,
          metastable_traj,
          ax=ax,
          zorder=-1)
     # set state numbers 1 ... nstates
     misc['cbar'].set_ticklabels(range(1, nstates + 1))  

     # Plot the network
     pyemma.plots.plot_network(
          inverse_mfpt,
          pos=coarse_state_centers,
          figpadding=0,
          arrow_label_format='%.1f ps',
          arrow_labels=mfpt,
          size=12,
          show_frame=True,
          ax=ax)

     ax.set_xlabel('Feat 1')
     ax.set_ylabel('Feat 2')
     ax.set_xlim(
         min(data_concatenated[:,0]),
         max(data_concatenated[:,0])
         )
     ax.set_ylim(
         min(data_concatenated[:,1]),
         max(data_concatenated[:,1])
         )
     
     if save:
        if outdir=='':
            raise Exception('Please provide a directory to save the file')
        else:
            plt.savefig(f'{outdir}/mfpt.pdf',dpi=300,bbox_inches='tight')

     if display:
        plt.show()

def tpt(msm,state):
     """Transition Path Theory between two markov states

     Parameters
     ----------
     msm : pyemma.msm
        MSM or bayesian MSM
     state : list
         List (len = 2) that contain the two state to study path

     Returns
     -------
     flux : pyemma.msm.tpt
         Flux between the two states
     cgflux : flux.coarse_grain
          Coarse grained flux between the two states
     """

     # Initiate the two states
     A = msm.metastable_sets[state[0]]
     B = msm.metastable_sets[state[1]]
     
     # Compute the flux and the coarse grained
     flux = pyemma.msm.tpt(msm, A, B)
     cg, cgflux = flux.coarse_grain(msm.metastable_sets)

     # Get the pathes
     paths,path_fluxes = cgflux.pathways(fraction=0.99)
     print('percentage       \tpath')
     print('-------------------------------------')
     for i in range(len(paths)):
         print(
             np.round(path_fluxes[i] / np.sum(path_fluxes), 3),
             ' \t',
             paths[i] + 1)

     return flux, cgflux

def plot_committor_tpt(
        data,
        cluster,
        flux,
        state,
        cgflux,
        coarse_state_centers,
        nstates,
        save=False,
        outdir='',
        display=False
        ):
     """Plot the committor map

     Parameters
     ----------
     data : pyemma.load
        Data loaded from pyemma loader
     cluster : pyemma.cluster
        Cluster to make the analysis
     flux : pyemma.msm.tpt
         Flux between the two states
     state : list
         List (len = 2) that contain the two state to study path
     cgflux : flux.coarse_grain
          Coarse grained flux between the two states
     coarse_state_centers : pyemma.cluster.clustercenters
          Coarse state centers
     nstates : int
         Number of meta stable states to consider
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
     # Data without dimension reduction
     if type(data) == list:
         data_concatenated = np.concatenate(data)
     # Dimension reduction
     else:
          data_concatenated = np.concatenate(data.get_output())
     
     dtrajs_concatenated = np.concatenate(cluster.dtrajs)

     # Committor map behind
     fig, ax = plt.subplots(figsize=(10, 7))
     pyemma.plots.plot_contour(
         *data_concatenated.T,
         flux.committor[dtrajs_concatenated],
         cmap='brg',
         ax=ax,
         mask=True,
         cbar_label=fr'Committor {state[0]} $\to$ {state[1]}',
         alpha=0.8,
         zorder=-1)
     
     # State label
     state_labels=['']*nstates
     state_labels[state[0]] = 'A'
     state_labels[state[1]] = 'B'

     # Flux above
     pyemma.plots.plot_flux(
         cgflux,
         coarse_state_centers,
         cgflux.stationary_distribution,
         state_labels=state_labels, 
         ax=ax,
         show_committor=False,
         figpadding=0,
         show_frame=True,
         arrow_label_format='%2.e / ps');
     ax.set_xlabel('Feat 1')
     ax.set_ylabel('Feat 2')
     ax.set_xlim(
         min(data_concatenated[:,0]),
         max(data_concatenated[:,0])
         )
     ax.set_ylim(
         min(data_concatenated[:,1]),
         max(data_concatenated[:,1])
         )
     
     if save:
        if outdir=='':
            raise Exception('Please provide a directory to save the file')
        else:
            plt.savefig(f'{outdir}/mfpt_committor.pdf',dpi=300,bbox_inches='tight')

     if display:
        plt.show()
    


if __name__ == '__main__':

     # Path
    pdb = '/data/cloison/Simulations/HSP90-NT/SIMULATIONS_TRAJECTORIES/AMBER19SB_OPC/GS_cluster1.pdb'
    traj = ['/data/cloison/Simulations/HSP90-NT/SIMULATIONS_TRAJECTORIES/AMBER19SB_OPC/GS01_md_all_fitBB_protonly.xtc','/data/cloison/Simulations/HSP90-NT/SIMULATIONS_TRAJECTORIES/AMBER19SB_OPC/GS02_md_all_fitBB_protonly.xtc']
    outdir='/home/ccattin/Documents/Code/outputs'
    filename='test.pyemma'
    model_name = 'GS01_GS02'
    # Feat
    pairNames = ['64_CA-130_CA', '119_CA-24_CA']
    # Parameters
    save = False
    display = False
    T = 300
    lag=1000
    nits = 4
    lags=[1, 2, 5, 10, 20, 50]
    stable_state = 3

    pair_indices = tools.create_pairIndices_from_pairNames(pdb,pairNames)
    feat = create_feat(pdb,pair_indices)
    data = load_data(traj,feat)

    tica = tica_reduction(data=data,
                          lag=lag,
                          T=T,
                          save=save,
                          display=display,
                          outdir=outdir)
    
#     cluster = clustering(reduction=tica,
#                          method='kmeans',
#                          k=200,
#                          stride=1)
    
#     msm = create_msm(cluster=cluster,
#            lag=lag,
#            error=False)
    
#     tools.save_model(
#         cluster=cluster,
#         msm=msm,
#         outdir=outdir,
#         model_name=model_name,
#         filename=filename
#         )
    msm, cluster = tools.load_model(
         outdir=outdir,
         filename=filename,
         model_name=model_name
    )

    stationary_prob(
        msm=msm,
        nstate=stable_state
        )
    plot_metastable_membership(
        msm=msm,
        nstate=stable_state,
        data=tica,
        cluster=cluster,
        display=display,
        save=save,
        outdir=outdir
    )

    (
        metastable_traj,
        highest_membership,
        coarse_state_centers
        ) = concatenate(
        msm=msm,
        cluster=cluster
    )
    print(
        metastable_traj,
        highest_membership,
        coarse_state_centers
        )
    
    mfpt, inverse_mfpt = get_mfpt(
         msm=msm,
         nstates=stable_state
    )
    print(mfpt,inverse_mfpt)


    plot_mftp(
        data=tica,
        nstates=stable_state,
        mfpt=mfpt,
        inverse_mfpt=inverse_mfpt,
        metastable_traj=metastable_traj,
        coarse_state_centers=coarse_state_centers,
        display=display,
        save=save,
        outdir=outdir
    )

    flux, cgflux = tpt(
        msm=msm,
        state=[1,2]
    )

    plot_committor_tpt(
        data=tica,
        cluster=cluster,
        flux=flux,
        state=[1,2],
        cgflux=cgflux,
        coarse_state_centers=coarse_state_centers,
        nstates=stable_state,
        display=display,
        outdir=outdir,
        save=save
    )
