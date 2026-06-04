#!/usr/bin/env python3
"""
GenoScene - Example Usage Script
===============================

This script demonstrates how to use the GenoScene phenotype prediction system
for forensic DNA analysis.

Author: GenoScene Team
Date: 2025-01-15
"""

import sys
import os
import pandas as pd

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from phenotypicprediction import phenotypic_prediction
from plotphenodc import plot_pheno_dc
from plotphenogl import plot_pheno_gl

def main():
    """
    Main function demonstrating GenoScene usage
    """
    print("🧬 GenoScene - AI-Powered Forensic Phenotype Prediction System")
    print("=" * 60)
    
    # Example sample data
    sample_id = "EXAMPLE_001"
    
    # Create example CSV data
    print(f"\n📊 Creating example data for sample: {sample_id}")
    
    # Example SNP data (simplified for demonstration)
    example_data = {
        'sampleid': [sample_id],
        'PBlueEye': [0.15],
        'PIntermediateEye': [0.25],
        'PBrownEye': [0.60],
        'PBlondHair': [0.20],
        'PBrownHair': [0.45],
        'PRedHair': [0.05],
        'PBlackHair': [0.30],
        'PLightHair': [0.25],
        'PDarkHair': [0.75],
        'PVeryPaleSkin': [0.10],
        'PPaleSkin': [0.30],
        'PIntermediateSkin': [0.40],
        'PDarkSkin': [0.15],
        'PDarktoBlackSkin': [0.05]
    }
    
    # Create DataFrame
    df = pd.DataFrame(example_data)
    
    # Save example data
    example_file = f"examples/{sample_id}_example.csv"
    df.to_csv(example_file, index=False)
    print(f"✅ Example data saved to: {example_file}")
    
    # Run phenotype prediction
    print(f"\n🔬 Running phenotype prediction...")
    try:
        phenotypic_prediction([sample_id, example_file])
        print("✅ Phenotype prediction completed successfully!")
    except Exception as e:
        print(f"❌ Error in phenotype prediction: {e}")
        return
    
    # Generate plots for digital display
    print(f"\n📈 Generating plots for digital display...")
    try:
        plot_pheno_dc([sample_id])
        print("✅ Digital display plots generated!")
    except Exception as e:
        print(f"❌ Error generating digital plots: {e}")
    
    # Generate plots for scientific publication
    print(f"\n📊 Generating plots for scientific publication...")
    try:
        plot_pheno_gl([sample_id])
        print("✅ Scientific publication plots generated!")
    except Exception as e:
        print(f"❌ Error generating scientific plots: {e}")
    
    # Display results
    print(f"\n📋 Results Summary:")
    print("-" * 30)
    
    try:
        # Read prediction results
        results_file = f"{sample_id}_phenotypicPrediction.csv"
        if os.path.exists(results_file):
            results_df = pd.read_csv(results_file, sep=';')
            
            print(f"Sample ID: {results_df.iloc[0]['sampleid']}")
            print(f"Predicted Eye Color: {results_df.iloc[0]['predicted_eye_colour']}")
            print(f"Predicted Hair Color: {results_df.iloc[0]['predicted_hair_colour']}")
            print(f"Predicted Skin Color: {results_df.iloc[0]['predicted_skin_colour']}")
            
            # Move results to output directory
            os.makedirs("output", exist_ok=True)
            os.rename(results_file, f"output/{results_file}")
            print(f"\n📁 Results moved to output directory")
        else:
            print("❌ Results file not found")
            
    except Exception as e:
        print(f"❌ Error reading results: {e}")
    
    print(f"\n🎉 GenoScene analysis completed!")
    print(f"📁 Check the 'output' directory for all generated files")

if __name__ == "__main__":
    main()
