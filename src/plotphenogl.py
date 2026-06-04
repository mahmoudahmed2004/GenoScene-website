import pandas as pd
import matplotlib.pyplot as plt

def plot_pheno_gl(args):
    sample_id = args[0]
    sample_csv = pd.read_csv(f"{sample_id}_phenotypicPrediction.csv", sep=';', header=0)
    
    eye_colour_counts = sample_csv['predicted_eye_colour'].value_counts()
    eye_colour_df = pd.DataFrame({'Eye_colour': eye_colour_counts.index, 'Count': eye_colour_counts.values})
    eye_colour_levels = ['Brown', 'Intermediate', 'Blue', 'Not predicted']
    eye_colour_df = pd.merge(pd.DataFrame({'Eye_colour': eye_colour_levels}), eye_colour_df, on='Eye_colour', how='left').fillna(0)
    eye_colour_df['Percent'] = eye_colour_df['Count'] / eye_colour_df['Count'].sum() * 100
    eye_colour_df['Eye_colour'] = pd.Categorical(eye_colour_df['Eye_colour'], categories=eye_colour_levels, ordered=True)
    
    fig, ax = plt.subplots(figsize=(3.5, 3))
    ax.pie(eye_colour_df['Count'], labels=eye_colour_df['Eye_colour'], autopct='%1.1f%%',
           colors=['#713012', '#597133', '#3D85C7', '#BFBFBF'])
    ax.set_title('Eye colour phenotype')
    plt.savefig(f"{sample_id}_GL_eye.jpg", dpi=300, bbox_inches='tight')
    plt.close()
    
    hair_colour_counts = sample_csv['predicted_hair_colour'].value_counts()
    hair_colour_df = pd.DataFrame({'Hair_colour': hair_colour_counts.index, 'Count': hair_colour_counts.values})
    hair_colour_levels = ['Black', 'Dark brown/black', 'Brown/dark brown', 'Brown', 'Dark blond', 'Blond', 'Red', 'Not predicted']
    hair_colour_df = pd.merge(pd.DataFrame({'Hair_colour': hair_colour_levels}), hair_colour_df, on='Hair_colour', how='left').fillna(0)
    hair_colour_df['Percent'] = hair_colour_df['Count'] / hair_colour_df['Count'].sum() * 100
    hair_colour_df['Hair_colour'] = pd.Categorical(hair_colour_df['Hair_colour'], categories=hair_colour_levels, ordered=True)
    
    fig, ax = plt.subplots(figsize=(3.5, 3))
    ax.pie(hair_colour_df['Count'], labels=hair_colour_df['Hair_colour'], autopct='%1.1f%%',
           colors=['#000000', '#1c0e04', '#381c08', '#6f370f', '#7e5414', '#dcba7f', '#cf5f17', '#BFBFBF'])
    ax.set_title('Hair colour phenotype')
    plt.savefig(f"{sample_id}_GL_hair.jpg", dpi=300, bbox_inches='tight')
    plt.close()
    
    skin_colour_counts = sample_csv['predicted_skin_colour'].value_counts()
    skin_colour_df = pd.DataFrame({'Skin_colour': skin_colour_counts.index, 'Count': skin_colour_counts.values})
    skin_colour_levels = ['Dark to black', 'Dark', 'Intermediate', 'Pale', 'Very pale', 'Not predicted']
    skin_colour_df = pd.merge(pd.DataFrame({'Skin_colour': skin_colour_levels}), skin_colour_df, on='Skin_colour', how='left').fillna(0)
    skin_colour_df['Percent'] = skin_colour_df['Count'] / skin_colour_df['Count'].sum() * 100
    skin_colour_df['Skin_colour'] = pd.Categorical(skin_colour_df['Skin_colour'], categories=skin_colour_levels, ordered=True)
    
    fig, ax = plt.subplots(figsize=(3.5, 3))
    ax.pie(skin_colour_df['Count'], labels=skin_colour_df['Skin_colour'], autopct='%1.1f%%',
           colors=['#452F17', '#81582B', '#C18747', '#D5AD81', '#EAD6C0', '#BFBFBF'])
    ax.set_title('Skin colour phenotype')
    plt.savefig(f"{sample_id}_GL_skin.jpg", dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Plot GL phenotypes')
    parser.add_argument('sample_id', help='Sample ID')
    
    args = parser.parse_args()
    plot_pheno_gl([args.sample_id])