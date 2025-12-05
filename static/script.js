// DOM Elements
const extractBtn = document.getElementById('extractBtn');
const urlInput = document.getElementById('urlInput');
const filterInput = document.getElementById('filterInput');
const resultsSection = document.getElementById('resultsSection');
const loadingState = document.getElementById('loadingState');
const linksList = document.getElementById('linksList');
const linkCount = document.getElementById('linkCount');
const copyBtn = document.getElementById('copyBtn');

let currentLinks = [];

// Extract Links
extractBtn.addEventListener('click', async () => {
    const url = urlInput.value.trim();
    const filter = filterInput.value.trim();
    
    if (!url) {
        showError('Veuillez entrer une URL');
        return;
    }
    
    // Show loading state
    resultsSection.classList.add('hidden');
    loadingState.classList.remove('hidden');
    
    try {
        const response = await fetch('/extract', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url, filter })
        });
        
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        currentLinks = data.links;
        displayResults(data.links, data.count);
        
    } catch (error) {
        showError(error.message);
    } finally {
        loadingState.classList.add('hidden');
    }
});

// Display Results
function displayResults(links, count) {
    linkCount.textContent = `${count} ${count === 1 ? 'lien' : 'liens'}`;
    
    linksList.innerHTML = '';
    
    if (links.length === 0) {
        linksList.innerHTML = '<p style="text-align: center; color: var(--text-tertiary); padding: 2rem;">Aucun lien trouvé</p>';
    } else {
        links.forEach((link, index) => {
            const linkItem = document.createElement('div');
            linkItem.className = 'link-item';
            linkItem.textContent = link;
            linkItem.style.animationDelay = `${index * 0.02}s`;
            linksList.appendChild(linkItem);
        });
    }
    
    resultsSection.classList.remove('hidden');
}

// Copy Links
copyBtn.addEventListener('click', async () => {
    try {
        await navigator.clipboard.writeText(currentLinks.join('\n'));
        
        // Update button text temporarily
        const originalHTML = copyBtn.innerHTML;
        copyBtn.innerHTML = `
            <svg width="18" height="18" viewBox="0 0 20 20" fill="none">
                <path d="M4 10L8 14L16 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            Copié !
        `;
        copyBtn.style.background = 'var(--success)';
        copyBtn.style.color = 'white';
        
        setTimeout(() => {
            copyBtn.innerHTML = originalHTML;
            copyBtn.style.background = '';
            copyBtn.style.color = '';
        }, 2000);
        
    } catch (error) {
        showError('Erreur lors de la copie');
    }
});

// Show Error
function showError(message) {
    loadingState.classList.add('hidden');
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'card';
    errorDiv.style.marginTop = 'var(--spacing-lg)';
    errorDiv.style.background = 'rgba(255, 59, 48, 0.1)';
    errorDiv.style.border = '1px solid var(--error)';
    errorDiv.style.color = 'var(--error)';
    errorDiv.style.textAlign = 'center';
    errorDiv.textContent = `❌ ${message}`;
    
    const existing = document.querySelector('.error-message');
    if (existing) existing.remove();
    
    errorDiv.classList.add('error-message');
    document.querySelector('.main-content').appendChild(errorDiv);
    
    setTimeout(() => errorDiv.remove(), 3000);
}

// Enter key support
urlInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') extractBtn.click();
});

filterInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') extractBtn.click();
});


