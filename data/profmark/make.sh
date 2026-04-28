#!/usr/bin/env bash

# Index UniProt (for create-profmark)
~/bin/easel/miniapps/esl-sfetch --index ~/data/uniprot/uniprot_sprot.fasta

# Generate profmark benchmark
~/bin/hmmer-3.4/profmark/create-profmark pmark \
    ~/data/PFAM/Pfam-A.seed \
    ~/data/uniprot/uniprot_sprot.fasta

# Index the MSA file
~/bin/easel/miniapps/esl-afetch --index pmark.train.msa

# Create output directory
mkdir -p train_msa

# Extract each MSA by ID (first column of .tbl)
python split_tbl_msa.py pmark.tbl pmark.train.msa -o train_msa \
    --esl-afetch "/home/felix/bin/easel/miniapps/esl-afetch"