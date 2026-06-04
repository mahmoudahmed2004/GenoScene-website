# GenoScene API Documentation

## نظرة عامة / Overview

هذا المستند يوضح كيفية استخدام واجهات برمجة التطبيقات (APIs) في نظام GenoScene للتنبؤ بالسمات الوراثية.

This document explains how to use the Application Programming Interfaces (APIs) in the GenoScene phenotype prediction system.

## الملفات الرئيسية / Main Files

### 1. phenotypicprediction.py

#### الوصف / Description
الملف الرئيسي للتنبؤ بالسمات الوراثية بناءً على بيانات SNP.

The main file for phenotype prediction based on SNP data.

#### الدوال / Functions

##### `phenotypic_prediction(args)`
```python
def phenotypic_prediction(args):
    """
    Predict phenotypes from SNP data
    
    Parameters:
    -----------
    args : list
        [sample_id, sample_csv_file]
        - sample_id (str): معرف العينة
        - sample_csv_file (str): مسار ملف CSV يحتوي على بيانات SNP
    
    Returns:
    --------
    None
        Creates {sample_id}_phenotypicPrediction.csv file
    """
```

#### مثال الاستخدام / Usage Example
```python
from phenotypicprediction import phenotypic_prediction

# تشغيل التنبؤ
phenotypic_prediction(["SAMPLE_001", "data/sample_data.csv"])
```

### 2. mpileuptocsv.py

#### الوصف / Description
تحويل ملفات mpileup إلى تنسيق CSV للتحليل.

Converts mpileup files to CSV format for analysis.

#### الدوال / Functions

##### `mpileup_to_csv(args)`
```python
def mpileup_to_csv(args):
    """
    Convert mpileup file to CSV format
    
    Parameters:
    -----------
    args : list
        [sampleid, mpileup_file, allele_rs, geno_indel, geno_imputed]
        - sampleid (str): معرف العينة
        - mpileup_file (str): مسار ملف mpileup
        - allele_rs (str): مسار ملف Allele_rs_hs37d5.csv
        - geno_indel (str): نوع الجين للـ INDEL
        - geno_imputed (str, optional): مسار ملف البيانات المُستكملة
    
    Returns:
    --------
    None
        Creates {sampleid}_1000sampling.csv file
    """
```

#### مثال الاستخدام / Usage Example
```python
from mpileuptocsv import mpileup_to_csv

# تحويل mpileup إلى CSV
mpileup_to_csv([
    "SAMPLE_001",
    "data/sample.mpileup",
    "data/Allele_rs_hs37d5.csv",
    "AA",
    "data/imputed_data.txt"
])
```

### 3. vcftocsv.py

#### الوصف / Description
تحويل ملفات VCF إلى تنسيق CSV للتحليل.

Converts VCF files to CSV format for analysis.

#### الدوال / Functions

##### `vcf_to_csv(args)`
```python
def vcf_to_csv(args):
    """
    Convert VCF file to CSV format
    
    Parameters:
    -----------
    args : list
        [sampleid, allele_rs, geno_indel, geno_vcf]
        - sampleid (str): معرف العينة
        - allele_rs (str): مسار ملف Allele_rs_hs37d5.csv
        - geno_indel (str): نوع الجين للـ INDEL
        - geno_vcf (str, optional): مسار ملف VCF
    
    Returns:
    --------
    None
        Creates {sampleid}_directCall.csv file
    """
```

#### مثال الاستخدام / Usage Example
```python
from vcftocsv import vcf_to_csv

# تحويل VCF إلى CSV
vcf_to_csv([
    "SAMPLE_001",
    "data/Allele_rs_hs37d5.csv",
    "AA",
    "data/sample.vcf"
])
```

### 4. plotphenodc.py

#### الوصف / Description
إنشاء الرسوم البيانية للعرض الرقمي.

Creates plots for digital display.

#### الدوال / Functions

##### `plot_pheno_dc(args)`
```python
def plot_pheno_dc(args):
    """
    Generate plots for digital display
    
    Parameters:
    -----------
    args : list
        [sample_id]
        - sample_id (str): معرف العينة
    
    Returns:
    --------
    None
        Creates {sample_id}_DC_eye.jpg, {sample_id}_DC_hair.jpg, {sample_id}_DC_skin.jpg
    """
```

#### مثال الاستخدام / Usage Example
```python
from plotphenodc import plot_pheno_dc

# إنشاء الرسوم للعرض الرقمي
plot_pheno_dc(["SAMPLE_001"])
```

### 5. plotphenogl.py

#### الوصف / Description
إنشاء الرسوم البيانية للنشر العلمي.

Creates plots for scientific publication.

#### الدوال / Functions

##### `plot_pheno_gl(args)`
```python
def plot_pheno_gl(args):
    """
    Generate plots for scientific publication
    
    Parameters:
    -----------
    args : list
        [sample_id]
        - sample_id (str): معرف العينة
    
    Returns:
    --------
    None
        Creates {sample_id}_GL_eye.jpg, {sample_id}_GL_hair.jpg, {sample_id}_GL_skin.jpg
    """
```

#### مثال الاستخدام / Usage Example
```python
from plotphenogl import plot_pheno_gl

# إنشاء الرسوم للنشر العلمي
plot_pheno_gl(["SAMPLE_001"])
```

## تنسيقات البيانات / Data Formats

### ملف CSV للعينة / Sample CSV File

يجب أن يحتوي ملف CSV على الأعمدة التالية:

The CSV file must contain the following columns:

```csv
sampleid,PBlueEye,PIntermediateEye,PBrownEye,PBlondHair,PBrownHair,PRedHair,PBlackHair,PLightHair,PDarkHair,PVeryPaleSkin,PPaleSkin,PIntermediateSkin,PDarkSkin,PDarktoBlackSkin
SAMPLE_001,0.15,0.25,0.60,0.20,0.45,0.05,0.30,0.25,0.75,0.10,0.30,0.40,0.15,0.05
```

### ملف Allele_rs_hs37d5.csv

يحتوي على معلومات علامات SNP:

Contains SNP marker information:

```csv
Num,Position,Rs_allele,Strand
1,16:89985753,rs312262906_A,A
2,16:89986091,rs11547464_A,A
...
```

## معالجة الأخطاء / Error Handling

### الأخطاء الشائعة / Common Errors

1. **ملف غير موجود** / **File Not Found**
   ```python
   FileNotFoundError: [Errno 2] No such file or directory: 'sample.csv'
   ```
   **الحل** / **Solution**: تأكد من صحة مسار الملف

2. **تنسيق بيانات خاطئ** / **Invalid Data Format**
   ```python
   KeyError: 'PBlueEye'
   ```
   **الحل** / **Solution**: تأكد من وجود جميع الأعمدة المطلوبة

3. **قيم مفقودة** / **Missing Values**
   ```python
   ValueError: cannot convert float NaN to integer
   ```
   **الحل** / **Solution**: تأكد من عدم وجود قيم مفقودة في البيانات

## أمثلة متقدمة / Advanced Examples

### معالجة متعددة العينات / Batch Processing

```python
import os
import glob
from phenotypicprediction import phenotypic_prediction

def process_multiple_samples(data_directory):
    """
    Process multiple samples in batch
    """
    csv_files = glob.glob(os.path.join(data_directory, "*.csv"))
    
    for csv_file in csv_files:
        sample_id = os.path.basename(csv_file).replace('.csv', '')
        print(f"Processing sample: {sample_id}")
        
        try:
            phenotypic_prediction([sample_id, csv_file])
            print(f"✅ Successfully processed {sample_id}")
        except Exception as e:
            print(f"❌ Error processing {sample_id}: {e}")

# استخدام الدالة
process_multiple_samples("data/samples/")
```

### تخصيص الرسوم البيانية / Customizing Plots

```python
import matplotlib.pyplot as plt
from plotphenodc import plot_pheno_dc

# تخصيص ألوان الرسوم
plt.style.use('seaborn-v0_8')
plot_pheno_dc(["SAMPLE_001"])

# إضافة عنوان مخصص
plt.title("Custom Phenotype Analysis", fontsize=16, fontweight='bold')
plt.show()
```

## الدعم والمساعدة / Support and Help

للحصول على المساعدة أو الإبلاغ عن مشاكل:

For support or to report issues:

- **البريد الإلكتروني** / **Email**: support@genoscene.com
- **المستودع** / **Repository**: https://github.com/your-username/genoscene
- **التوثيق** / **Documentation**: https://genoscene.readthedocs.io

---

**ملاحظة** / **Note**: هذا التوثيق يتم تحديثه باستمرار. يرجى مراجعة أحدث إصدار.

This documentation is continuously updated. Please check for the latest version.
