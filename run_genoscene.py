#!/usr/bin/env python3
"""
GenoScene - Quick Start Script
==============================

This script provides a quick way to run GenoScene with example data
or your own data files.

Usage:
    python run_genoscene.py [sample_id] [data_file]
    python run_genoscene.py --demo
    python run_genoscene.py --help
"""

import sys
import os
import argparse
import subprocess
import webbrowser
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(
        description="GenoScene - AI-Powered Forensic Phenotype Prediction System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_genoscene.py --demo                    # Run with demo data
  python run_genoscene.py SAMPLE_001 data.csv      # Run with your data
  python run_genoscene.py --web                    # Open web interface
  python run_genoscene.py --help                   # Show this help
        """
    )
    
    parser.add_argument(
        "sample_id",
        nargs="?",
        help="Sample ID for analysis"
    )
    
    parser.add_argument(
        "data_file",
        nargs="?",
        help="Path to CSV data file"
    )
    
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run with demo data"
    )
    
    parser.add_argument(
        "--web",
        action="store_true",
        help="Open web interface"
    )
    
    parser.add_argument(
        "--install",
        action="store_true",
        help="Install required packages"
    )
    
    args = parser.parse_args()
    
    print("🧬 GenoScene - AI-Powered Forensic Phenotype Prediction System")
    print("=" * 60)
    
    # Install packages if requested
    if args.install:
        install_packages()
        return
    
    # Open web interface if requested
    if args.web:
        open_web_interface()
        return
    
    # Run demo if requested
    if args.demo:
        run_demo()
        return
    
    # Run with provided data
    if args.sample_id and args.data_file:
        run_analysis(args.sample_id, args.data_file)
        return
    
    # Show help if no arguments
    if not any([args.sample_id, args.data_file, args.demo, args.web, args.install]):
        parser.print_help()
        return

def install_packages():
    """Install required packages"""
    print("📦 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Packages installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing packages: {e}")
        return False
    return True

def open_web_interface():
    """Open the web interface"""
    print("🌐 Opening web interface...")
    html_file = Path("index.html")
    if html_file.exists():
        webbrowser.open(f"file://{html_file.absolute()}")
        print("✅ Web interface opened in your browser!")
    else:
        print("❌ index.html not found!")

def run_demo():
    """Run with demo data"""
    print("🎯 Running demo analysis...")
    try:
        # Run the example script
        subprocess.check_call([sys.executable, "examples/example_usage.py"])
        print("✅ Demo completed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running demo: {e}")
    except FileNotFoundError:
        print("❌ Example script not found!")

def run_analysis(sample_id, data_file):
    """Run analysis with provided data"""
    print(f"🔬 Running analysis for sample: {sample_id}")
    print(f"📊 Data file: {data_file}")
    
    # Check if data file exists
    if not os.path.exists(data_file):
        print(f"❌ Data file not found: {data_file}")
        return
    
    try:
        # Import and run analysis
        sys.path.append("src")
        from phenotypicprediction import phenotypic_prediction
        from plotphenodc import plot_pheno_dc
        from plotphenogl import plot_pheno_gl
        
        # Run phenotype prediction
        print("🔬 Running phenotype prediction...")
        phenotypic_prediction([sample_id, data_file])
        print("✅ Phenotype prediction completed!")
        
        # Generate plots
        print("📈 Generating plots...")
        plot_pheno_dc([sample_id])
        plot_pheno_gl([sample_id])
        print("✅ Plots generated!")
        
        # Move results to output directory
        move_results_to_output(sample_id)
        
        print(f"🎉 Analysis completed for sample: {sample_id}")
        print("📁 Check the 'output' directory for results")
        
    except ImportError as e:
        print(f"❌ Error importing modules: {e}")
        print("💡 Try running: python run_genoscene.py --install")
    except Exception as e:
        print(f"❌ Error during analysis: {e}")

def move_results_to_output(sample_id):
    """Move result files to output directory"""
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    result_files = [
        f"{sample_id}_phenotypicPrediction.csv",
        f"{sample_id}_DC_eye.jpg",
        f"{sample_id}_DC_hair.jpg",
        f"{sample_id}_DC_skin.jpg",
        f"{sample_id}_GL_eye.jpg",
        f"{sample_id}_GL_hair.jpg",
        f"{sample_id}_GL_skin.jpg"
    ]
    
    for file in result_files:
        if os.path.exists(file):
            os.rename(file, output_dir / file)
            print(f"📁 Moved {file} to output directory")

if __name__ == "__main__":
    main()
