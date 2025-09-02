// 3D Bioprinting Platform JavaScript

// Global variables
let scene, camera, renderer, controls;
let currentModel = null;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    initializeTooltips();
});

function initializeApp() {
    console.log('3D Bioprinting Platform initialized');

    // Initialize 3D viewer if container exists
    const container = document.getElementById('threejs-container');
    if (container) {
        init3DViewer(container);
    }

    // Add loading states to forms
    setupFormLoading();

    // Initialize patient data validation
    setupFormValidation();
}

function setupEventListeners() {
    // Organ selection cards
    document.querySelectorAll('.organ-card').forEach(card => {
        card.addEventListener('click', function() {
            selectOrganCard(this);
        });
    });

    // Form submissions
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
                return false;
            }
            showLoadingState(this);
        });
    });

    // Download buttons
    document.querySelectorAll('[data-download]').forEach(btn => {
        btn.addEventListener('click', function() {
            trackDownload(this.dataset.download);
        });
    });
}

function selectOrganCard(card) {
    // Remove selection from all cards
    document.querySelectorAll('.organ-card').forEach(c => {
        c.classList.remove('selected');
    });

    // Add selection to clicked card
    card.classList.add('selected');

    // Extract organ type from the card
    const organIcon = card.querySelector('i').classList;
    let organType = '';
    if (organIcon.contains('fa-heart')) organType = 'heart';
    else if (organIcon.contains('fa-lungs')) organType = 'liver';
    else if (organIcon.contains('fa-kidneys')) organType = 'kidney';
    else if (organIcon.contains('fa-deaf')) organType = 'ear';

    // Set hidden input if exists
    const hiddenInput = document.getElementById('organ_type');
    if (hiddenInput) {
        hiddenInput.value = organType;
    }

    // Enable generate button
    const generateBtn = document.getElementById('generateBtn');
    if (generateBtn) {
        generateBtn.disabled = false;
        generateBtn.classList.add('pulse');
    }

    // Show organ info
    showOrganInfo(organType);
}

function showOrganInfo(organType) {
    const organInfo = {
        heart: {
            name: 'Heart',
            description: 'Cardiac tissue engineering with specialized bioink formulation',
            complexity: 'High',
            printTime: '8-12 hours',
            cellTypes: 'Cardiomyocytes, endothelial cells, fibroblasts'
        },
        liver: {
            name: 'Liver',
            description: 'Hepatic tissue construct for regenerative medicine',
            complexity: 'Medium',
            printTime: '6-10 hours',
            cellTypes: 'Hepatocytes, stellate cells, Kupffer cells'
        },
        kidney: {
            name: 'Kidney',
            description: 'Renal tissue construct with filtration capabilities',
            complexity: 'High',
            printTime: '10-15 hours',
            cellTypes: 'Podocytes, tubular epithelial cells, mesangial cells'
        },
        ear: {
            name: 'Ear',
            description: 'Auricular cartilage construct for reconstructive surgery',
            complexity: 'Medium',
            printTime: '4-6 hours',
            cellTypes: 'Chondrocytes, perichondrial cells'
        }
    };

    const info = organInfo[organType];
    if (info) {
        // Create or update info panel
        let infoPanel = document.getElementById('organ-info-panel');
        if (!infoPanel) {
            infoPanel = document.createElement('div');
            infoPanel.id = 'organ-info-panel';
            infoPanel.className = 'alert alert-info mt-3';
            document.querySelector('.organ-card').parentNode.parentNode.appendChild(infoPanel);
        }

        infoPanel.innerHTML = `
            <h6><i class="fas fa-info-circle"></i> ${info.name} Information</h6>
            <p><strong>Description:</strong> ${info.description}</p>
            <p><strong>Complexity:</strong> <span class="badge bg-${info.complexity === 'High' ? 'danger' : 'warning'}">${info.complexity}</span></p>
            <p><strong>Estimated Print Time:</strong> ${info.printTime}</p>
            <p><strong>Required Cell Types:</strong> ${info.cellTypes}</p>
        `;
    }
}

function init3DViewer(container) {
    // Create scene
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0xf0f0f0);

    // Create camera
    camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
    camera.position.set(0, 0, 5);

    // Create renderer
    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    container.appendChild(renderer.domElement);

    // Add lights
    const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(10, 10, 5);
    directionalLight.castShadow = true;
    scene.add(directionalLight);

    // Add orbit controls (would need to include OrbitControls.js)
    // controls = new THREE.OrbitControls(camera, renderer.domElement);

    // Create a sample geometry for demonstration
    createSampleModel();

    // Start animation loop
    animate();

    // Handle window resize
    window.addEventListener('resize', onWindowResize);
}

function createSampleModel() {
    // Create a sample heart-like shape for demonstration
    const geometry = new THREE.SphereGeometry(1, 32, 32);
    const material = new THREE.MeshPhongMaterial({ 
        color: 0xff6b6b,
        transparent: true,
        opacity: 0.8
    });

    currentModel = new THREE.Mesh(geometry, material);
    currentModel.castShadow = true;
    scene.add(currentModel);

    // Add wireframe
    const wireframe = new THREE.WireframeGeometry(geometry);
    const line = new THREE.LineSegments(wireframe);
    line.material.color.setHex(0x000000);
    line.material.transparent = true;
    line.material.opacity = 0.1;
    scene.add(line);
}

function animate() {
    requestAnimationFrame(animate);

    // Rotate the model
    if (currentModel) {
        currentModel.rotation.x += 0.005;
        currentModel.rotation.y += 0.01;
    }

    renderer.render(scene, camera);
}

function onWindowResize() {
    const container = document.getElementById('threejs-container');
    if (container && camera && renderer) {
        camera.aspect = container.clientWidth / container.clientHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(container.clientWidth, container.clientHeight);
    }
}

function setupFormLoading() {
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<span class="loading-spinner"></span> Processing...';
                submitBtn.disabled = true;

                // Re-enable after 30 seconds as fallback
                setTimeout(() => {
                    submitBtn.innerHTML = originalText;
                    submitBtn.disabled = false;
                }, 30000);
            }
        });
    });
}

function setupFormValidation() {
    // Height validation
    const heightInput = document.getElementById('height');
    if (heightInput) {
        heightInput.addEventListener('input', function() {
            const height = parseFloat(this.value);
            if (height < 50 || height > 250) {
                this.setCustomValidity('Height must be between 50 and 250 cm');
            } else {
                this.setCustomValidity('');
            }
        });
    }

    // Weight validation
    const weightInput = document.getElementById('weight');
    if (weightInput) {
        weightInput.addEventListener('input', function() {
            const weight = parseFloat(this.value);
            if (weight < 1 || weight > 300) {
                this.setCustomValidity('Weight must be between 1 and 300 kg');
            } else {
                this.setCustomValidity('');
            }
        });
    }

    // Age validation
    const ageInput = document.getElementById('age');
    if (ageInput) {
        ageInput.addEventListener('input', function() {
            const age = parseInt(this.value);
            if (age < 0 || age > 120) {
                this.setCustomValidity('Age must be between 0 and 120 years');
            } else {
                this.setCustomValidity('');
            }
        });
    }
}

function validateForm(form) {
    let isValid = true;
    const requiredFields = form.querySelectorAll('[required]');

    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
        }
    });

    return isValid;
}

function showLoadingState(form) {
    const loadingOverlay = document.createElement('div');
    loadingOverlay.className = 'loading-overlay';
    loadingOverlay.innerHTML = `
        <div class="loading-content">
            <div class="loading-spinner"></div>
            <p>Processing your request...</p>
        </div>
    `;
    document.body.appendChild(loadingOverlay);
}

function trackDownload(filename) {
    console.log(`Downloading: ${filename}`);
    // Could integrate with analytics here
}

function initializeTooltips() {
    // Initialize Bootstrap tooltips if they exist
    if (typeof bootstrap !== 'undefined') {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
}

// Utility functions
function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(notification);

    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 5000);
}

// Export functions for use in other scripts
window.BioPrintingPlatform = {
    selectOrganCard,
    showOrganInfo,
    validateForm,
    showNotification,
    formatBytes
};