#!/usr/bin/env python3
from xml.dom import minidom
import xml.etree.cElementTree as ET
import pandas as pd
import sys
from argparse import ArgumentParser
import uuid


def indent(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

def makeSampleRegistrationXML(df, outf):

    sample_set = ET.Element('SAMPLE_SET')

    cols=['scientific_name',	'sample_alias',	'sample_title',	'isolation_source',
          	'collection date',	'geographic location (country and/or sea)',	'host health state',
                	'host scientific name',	'isolate']

    for index,row in df.iterrows():
        alias=row['sample_alias']
        #collection_date=row['collection date']

        ## XML
        sample = ET.SubElement(sample_set, 'SAMPLE', alias=alias)
        #experiment_ref = ET.SubElement(run, "EXPERIMENT_REF", refname=exp_ref)

        # indent
        title = ET.SubElement(sample, "TITLE").text = alias
        sample_name = ET.SubElement(sample, "SAMPLE_NAME")
        
        # indent
        taxon_ID = ET.SubElement(sample_name, "TAXON_ID").text = str(row['tax_id'])

        #dedent
        sample_attributes = ET.SubElement(sample, "SAMPLE_ATTRIBUTES")

        # indent
        sample_attribute = ET.SubElement(sample_attributes, "SAMPLE_ATTRIBUTE")

        ET.SubElement(sample_attribute,"TAG").text = 'ENA-CHECKLIST'
        ET.SubElement(sample_attribute,"VALUE").text = 'ERC000028'

        for col in cols:
            value=row[col]
            sample_attribute = ET.SubElement(sample_attributes, "SAMPLE_ATTRIBUTE")
            ET.SubElement(sample_attribute,"TAG").text = str(col)
            ET.SubElement(sample_attribute,"VALUE").text = str(value)

    # use the indent function to indent the xml file
    indent(sample_set)
    # create tree
    tree = ET.ElementTree(sample_set)

    # outfile
    with open(outf, 'wb') as outfile:
        tree.write(outfile, xml_declaration=True, encoding='utf-8', method="xml")

    df.to_csv('sample_meta_alias.csv',index=False)

def parse_receipt_xml(xmlFile):
    xmldoc = minidom.parse(xmlFile)
    samples = xmldoc.getElementsByTagName('SAMPLE')
    l=[]
    for sample in samples:
        d={}
        d['alias'] = sample.attributes['alias'].value
        d['accession'] = sample.attributes['accession'].value
        EXT_ID = sample.getElementsByTagName('EXT_ID')
        for e in EXT_ID:
            d['ENA biosample accession'] = e.attributes["accession"].value
        l.append(d)
    
    df=pd.DataFrame(l)
    df.to_csv('receipt.csv',index=False)
    return df
    

def makeExperimentXML(df, outf):
    experiment_set = ET.Element('EXPERIMENT_SET')
    for index,row in df.iterrows():
        alias=row['ALIAS']
        accession=row['ACCESSION']
        refname=row['Study']
        library_strategy=row['library_strategy']
        library_selection=row['library_selection']
        library_source=row['library_source']
        instrument_model=row['instrument_model']
        center_name=row['center_name']
    
        ## XML
        experiment = ET.SubElement(experiment_set, 'EXPERIMENT', alias=alias)
        study_ref = ET.SubElement(experiment, "STUDY_REF", accession=refname)
        
        # indent
        design = ET.SubElement(experiment, "DESIGN")
        
        # indent
        design_description = ET.SubElement(design, "DESIGN_DESCRIPTION")
        sample_descriptor = ET.SubElement(design, 'SAMPLE_DESCRIPTOR', accession=accession)
        library_descriptor = ET.SubElement(design, "LIBRARY_DESCRIPTOR")
        library_name = ET.SubElement(library_descriptor, "LIBRARY_NAME")
        library_strategy = ET.SubElement(library_descriptor, "LIBRARY_STRATEGY").text = str(library_strategy)
        library_source = ET.SubElement(library_descriptor, "LIBRARY_SOURCE").text = str(library_source)
        library_selection = ET.SubElement(library_descriptor, "LIBRARY_SELECTION").text = str(library_selection)
        library_layout_dir = ET.SubElement(library_descriptor, "LIBRARY_LAYOUT")
        #indent
        paired = ET.SubElement(library_layout_dir, "SINGLE") 
        
        # dedent
        platform = ET.SubElement(experiment, "PLATFORM")
        ont = ET.SubElement(platform, "OXFORD_NANOPORE")
        
        #indent
        instrument_model = ET.SubElement(ont, "INSTRUMENT_MODEL").text = str(instrument_model)
        
        # dedent
        #processing = ET.SubElement(experiment, "PROCESSING")
    
    # use the indent function to indent the xml file
    indent(experiment_set)
    # create tree
    tree = ET.ElementTree(experiment_set)
    
    # outfile
    with open(outf, 'wb') as outfile:
    	tree.write(outfile, xml_declaration=True, encoding='utf-8', method="xml")

def makeRunXML(df, outf):
    run_set = ET.Element('RUN_SET')
    for index,row in df.iterrows():
        alias=row['ALIAS']
        exp_ref=row['ALIAS']
        f=row['file']

        ## XML
        run = ET.SubElement(run_set, 'RUN', alias=alias)
        experiment_ref = ET.SubElement(run, "EXPERIMENT_REF", refname=exp_ref)

        # indent
        data_block = ET.SubElement(run, "DATA_BLOCK")

        # indent
        files = ET.SubElement(data_block, "FILES")
        file = ET.SubElement(files,"FILE", filename=f, filetype="OxfordNanopore_native",
                checksum_method="MD5", checksum=row['md5'])

    # use the indent function to indent the xml file
    indent(run_set)
    # create tree
    tree = ET.ElementTree(run_set)

    # outfile
    with open(outf, 'wb') as outfile:
        tree.write(outfile, xml_declaration=True, encoding='utf-8', method="xml")

def mergeMD5(df,md5):
    df2=pd.read_csv(md5,sep='  ',names=['md5','file'])
    print(df)
    print(df2)
    df=df.merge(df2, on='file', how='left')
    return df

def run(opts):
    ## Make Sample registrastion XML 
    if opts.sample_meta_file != None:
        dfSM=pd.read_csv(opts.sample_meta_file)
        makeSampleRegistrationXML(dfSM, opts.sample_XML)

    ## Parse receipt XML
    if opts.receipt_XML != None:
        dfR=parse_receipt_xml(opts.receipt_XML)

    ## Make experiment and run XMLs
    if opts.csv_file != None:
        df=pd.read_csv(opts.csv_file)
        if opts.md5sum:
            df=mergeMD5(df,opts.md5sum)
        makeExperimentXML(df, opts.experiment_XML)
        makeRunXML(df, opts.run_XML)

if __name__ == '__main__':
    parser = ArgumentParser(description='Take input CSV and create XML files for ONT fast5 files')
    parser.add_argument('-c', '--csv_file', required=False,
            help='input CSV file')
    parser.add_argument('-sm', '--sample_meta_file', required=False,
            help='input sample meta data CSV file')
    parser.add_argument('-os', '--sample_XML', required=False,default='sample.xml',
            help='output sample XML default=sample.xml')
    parser.add_argument('-rx', '--receipt_XML', required=False,
            help='receipt sample XML')
    parser.add_argument('-r', '--run_XML', required=False,default='run.xml',
            help='output run XML default=run.xml')
    parser.add_argument('-m5', '--md5sum', required=False,default=None,
            help='input md5sum to merge with samples, optional')
    parser.add_argument('-e', '--experiment_XML', required=False,default='experiment.xml',
            help='output experiment XML default=experiment.xml')
    opts, unknown_args = parser.parse_known_args()
    run(opts)
