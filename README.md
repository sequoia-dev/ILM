# ILM
Repository of the different codes developed during my M2 insternship at the ILM. 

## Water simulation
  Inside the water/ directory.
  Run eau_CLI -h for manual of the CLI
  The bash files are automated pipeline for single run, analysis of the cutoff and of the simulation length of water MD simulations.
  
## GMX
  File for automated running gromacs. Energy minimization, equilibration NVT/NPT, production, analysis.
  
## PSMN
  File for submiting jobs to the PSMN on the correct node.
  
  ![mercure](https://github.com/comecattin/ILM/assets/75748278/3e3b2e33-75dd-47b4-99ec-363b52f817be)

  ✉️ Mercure is a submit script to break down in smaller simulation one big simulation. See documentation in [PSMN/Mercure](https://github.com/comecattin/ILM/tree/main/PSMN/Mercure)
  
## Outputs
  Test outputs of the various script done.

## Markov
  Various codes that use MSM or PyEmma

<img width="472" alt="LETHE_logo" src="https://github.com/comecattin/ILM/assets/75748278/7b46129f-ab24-48b5-86fb-514de5e4f718">

  
  🚅 Lethe is an implementation of automatize PyEmma MSM pipeline. Manual available using `./LETHE.py -h/--help` or in [Markov/Lethe](https://github.com/comecattin/ILM/tree/main/Markov/Lethe)

## Cluster
  Codes that rely on TTClust and extract its result
  
## VMD
  Scripts for VMD
