// Global variables
let webcamStream = null;
let isWebcamActive = false;

// DOM Ready
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    initializeSpotifyTheme();
});

function initializeSpotifyTheme() {
    // Add Spotify font
    const fontLink = document.createElement('link');
    fontLink.href = 'https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap';
    fontLink.rel = 'stylesheet';
    document.head.appendChild(fontLink);
    
    // Apply font to body
    document.body.style.fontFamily = "'Montserrat', 'Helvetica Neue', Helvetica, Arial, sans-serif";
}

function initializeEventListeners() {
    // Image analysis form
    document.getElementById('imageForm').addEventListener('submit', handleImageAnalysis);
    document.getElementById('imageUpload').addEventListener('change', handleImagePreview);
    
    // Text analysis form
    document.getElementById('textForm').addEventListener('submit', handleTextAnalysis);
    
    // Webcam controls
    document.getElementById('startWebcam').addEventListener('click', startWebcam);
    document.getElementById('captureEmotion').addEventListener('click', captureAndAnalyze);
    document.getElementById('stopWebcam').addEventListener('click', stopWebcam);
    
    // Search form
    document.getElementById('searchForm').addEventListener('submit', handleSearch);

    // Stop webcam when switching tabs
    document.querySelectorAll('.nav-link').forEach(tab => {
        tab.addEventListener('click', function() {
            if (!this.id.includes('webcam') && isWebcamActive) {
                stopWebcam();
            }
        });
    });
}

// Image Analysis
function handleImagePreview(event) {
    const file = event.target.files[0];
    const preview = document.getElementById('imagePreview');
    
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            preview.innerHTML = `<img src="${e.target.result}" class="img-fluid rounded" style="max-height: 200px;">`;
        };
        reader.readAsDataURL(file);
    } else {
        preview.innerHTML = '';
    }
}

async function handleImageAnalysis(event) {
    event.preventDefault();
    
    const fileInput = document.getElementById('imageUpload');
    const file = fileInput.files[0];
    
    if (!file) {
        showNotification('Please select an image file', 'warning');
        return;
    }
    
    showLoading();
    
    const formData = new FormData();
    formData.append('image', file);
    
    try {
        const response = await fetch('/analyze_image', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || 'Image analysis failed');
        }
        
        displayResults(result, 'imageResults');
        showNotification(`🎭 Emotion detected: ${result.emotion} with ${(result.confidence * 100).toFixed(1)}% confidence`, 'success');
    } catch (error) {
        console.error('Error:', error);
        displayError('imageResults', error.message);
        showNotification(error.message, 'error');
    } finally {
        hideLoading();
    }
}

// Text Analysis
async function handleTextAnalysis(event) {
    event.preventDefault();
    
    const textInput = document.getElementById('textInput');
    const text = textInput.value.trim();
    
    if (!text) {
        showNotification('Please enter some text describing your mood', 'warning');
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch('/analyze_text', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text: text })
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || 'Text analysis failed');
        }
        
        displayResults(result, 'textResults');
        showNotification(`🎭 Emotion detected: ${result.emotion}`, 'success');
    } catch (error) {
        console.error('Error:', error);
        displayError('textResults', error.message);
        showNotification(error.message, 'error');
    } finally {
        hideLoading();
    }
}

// Webcam Functions
async function startWebcam() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ 
            video: { 
                width: { ideal: 640 },
                height: { ideal: 480 },
                facingMode: 'user'
            } 
        });
        
        const video = document.getElementById('webcamVideo');
        video.srcObject = stream;
        webcamStream = stream;
        isWebcamActive = true;
        
        document.getElementById('startWebcam').disabled = true;
        document.getElementById('captureEmotion').disabled = false;
        document.getElementById('stopWebcam').disabled = false;
        
        showNotification('Webcam started successfully', 'success');
        
    } catch (error) {
        console.error('Error accessing webcam:', error);
        showNotification('Could not access webcam. Please check permissions.', 'error');
    }
}

function stopWebcam() {
    if (webcamStream) {
        webcamStream.getTracks().forEach(track => track.stop());
        webcamStream = null;
    }
    
    const video = document.getElementById('webcamVideo');
    video.srcObject = null;
    isWebcamActive = false;
    
    document.getElementById('startWebcam').disabled = false;
    document.getElementById('captureEmotion').disabled = true;
    document.getElementById('stopWebcam').disabled = true;
    
    showNotification('Webcam stopped', 'info');
}

async function captureAndAnalyze() {
    if (!isWebcamActive) {
        showNotification('Please start the webcam first', 'warning');
        return;
    }
    
    const video = document.getElementById('webcamVideo');
    const canvas = document.getElementById('webcamCanvas');
    const overlay = document.getElementById('captureOverlay');
    const context = canvas.getContext('2d');
    
    // Show capture overlay
    overlay.style.display = 'flex';
    
    // Wait a moment for user to see the capture
    await new Promise(resolve => setTimeout(resolve, 500));
    
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    const imageData = canvas.toDataURL('image/jpeg');
    
    // Hide overlay
    overlay.style.display = 'none';
    
    showLoading();
    
    try {
        const response = await fetch('/analyze_webcam', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ image: imageData })
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || 'Webcam analysis failed');
        }
        
        displayResults(result, 'webcamResults');
        showNotification(`🎭 Emotion detected: ${result.emotion} with ${(result.confidence * 100).toFixed(1)}% confidence`, 'success');
    } catch (error) {
        console.error('Error:', error);
        displayError('webcamResults', error.message);
        showNotification(error.message, 'error');
    } finally {
        hideLoading();
    }
}

// Music Search
async function handleSearch(event) {
    event.preventDefault();
    
    const searchInput = document.getElementById('searchInput');
    const query = searchInput.value.trim();
    
    if (!query) {
        showNotification('Please enter a search query', 'warning');
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch('/search_music', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query: query })
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || 'Music search failed');
        }
        
        displaySearchResults(result, 'searchResults');
        showNotification(`🎵 Found ${result.tracks.length} tracks for "${query}"`, 'success');
    } catch (error) {
        console.error('Error:', error);
        displayError('searchResults', error.message);
        showNotification(error.message, 'error');
    } finally {
        hideLoading();
    }
}

// Display Functions
function displayResults(result, containerId) {
    const container = document.getElementById(containerId);
    
    const emotion = result.emotion;
    const confidence = (result.confidence * 100).toFixed(1);
    const tracks = result.tracks || [];
    const method = result.method || 'deepface';
    
    // Emotion badge with color coding
    const emotionClass = `bg-${emotion.toLowerCase()}`;
    
    let html = `
        <div class="card">
            <div class="card-header">
                <h5 class="card-title mb-0">
                    <i class="fas fa-analytics me-2"></i>Emotion Analysis Result
                </h5>
            </div>
            <div class="card-body">
                <div class="d-flex align-items-center mb-4">
                    <span class="emotion-badge ${emotionClass} me-3">
                        ${emotion.charAt(0).toUpperCase() + emotion.slice(1)}
                    </span>
                    <div>
                        <span class="text-muted">Confidence: </span>
                        <span class="text-success fw-bold">${confidence}%</span>
                        ${method === 'fallback' ? '<span class="badge bg-warning ms-2">Fallback</span>' : ''}
                    </div>
                </div>
    `;
    
    // Emotion breakdown if available
    if (result.all_emotions) {
        html += `
            <div class="emotion-breakdown">
                <h6><i class="fas fa-chart-bar me-2"></i>Emotion Breakdown</h6>
                <div class="row">
        `;
        
        Object.entries(result.all_emotions).forEach(([emotionName, score]) => {
            const percentage = typeof score === 'number' ? score.toFixed(1) : score;
            html += `
                <div class="col-6 col-md-4 mb-3">
                    <div class="emotion-item">
                        <div class="d-flex justify-content-between mb-1">
                            <span class="emotion-label">${emotionName}</span>
                            <span class="emotion-value">${percentage}%</span>
                        </div>
                        <div class="progress">
                            <div class="progress-bar bg-${emotionName.toLowerCase()}" 
                                 role="progressbar" 
                                 style="width: ${percentage}%">
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });
        
        html += `</div></div>`;
    }
    
    // Music recommendations
    if (tracks.length > 0) {
        html += `
            <div class="mt-4">
                <h6><i class="fas fa-music me-2"></i>Recommended Music</h6>
                <p class="text-muted mb-3">Based on your ${emotion} mood</p>
                <div class="tracks-container">
        `;
        
        tracks.forEach(track => {
            html += `
                <div class="track-card">
                    <div class="row align-items-center">
                        <div class="col-auto">
                            ${track.album_image ? 
                                `<img src="${track.album_image}" class="track-image" alt="Album cover">` :
                                `<div class="track-image">
                                    <i class="fas fa-music"></i>
                                </div>`
                            }
                        </div>
                        <div class="col">
                            <h6 class="card-title">${track.name}</h6>
                            <p class="card-text">${track.artists.join(', ')}</p>
                            <p class="card-text small">${track.album}</p>
                        </div>
                        <div class="col-auto">
                            <div class="d-flex gap-2 align-items-center">
                                ${track.preview_url ? 
                                    `<audio controls class="small-audio">
                                        <source src="${track.preview_url}" type="audio/mpeg">
                                    </audio>` : 
                                    '<span class="badge bg-warning">No preview</span>'
                                }
                                <a href="${track.external_url}" target="_blank" class="btn btn-outline-primary btn-sm">
                                    <i class="fab fa-spotify"></i>
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });
        
        html += `</div></div>`;
    } else {
        html += `
            <div class="alert alert-warning mt-3">
                <i class="fas fa-music me-2"></i>
                No music recommendations found.
            </div>
        `;
    }
    
    html += `</div></div>`;
    container.innerHTML = html;
}

function displaySearchResults(result, containerId) {
    const container = document.getElementById(containerId);
    const tracks = result.tracks || [];
    
    if (tracks.length === 0) {
        container.innerHTML = `
            <div class="alert alert-warning">
                <i class="fas fa-search me-2"></i>
                No tracks found for "${result.search_query}".
            </div>
        `;
        return;
    }
    
    let html = `
        <div class="card">
            <div class="card-header">
                <h5 class="card-title mb-0">
                    <i class="fas fa-search me-2"></i>Search Results for "${result.search_query}"
                </h5>
            </div>
            <div class="card-body">
                <div class="tracks-container">
    `;
    
    tracks.forEach(track => {
        html += `
            <div class="track-card">
                <div class="row align-items-center">
                    <div class="col-auto">
                        ${track.album_image ? 
                            `<img src="${track.album_image}" class="track-image" alt="Album cover">` :
                            `<div class="track-image">
                                <i class="fas fa-music"></i>
                            </div>`
                        }
                    </div>
                    <div class="col">
                        <h6 class="card-title">${track.name}</h6>
                        <p class="card-text">${track.artists.join(', ')}</p>
                        <p class="card-text small">${track.album}</p>
                    </div>
                    <div class="col-auto">
                        <div class="d-flex gap-2 align-items-center">
                            ${track.preview_url ? 
                                `<audio controls class="small-audio">
                                    <source src="${track.preview_url}" type="audio/mpeg">
                                </audio>` : 
                                '<span class="badge bg-warning">No preview</span>'
                            }
                            <a href="${track.external_url}" target="_blank" class="btn btn-outline-primary btn-sm">
                                <i class="fab fa-spotify"></i>
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        `;
    });
    
    html += `</div></div></div>`;
    container.innerHTML = html;
}

function displayError(containerId, message) {
    const container = document.getElementById(containerId);
    container.innerHTML = `
        <div class="alert alert-danger">
            <i class="fas fa-exclamation-triangle me-2"></i>
            ${message}
        </div>
    `;
}

// Utility Functions
function showLoading() {
    document.getElementById('loading').classList.remove('d-none');
    document.getElementById('loading').classList.add('d-flex');
}

function hideLoading() {
    document.getElementById('loading').classList.remove('d-flex');
    document.getElementById('loading').classList.add('d-none');
}

function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existingNotifications = document.querySelectorAll('.custom-notification');
    existingNotifications.forEach(notification => notification.remove());
    
    const notification = document.createElement('div');
    notification.className = `custom-notification alert alert-${type === 'error' ? 'danger' : type}`;
    
    const icons = {
        'success': 'fa-check-circle',
        'warning': 'fa-exclamation-triangle',
        'error': 'fa-times-circle',
        'info': 'fa-info-circle'
    };
    
    notification.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="fas ${icons[type]} me-2"></i>
            <span>${message}</span>
            <button type="button" class="btn-close btn-close-white ms-auto" onclick="this.parentElement.parentElement.remove()"></button>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

// Add Font Awesome for icons
const fontAwesome = document.createElement('link');
fontAwesome.rel = 'stylesheet';
fontAwesome.href = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css';
document.head.appendChild(fontAwesome);