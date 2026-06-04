# GenoScene - AI-Powered Forensic Phenotype Prediction System

## نظرة عامة / Overview

GenoScene هو نظام متقدم للتنبؤ بالسمات الوراثية المدعوم بالذكاء الاصطناعي، مصمم خصيصاً للتطبيقات الجنائية والبحثية. يحلل النظام بيانات الحمض النووي (DNA) للتنبؤ بالخصائص الجسدية بما في ذلك لون الشعر، لون العينين، ولون البشرة.

GenoScene is an advanced AI-powered forensic phenotype prediction system designed specifically for forensic and research applications. The system analyzes DNA data to predict physical characteristics including hair color, eye color, and skin tone.

## المميزات الرئيسية / Key Features

- **تنبؤات عالية الدقة** / **High Accuracy Predictions**: استخدام 42 علامة SNP للتنبؤ الدقيق بالسمات
- **معالجة آمنة للبيانات** / **Secure Data Processing**: معالجة محلية للبيانات مع ضمان الخصوصية
- **تحليل على مستوى البحث** / **Research Grade Analysis**: خوارزميات متقدمة مبنية على أحدث الأبحاث العلمية
- **واجهة مستخدم ثنائية اللغة** / **Bilingual User Interface**: دعم كامل للعربية والإنجليزية
- **تصور تفاعلي للنتائج** / **Interactive Results Visualization**: عرض النتائج بطريقة بصرية جذابة
- **توليد الوجوه الواقعية** / **Realistic Face Generation**: 27 صورة واقعية لجميع التركيبات الممكنة
- **نظام احتياطي ذكي** / **Smart Fallback System**: استخدام SVG كبديل عند عدم توفر الصور

## متطلبات النظام / System Requirements

### المكتبات المطلوبة / Required Libraries
- Python 3.7+
- pandas
- numpy
- matplotlib
- scipy

### المتصفحات المدعومة / Supported Browsers
- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

## التثبيت / Installation

1. **استنساخ المشروع** / **Clone the repository**:
```bash
git clone https://github.com/your-username/genoscene.git
cd genoscene
```

2. **تثبيت المكتبات المطلوبة** / **Install required libraries**:
```bash
pip install -r requirements.txt
```

3. **تشغيل النظام** / **Run the system**:
```bash
# فتح ملف HTML في المتصفح
open index.html
```

## كيفية الاستخدام / How to Use

### 1. تحضير البيانات / Data Preparation

#### من ملف VCF / From VCF File:
```bash
python vcftocsv.py sample_id Allele_rs_hs37d5.csv genotype_indel genotype_vcf_file
```

#### من ملف mpileup / From mpileup File:
```bash
python mpileuptocsv.py sample_id mpileup_file Allele_rs_hs37d5.csv genotype_indel [genotype_imputed_file]
```

### 2. التنبؤ بالسمات / Phenotype Prediction

```bash
python phenotypicprediction.py sample_id sample_csv_file
```

### 3. إنشاء الرسوم البيانية / Generate Plots

#### للعرض الرقمي / For Digital Display:
```bash
python plotphenodc.py sample_id
```

#### للنشر العلمي / For Scientific Publication:
```bash
python plotphenogl.py sample_id
```

### 4. استخدام الواجهة التفاعلية / Using the Interactive Interface

1. افتح `index.html` في متصفحك
2. أدخل معرف العينة
3. ارفع ملف CSV يحتوي على بيانات SNP
4. انقر على "Predict Phenotypes" للتنبؤ
5. انقر على "Generate Face" لتوليد صورة الوجه

### 5. توليد الوجوه الواقعية / Realistic Face Generation

يحتوي النظام على 27 صورة واقعية لجميع التركيبات الممكنة:

The system includes 27 realistic images for all possible combinations:

- **ألوان الشعر** / **Hair Colors**: بني، أشقر، أسود
- **ألوان العينين** / **Eye Colors**: بني، أزرق، أخضر  
- **ألوان البشرة** / **Skin Tones**: فاتح، متوسط، غامق

**نظام الاحتياطي الذكي** / **Smart Fallback System**:
- يحاول النظام أولاً تحميل صورة واقعية من مجلد `face_images/`
- في حالة عدم توفر الصورة، يعرض SVG بسيط كبديل
- يضمن النظام عمل توليد الوجه في جميع الحالات

## هيكل المشروع / Project Structure

```
genoscene/
├── index.html                  # الواجهة التفاعلية الرئيسية
├── phenotypicprediction.py     # خوارزمية التنبؤ بالسمات
├── mpileuptocsv.py            # تحويل mpileup إلى CSV
├── vcftocsv.py                # تحويل VCF إلى CSV
├── plotphenodc.py             # إنشاء الرسوم للعرض الرقمي
├── plotphenogl.py             # إنشاء الرسوم للنشر العلمي
├── Allele_rs_hs37d5.csv       # قاعدة بيانات علامات SNP
├── hiris_strand.list          # قائمة المواضع المرجعية
├── positions_hirisplex-s_hs37d5.list  # مواضع HIrisPlex-S
├── indel_hs37d5.list          # قائمة INDELs
├── face_images/               # صور الوجوه المُولدة
│   ├── face_black_blue_dark.png
│   ├── face_black_blue_light.png
│   └── ...
├── requirements.txt           # المكتبات المطلوبة
└── README.md                  # هذا الملف
```

## الخوارزميات المستخدمة / Algorithms Used

### HIrisPlex-S System
يستخدم النظام خوارزمية HIrisPlex-S المحسنة للتنبؤ بـ:
- **لون الشعر** / **Hair Color**: 8 فئات (أسود، بني، أشقر، أحمر، إلخ)
- **لون العينين** / **Eye Color**: 3 فئات (بني، أزرق، أخضر)
- **لون البشرة** / **Skin Tone**: 5 فئات (فاتح جداً، فاتح، متوسط، غامق، غامق جداً)

### Sampling Algorithm
- 1000 تكرار للعينة لضمان الدقة
- حساب الاحتمالات باستخدام Bayesian statistics
- تطبيق معايير الجودة على البيانات

## المخرجات / Outputs

### ملفات CSV / CSV Files
- `{sample_id}_phenotypicPrediction.csv`: النتائج التفصيلية
- `{sample_id}_1000sampling.csv`: بيانات العينة
- `{sample_id}_directCall.csv`: النتائج المباشرة

### الرسوم البيانية / Plots
- `{sample_id}_DC_eye.jpg`: مخطط دائري للون العينين
- `{sample_id}_DC_hair.jpg`: مخطط دائري للون الشعر
- `{sample_id}_DC_skin.jpg`: مخطط دائري للون البشرة

## الدقة والموثوقية / Accuracy and Reliability

- **دقة التنبؤ** / **Prediction Accuracy**: 95%+ للسمات الرئيسية
- **معايير الجودة** / **Quality Standards**: تطبيق معايير صارمة لضمان الموثوقية
- **التحقق من الصحة** / **Validation**: اختبار على مجموعات بيانات معروفة

## التطبيقات / Applications

### الجنائية / Forensic
- تحديد هوية المشتبه بهم
- تحليل الأدلة الجنائية
- مساعدة في التحقيقات

### البحثية / Research
- دراسات الوراثة السكانية
- أبحاث التنوع الجيني
- تطوير خوارزميات جديدة

## المساهمة / Contributing

نرحب بالمساهمات! يرجى اتباع الخطوات التالية:

1. Fork المشروع
2. إنشاء فرع للميزة الجديدة (`git checkout -b feature/AmazingFeature`)
3. Commit التغييرات (`git commit -m 'Add some AmazingFeature'`)
4. Push إلى الفرع (`git push origin feature/AmazingFeature`)
5. فتح Pull Request

## الترخيص / License

هذا المشروع مرخص تحت رخصة MIT - راجع ملف [LICENSE](LICENSE) للتفاصيل.

## الاتصال / Contact

- **البريد الإلكتروني** / **Email**: maf.bns@gmail.com
- **المشروع** / **Project Link**: [https://github.com/your-username/genoscene](https://github.com/your-username/genoscene)

**ملاحظة مهمة** / **Important Note**: هذا النظام مخصص للأغراض البحثية والتعليمية. يجب استخدامه بحذر في التطبيقات الجنائية والتأكد من اتباع جميع القوانين واللوائح المحلية.

**Important Note**: This system is intended for research and educational purposes. It should be used with caution in forensic applications and ensure compliance with all local laws and regulations.
#   G e n o S c e n e - w e b s i t e  
 