const state = {
  lang: 'en',
  probs: {
    hair: {blonde: 0.25, brown: 0.25, red: 0.25, black: 0.25},
    eye: {blue: 0.34, intermediate: 0.33, brown: 0.33},
    skin: {veryPale: 0.2, pale: 0.2, intermediate: 0.2, dark: 0.2, darkToBlack: 0.2}
  },
  hasPrediction: false,
  uploadedFile: null,
  modelMeta: null
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
    const nameLower = file.name.toLowerCase();
    if (nameLower.endsWith('.csv')) {
      state.uploadedFile = file;
      state.hasPrediction = false;
      state.modelMeta = null;
      document.getElementById('generateFaceBtn').disabled = true;
      clearPredictionDisplay();
      fileInfo.textContent = `${file.name} (${formatFileSize(file.size)}) — ready for AI analysis`;
      fileInfo.style.color = '#22d3ee';
    } else {
      state.uploadedFile = null;
      state.hasPrediction = false;
      document.getElementById('generateFaceBtn').disabled = true;
      clearPredictionDisplay();
      fileInfo.textContent = state.lang === 'en' ? 'Please select a CSV file.' : 'يرجى اختيار ملف CSV.';
      fileInfo.style.color = '#fb7185';
    }
  } else {
    state.uploadedFile = null;
    state.hasPrediction = false;
    document.getElementById('generateFaceBtn').disabled = true;
    clearPredictionDisplay();
    fileInfo.textContent = '';
  }
}

// دالة لتنسيق حجم الملف
function formatFileSize(bytes) {
  if (bytes < 1024) return bytes + ' bytes';
  else if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
  else return (bytes / 1048576).toFixed(1) + ' MB';
}

function parseCSVLine(line) {
  const values = [];
  let value = '';
  let quoted = false;

  for (let index = 0; index < line.length; index += 1) {
    const character = line[index];
    if (character === '"' && line[index + 1] === '"') {
      value += '"';
      index += 1;
    } else if (character === '"') {
      quoted = !quoted;
    } else if (character === ',' && !quoted) {
      values.push(value.trim());
      value = '';
    } else {
      value += character;
    }
  }
  values.push(value.trim());
  return values;
}

function parseCSVText(text) {
  const lines = text.replace(/^\uFEFF/, '').split(/\r?\n/).filter(line => line.trim());
  if (lines.length < 2) {
    throw new Error(state.lang === 'en'
      ? 'CSV file must contain a header and at least one data row.'
      : 'يجب أن يحتوي ملف CSV على عناوين وصف بيانات واحد على الأقل.');
  }

  const headers = parseCSVLine(lines[0]);
  const snpCount = headers.filter(header => header.startsWith('rs')).length;
  if (snpCount === 0) {
    throw new Error(state.lang === 'en'
      ? 'No SNP columns were found. Expected columns such as rs12913832_T.'
      : 'لم يتم العثور على أعمدة SNP مثل rs12913832_T.');
  }

  return lines.slice(1, 26).map(line => {
    const values = parseCSVLine(line);
    return Object.fromEntries(headers.map((header, index) => [header, values[index] ?? '']));
  });
}

// دالة لإظهار التحميل
function showLoading() {
  document.getElementById('processingOverlay').classList.remove('hidden');
}

// دالة لإخفاء التحميل
function hideLoading() {
  document.getElementById('processingOverlay').classList.add('hidden');
}

function clearPredictionDisplay() {
  document.getElementById('generatedFace').classList.add('hidden');
  document.getElementById('faceSvg').classList.add('hidden');
  document.getElementById('facePlaceholder').classList.remove('hidden');
  document.getElementById('avatarSummary').textContent =
    state.lang === 'en' ? 'No predictions yet' : 'لا توجد تنبؤات بعد';

  document.getElementById('hairTxt').textContent = state.lang === 'en' ? 'Hair: —' : 'الشعر: —';
  document.getElementById('eyeTxt').textContent = state.lang === 'en' ? 'Eyes: —' : 'العينان: —';
  document.getElementById('skinTxt').textContent = state.lang === 'en' ? 'Skin: —' : 'البشرة: —';

  ['Hair', 'Eye', 'Skin'].forEach(trait => {
    const bar = document.getElementById(`bar${trait}`);
    bar.style.height = '30%';
    bar.innerHTML = '';
    document.getElementById(`${trait.toLowerCase()}Details`).innerHTML = '';
  });
}

// دالة لتحميل بيانات تجريبية
function loadDemo(){
  document.getElementById('sampleId').value = 'DEMO-FTDNA-001';
  // Show a placeholder file name for demo SNP CSV
  document.getElementById('vcfFileInfo').textContent = 'demo_snps.csv (0.1 MB)';
  
  // إعداد احتمالات تجريبية
  state.probs = {
    hair: {blonde: 0.18, brown: 0.56, red: 0.06, black: 0.20},
    eye: {blue: 0.25, intermediate: 0.20, brown: 0.55},
    skin: {veryPale: 0.08, pale: 0.27, intermediate: 0.45, dark: 0.15, darkToBlack: 0.05}
  };
  state.uploadedFile = null;
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
async function predict(){
  // التحقق من وجود بيانات
  const sampleId = document.getElementById('sampleId').value;
  if (!sampleId) {
    alert(state.lang === 'en' ? 'Please enter a sample ID' : 'يرجى إدخال معرف العينة');
    return;
  }
  
  if (!state.uploadedFile && !state.hasPrediction) {
    alert(state.lang === 'en' ? 'Please upload a SNP CSV file or load demo/random data first.' : 'يرجى رفع ملف CSV يحتوي على SNPs أو تحميل بيانات تجريبية/عشوائية أولاً.');
    return;
  }

  if (!state.uploadedFile && state.hasPrediction) {
    render();
    return;
  }

  showLoading();
  try {
    const samples = parseCSVText(await state.uploadedFile.text());
    const response = await fetch('/api/analyze', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({sample_id: sampleId, samples})
    });
    const payload = await response.json();
    if (!response.ok || !payload.success) {
      throw new Error(payload.error || 'AI analysis failed.');
    }

    state.probs = payload.results[0].probabilities;
    state.modelMeta = payload.model;
    state.hasPrediction = true;
    document.getElementById('generateFaceBtn').disabled = false;
    document.getElementById('vcfFileInfo').textContent =
      `${state.uploadedFile.name} — ${payload.count} sample${payload.count === 1 ? '' : 's'} analyzed by AI`;
    saveState();
    render();
  } catch (error) {
    console.error(error);
    alert(state.lang === 'en'
      ? `Could not analyze this file: ${error.message}`
      : `تعذر تحليل الملف: ${error.message}`);
  } finally {
    hideLoading();
  }
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

  // Match the detailed model classes to the simplified pre-generated image set.
  const imageEye = eye === 'intermediate' ? 'green' : eye;
  const imageSkin = ['veryPale', 'pale'].includes(skin)
    ? 'light'
    : skin === 'intermediate' ? 'medium' : 'dark';
  const filePath = `face_images/face_${hair}_${imageEye}_${imageSkin}.png`;
  
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
    red: '#a63d24',
    black: '#2f2f2f'
  };
  const eyeColorMap = {
    brown: '#4e3629',
    blue: '#0072b5',
    intermediate: '#708238'
  };
  const skinColorMap = {
    veryPale: '#fae1d2',
    pale: '#f4d1b6',
    intermediate: '#d1a679',
    dark: '#9a6742',
    darkToBlack: '#5b3825'
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
    'red': state.lang === 'en' ? 'Red' : 'أحمر',
    'black': state.lang === 'en' ? 'Black' : 'أسود'
  };
  const eyeLabels = {
    'brown': state.lang === 'en' ? 'Brown' : 'بني', 
    'blue': state.lang === 'en' ? 'Blue' : 'أزرق', 
    'intermediate': state.lang === 'en' ? 'Intermediate' : 'متوسط'
  };
  const skinLabels = {
    'veryPale': state.lang === 'en' ? 'Very Pale' : 'فاتح جدًا',
    'pale': state.lang === 'en' ? 'Pale' : 'فاتح',
    'intermediate': state.lang === 'en' ? 'Intermediate' : 'متوسط',
    'dark': state.lang === 'en' ? 'Dark' : 'غامق',
    'darkToBlack': state.lang === 'en' ? 'Dark to Black' : 'غامق جدًا'
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
  const maxProbability = probs => Math.max(...Object.values(probs));
  const hairP = maxProbability(state.probs.hair);
  const eyeP = maxProbability(state.probs.eye);
  const skinP = maxProbability(state.probs.skin);

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
    'red': state.lang === 'en' ? 'red' : 'أحمر',
    'black': state.lang === 'en' ? 'black' : 'أسود'
  };
  const eyeLabels = {
    'brown': state.lang === 'en' ? 'brown' : 'بني', 
    'blue': state.lang === 'en' ? 'blue' : 'أزرق', 
    'intermediate': state.lang === 'en' ? 'intermediate' : 'متوسط'
  };
  const skinLabels = {
    'veryPale': state.lang === 'en' ? 'very pale' : 'فاتح جدًا',
    'pale': state.lang === 'en' ? 'pale' : 'فاتح',
    'intermediate': state.lang === 'en' ? 'intermediate' : 'متوسط',
    'dark': state.lang === 'en' ? 'dark' : 'غامق',
    'darkToBlack': state.lang === 'en' ? 'dark to black' : 'غامق جدًا'
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
      red: lang === 'en' ? 'Red' : 'أحمر',
      black: lang === 'en' ? 'Black' : 'أسود'
    },
    eye: {
      brown: lang === 'en' ? 'Brown' : 'بني',
      blue: lang === 'en' ? 'Blue' : 'أزرق', 
      intermediate: lang === 'en' ? 'Intermediate' : 'متوسط'
    },
    skin: {
      veryPale: lang === 'en' ? 'Very Pale' : 'فاتح جدًا',
      pale: lang === 'en' ? 'Pale' : 'فاتح',
      intermediate: lang === 'en' ? 'Intermediate' : 'متوسط',
      dark: lang === 'en' ? 'Dark' : 'غامق',
      darkToBlack: lang === 'en' ? 'Dark to Black' : 'غامق جدًا'
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
    hair: {blonde: 0.25, brown: 0.25, red: 0.25, black: 0.25},
    eye: {blue: 0.34, intermediate: 0.33, brown: 0.33},
    skin: {veryPale: 0.2, pale: 0.2, intermediate: 0.2, dark: 0.2, darkToBlack: 0.2}
  };
  state.hasPrediction = false;
  state.uploadedFile = null;
  state.modelMeta = null;
  
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
