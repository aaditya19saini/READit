/* ======================================
   ReadIt — Free PDF Reader
   Main Application Logic
   ====================================== */

// ============ PDF.JS SETUP ============
const pdfjsLib = await import('https://cdnjs.cloudflare.com/ajax/libs/pdf.js/4.4.168/pdf.min.mjs');
pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/4.4.168/pdf.worker.min.mjs';

// ============ STATE ============
const state = {
    pdfDoc: null,
    currentPage: 1,
    totalPages: 0,
    scale: 1.0,
    rendering: false,
    searchMatches: [],
    searchIndex: -1,
    searchText: '',
    sidebarOpen: true,
    isDarkMode: true,
    pageTextContents: [], // cached text content per page
    renderedPages: new Set(), // pages already rendered
    observer: null, // IntersectionObserver for lazy loading
};

// ============ DOM REFS ============
const $ = (id) => document.getElementById(id);
const welcomeScreen = $('welcome-screen');
const app = $('app');
const fileInput = $('file-input');
const dropZone = $('drop-zone');
const viewer = $('viewer');
const viewerContainer = $('viewer-container');
const thumbnailContainer = $('thumbnail-container');
const sidebar = $('sidebar');
const searchBar = $('search-bar');
const searchInput = $('search-input');
const searchCount = $('search-count');
const pageInput = $('page-input');
const pageTotal = $('page-total');
const zoomLevel = $('zoom-level');
const zoomSelect = $('zoom-select');
const progressFill = $('progress-fill');

// Buttons
const btnOpenFile = $('btn-open-file');
const btnOpen = $('btn-open');
const btnPrev = $('btn-prev');
const btnNext = $('btn-next');
const btnZoomIn = $('btn-zoom-in');
const btnZoomOut = $('btn-zoom-out');
const btnSearch = $('btn-search');
const btnSearchClose = $('btn-search-close');
const btnSearchPrev = $('btn-search-prev');
const btnSearchNext = $('btn-search-next');
const btnPrint = $('btn-print');
const btnFullscreen = $('btn-fullscreen');
const btnDarkmode = $('btn-darkmode');
const btnSidebarToggle = $('btn-sidebar-toggle');

// ============ INITIALIZE ============
function init() {
    loadThemePreference();
    setupEventListeners();
}

// ============ EVENT LISTENERS ============
function setupEventListeners() {
    // File open
    btnOpenFile.addEventListener('click', () => fileInput.click());
    btnOpen.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', handleFileSelect);

    // Drag & Drop on drop zone
    dropZone.addEventListener('click', () => fileInput.click());
    dropZone.addEventListener('dragover', handleDragOver);
    dropZone.addEventListener('dragleave', handleDragLeave);
    dropZone.addEventListener('drop', handleDrop);

    // Drag & Drop on entire window (when app is visible)
    window.addEventListener('dragover', handleWindowDragOver);
    window.addEventListener('drop', handleWindowDrop);

    // Navigation
    btnPrev.addEventListener('click', () => goToPage(state.currentPage - 1));
    btnNext.addEventListener('click', () => goToPage(state.currentPage + 1));
    pageInput.addEventListener('change', handlePageInputChange);
    pageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            e.target.blur();
            handlePageInputChange();
        }
    });

    // Zoom
    btnZoomIn.addEventListener('click', () => setZoom(state.scale + 0.25));
    btnZoomOut.addEventListener('click', () => setZoom(state.scale - 0.25));
    zoomSelect.addEventListener('change', handleZoomSelectChange);

    // Search
    btnSearch.addEventListener('click', toggleSearch);
    btnSearchClose.addEventListener('click', closeSearch);
    btnSearchPrev.addEventListener('click', () => navigateSearch(-1));
    btnSearchNext.addEventListener('click', () => navigateSearch(1));
    searchInput.addEventListener('input', debounce(performSearch, 300));
    searchInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            navigateSearch(e.shiftKey ? -1 : 1);
        }
    });

    // Toolbar actions
    btnPrint.addEventListener('click', handlePrint);
    btnFullscreen.addEventListener('click', toggleFullscreen);
    btnDarkmode.addEventListener('click', toggleDarkMode);
    btnSidebarToggle.addEventListener('click', toggleSidebar);

    // Scroll tracking
    viewerContainer.addEventListener('scroll', debounce(handleScroll, 100));

    // Keyboard shortcuts
    document.addEventListener('keydown', handleKeyboard);
}

// ============ FILE HANDLING ============
function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file && file.type === 'application/pdf') {
        loadPDF(file);
    }
}

function handleDragOver(e) {
    e.preventDefault();
    e.stopPropagation();
    dropZone.classList.add('drag-over');
}

function handleDragLeave(e) {
    e.preventDefault();
    e.stopPropagation();
    dropZone.classList.remove('drag-over');
}

function handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    dropZone.classList.remove('drag-over');
    const file = e.dataTransfer.files[0];
    if (file && file.type === 'application/pdf') {
        loadPDF(file);
    }
}

function handleWindowDragOver(e) {
    e.preventDefault();
}

function handleWindowDrop(e) {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file && file.type === 'application/pdf') {
        loadPDF(file);
    }
}

// ============ PDF LOADING ============
async function loadPDF(file) {
    showLoading('Loading PDF...');
    try {
        const arrayBuffer = await file.arrayBuffer();
        const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
        state.pdfDoc = pdf;
        state.totalPages = pdf.numPages;
        state.currentPage = 1;
        state.pageTextContents = new Array(pdf.numPages).fill(null);
        state.renderedPages.clear();
        state.searchMatches = [];
        state.searchIndex = -1;
        state.searchText = '';

        // Update UI
        pageTotal.textContent = state.totalPages;
        pageInput.max = state.totalPages;
        updatePageInput();

        // Switch to app view
        welcomeScreen.classList.add('hidden');
        app.classList.remove('hidden');

        // Set document title
        document.title = `${file.name} — ReadIt`;

        // Switch to app view first so container dimensions are available
        // then auto-fit to page
        await autoFitPage();
        renderThumbnails();
        updateNavButtons();
        updateProgressBar();
        hideLoading();
    } catch (err) {
        console.error('Error loading PDF:', err);
        hideLoading();
        alert('Failed to load PDF. The file may be corrupted or password-protected.');
    }
}

// ============ PAGE RENDERING ============
async function renderAllPages() {
    viewer.innerHTML = '';
    state.renderedPages.clear();
    
    // Setup IntersectionObserver for lazy rendering
    if (state.observer) {
        state.observer.disconnect();
    }
    
    state.observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const pageNum = parseInt(entry.target.dataset.page);
                if (!state.renderedPages.has(pageNum)) {
                    state.renderedPages.add(pageNum);
                    renderPage(pageNum, entry.target);
                }
            }
        });
    }, {
        root: viewerContainer,
        rootMargin: '1000px 0px', // Pre-render 1000px above and below viewport
        threshold: 0
    });

    // Create placeholders for all pages
    const pagePromises = [];
    for (let i = 1; i <= state.totalPages; i++) {
        const pageWrapper = document.createElement('div');
        pageWrapper.className = 'page-wrapper';
        pageWrapper.id = `page-${i}`;
        pageWrapper.dataset.page = i;
        
        // Calculate empty placeholder dimensions based on page 1
        pagePromises.push(state.pdfDoc.getPage(i).then(page => {
            const viewport = page.getViewport({ scale: state.scale });
            pageWrapper.style.width = `${viewport.width}px`;
            pageWrapper.style.height = `${viewport.height}px`;
            
            const canvas = document.createElement('canvas');
            pageWrapper.appendChild(canvas);

            const textLayerDiv = document.createElement('div');
            textLayerDiv.className = 'textLayer';
            pageWrapper.appendChild(textLayerDiv);
            
            const annotationLayerDiv = document.createElement('div');
            annotationLayerDiv.className = 'annotationLayer';
            pageWrapper.appendChild(annotationLayerDiv);

            viewer.appendChild(pageWrapper);
            state.observer.observe(pageWrapper);
        }));
    }
    
    // Wait for all placeholders to be sized and appended
    await Promise.all(pagePromises);
    
    // Make sure pages are in correct order (Promises might resolve out of order)
    const wrappers = Array.from(viewer.children);
    wrappers.sort((a, b) => parseInt(a.dataset.page) - parseInt(b.dataset.page));
    wrappers.forEach(w => viewer.appendChild(w));
}

async function renderPage(pageNum, pageWrapper) {
    try {
        const canvas = pageWrapper.querySelector('canvas');
        const textLayerDiv = pageWrapper.querySelector('.textLayer');
        const annotationLayerDiv = pageWrapper.querySelector('.annotationLayer');
        
        const page = await state.pdfDoc.getPage(pageNum);
        const viewport = page.getViewport({ scale: state.scale * window.devicePixelRatio });
        const displayViewport = page.getViewport({ scale: state.scale });

        // Update wrapper dimensions (in case it changed from placeholder)
        pageWrapper.style.width = `${displayViewport.width}px`;
        pageWrapper.style.height = `${displayViewport.height}px`;

        canvas.width = viewport.width;
        canvas.height = viewport.height;
        canvas.style.width = `${displayViewport.width}px`;
        canvas.style.height = `${displayViewport.height}px`;

        const ctx = canvas.getContext('2d');
        await page.render({
            canvasContext: ctx,
            viewport: viewport,
        }).promise;

        // Text layer for selection/copy
        textLayerDiv.innerHTML = '';
        textLayerDiv.style.width = `${displayViewport.width}px`;
        textLayerDiv.style.height = `${displayViewport.height}px`;

        const textContent = await page.getTextContent();
        state.pageTextContents[pageNum - 1] = textContent;

        // Render text layer spans
        const textItems = textContent.items;
        for (const item of textItems) {
            if (!item.str) continue;
            const span = document.createElement('span');
            span.textContent = item.str;

            const tx = pdfjsLib.Util.transform(displayViewport.transform, item.transform);
            const fontSize = Math.sqrt(tx[2] * tx[2] + tx[3] * tx[3]);

            span.style.left = `${tx[4]}px`;
            span.style.top = `${tx[5] - fontSize}px`;
            span.style.fontSize = `${fontSize}px`;
            span.style.fontFamily = item.fontName || 'sans-serif';

            if (item.width > 0) {
                span.style.width = `${item.width * displayViewport.scale}px`;
                span.style.transformOrigin = 'left bottom';
            }

            textLayerDiv.appendChild(span);
        }
        
        // Render annotations (links, etc.)
        const annotations = await page.getAnnotations();
        if (annotations.length > 0) {
            annotationLayerDiv.innerHTML = '';
            annotationLayerDiv.style.width = `${displayViewport.width}px`;
            annotationLayerDiv.style.height = `${displayViewport.height}px`;
            
            pdfjsLib.AnnotationLayer.render({
                viewport: displayViewport,
                div: annotationLayerDiv,
                annotations: annotations,
                page: page,
                linkService: {
                    getDestinationHash: (dest) => dest, // Dummy link service for now
                    navigateTo: (dest) => console.log('Link destination:', dest)
                },
                downloadManager: null,
            });
        }
        
    } catch (err) {
        console.error(`Error rendering page ${pageNum}:`, err);
    }
}

// ============ THUMBNAILS ============
async function renderThumbnails() {
    thumbnailContainer.innerHTML = '';
    const thumbScale = 0.3;

    for (let i = 1; i <= state.totalPages; i++) {
        const wrapper = document.createElement('div');
        wrapper.className = 'thumbnail-wrapper';
        if (i === state.currentPage) wrapper.classList.add('active');
        wrapper.dataset.page = i;
        wrapper.addEventListener('click', () => goToPage(i));

        const canvas = document.createElement('canvas');
        canvas.className = 'thumbnail-canvas';
        wrapper.appendChild(canvas);

        const label = document.createElement('span');
        label.className = 'thumbnail-label';
        label.textContent = i;
        wrapper.appendChild(label);

        thumbnailContainer.appendChild(wrapper);

        // Render thumbnail
        try {
            const page = await state.pdfDoc.getPage(i);
            const viewport = page.getViewport({ scale: thumbScale });
            canvas.width = viewport.width;
            canvas.height = viewport.height;
            const ctx = canvas.getContext('2d');
            await page.render({ canvasContext: ctx, viewport }).promise;
        } catch (err) {
            console.error(`Error rendering thumbnail ${i}:`, err);
        }
    }
}

function updateActiveThumbnail() {
    const thumbnails = thumbnailContainer.querySelectorAll('.thumbnail-wrapper');
    thumbnails.forEach((thumb) => {
        const page = parseInt(thumb.dataset.page);
        thumb.classList.toggle('active', page === state.currentPage);
    });

    // Scroll thumbnail into view
    const active = thumbnailContainer.querySelector('.thumbnail-wrapper.active');
    if (active) {
        active.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
}

// ============ NAVIGATION ============
function goToPage(pageNum) {
    if (pageNum < 1 || pageNum > state.totalPages) return;
    state.currentPage = pageNum;
    updatePageInput();
    updateNavButtons();
    updateActiveThumbnail();
    updateProgressBar();

    // Scroll page into view
    const pageEl = document.getElementById(`page-${pageNum}`);
    if (pageEl) {
        pageEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

function handlePageInputChange() {
    let val = parseInt(pageInput.value);
    if (isNaN(val)) val = state.currentPage;
    val = Math.max(1, Math.min(val, state.totalPages));
    goToPage(val);
}

function updatePageInput() {
    pageInput.value = state.currentPage;
}

function updateNavButtons() {
    btnPrev.disabled = state.currentPage <= 1;
    btnNext.disabled = state.currentPage >= state.totalPages;
}

function updateProgressBar() {
    if (state.totalPages === 0) return;
    const progress = (state.currentPage / state.totalPages) * 100;
    progressFill.style.width = `${progress}%`;
}

// ============ SCROLL TRACKING ============
function handleScroll() {
    if (!state.pdfDoc) return;

    const containerRect = viewerContainer.getBoundingClientRect();
    const containerCenter = containerRect.top + containerRect.height / 3;
    let closestPage = 1;
    let closestDist = Infinity;

    for (let i = 1; i <= state.totalPages; i++) {
        const pageEl = document.getElementById(`page-${i}`);
        if (!pageEl) continue;
        const pageRect = pageEl.getBoundingClientRect();
        const pageCenter = pageRect.top + pageRect.height / 2;
        const dist = Math.abs(pageCenter - containerCenter);
        if (dist < closestDist) {
            closestDist = dist;
            closestPage = i;
        }
    }

    if (closestPage !== state.currentPage) {
        state.currentPage = closestPage;
        updatePageInput();
        updateNavButtons();
        updateActiveThumbnail();
        updateProgressBar();
    }
}

// ============ ZOOM ============
function setZoom(newScale) {
    newScale = Math.max(0.25, Math.min(5, newScale));
    state.scale = newScale;
    zoomLevel.textContent = `${Math.round(newScale * 100)}%`;

    // Update zoom select if there's a matching value
    const matchOption = Array.from(zoomSelect.options).find(
        (o) => parseFloat(o.value) === newScale
    );
    if (matchOption) {
        zoomSelect.value = matchOption.value;
    } else {
        zoomSelect.value = '';
    }

    reRenderPages();
}

function handleZoomSelectChange() {
    const val = zoomSelect.value;
    if (val === 'fit-width') {
        fitWidth();
    } else if (val === 'fit-page') {
        fitPage();
    } else {
        setZoom(parseFloat(val));
    }
}

async function fitWidth() {
    if (!state.pdfDoc) return;
    const page = await state.pdfDoc.getPage(state.currentPage);
    const viewport = page.getViewport({ scale: 1 });
    const containerWidth = viewerContainer.clientWidth - 60; // padding
    const newScale = containerWidth / viewport.width;
    state.scale = newScale;
    zoomLevel.textContent = `${Math.round(newScale * 100)}%`;
    reRenderPages();
}

async function fitPage() {
    if (!state.pdfDoc) return;
    const page = await state.pdfDoc.getPage(state.currentPage);
    const viewport = page.getViewport({ scale: 1 });
    const containerWidth = viewerContainer.clientWidth - 60;
    const containerHeight = viewerContainer.clientHeight - 60;
    const scaleW = containerWidth / viewport.width;
    const scaleH = containerHeight / viewport.height;
    const newScale = Math.min(scaleW, scaleH);
    state.scale = newScale;
    zoomLevel.textContent = `${Math.round(newScale * 100)}%`;
    reRenderPages();
}

async function autoFitPage() {
    if (!state.pdfDoc) return;
    const page = await state.pdfDoc.getPage(1);
    const viewport = page.getViewport({ scale: 1 });
    const containerWidth = viewerContainer.clientWidth - 60;
    const containerHeight = viewerContainer.clientHeight - 60;
    const scaleW = containerWidth / viewport.width;
    const scaleH = containerHeight / viewport.height;
    const newScale = Math.min(scaleW, scaleH);
    state.scale = newScale;
    zoomLevel.textContent = `${Math.round(newScale * 100)}%`;
    zoomSelect.value = 'fit-page';
    await renderAllPages();
}

async function reRenderPages() {
    if (!state.pdfDoc || state.rendering) return;
    state.rendering = true;

    // Remember scroll position relative to current page
    const currentPageEl = document.getElementById(`page-${state.currentPage}`);
    const scrollBefore = currentPageEl ? currentPageEl.getBoundingClientRect().top : 0;

    await renderAllPages();

    // Restore scroll position
    const newPageEl = document.getElementById(`page-${state.currentPage}`);
    if (newPageEl) {
        const scrollAfter = newPageEl.getBoundingClientRect().top;
        viewerContainer.scrollTop += (scrollAfter - scrollBefore);
    }

    // Re-apply search highlights if active
    if (state.searchText) {
        highlightSearchMatches();
    }

    state.rendering = false;
}

// ============ SEARCH ============
function toggleSearch() {
    if (searchBar.classList.contains('hidden')) {
        searchBar.classList.remove('hidden');
        searchInput.focus();
        searchInput.select();
    } else {
        closeSearch();
    }
}

function closeSearch() {
    searchBar.classList.add('hidden');
    searchInput.value = '';
    searchCount.textContent = '';
    state.searchMatches = [];
    state.searchIndex = -1;
    state.searchText = '';
    clearSearchHighlights();
}

async function performSearch() {
    const query = searchInput.value.trim().toLowerCase();
    if (!query) {
        searchCount.textContent = '';
        state.searchMatches = [];
        state.searchIndex = -1;
        state.searchText = '';
        clearSearchHighlights();
        return;
    }

    state.searchText = query;
    state.searchMatches = [];

    // Search through all pages' text content
    for (let i = 0; i < state.totalPages; i++) {
        let textContent = state.pageTextContents[i];
        if (!textContent) {
            const page = await state.pdfDoc.getPage(i + 1);
            textContent = await page.getTextContent();
            state.pageTextContents[i] = textContent;
        }

        const items = textContent.items;
        for (let j = 0; j < items.length; j++) {
            const text = items[j].str.toLowerCase();
            if (text.includes(query)) {
                state.searchMatches.push({ page: i + 1, itemIndex: j });
            }
        }
    }

    if (state.searchMatches.length > 0) {
        state.searchIndex = 0;
        searchCount.textContent = `1 of ${state.searchMatches.length}`;
    } else {
        state.searchIndex = -1;
        searchCount.textContent = 'No results';
    }

    highlightSearchMatches();
}

function navigateSearch(direction) {
    if (state.searchMatches.length === 0) return;

    state.searchIndex += direction;
    if (state.searchIndex >= state.searchMatches.length) state.searchIndex = 0;
    if (state.searchIndex < 0) state.searchIndex = state.searchMatches.length - 1;

    searchCount.textContent = `${state.searchIndex + 1} of ${state.searchMatches.length}`;
    highlightSearchMatches();

    // Scroll to current match
    const match = state.searchMatches[state.searchIndex];
    goToPage(match.page);
}

function highlightSearchMatches() {
    clearSearchHighlights();
    if (!state.searchText || state.searchMatches.length === 0) return;

    for (let matchIdx = 0; matchIdx < state.searchMatches.length; matchIdx++) {
        const match = state.searchMatches[matchIdx];
        const pageWrapper = document.getElementById(`page-${match.page}`);
        if (!pageWrapper) continue;

        const textLayer = pageWrapper.querySelector('.textLayer');
        if (!textLayer) continue;

        const spans = textLayer.querySelectorAll('span');
        const textContent = state.pageTextContents[match.page - 1];
        if (!textContent) continue;

        // Find the corresponding span
        let spanIndex = 0;
        for (let i = 0; i < match.itemIndex && i < textContent.items.length; i++) {
            if (textContent.items[i].str) spanIndex++;
        }

        if (spanIndex < spans.length) {
            const span = spans[spanIndex];
            span.classList.add('highlight');
            if (matchIdx === state.searchIndex) {
                span.classList.add('active');
                // Scroll into view for active match
                span.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        }
    }
}

function clearSearchHighlights() {
    viewer.querySelectorAll('.highlight').forEach((el) => {
        el.classList.remove('highlight', 'active');
    });
}

// ============ DARK MODE ============
function toggleDarkMode() {
    state.isDarkMode = !state.isDarkMode;
    document.body.classList.toggle('dark-mode', state.isDarkMode);
    $('icon-moon').classList.toggle('hidden', !state.isDarkMode);
    $('icon-sun').classList.toggle('hidden', state.isDarkMode);
    localStorage.setItem('readit-dark-mode', state.isDarkMode);
}

function loadThemePreference() {
    const saved = localStorage.getItem('readit-dark-mode');
    if (saved !== null) {
        state.isDarkMode = saved === 'true';
    }
    document.body.classList.toggle('dark-mode', state.isDarkMode);
    $('icon-moon').classList.toggle('hidden', !state.isDarkMode);
    $('icon-sun').classList.toggle('hidden', state.isDarkMode);
}

// ============ SIDEBAR ============
function toggleSidebar() {
    state.sidebarOpen = !state.sidebarOpen;
    sidebar.classList.toggle('collapsed', !state.sidebarOpen);
}

// ============ FULLSCREEN ============
function toggleFullscreen() {
    if (document.fullscreenElement) {
        document.exitFullscreen();
    } else {
        document.documentElement.requestFullscreen();
    }
}

// ============ PRINT ============
function handlePrint() {
    window.print();
}

// ============ KEYBOARD SHORTCUTS ============
function handleKeyboard(e) {
    // Don't trigger shortcuts when typing in inputs
    const tag = e.target.tagName.toLowerCase();
    const isInput = tag === 'input' || tag === 'textarea' || tag === 'select';

    // Ctrl+O — Open file
    if (e.ctrlKey && e.key === 'o') {
        e.preventDefault();
        fileInput.click();
        return;
    }

    // Ctrl+F — Search
    if (e.ctrlKey && e.key === 'f') {
        e.preventDefault();
        toggleSearch();
        return;
    }

    // Ctrl+P — Print
    if (e.ctrlKey && e.key === 'p') {
        e.preventDefault();
        handlePrint();
        return;
    }

    // Escape — Close search
    if (e.key === 'Escape') {
        if (!searchBar.classList.contains('hidden')) {
            closeSearch();
            return;
        }
    }

    // Don't process remaining shortcuts in input fields
    if (isInput) return;

    // Arrow keys — Navigation
    if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
        e.preventDefault();
        goToPage(state.currentPage - 1);
        return;
    }
    if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
        e.preventDefault();
        goToPage(state.currentPage + 1);
        return;
    }

    // Home / End
    if (e.key === 'Home') {
        e.preventDefault();
        goToPage(1);
        return;
    }
    if (e.key === 'End') {
        e.preventDefault();
        goToPage(state.totalPages);
        return;
    }

    // + / - — Zoom
    if (e.key === '+' || e.key === '=') {
        e.preventDefault();
        setZoom(state.scale + 0.25);
        return;
    }
    if (e.key === '-' || e.key === '_') {
        e.preventDefault();
        setZoom(state.scale - 0.25);
        return;
    }

    // T — Toggle sidebar
    if (e.key === 't' || e.key === 'T') {
        toggleSidebar();
        return;
    }

    // F11 — Fullscreen
    if (e.key === 'F11') {
        e.preventDefault();
        toggleFullscreen();
        return;
    }
}

// ============ LOADING OVERLAY ============
function showLoading(message) {
    let overlay = document.querySelector('.loading-overlay');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.className = 'loading-overlay';
        overlay.innerHTML = `
            <div class="spinner"></div>
            <span class="loading-text">${message}</span>
        `;
        document.body.appendChild(overlay);
    } else {
        overlay.querySelector('.loading-text').textContent = message;
        overlay.classList.remove('hidden');
    }
}

function hideLoading() {
    const overlay = document.querySelector('.loading-overlay');
    if (overlay) overlay.remove();
}

// ============ UTILITIES ============
function debounce(fn, delay) {
    let timer;
    return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(() => fn(...args), delay);
    };
}

// ============ START ============
init();
