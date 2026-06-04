import pandas as pd
import numpy as np
from scipy.special import logsumexp

def mpileup_to_csv(args):
    sampleid = args[0]
    mpileup_file = args[1]
    allele_rs = pd.read_csv(args[2], header=0)
    geno_indel = args[3]
    geno_imputed = args[4] if len(args) > 4 else "0"

    mpileup = pd.read_csv(mpileup_file, sep='\t', header=None, 
                         names=["chr", "pos", "ref", "depth", "bases", "qualities_ASCII"])
    
    for i in range(len(mpileup)):
        mpileup.at[i, 'bases'] = mpileup.at[i, 'bases'].replace('$', '')
        mpileup.at[i, 'bases'] = mpileup.at[i, 'bases'].replace(r'\^.', '', regex=True)
        mpileup.at[i, 'bases'] = mpileup.at[i, 'bases'].replace('[<>]', '', regex=True)
        mpileup.at[i, 'bases'] = mpileup.at[i, 'bases'].replace('.', mpileup.at[i, 'ref'])
        mpileup.at[i, 'bases'] = mpileup.at[i, 'bases'].replace(',', mpileup.at[i, 'ref'])
        mpileup.at[i, 'bases'] = mpileup.at[i, 'bases'].upper()
    
    mpileup = mpileup[mpileup['bases'] != '*']
    
    if len(mpileup) > 0:
        for i in range(len(mpileup)):
            qualities = [ord(c) - 33 for c in mpileup.at[i, 'qualities_ASCII']]
            bases_list = list(mpileup.at[i, 'bases'])
            filtered_bases = [b for j, b in enumerate(bases_list) if qualities[j] >= 30]
            mpileup.at[i, 'bases'] = ''.join(filtered_bases)
            
            filtered_qualities = [q for q in qualities if q >= 30]
            mpileup.at[i, 'qualities_ASCII'] = ''.join([chr(q + 33) for q in filtered_qualities])
        
        mpileup = mpileup[mpileup['bases'] != '']
        mpileup['depth'] = mpileup['bases'].apply(len)
        mpileup['qualities'] = mpileup['qualities_ASCII'].apply(lambda x: [ord(c) - 33 for c in x])
        mpileup['log10_err'] = mpileup['qualities'].apply(lambda x: [-q/10 for q in x])
        mpileup['bases'] = mpileup['bases'].apply(lambda x: ','.join(list(x)))
        
        genotypes = ['AA', 'AC', 'AG', 'AT', 'CC', 'CG', 'CT', 'GG', 'GT', 'TT']
        risultati_list = []
        
        for i in range(len(mpileup)):
            bases = mpileup.at[i, 'bases'].split(',')
            log10_err = mpileup.at[i, 'log10_err']
            risultati = np.full((len(bases), len(genotypes)), np.nan)
            
            for j, genotype in enumerate(genotypes):
                A1, A2 = list(genotype)
                
                for k, base in enumerate(bases):
                    if base == A1 and base == A2:
                        risultati[k, j] = np.log10(1 - 10**log10_err[k])
                    elif (base == A1 and base != A2) or (base != A1 and base == A2):
                        risultati[k, j] = logsumexp([np.log10(1 - 10**log10_err[k]) - np.log10(2), 
                                                   (log10_err[k] - np.log10(3)) - np.log10(2)])
                    else:
                        risultati[k, j] = log10_err[k] - np.log10(3)
            
            risultati_list.append(risultati)
        
        genLogLikelihood = pd.DataFrame(np.nan, index=mpileup['chr'] + ':' + mpileup['pos'].astype(str),
                                       columns=genotypes)
        
        for i in range(len(genLogLikelihood)):
            for j, genotype in enumerate(genotypes):
                genLogLikelihood.iloc[i, j] = np.sum(risultati_list[i][:, j])
        
        genLogLikelihood_normalized = genLogLikelihood.apply(lambda row: row - logsumexp(row), axis=1)
        genLogLikelihood_normalized.to_csv(f"{sampleid}_genLogLikelihood.txt", sep='\t')
        
        genPosteriors = genLogLikelihood_normalized.copy()
        prior_hom = np.log10(0.999)
        prior_het = np.log10(0.001)
        
        for col in genPosteriors.columns:
            if col in ['AA', 'CC', 'GG', 'TT']:
                genPosteriors[col] = genPosteriors[col] + prior_hom
            else:
                genPosteriors[col] = genPosteriors[col] + prior_het
        
        for i in range(len(genPosteriors)):
            row = genPosteriors.iloc[i]
            row = row - logsumexp(row)
            row = 10**row
            row = row / row.sum()
            genPosteriors.iloc[i] = row
        
        genPosteriors.to_csv(f"{sampleid}_genPosteriors.txt", sep='\t')
        
        genPosteriors = genPosteriors.reset_index().rename(columns={'index': 'Position'})
        Hps_SNPs = allele_rs
        genPosteriors = pd.merge(genPosteriors, Hps_SNPs, on='Position', how='left')
        genPosteriors = genPosteriors.sort_values('Num')
        
        sampling_list = []
        
        for j in range(1000):
            sampling = pd.DataFrame(index=genPosteriors.index)
            sampling['Num'] = genPosteriors['Num']
            sampling['Rs_allele'] = genPosteriors['Rs_allele']
            sampling['Strand'] = genPosteriors['Strand']
            sampling['Position'] = genPosteriors['Position']
            
            for i in range(len(genPosteriors)):
                allele_interesse = genPosteriors.at[i, 'Strand']
                probabilita = genPosteriors.iloc[i, 1:11].fillna(0).values
                
                if np.all(probabilita == 0):
                    genotipo_i = np.nan
                else:
                    genotipo_i = np.random.choice(genotypes, p=probabilita/np.sum(probabilita))
                
                sampling.at[i, 'Sampling Genotype'] = genotipo_i
                
                if pd.isna(genotipo_i):
                    sampling.at[i, 'Sampled'] = np.nan
                elif genotipo_i == allele_interesse * 2:
                    sampling.at[i, 'Sampled'] = 2
                elif allele_interesse in genotipo_i:
                    sampling.at[i, 'Sampled'] = 1
                else:
                    sampling.at[i, 'Sampled'] = 0
            
            sampling_list.append(sampling)
        
        for j, sampling in enumerate(sampling_list):
            sampling.columns = [f"{col}_{j+1}" for col in sampling.columns]
        
        sampling_df_check = pd.concat(sampling_list, axis=1)
        sampled_columns = [col for col in sampling_df_check.columns if 'Sampled' in col]
        sampling_df = sampling_df_check[sampled_columns]
        sampling_df = sampling_df.T
        sampling_df.columns = Hps_SNPs['Rs_allele']
        
        sampling_df['rs312262906_A'] = geno_indel
        
        if geno_imputed != "0":
            geno_imputed_df = pd.read_csv(geno_imputed, sep='\t', header=None,
                                         names=["Chr", "Position", "Ref", "Alt", "GT", "Rs_allele"])
            for _, row in geno_imputed_df.iterrows():
                sampling_df[row['Rs_allele']] = row['GT']
        
        sampling_df.index = [f"{sampleid}_{i}" for i in range(1, 1001)]
        sampling_df.reset_index(inplace=True)
        sampling_df.rename(columns={'index': 'sampleid'}, inplace=True)
        sampling_df.to_csv(f"{sampleid}_1000sampling.csv", index=False)
    
    else:
        output_df = pd.DataFrame(columns=['sampleid'] + list(allele_rs['Rs_allele']))
        output_df.loc[0, 'sampleid'] = sampleid
        output_df['rs312262906_A'] = geno_indel
        
        if geno_imputed != "0":
            geno_imputed_df = pd.read_csv(geno_imputed, sep='\t', header=None,
                                         names=["Chr", "Position", "Ref", "Alt", "GT", "Rs_allele"])
            for _, row in geno_imputed_df.iterrows():
                output_df[row['Rs_allele']] = row['GT']
        
        output_df.to_csv(f"{sampleid}_onlyimputedcalls.csv", index=False)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Convert mpileup to CSV')
    parser.add_argument('sampleid', help='Sample ID')
    parser.add_argument('mpileup_file', help='Mpileup file path')
    parser.add_argument('allele_rs', help='Allele RS file path')
    parser.add_argument('geno_indel', help='Genotype indel')
    parser.add_argument('geno_imputed', nargs='?', default='0', help='Genotype imputed file path')
    
    args = parser.parse_args()
    mpileup_to_csv([args.sampleid, args.mpileup_file, args.allele_rs, args.geno_indel, args.geno_imputed])