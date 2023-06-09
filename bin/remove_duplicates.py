#!/usr/bin/env python3
from Bio import SeqIO
import sys
import gzip


def _getReads(fq):
    read_names=[]
    for seq in SeqIO.parse(gzip.open(fq,'rt'),'fastq'):
        if seq.id not in read_names:
            read_names.append(seq.id)
            seq.description = ''
            yield seq

with open(sys.argv[2],'wt') as outf:
    seqs=_getReads(sys.argv[1])
    SeqIO.write(seqs, outf, 'fastq')
