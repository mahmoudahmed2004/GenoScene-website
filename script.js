const state = {
  lang: 'en',
  probs: {
    hair: {brown: 0.4, blonde: 0.3, black: 0.3}, 
    eye: {brown: 0.5, blue: 0.3, green: 0.2}, 
    skin: {light: 0.4, medium: 0.4, dark: 0.2}
  },
  hasPrediction: false
};

// API key for Stable Diffusion text-to-image service. Replace with your
// actual API key if you have signed up for a provider such as
// stablediffusionapi.com. If left blank, the app will fallback to a
// simple SVG illustration instead of generating a photorealistic face.
// Set your ModelsLab API key here. This key is used to authenticate
// requests to the Stable Diffusion text-to-image endpoint provided
// by ModelsLab. Do not expose your personal key in publicly shared
// repositories.
// const STABLE_DIFFUSION_API_KEY = 'UURNjd1ycZ5A1sHkZDrm49lwGQWCrvK0h2sRTr3fpDsD1ez5O3CqDfyBUtKC';

document.addEventListener('DOMContentLoaded', function() {

  document.getElementById('toggleLangBtn').addEventListener('click', toggleLang);
  document.getElementById('loadDemoBtn').addEventListener('click', loadDemo);
  document.getElementById('predictBtn').addEventListener('click', predict);
  document.getElementById('generateFaceBtn').addEventListener('click', generateFace);
  document.getElementById('resetBtn').addEventListener('click', resetApp);
  
  document.getElementById('vcfFile').addEventListener('change', handleFileSelect);
  
  // التهيئة الأولية
  initApp();
});

// دالة لمزامنة النصوص بناءً على اللغة المحددة
function tSync(){
  document.querySelectorAll('[data-en]').forEach(el => {
    if (el.getAttribute('data-en') && el.getAttribute('data-ar')) {
      el.textContent = state.lang === 'en' ? el.getAttribute('data-en') : el.getAttribute('data-ar');
    }
  });
  document.getElementById('langLabel').textContent = state.lang.toUpperCase();
  
  // تحديث الملصقات الديناميكية
  updateDynamicLabels();
}

// دالة لتبديل اللغة بين الإنجليزية والعربية
function toggleLang(){
  state.lang = state.lang === 'en' ? 'ar' : 'en';
  document.documentElement.dir = state.lang === 'ar' ? 'rtl' : 'ltr';
  document.documentElement.lang = state.lang;
  tSync();
}

// دالة للتعامل مع اختيار الملفات
function handleFileSelect(event) {
  const fileInput = event.target;
  const fileInfo = document.getElementById(fileInput.id + 'Info');
  
  if (fileInput.files.length > 0) {
    const file = fileInput.files[0];
    fileInfo.textContent = `${file.name} (${formatFileSize(file.size)})`;
    fileInfo.style.color = '#22d3ee';
    // If the selected file is a CSV, parse it to compute phenotype probabilities
    const nameLower = file.name.toLowerCase();
    if (nameLower.endsWith('.csv')) {
      parseCSVFile(file);
    } else {
      // Clear previous probabilities and inform the user to upload a CSV for SNP analysis
      state.hasPrediction = false;
    }
  } else {
    fileInfo.textContent = '';
  }
}

// دالة لتنسيق حجم الملف
function formatFileSize(bytes) {
  if (bytes < 1024) return bytes + ' bytes';
  else if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
  else return (bytes / 1048576).toFixed(1) + ' MB';
}

/**
 * Compute phenotype probabilities based on a sample's SNP genotype data. The
 * sample argument is an object mapping SNP column names (e.g.
 * 'rs12913832_T') to genotype strings (e.g. 'AA', 'AG'). For
 * demonstration purposes we implement simplified heuristics derived from
 * published associations in the HIrisPlex-S system. These heuristics
 * approximate the probability of hair colour (brown, blonde, black), eye
 * colour (brown, blue, green) and skin tone (light, medium, dark).
 *
 * @param {Object} sample - key/value pairs of SNP column and genotype
 * @returns {Object} An object with `hair`, `eye` and `skin` probability
 *   distributions, each summing to 1.
 */
function computePhenotypeProbs(sample) {
  // Eye colour heuristics
  let eyeBlue = 1, eyeBrown = 1, eyeGreen = 1;
  // rs12913832_T strongly associated with blue eyes
  if (sample['rs12913832_T']) {
    eyeBlue += 3;
  } else {
    eyeBrown += 2;
  }
  // rs12896399_T and rs1393350_T contribute to green/blue
  if (sample['rs12896399_T']) {
    eyeGreen += 1;
  }
  if (sample['rs1393350_T']) {
    eyeBlue += 0.5;
  }
  const eyeSum = eyeBlue + eyeBrown + eyeGreen;
  const eye = {
    blue: eyeBlue / eyeSum,
    brown: eyeBrown / eyeSum,
    green: eyeGreen / eyeSum
  };

  // Hair colour heuristics
  let hairBlonde = 1, hairBrown = 1, hairBlack = 1;
  // Alleles contributing to blonde hair
  if (sample['rs12821256_G']) hairBlonde += 1;
  if (sample['rs12203592_T']) hairBlonde += 0.8;
  if (sample['rs1393350_T']) hairBlonde += 0.5;
  if (sample['rs683_G']) hairBlonde += 0.3;
  // Alleles associated with darker hair
  if (sample['rs16891982_C']) hairBrown += 0.5;
  // MC1R variants associated with red/dark hair
  if (sample['rs1805008_T'] || sample['rs1805005_T'] || sample['rs1805006_A'] || sample['rs1805007_T'] || sample['rs1805009_C']) {
    hairBrown += 1;
  }
  const hairSum = hairBlonde + hairBrown + hairBlack;
  const hair = {
    blonde: hairBlonde / hairSum,
    brown: hairBrown / hairSum,
    black: hairBlack / hairSum
  };

  // Skin tone heuristics
  let lightScore = 1, darkScore = 1;
  // rs1426654_G: ancestral allele associated with darker skin
  if (sample['rs1426654_G']) {
    darkScore += 2;
  } else {
    lightScore += 1;
  }
  // rs16891982_C (SLC45A2) associated with lighter skin
  if (sample['rs16891982_C']) {
    lightScore += 2;
  } else {
    darkScore += 1;
  }
  // rs6119471_C and rs1545397_T also associated with lighter skin
  if (sample['rs6119471_C']) {
    lightScore += 1;
  } else {
    darkScore += 0.5;
  }
  if (sample['rs1545397_T']) {
    lightScore += 1;
  } else {
    darkScore += 0.5;
  }
  const skinSum = lightScore + darkScore;
  let skinLight = lightScore / skinSum;
  let skinDark = darkScore / skinSum;
  let skinMedium = 1 - skinLight - skinDark;
  if (skinMedium < 0) skinMedium = 0;
  const skin = {
    light: skinLight,
    medium: skinMedium,
    dark: skinDark
  };
  return { hair, eye, skin };
}

/**
 * Parse a CSV file containing SNP genotype data. The CSV must have a
 * header row and at least one data row. Column names should match the
 * SNP identifiers used in the HIrisPlex-S system (e.g. 'rs12913832_T').
 * The first data row will be used to compute phenotype probabilities.
 *
 * When parsing succeeds, the computed probabilities are stored in
 * `state.probs` and the UI is updated via `render()`. The generate face
 * button is enabled and `state.hasPrediction` is set to true. If
 * parsing fails, an alert is shown.
 *
 * @param {File} file - The uploaded CSV file
 */
function parseCSVFile(file) {
  const reader = new FileReader();
  reader.onload = function(e) {
    const text = e.target.result.trim();
    const lines = text.split(/\r?\n/);
    if (lines.length < 2) {
      alert(state.lang === 'en' ? 'CSV file must contain at least one data row.' : 'يجب أن يحتوي ملف CSV على صف بيانات واحد على الأقل.');
      return;
    }
    const header = lines[0].split(',');
    const row = lines[1].split(',');
    const sample = {};
    for (let i = 0; i < header.length; i++) {
      const key = header[i].trim();
      const value = row[i] ? row[i].trim() : '';
      if (value && value !== 'NA' && value !== '0') {
        sample[key] = value;
      }
    }
    const probs = computePhenotypeProbs(sample);
    state.probs = probs;
    state.hasPrediction = true;
    // Enable generate face button
    document.getElementById('generateFaceBtn').disabled = false;
    render();
  };
  reader.onerror = function() {
    alert(state.lang === 'en' ? 'Failed to read the CSV file.' : 'فشل في قراءة ملف CSV');
  };
  reader.readAsText(file);
}

// دالة لإظهار التحميل
function showLoading() {
  document.getElementById('processingOverlay').classList.remove('hidden');
}

// دالة لإخفاء التحميل
function hideLoading() {
  document.getElementById('processingOverlay').classList.add('hidden');
}

// دالة لتحميل بيانات تجريبية
function loadDemo(){
  document.getElementById('sampleId').value = 'DEMO-FTDNA-001';
  // Show a placeholder file name for demo SNP CSV
  document.getElementById('vcfFileInfo').textContent = 'demo_snps.csv (0.1 MB)';
  
  // إعداد احتمالات تجريبية
  state.probs = {
    hair: {brown: 0.62, blonde: 0.18, black: 0.20},
    eye: {brown: 0.55, blue: 0.25, green: 0.20},
    skin: {light: 0.35, medium: 0.45, dark: 0.20}
  };
  // Mark that we have a prediction from demo data
  state.hasPrediction = true;
  // تمكين زر توليد الوجه
  document.getElementById('generateFaceBtn').disabled = false;
  
  // إعادة تعيين عرض الوجه
  document.getElementById('generatedFace').classList.add('hidden');
  document.getElementById('faceSvg').classList.add('hidden');
  document.getElementById('facePlaceholder').classList.remove('hidden');
  
  render();
}

// دالة للتنبؤ بالسمات
function predict(){
  // التحقق من وجود بيانات
  const sampleId = document.getElementById('sampleId').value;
  if (!sampleId) {
    alert(state.lang === 'en' ? 'Please enter a sample ID' : 'يرجى إدخال معرف العينة');
    return;
  }
  
  // If no phenotype probabilities computed from a CSV or demo, alert the user
  if (!state.hasPrediction) {
    alert(state.lang === 'en' ? 'Please upload a SNP CSV file or load demo/random data first.' : 'يرجى رفع ملف CSV يحتوي على SNPs أو تحميل بيانات تجريبية/عشوائية أولاً.');
    return;
  }
  showLoading();
  // Simulate a short processing delay
  setTimeout(() => {
    // Save current state if needed
    saveState();
    render();
    hideLoading();
  }, 800);
}

// دالة لتوليد الوجه
async function generateFace() {
  if (!state.hasPrediction) {
    alert(state.lang === 'en'
      ? 'Please predict phenotypes first'
      : 'يرجى تنبؤ السمات أولاً');
    return;
  }
  showLoading();
  
  // تحديد السمة ذات الاحتمال الأعلى لكل خاصية
  const pickMax = (obj) => Object.entries(obj).sort((a, b) => b[1] - a[1])[0];
  const hair = pickMax(state.probs.hair)[0];
  const eye = pickMax(state.probs.eye)[0];
  const skin = pickMax(state.probs.skin)[0];

  const faceImg = document.getElementById('generatedFace');
  const facePlaceholder = document.getElementById('facePlaceholder');
  const faceSvg = document.getElementById('faceSvg');

  // إخفاء العناصر السابقة
  faceImg.classList.add('hidden');
  faceSvg.classList.add('hidden');
  facePlaceholder.classList.add('hidden');

  // محاولة تحميل صورة واقعية من الصور المسبقة التخزين
  const filePath = `face_images/face_${hair}_${eye}_${skin}.png`;
  
  // إعداد معالجات الأحداث
  faceImg.onload = () => {
    // بمجرد تحميل الصورة بنجاح، إظهار الصورة وإخفاء العناصر الأخرى
    faceSvg.classList.add('hidden');
    facePlaceholder.classList.add('hidden');
    faceImg.classList.remove('hidden');
    hideLoading();
    
    // تحديث ملخص الصورة الرمزية
    updateAvatarSummary(hair, eye, skin);
  };
  
  faceImg.onerror = () => {
    // إذا فشل تحميل الصورة (غير متوفرة)، عد إلى الوجه البسيط
    console.log(`Image not found: ${filePath}, falling back to SVG`);
    renderSimpleFace(hair, eye, skin);
    hideLoading();
  };
  
  // ضبط مسار الصورة؛ سيؤدي هذا إلى تشغيل onload أو onerror
  faceImg.src = filePath;
}

// رسم وجه بسيط على أساس السمات (الطريقة المستخدمة سابقًا)
function renderSimpleFace(hair, eye, skin) {
  const faceImg = document.getElementById('generatedFace');
  const facePlaceholder = document.getElementById('facePlaceholder');
  const faceSvg = document.getElementById('faceSvg');
  
  const hairColorMap = {
    brown: '#8b4513',
    blonde: '#d2b48c',
    black: '#2f2f2f'
  };
  const eyeColorMap = {
    brown: '#4e3629',
    blue: '#0072b5',
    green: '#2e8b57'
  };
  const skinColorMap = {
    light: '#f4d1b6',
    medium: '#d1a679',
    dark: '#8d5524'
  };
  
  // تحديث ألوان SVG
  document.getElementById('svgHair').setAttribute('fill', hairColorMap[hair]);
  document.getElementById('svgHead').setAttribute('fill', skinColorMap[skin]);
  document.getElementById('svgEyeLeft').setAttribute('fill', eyeColorMap[eye]);
  document.getElementById('svgEyeRight').setAttribute('fill', eyeColorMap[eye]);
  
  // إخفاء الصورة والنص البديل وإظهار SVG
  faceImg.classList.add('hidden');
  facePlaceholder.classList.add('hidden');
  faceSvg.classList.remove('hidden');
  
  // تحديث ملخص الصورة الرمزية
  updateAvatarSummary(hair, eye, skin);
}

// دالة لتحديث ملخص الصورة الرمزية
function updateAvatarSummary(hair, eye, skin) {
  const hairLabels = {
    'brown': state.lang === 'en' ? 'Brown' : 'بني', 
    'blonde': state.lang === 'en' ? 'Blonde' : 'أشقر', 
    'black': state.lang === 'en' ? 'Black' : 'أسود'
  };
  const eyeLabels = {
    'brown': state.lang === 'en' ? 'Brown' : 'بني', 
    'blue': state.lang === 'en' ? 'Blue' : 'أزرق', 
    'green': state.lang === 'en' ? 'Green' : 'أخضر'
  };
  const skinLabels = {
    'light': state.lang === 'en' ? 'Light' : 'فاتح', 
    'medium': state.lang === 'en' ? 'Medium' : 'متوسط', 
    'dark': state.lang === 'en' ? 'Dark' : 'غامق'
  };
  
  const summary = state.lang === 'en' 
    ? `Hair: ${hairLabels[hair]}, Eyes: ${eyeLabels[eye]}, Skin: ${skinLabels[skin]}`
    : `الشعر: ${hairLabels[hair]}, العينان: ${eyeLabels[eye]}, البشرة: ${skinLabels[skin]}`;
  
  document.getElementById('avatarSummary').textContent = summary;
}

// دالة لتحويل القيمة العشرية إلى نسبة مئوية
function pct(x) { 
  return Math.round(x * 100); 
}

// دالة لعرض البيانات على المخططات والنصوص
function render() {
  const hairP = Math.max(state.probs.hair.brown, state.probs.hair.blonde, state.probs.hair.black);
  const eyeP = Math.max(state.probs.eye.brown, state.probs.eye.blue, state.probs.eye.green);
  const skinP = Math.max(state.probs.skin.light, state.probs.skin.medium, state.probs.skin.dark);

  const labelHair = state.lang === 'en' ? 'Hair' : 'الشعر';
  const labelEye = state.lang === 'en' ? 'Eyes' : 'العينان';
  const labelSkin = state.lang === 'en' ? 'Skin' : 'البشرة';

  const barH = document.getElementById('barHair');
  const barE = document.getElementById('barEye');
  const barS = document.getElementById('barSkin');
  
  barH.style.height = (10 + hairP * 90) + '%';
  barE.style.height = (10 + eyeP * 90) + '%';
  barS.style.height = (10 + skinP * 90) + '%';
  
  barH.setAttribute('data-label', labelHair);
  barE.setAttribute('data-label', labelEye);
  barS.setAttribute('data-label', labelSkin);
  
  barH.innerHTML = '<span>' + pct(hairP) + '%</span>';
  barE.innerHTML = '<span>' + pct(eyeP) + '%</span>';
  barS.innerHTML = '<span>' + pct(skinP) + '%</span>';

  const pickMax = (obj) => Object.entries(obj).sort((a, b) => b[1] - a[1])[0];
  const h = pickMax(state.probs.hair);
  const e = pickMax(state.probs.eye);
  const s = pickMax(state.probs.skin);
  
  const hairLabels = {
    'brown': state.lang === 'en' ? 'brown' : 'بني', 
    'blonde': state.lang === 'en' ? 'blonde' : 'أشقر', 
    'black': state.lang === 'en' ? 'black' : 'أسود'
  };
  const eyeLabels = {
    'brown': state.lang === 'en' ? 'brown' : 'بني', 
    'blue': state.lang === 'en' ? 'blue' : 'أزرق', 
    'green': state.lang === 'en' ? 'green' : 'أخضر'
  };
  const skinLabels = {
    'light': state.lang === 'en' ? 'light' : 'فاتح', 
    'medium': state.lang === 'en' ? 'medium' : 'متوسط', 
    'dark': state.lang === 'en' ? 'dark' : 'غامق'
  };
  
  document.getElementById('hairTxt').textContent =
    (state.lang === 'en' ? 'Hair: ' : 'الشعر: ') + hairLabels[h[0]] + ' (' + pct(h[1]) + '%)';
  document.getElementById('eyeTxt').textContent =
    (state.lang === 'en' ? 'Eyes: ' : 'العينان: ') + eyeLabels[e[0]] + ' (' + pct(e[1]) + '%)';
  document.getElementById('skinTxt').textContent =
    (state.lang === 'en' ? 'Skin: ' : 'البشرة: ') + skinLabels[s[0]] + ' (' + pct(s[1]) + '%)';

  // تحديث التفاصيل
  updateDetails();
  
  tSync();
}

// دالة لتحديث التفاصيل
function updateDetails() {
  const hairDetails = document.getElementById('hairDetails');
  const eyeDetails = document.getElementById('eyeDetails');
  const skinDetails = document.getElementById('skinDetails');
  
  hairDetails.innerHTML = generateDetailHTML(state.probs.hair, state.lang, 'hair');
  eyeDetails.innerHTML = generateDetailHTML(state.probs.eye, state.lang, 'eye');
  skinDetails.innerHTML = generateDetailHTML(state.probs.skin, state.lang, 'skin');
}

// دالة لإنشاء HTML للتفاصيل
function generateDetailHTML(probs, lang, type) {
  const labels = {
    hair: {
      brown: lang === 'en' ? 'Brown' : 'بني',
      blonde: lang === 'en' ? 'Blonde' : 'أشقر', 
      black: lang === 'en' ? 'Black' : 'أسود'
    },
    eye: {
      brown: lang === 'en' ? 'Brown' : 'بني',
      blue: lang === 'en' ? 'Blue' : 'أزرق', 
      green: lang === 'en' ? 'Green' : 'أخضر'
    },
    skin: {
      light: lang === 'en' ? 'Light' : 'فاتح',
      medium: lang === 'en' ? 'Medium' : 'متوسط', 
      dark: lang === 'en' ? 'Dark' : 'غامق'
    }
  };
  
  let html = '';
  for (const [key, value] of Object.entries(probs)) {
    const width = value * 100;
    html += `
      <div class="probability-bar">
        <div class="label">
          <span>${labels[type][key]}</span>
          <span>${pct(value)}%</span>
        </div>
        <div class="bar-container">
          <div class="bar-fill" style="width: ${width}%"></div>
        </div>
      </div>
    `;
  }
  return html;
}

// دالة لتحديث التسميات الديناميكية
function updateDynamicLabels() {
  if (state.hasPrediction) {
    const pickMax = (obj) => Object.entries(obj).sort((a, b) => b[1] - a[1])[0];
    const hair = pickMax(state.probs.hair)[0];
    const eye = pickMax(state.probs.eye)[0];
    const skin = pickMax(state.probs.skin)[0];
    
    updateAvatarSummary(hair, eye, skin);
  }
}

// دالة لحفظ الحالة الحالية
function saveState() {
  // يمكن استخدامها لحفظ الحالة في localStorage إذا لزم الأمر
}

// دالة لإعادة تعيين التطبيق
function resetApp() {
  document.getElementById('sampleId').value = '';
  document.getElementById('vcfFile').value = '';
  // Clear SNP file info
  document.getElementById('vcfFileInfo').textContent = '';
  
  // إعادة تعيين عرض الوجه
  document.getElementById('generatedFace').classList.add('hidden');
  document.getElementById('faceSvg').classList.add('hidden');
  document.getElementById('facePlaceholder').classList.remove('hidden');
  
  document.getElementById('generateFaceBtn').disabled = true;
  
  state.probs = {
    hair: {brown: 0.4, blonde: 0.3, black: 0.3},
    eye: {brown: 0.5, blue: 0.3, green: 0.2},
    skin: {light: 0.4, medium: 0.4, dark: 0.2}
  };
  state.hasPrediction = false;
  
  document.getElementById('hairTxt').textContent = state.lang === 'en' ? 'Hair: —' : 'الشعر: —';
  document.getElementById('eyeTxt').textContent = state.lang === 'en' ? 'Eyes: —' : 'العينان: —';
  document.getElementById('skinTxt').textContent = state.lang === 'en' ? 'Skin: —' : 'البشرة: —';
  
  document.getElementById('avatarSummary').textContent = state.lang === 'en' ? 'No predictions yet' : 'لا توجد تنبؤات بعد';
  
  document.getElementById('barHair').style.height = '30%';
  document.getElementById('barEye').style.height = '30%';
  document.getElementById('barSkin').style.height = '30%';
  
  document.getElementById('barHair').innerHTML = '';
  document.getElementById('barEye').innerHTML = '';
  document.getElementById('barSkin').innerHTML = '';
  
  document.getElementById('hairDetails').innerHTML = '';
  document.getElementById('eyeDetails').innerHTML = '';
  document.getElementById('skinDetails').innerHTML = '';
}

// دالة لتهيئة التطبيق
function initApp() {
  render();
  tSync();
}

// Functions from index.html
function startAnalysis() {
  // Scroll to the main application section
  document.querySelector('.wrap').scrollIntoView({ 
    behavior: 'smooth' 
  });
}

function learnMore() {
  // Scroll to the about section
  document.querySelector('.about-section').scrollIntoView({ 
    behavior: 'smooth' 
  });
}

function goToApp() {
  // Scroll to the main application section
  document.querySelector('.wrap').scrollIntoView({ 
    behavior: 'smooth' 
  });
}
