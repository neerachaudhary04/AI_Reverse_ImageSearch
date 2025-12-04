/**
 * AI Image Lens - Main Application Script
 * Handles image upload, search, and results display
 */

// DOM Elements 
const fileInput = document.getElementById('fileInput');
const fileName = document.getElementById('fileName');
const kInput = document.getElementById('kInput');
const searchBtn = document.getElementById('searchBtn');
const btnText = searchBtn.querySelector('.btn-text');
const spinner = searchBtn.querySelector('.spinner');
const previewContainer = document.getElementById('previewContainer');
const previewImage = document.getElementById('previewImage');
const resultsSection = document.getElementById('resultsSection');
const resultsDiv = document.getElementById('results');
const resultsCount = document.getElementById('resultsCount');
const errorMessage = document.getElementById('errorMessage');

// State Management
let selectedFile = null;

// Event Listeners

/**
 * Handle file selection
 */
fileInput.addEventListener('change', (event) => {
    const file = event.target.files[0];
    
    if (!file) {
        resetFileInput();
        return;
    }

    // Validate file type
    if (!file.type.startsWith('image/')) {
        showError('Please select a valid image file');
        resetFileInput();
        return;
    }

    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
        showError('Image file is too large. Please select an image under 10MB');
        resetFileInput();
        return;
    }

    selectedFile = file;
    fileName.textContent = file.name;
    searchBtn.disabled = false;

    // Show image preview
    showPreview(file);
    hideError();
});

/**
 * Handle search button click
 */
searchBtn.addEventListener('click', async () => {
    if (!selectedFile) return;
    
    await performSearch();
});

/**
 * Handle Enter key in k-input
 */
kInput.addEventListener('keypress', (event) => {
    if (event.key === 'Enter' && !searchBtn.disabled) {
        performSearch();
    }
});

/**
 * Validate k-input value
 */
kInput.addEventListener('input', () => {
    let value = parseInt(kInput.value);
    
    if (isNaN(value) || value < 1) {
        kInput.value = 1;
    } else if (value > 100) {
        kInput.value = 100;
    }
});

// Core Functions

/**
 * Perform image search
 */
async function performSearch() {
    if (!selectedFile) return;

    setLoading(true);
    hideError();
    resultsSection.style.display = 'none';

    try {
        const k = parseInt(kInput.value) || 5;

        // Create FormData to send file as multipart/form-data
        const formData = new FormData();
        formData.append('file', selectedFile);
        formData.append('k', k.toString());

        const response = await fetch('/api/search-image', {
            method: 'POST',
            body: formData 
        });

        if (!response.ok) {
            throw new Error(`Search failed: ${response.statusText}`);
        }

        const data = await response.json();
        displayResults(data.results || []);

    } catch (error) {
        console.error('Search error:', error);
        showError(`Search failed: ${error.message}`);
    } finally {
        setLoading(false);
    }
}

/**
 * Display search results
 * @param {Array} results - Array of result objects
 */
function displayResults(results) {
    if (!results || results.length === 0) {
        showError('No results found');
        return;
    }

    resultsDiv.innerHTML = '';
    resultsCount.textContent = `${results.length} results found`;

    results.forEach(result => {
        const card = createResultCard(result);
        resultsDiv.appendChild(card);
    });

    resultsSection.style.display = 'block';
    
    setTimeout(() => {
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);
}

/**
 * Create a result card element
 * @param {Object} result - Result object
 * @returns {HTMLElement} Result card element
 */
function createResultCard(result) {
    const card = document.createElement('div');
    card.className = 'result-card';
    
    const img = document.createElement('img');
    img.src = getImageSrc(result);
    img.alt = result.label;
    img.className = 'result-image';
    img.loading = 'lazy';
    
    // Add error handling for image loading
    img.onerror = function() {
        this.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="200" height="200"%3E%3Crect fill="%23f0f0f0" width="200" height="200"/%3E%3Ctext fill="%23999" x="50%25" y="50%25" text-anchor="middle" dy=".3em"%3EImage not available%3C/text%3E%3C/svg%3E';
    };
    
    const info = document.createElement('div');
    info.className = 'result-info';
    
    const rank = document.createElement('div');
    rank.className = 'result-rank';
    rank.textContent = `#${result.rank}`;
    
    const label = document.createElement('div');
    label.className = 'result-label';
    label.textContent = result.label;
    label.title = result.label; 
    
    const score = document.createElement('div');
    score.className = 'result-score';
    score.textContent = `Score: ${result.score.toFixed(3)}`;
    
    info.appendChild(rank);
    info.appendChild(label);
    info.appendChild(score);
    
    card.appendChild(img);
    card.appendChild(info);
    
    return card;
}

/**
 * Get image source URL
 * @param {Object} result - Result object
 * @returns {string} Image URL
 */
function getImageSrc(result) {
    if (result.path && result.path.startsWith('http')) {
        return result.path;
    }
    // Use thumb_url from backend
    return result.thumb_url;
}

/**
 * Show image preview
 * @param {File} file - Image file to preview
 */
function showPreview(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
        previewImage.src = e.target.result;
        previewContainer.style.display = 'block';
    };
    reader.readAsDataURL(file);
}

/**
 * Set loading state
 * @param {boolean} loading - Loading state
 */
function setLoading(loading) {
    searchBtn.disabled = loading;
    fileInput.disabled = loading;
    kInput.disabled = loading;
    
    if (loading) {
        btnText.textContent = 'Searching...';
        spinner.style.display = 'inline-block';
    } else {
        btnText.textContent = 'Search';
        spinner.style.display = 'none';
    }
}

/**
 * Show error message
 * @param {string} message - Error message to display
 */
function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
    
    setTimeout(hideError, 5000);
}

/**
 * Hide error message
 */
function hideError() {
    errorMessage.style.display = 'none';
}

/**
 * Reset file input
 */
function resetFileInput() {
    selectedFile = null;
    fileName.textContent = 'Choose an image...';
    searchBtn.disabled = true;
    previewContainer.style.display = 'none';
    fileInput.value = '';
}

//  Initialization 

/**
 * Check API health on page load
 */
async function checkHealth() {
    try {
        const response = await fetch('/api/health');
        const data = await response.json();
        console.log('API Health:', data);
    } catch (error) {
        console.error('API health check failed:', error);
        showError('Unable to connect to the search service. Please refresh the page.');
    }
}

// Run health check when page loads
document.addEventListener('DOMContentLoaded', checkHealth);
