# Minimal pathogen fastq ENA upload workflow

This needs a CSV file with the format:

| Sample Name |  tax_id | scientific_name | sample_alias | sample_title | isolation_source | collection date | geographic location (country and/or sea) | host health state | host scientific name | isolate |
| ------------ | ------- | --------------- | ------------ | ------------ | ---------------- | --------------- | ---------------------------------------- | ----------------- | -------------------- | ------- |
| DS135_SP     | 256318 | metagenome      | DS135_SP     | DS135_SP     | Nasel or sputum  |           2,020 | United Kingdom                           | diseased          | Homo sapiens         |         |
| DS137_SP     | 256318 | metagenome      | DS137_SP     | DS137_SP     | Nasel or sputum  |           2,020 | United Kingdom                           | diseased          | Homo sapiens         |         |
| DS138_SP     | 256318 | metagenome      | DS138_SP     | DS138_SP     | Nasel or sputum  |           2,020 | United Kingdom                           | diseased          | Homo sapiens         |         |
| DS148_SP     | 256318 | metagenome      | DS148_SP     | DS148_SP     | Nasel or sputum  |           2,020 | United Kingdom                           | diseased          | Homo sapiens         |         |
| H010066N9_NL | 256318 | metagenome      | H010066N9_NL | H010066N9_NL | Nasel or sputum  |           2,020 | United Kingdom                           | diseased          | Homo sapiens         |         |
| H010174N9_NL | 256318 | metagenome      | H010174N9_NL | H010174N9_NL | Nasel or sputum  |           2,020 | United Kingdom                           | diseased          | Homo sapiens         |         |
| H010175N9_NL | 256318 | metagenome      | H010175N9_NL | H010175N9_NL | Nasel or sputum  |           2,020 | United Kingdom                           | diseased          | Homo sapiens         |         |
| H010177N9_NL | 256318 | metagenome      | H010177N9_NL | H010177N9_NL | Nasel or sputum  |           2,020 | United Kingdom                           | diseased          | Homo sapiens         |         |
| H010180N9_NL | 256318 | metagenome      | H010180N9_NL | H010180N9_NL | Nasel or sputum  |           2,020 | United Kingdom                           | diseased          | Homo sapiens


Your ena account and password in the `ena.netrc` file in this format:
```bash
default login Webin-XXXXX password YOURENAPASSWORD
```
Your ena password in the `ena.txt` file.

Test with the following command.

```bash
nextflow run minimal_pathogen_fq_ENA_upload/main.nf \
        --fastqs submit_fqs \
        --sample_meta sample_meta.csv \
        --netrc ena.netrc \
        --webpasswd ena.txt \
        --webuser Webin-XXXXX \
        --studyName PRJEB62780 \
        --ENA test \
        -profile conda \
        -with-trace -resume
```

Then run live with the following command:
```bash
nextflow run minimal_pathogen_fq_ENA_upload/main.nf \
        --fastqs submit_fqs \
        --sample_meta sample_meta.csv \
        --netrc ena.netrc \
        --webpasswd ena.txt \
        --webuser Webin-XXXXX \
        --studyName PRJEB62780 \
        --ENA live \
        -profile conda \
        -with-trace -resume
```
