#!/usr/bin/env python3
from argparse import ArgumentParser
import pandas as pd

genomecols=['Sample Name','STUDY', 'SAMPLE', 'ASSEMBLYNAME','ASSEMBLY_TYPE',
	'COVERAGE','PROGRAM','PLATFORM','CHROMOSOME_LIST', 'FASTA']

fqcols=['Sample Name','STUDY', 'SAMPLE', 'NAME','PLATFORM',
	'INSTRUMENT','LIBRARY_SOURCE','LIBRARY_SELECTION','LIBRARY_STRATEGY','FASTQ']

def makeGenome(df):
	df2=df[genomecols]
	df2.set_index('Sample Name',inplace=True)
	df3=df2.T
	#print(df3)
	for i in df3.columns:
		df3[i].to_csv('{0}.genome.txt'.format(i),sep='\t',header=False)

def makeFQ(df):
	df2=df[fqcols]
	df2.set_index('Sample Name',inplace=True)
	df3=df2.T
	#print(df3)
	for i in df3.columns:
		df3[i].to_csv('{0}.fq.txt'.format(i),sep='\t',header=False)

def makeDF(df, opts):
	df['STUDY']=opts.study_name
	df['SAMPLE']=df['accession']
	df['ASSEMBLYNAME']=df['alias'] + '_ONT_mapped'
	df['ASSEMBLY_TYPE']='ISOLATE'
	df['COVERAGE']=50
	df['PROGRAM']='minimap2 and Clair3'
	df['PLATFORM']='OXFORD_NANOPORE'
	df['CHROMOSOME_LIST']='chrom_list.txt.gz'
	df['FASTA']='assembly.fasta.gz'

	# For the fastq file
	df['NAME'] = df['alias'] + '_fastq'
	df['INSTRUMENT'] = 'GridION'
	df['LIBRARY_SOURCE'] = 'METAGENOMIC'
	df['LIBRARY_SELECTION'] = 'RANDOM PCR'
	df['LIBRARY_STRATEGY'] = 'WGS'
	df['FASTQ'] = 'reads.fastq.gz'

	return df

def run(opts):
	df=pd.read_csv(opts.sample_meta)
	df2=pd.read_csv(opts.receipt)
	df=df.merge(df2, left_on='sample_alias',right_on='alias', how='left')
	
	df=makeDF(df, opts)

	makeGenome(df)
	makeFQ(df)



def getArgs(parser):
    parser.add_argument('-r', '--receipt', required=True, 
	    help='sample receipt from ena')
    parser.add_argument('-m', '--sample_meta', required=True, 
	    help='sample meta data')
    parser.add_argument('-s', '--study_name', required=True, 
	    help='Study name')
    return parser



if __name__ == '__main__':
	parser = ArgumentParser(description='Make manifests files from input csv')
	parser=getArgs(parser)
	opts, unknown_args = parser.parse_known_args()
	run(opts)