java -Xmx8g -jar picard.jar LiftoverVcf I=input38.vcf O=outputTo37.vcf CHAIN=../data/GRCh38ToGRCh37.chain REJECT=rejectTo37.vcf R=../data/grch37.fa
java -Xmx8g -jar picard.jar LiftoverVcf I=input37.vcf O=outputTo38.vcf CHAIN=../data/GRCh37ToGRCh38.chain REJECT=rejectTo38.vcf R=../data/grch38.fa
