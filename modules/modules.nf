process REGISTER {
    label 'ena'

    publishDir "ENA/${task.process.replaceAll(":","_")}_${params.ENA}", mode: 'copy'

    input:
    path('sample_meta.csv')
    each path('submission.xml')
    each path('ena.netrc')

    output:
	path('receipt.csv'), emit: receiptCSV
	path('receipt.xml'), emit: receiptXML
	path('sample_meta_alias.csv'), emit: sample_meta


    script:
	server = params.ENA_server
    """
	create_submission.py -sm sample_meta.csv

	curl --netrc-file ena.netrc \
		-F "SUBMISSION=@submission.xml" \
		-F "SAMPLE=@sample.xml" \
		$server \
		> receipt.xml

    create_submission.py -rx receipt.xml
    """
    stub:
    """
    touch receipt.csv receipt.xml
    """
}

process MAKE_MANIFESTS {
	label 'ena'

    publishDir 'accession', mode: 'copy', pattern: 'receiptCSV'

	input:
	tuple path('receiptCSV'), path('sampleMeta.csv')

	output:
	path('*.genome.txt'), emit: txt
	path('*.fq.txt'), emit: fqtxt
    path('receiptCSV'), emit: csv

	script:
	studyName=params.studyName
	"""
	makeManifests.py -r receiptCSV \
		-s $studyName \
		-m sampleMeta.csv
	"""
	
	stub:
	"""
	touch sample1.txt sample2.txt
	"""
}

process DOWNLOAD_JAR {
	label 'ena'

	output:
	path('*.jar'), emit: jar

	script:
    dl=params.webin_jar
	"""
    wget ${dl}
	"""
	
	stub:
	"""
	touch webin-cli-6.4.1.jar
	"""
}

process DEDUPE {
    tag {sample}
	label 'ena'
    maxForks 3

    input:
    tuple val(sample), path('reads.fastq.gz')

    output:
    tuple val(sample), path('ddreads.fastq.gz')

    script:
    """
    remove_duplicates.py reads.fastq.gz ddreads.fastq
    gzip ddreads.fastq
    """
}

process UPLOAD_FQS {
	tag {sample}
	label 'ena'

	publishDir "ENA/${task.process.replaceAll(":","_")}_${params.ENA}", pattern: 'webin-cli.report', mode: 'copy', saveAs: { filename -> "${sample}_${fluType}.cli.report.txt"} 
	publishDir "ENA/${task.process.replaceAll(":","_")}_${params.ENA}", pattern: '*.csv', mode: 'copy'

	input:
	tuple val(sample), path('reads.fastq.gz'), path('manifest.txt'), path('webpasswd')
    each path('webin.jar')

	output:
	path('webin-cli.report'), emit: report
	tuple val(sample), path("${sample}_accessions.csv"), emit: accessions, optional: true


	script:
	webuser=params.webuser
	if (params.ENA == 'test'){
	"""
	export PASS=`cat webpasswd`
	java -jar webin.jar \
		-username=$webuser \
		-passwordEnv=PASS \
		-context=reads \
		-manifest=manifest.txt -validate -test

	"""
	}
	else if (params.ENA == 'live'){
	"""
	export PASS=`cat webpasswd`
	java -jar webin.jar \
		-username=$webuser \
		-passwordEnv=PASS \
		-context=reads \
		-manifest=manifest.txt -submit

	checkWebin.py -rr webin-cli.report -s ${sample}
	"""	
	}
	stub:
	"""
	touch webin-cli.report ${sample}_accessions.csv
	"""
}
