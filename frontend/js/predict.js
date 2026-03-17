/**
 * Prediction Module
 * ==================
 * Handles image upload, preview, and disease prediction display.
 */

let selectedFile = null;

// ──── Initialize Upload Zone ────
function initUploadZone() {
    const zone = document.getElementById('uploadZone');
    const fileInput = document.getElementById('fileInput');

    if (!zone || !fileInput) return;

    // Click to upload
    zone.addEventListener('click', () => fileInput.click());

    // File selected
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileSelect(e.target.files[0]);
        }
    });

    // Drag & drop
    zone.addEventListener('dragover', (e) => {
        e.preventDefault();
        zone.classList.add('dragover');
    });

    zone.addEventListener('dragleave', () => {
        zone.classList.remove('dragover');
    });

    zone.addEventListener('drop', (e) => {
        e.preventDefault();
        zone.classList.remove('dragover');
        if (e.dataTransfer.files.length > 0) {
            handleFileSelect(e.dataTransfer.files[0]);
        }
    });
}

// ──── Handle File Selection ────
function handleFileSelect(file) {
    // Validate file type
    const validTypes = ['image/jpeg', 'image/png', 'image/bmp', 'image/tiff', 'image/jpg'];
    if (!validTypes.includes(file.type)) {
        showAlert('predictAlert', 'Please select a valid image file (JPG, PNG, BMP)', 'error');
        return;
    }

    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
        showAlert('predictAlert', 'File size must be less than 10MB', 'error');
        return;
    }

    selectedFile = file;

    // Show preview
    const reader = new FileReader();
    reader.onload = (e) => {
        const preview = document.getElementById('imagePreview');
        const previewImg = document.getElementById('previewImg');
        const fileName = document.getElementById('fileName');

        if (previewImg) previewImg.src = e.target.result;
        if (fileName) fileName.textContent = file.name;
        if (preview) preview.classList.add('active');

        // Show predict button
        const predictBtn = document.getElementById('predictBtn');
        if (predictBtn) predictBtn.style.display = 'inline-flex';
    };
    reader.readAsDataURL(file);
}

// ──── Remove Selected Image ────
function removeImage() {
    selectedFile = null;
    const preview = document.getElementById('imagePreview');
    const fileInput = document.getElementById('fileInput');
    const predictBtn = document.getElementById('predictBtn');
    const result = document.getElementById('resultSection');

    if (preview) preview.classList.remove('active');
    if (fileInput) fileInput.value = '';
    if (predictBtn) predictBtn.style.display = 'none';
    if (result) result.classList.remove('active');
}

// ──── Submit Prediction ────
async function submitPrediction() {
    if (!selectedFile) {
        showAlert('predictAlert', 'Please select an image first', 'error');
        return;
    }

    showLoading('Analyzing skin image with AI...');
    hideAlert('predictAlert');

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
        const data = await apiRequest('/api/predict', {
            method: 'POST',
            body: formData
        });

        hideLoading();
        displayResults(data.prediction);

    } catch (error) {
        hideLoading();
        showAlert('predictAlert', error.message || 'Prediction failed', 'error');
    }
}

// ──── Display Prediction Results ────
function displayResults(prediction) {
    const section = document.getElementById('resultSection');
    if (!section) return;

    // Disease name
    const diseaseName = document.getElementById('diseaseName');
    if (diseaseName) diseaseName.textContent = prediction.predicted_class;

    // Full name
    const diseaseFullName = document.getElementById('diseaseFullName');
    if (diseaseFullName) diseaseFullName.textContent = prediction.disease_info.full_name;

    // Description
    const diseaseDesc = document.getElementById('diseaseDescription');
    if (diseaseDesc) diseaseDesc.textContent = prediction.disease_info.description;

    // Confidence
    const confidenceValue = document.getElementById('confidenceValue');
    if (confidenceValue) confidenceValue.textContent = `${prediction.confidence}%`;

    const gaugeFill = document.getElementById('gaugeFill');
    if (gaugeFill) {
        gaugeFill.style.width = '0%';
        setTimeout(() => {
            gaugeFill.style.width = `${prediction.confidence}%`;
        }, 100);
    }

    // Severity badge
    const severityBadge = document.getElementById('severityBadge');
    if (severityBadge) {
        const severity = prediction.disease_info.severity.toLowerCase();
        severityBadge.textContent = prediction.disease_info.severity;
        severityBadge.className = 'result-badge';
        if (severity.includes('critical')) severityBadge.classList.add('severity-critical');
        else if (severity.includes('high')) severityBadge.classList.add('severity-high');
        else if (severity.includes('moderate')) severityBadge.classList.add('severity-moderate');
        else severityBadge.classList.add('severity-low');
    }

    // Precautions
    const precautionsList = document.getElementById('precautionsList');
    if (precautionsList && prediction.disease_info.precautions) {
        precautionsList.innerHTML = prediction.disease_info.precautions
            .map(p => `<li>${p}</li>`)
            .join('');
    }

    // All predictions bar chart
    const barsContainer = document.getElementById('predictionBars');
    if (barsContainer && prediction.all_predictions) {
        const sorted = Object.entries(prediction.all_predictions)
            .sort((a, b) => b[1] - a[1]);

        barsContainer.innerHTML = sorted.map(([name, value], idx) => `
            <div class="prediction-bar-item">
                <span class="prediction-bar-label">${name}</span>
                <div class="prediction-bar-track">
                    <div class="prediction-bar-fill ${idx === 0 ? 'top' : ''}" 
                         style="width: 0%;" 
                         data-width="${value}%"></div>
                </div>
                <span class="prediction-bar-value">${value.toFixed(1)}%</span>
            </div>
        `).join('');

        // Animate bars
        setTimeout(() => {
            barsContainer.querySelectorAll('.prediction-bar-fill').forEach(bar => {
                bar.style.width = bar.dataset.width;
            });
        }, 200);
    }

    // Show results section
    section.classList.add('active');
    section.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ──── Initialize on page load ────
document.addEventListener('DOMContentLoaded', () => {
    if (requireAuth()) {
        initUploadZone();
    }
});
