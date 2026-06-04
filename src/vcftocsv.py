import pandas as pd

def vcf_to_csv(args):
    sampleid = args[0]
    allele_rs = pd.read_csv(args[1], header=0)
    geno_indel = args[2]
    geno_vcf = args[3] if len(args) > 3 else "0"
    
    Hps_SNPs = allele_rs
    final_csv_df = pd.DataFrame(columns=['sampleid'] + list(Hps_SNPs['Rs_allele']))
    final_csv_df.loc[0, 'sampleid'] = sampleid
    final_csv_df['rs312262906_A'] = geno_indel
    
    if geno_vcf != "0":
        geno_vcf_df = pd.read_csv(geno_vcf, sep='\t', header=None,
                                 names=["Chr", "Position", "Ref", "Alt", "GT", "Rs_allele"])
        for _, row in geno_vcf_df.iterrows():
            final_csv_df[row['Rs_allele']] = row['GT']
    
    final_csv_df.to_csv(f"{sampleid}_directCall.csv", index=False)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Convert VCF to CSV')
    parser.add_argument('sampleid', help='Sample ID')
    parser.add_argument('allele_rs', help='Allele RS file path')
    parser.add_argument('geno_indel', help='Genotype indel')
    parser.add_argument('geno_vcf', nargs='?', default='0', help='Genotype VCF file path')
    
    args = parser.parse_args()
    vcf_to_csv([args.sampleid, args.allele_rs, args.geno_indel, args.geno_vcf])