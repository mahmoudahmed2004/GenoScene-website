# GenoScene - Quick Start Guide

## البدء السريع / Quick Start

### Windows
```bash
# تشغيل الملف
start_genoscene.bat

# أو مباشرة
python run_genoscene.py --demo
```

### Linux/macOS
```bash
# تشغيل الملف
./start_genoscene.sh

# أو مباشرة
python3 run_genoscene.py --demo
```

## الواجهة التفاعلية / Web Interface

افتح `index.html` في متصفحك للوصول إلى الواجهة التفاعلية.

Open `index.html` in your browser to access the interactive interface.

## أمثلة سريعة / Quick Examples

### 1. تشغيل البيانات التجريبية / Run Demo Data
```bash
python run_genoscene.py --demo
```

### 2. فتح الواجهة التفاعلية / Open Web Interface
```bash
python run_genoscene.py --web
```

### 3. تثبيت المكتبات المطلوبة / Install Required Packages
```bash
python run_genoscene.py --install
```

### 4. تحليل بيانات مخصصة / Analyze Custom Data
```bash
python run_genoscene.py SAMPLE_001 data/sample.csv
```

## الملفات المهمة / Important Files

- `index.html` - الواجهة التفاعلية الرئيسية
- `run_genoscene.py` - سكريبت التشغيل الرئيسي
- `src/` - ملفات Python للتحليل
- `data/` - ملفات البيانات المرجعية
- `output/` - نتائج التحليل
- `examples/` - أمثلة الاستخدام

## المساعدة / Help

```bash
python run_genoscene.py --help
```

## المتطلبات / Requirements

- Python 3.7+
- pandas, numpy, matplotlib, scipy

## الدعم / Support

- 📧 Email: maf.bns@gmail.com
- 📚 Documentation: README.md
- 🐛 Issues: GitHub Issues
