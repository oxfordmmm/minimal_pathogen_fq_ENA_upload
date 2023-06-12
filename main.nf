#!/usr/bin/env nextflow
// enable dsl2
nextflow.enable.dsl=2


params.webin_jar='https://github.com/enasequence/webin-cli/releases/download/6.4.1/webin-cli-6.4.1.jar'
params.submissionXML="${projectDir}/ENA/submission.xml"
params.receiptCSV=''
if (params.ENA == 'test'){
    params.ENA_server = "https://wwwdev.ebi.ac.uk/ena/submit/drop-box/submit/"
}
else if (params.ENA == 'live'){
    params.ENA_server = "https://www.ebi.ac.uk/ena/submit/drop-box/submit/"
}


//modules
include {REGISTER} from './modules/modules.nf' 
include {MAKE_MANIFESTS} from './modules/modules.nf' 
include {DOWNLOAD_JAR} from './modules/modules.nf' 
include {DEDUPE} from './modules/modules.nf' 
include {UPLOAD_FQS} from './modules/modules.nf' 

workflow {
//channels
Channel.fromPath("${params.fastqs}/*")
    .map {file -> tuple(file.simpleName, file)}
    .set{fqs}

Channel.fromPath("${params.sample_meta}")
    .set{sample_meta}

Channel.fromPath("${params.netrc}")
    .set{netrc}

Channel.fromPath("${params.webpasswd}")
    .set{webpasswd}

Channel.fromPath(params.submissionXML)
    .set{submissionXML}
if (params.receiptCSV != ''){
Channel.fromPath(params.receiptCSV)
    .set{receiptCSV}
}

main:
    if (params.receiptCSV == ''){
    REGISTER(sample_meta, submissionXML, netrc)
    receiptCSV=REGISTER.out.receiptCSV
    }

    MAKE_MANIFESTS(receiptCSV
			.combine(sample_meta))

    MAKE_MANIFESTS.out.fqtxt
			.flatten()
			.map {file -> tuple(file.simpleName, file)}
			.set{fqmanifests}

    DOWNLOAD_JAR()

    DEDUPE(fqs)

    UPLOAD_FQS(DEDUPE.out
			.combine(fqmanifests,by:0)
			.combine(webpasswd), 
            DOWNLOAD_JAR.out.jar)

}




