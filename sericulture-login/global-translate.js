// Inject Google Translate element and script into the document
document.addEventListener("DOMContentLoaded", () => {
    // Inject the translate div hidden from view
    const translateDiv = document.createElement('div');
    translateDiv.id = 'google_translate_element';
    translateDiv.style.display = 'none';
    document.body.appendChild(translateDiv);

    // Inject the Google Translate script
    const script = document.createElement('script');
    script.type = 'text/javascript';
    script.src = '//translate.google.com/translate_a/element.js?cb=googleTranslateElementInit';
    document.body.appendChild(script);

    // After a short delay, check if we need to auto-translate to Kannada
    if(localStorage.getItem('translateToKannada') === 'true') {
        setTimeout(translateToKannada, 1500);
        setTimeout(translateToKannada, 3000); // Retry in case script loads slow
    }

    // --- Floating Back Button Logic ---
    const excludedPages = ['index.html', 'farmer-home.html', 'farmer-login.html', 'create-account.html', 'farmer-create-account.html', ''];
    const currentPath = window.location.pathname;
    const currentPage = currentPath.split('/').pop();
    
    if (!excludedPages.includes(currentPage) && !currentPage.startsWith('index')) {
        const backBtn = document.createElement('a');
        // If there is history, go back. Otherwise go to dashboard.
        backBtn.onclick = (e) => {
            e.preventDefault();
            if (window.history.length > 2) {
                window.history.back();
            } else {
                window.location.href = 'farmer-home.html';
            }
        };
        backBtn.href = 'farmer-home.html'; // Fallback
        backBtn.innerHTML = `
            <div style="position: fixed; bottom: 30px; left: 30px; width: 56px; height: 56px; background: linear-gradient(135deg, #576341 0%, #3c4727 100%); color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 8px 24px rgba(87, 99, 65, 0.4); z-index: 9999; cursor: pointer; transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);">
                <svg width="24" height="24" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" style="transform: translateX(-1px);">
                    <path d="M15 18l-6-6 6-6"/>
                </svg>
            </div>
        `;
        
        // Add hover effects
        const btnInner = backBtn.firstElementChild;
        backBtn.addEventListener('mouseenter', () => {
            btnInner.style.transform = 'translateY(-4px)';
            btnInner.style.boxShadow = '0 12px 28px rgba(87, 99, 65, 0.6)';
        });
        backBtn.addEventListener('mouseleave', () => {
            btnInner.style.transform = 'translateY(0)';
            btnInner.style.boxShadow = '0 8px 24px rgba(87, 99, 65, 0.4)';
        });
        
        document.body.appendChild(backBtn);
    }
});

// Global initialization function required by Google Translate
window.googleTranslateElementInit = function() {
    new google.translate.TranslateElement({
        pageLanguage: 'en',
        includedLanguages: 'en,kn',
        layout: google.translate.TranslateElement.InlineLayout.SIMPLE,
        autoDisplay: false
    }, 'google_translate_element');
};

function translateToKannada() {
    // Programmatically select Kannada in the hidden Google Translate dropdown
    const select = document.querySelector('.goog-te-combo');
    if (select && select.value !== 'kn') {
        select.value = 'kn';
        select.dispatchEvent(new Event('change'));
    }
}

function translateToEnglish() {
    // Programmatically select English
    const select = document.querySelector('.goog-te-combo');
    if (select) {
        select.value = 'en';
        select.dispatchEvent(new Event('change'));
    }
    
    // Clear cookies
    document.cookie = "googtrans=/en/en; path=/; domain=" + window.location.hostname;
    document.cookie = "googtrans=/en/en; path=/;";
}
