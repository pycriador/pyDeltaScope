// Global variables
let currentUser = null;
let authToken = null;
let currentProject = null;
let projects = [];
let connections = [];

// API Base URL
const API_BASE = '/api';

// Notification system
function showNotification(message, type = 'info', title = null) {
    const modal = document.getElementById('notificationModal');
    const header = document.getElementById('notificationHeader');
    const titleEl = document.getElementById('notificationTitle');
    const messageEl = document.getElementById('notificationMessage');
    
    // Remove all type classes
    header.classList.remove('success', 'error', 'warning', 'info');
    
    // Add appropriate class
    header.classList.add(type);
    
    // Set title
    const titles = {
        'success': 'Sucesso',
        'error': 'Erro',
        'warning': 'Aviso',
        'info': 'Informação'
    };
    titleEl.textContent = title || titles[type] || 'Notificação';
    
    // Set message
    messageEl.textContent = message;
    
    // Show modal
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
}

// Helper functions for different notification types
function showSuccess(message, title = null) {
    showNotification(message, 'success', title);
}

function showError(message, title = null) {
    showNotification(message, 'error', title);
}

function showWarning(message, title = null) {
    showNotification(message, 'warning', title);
}

function showInfo(message, title = null) {
    showNotification(message, 'info', title);
}

// Helper function to clean up modal backdrops (defined early for use in showConfirmation)
function cleanupModalBackdrops() {
    const backdrops = document.querySelectorAll('.modal-backdrop');
    backdrops.forEach(backdrop => backdrop.remove());
    document.body.classList.remove('modal-open');
    document.body.style.overflow = '';
    document.body.style.paddingRight = '';
}

// Confirmation modal
// Show confirmation modal - returns a Promise
function showConfirmation(title, message) {
    return new Promise((resolve) => {
        const modal = document.getElementById('confirmationModal');
        const messageEl = document.getElementById('confirmationMessage');
        const titleEl = document.getElementById('confirmationTitle');
        const confirmBtn = document.getElementById('confirmationConfirmBtn');
        const cancelBtn = document.getElementById('confirmationCancelBtn');
        
        messageEl.textContent = message;
        titleEl.textContent = title;
        
        // Remove previous event listeners by cloning
        const newConfirmBtn = confirmBtn.cloneNode(true);
        confirmBtn.parentNode.replaceChild(newConfirmBtn, confirmBtn);
        
        const newCancelBtn = cancelBtn.cloneNode(true);
        cancelBtn.parentNode.replaceChild(newCancelBtn, cancelBtn);
        
        // Clean up modal backdrop before showing
        cleanupModalBackdrops();
        
        // Add new event listeners
        newConfirmBtn.addEventListener('click', () => {
            const modalInstance = bootstrap.Modal.getInstance(modal);
            if (modalInstance) {
                modalInstance.hide();
            }
            setTimeout(() => {
                cleanupModalBackdrops();
                resolve(true);
            }, 300);
        });
        
        newCancelBtn.addEventListener('click', () => {
            const modalInstance = bootstrap.Modal.getInstance(modal);
            if (modalInstance) {
                modalInstance.hide();
            }
            setTimeout(() => {
                cleanupModalBackdrops();
                resolve(false);
            }, 300);
        });
        
        // Show modal
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    });
}

// Helper function to check if we're on a template page
function isTemplatePage() {
    // Template pages don't have mainApp element
    return !document.getElementById('mainApp');
}

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    // Load theme preference (always safe to do)
    loadTheme();
    
    // If we're on a template page, don't run ANY JavaScript code
    if (isTemplatePage()) {
        // Template pages are fully server-rendered - no JavaScript needed
        // All functionality is handled server-side via Flask
        console.log('[TEMPLATE PAGE] Detected template page - skipping ALL JavaScript initialization');
        return; // Exit early - don't run ANY code
    }
    
    // We're on the SPA page - run normal SPA initialization
    console.log('[SPA PAGE] Detected SPA page - running SPA initialization');
    checkAuth();
    setupEventListeners();
});

// Theme Management
function loadTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-theme');
        updateThemeIcon(true);
    } else {
        document.body.classList.remove('dark-theme');
        updateThemeIcon(false);
    }
}

function toggleTheme() {
    const isDark = document.body.classList.toggle('dark-theme');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
    updateThemeIcon(isDark);
}

function updateThemeIcon(isDark) {
    const themeIcon = document.getElementById('themeIcon');
    if (themeIcon) {
        if (isDark) {
            themeIcon.classList.remove('fa-moon');
            themeIcon.classList.add('fa-sun');
        } else {
            themeIcon.classList.remove('fa-sun');
            themeIcon.classList.add('fa-moon');
        }
    }
}

// Check authentication status (only for SPA page)
async function checkAuth() {
    // Don't run on template pages
    if (isTemplatePage()) {
        return;
    }
    
    // First check if setup is needed - this MUST be checked before anything else
    let needsSetup = false;
    
    try {
        console.log('Checking if setup is needed...');
        const setupResponse = await fetch(`${API_BASE}/setup/check`);
        
        if (setupResponse.ok) {
            const setupData = await setupResponse.json();
            console.log('Setup check result:', setupData);
            needsSetup = setupData.needs_setup === true;
        } else {
            console.error('Setup check failed:', setupResponse.status);
            // If check fails, assume setup is needed to be safe
            needsSetup = true;
        }
    } catch (error) {
        console.error('Error checking setup:', error);
        // If there's an error, assume setup is needed to be safe
        needsSetup = true;
    }
    
    // If setup is needed, show modal and STOP here
    if (needsSetup) {
        console.log('Setup needed - showing setup modal');
        showSetupModal();
        return; // IMPORTANT: Don't continue with auth check
    }
    
    // Only continue with normal auth if setup is not needed
    // Try to get token and user from localStorage, but handle errors gracefully
    let token = null;
    let userStr = null;
    
    try {
        token = localStorage.getItem('authToken');
        userStr = localStorage.getItem('currentUser');
    } catch (error) {
        // Ignore localStorage errors (may be from browser extensions)
        console.warn('Could not access localStorage:', error);
    }
    
    if (token && userStr) {
        try {
            authToken = token;
            currentUser = JSON.parse(userStr);
            
            // Validate that currentUser is a valid object
            if (!currentUser || typeof currentUser !== 'object') {
                throw new Error('Invalid user data');
            }
            
            // We're on the SPA page
            showMainApp();
            // Load data but don't show connections section automatically
            loadConnections();
            loadProjects();
            // Load users and groups if user is admin
            if (currentUser && currentUser.is_admin) {
                loadUsers();
                loadGroups();
            }
        } catch (error) {
            // If there's an error parsing user data, clear storage and redirect to login
            console.error('Error parsing user data:', error);
            try {
                localStorage.removeItem('authToken');
                localStorage.removeItem('currentUser');
            } catch (e) {
                // Ignore errors clearing localStorage
            }
            authToken = null;
            currentUser = null;
            // Redirect to login page instead of showing login section
            window.location.href = '/login';
        }
    } else {
        // No token or user - redirect to login
        window.location.href = '/login';
    }
}

// Setup event listeners for template pages (minimal, safe listeners)
function setupTemplateEventListeners() {
    // Only setup listeners that are safe and don't interfere with template pages
    // Most functionality is handled server-side for template pages
}

// Setup event listeners for SPA page
function setupEventListeners() {
    // Only run if we're on SPA page
    if (isTemplatePage()) {
        return;
    }
    
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const sourceDbType = document.getElementById('sourceDbType');
    const targetDbType = document.getElementById('targetDbType');
    
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
    }
    
    if (sourceDbType) {
        sourceDbType.addEventListener('change', updateSourceDbConfig);
    }
    
    if (targetDbType) {
        targetDbType.addEventListener('change', updateTargetDbConfig);
    }
    
    // Add Enter key listener to password field for login
    const passwordField = document.getElementById('password');
    if (passwordField) {
        passwordField.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                if (loginForm) {
                    loginForm.dispatchEvent(new Event('submit'));
                }
            }
        });
    }
    
    // Add Enter key listener to register password field
    const regPassword = document.getElementById('regPassword');
    if (regPassword) {
        regPassword.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                if (registerForm) {
                    registerForm.dispatchEvent(new Event('submit'));
                }
            }
        });
    }
}

// Show login section
function showLogin() {
    const loginSection = document.getElementById('loginSection');
    const registerSection = document.getElementById('registerSection');
    const mainApp = document.getElementById('mainApp');
    const setupModal = document.getElementById('setupModal');
    
    if (loginSection) loginSection.style.display = 'block';
    if (registerSection) registerSection.style.display = 'none';
    if (mainApp) mainApp.style.display = 'none';
    if (setupModal) setupModal.style.display = 'none';
    
    // Hide navbar on login page
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        navbar.style.display = 'none';
    }
}

// Show setup modal (first time)
function showSetupModal() {
    console.log('Showing setup modal - first run detected');
    
    // Hide all other sections
    const loginSection = document.getElementById('loginSection');
    const registerSection = document.getElementById('registerSection');
    const mainApp = document.getElementById('mainApp');
    
    if (loginSection) loginSection.style.display = 'none';
    if (registerSection) registerSection.style.display = 'none';
    if (mainApp) mainApp.style.display = 'none';
    
    // Ensure modal is visible
    const setupModalEl = document.getElementById('setupModal');
    if (!setupModalEl) {
        console.error('Setup modal element not found!');
        alert('Erro: Modal de configuração não encontrado. Por favor, recarregue a página.');
        return;
    }
    
    // Clean up any existing modal instances
    cleanupModalBackdrops();
    
    // Wait a bit for DOM to be ready, then show modal
    setTimeout(() => {
        try {
            // Hide any existing modals first
            const existingModals = document.querySelectorAll('.modal.show');
            existingModals.forEach(modal => {
                const bsModal = bootstrap.Modal.getInstance(modal);
                if (bsModal) bsModal.hide();
            });
            
            // Show setup modal
            const setupModal = new bootstrap.Modal(setupModalEl, {
                backdrop: 'static',
                keyboard: false
            });
            setupModal.show();
            
            console.log('Setup modal shown successfully');
        } catch (error) {
            console.error('Error showing setup modal:', error);
            // Fallback: show alert if modal fails
            alert('Esta é a primeira execução do sistema. Por favor, crie o usuário administrador através da interface.');
        }
    }, 100);
}

// Create first admin user
async function createFirstAdmin() {
    const username = document.getElementById('setupUsername').value.trim();
    const email = document.getElementById('setupEmail').value.trim();
    const password = document.getElementById('setupPassword').value;
    const passwordConfirm = document.getElementById('setupPasswordConfirm').value;
    
    if (!username || !email || !password || !passwordConfirm) {
        showError('Preencha todos os campos obrigatórios.');
        return;
    }
    
    if (password !== passwordConfirm) {
        showError('As senhas não coincidem.');
        return;
    }
    
    if (password.length < 6) {
        showError('A senha deve ter pelo menos 6 caracteres.');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/setup/create-admin`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username,
                email,
                password
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            bootstrap.Modal.getInstance(document.getElementById('setupModal')).hide();
            showSuccess('Usuário administrador criado com sucesso! Faça login para continuar.');
            showLogin();
        } else {
            showError(data.message || 'Erro ao criar usuário administrador');
        }
    } catch (error) {
        showError('Erro ao criar usuário administrador: ' + error.message);
    }
}

// Show register section
function showRegister() {
    const loginSection = document.getElementById('loginSection');
    const registerSection = document.getElementById('registerSection');
    const mainApp = document.getElementById('mainApp');
    
    if (loginSection) loginSection.style.display = 'none';
    if (registerSection) registerSection.style.display = 'block';
    if (mainApp) mainApp.style.display = 'none';
    
    // Hide navbar on register page
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        navbar.style.display = 'none';
    }
}

// Show main application (only for SPA page)
function showMainApp() {
    // Don't run on template pages
    if (isTemplatePage()) {
        return;
    }
    
    const loginSection = document.getElementById('loginSection');
    const registerSection = document.getElementById('registerSection');
    const mainApp = document.getElementById('mainApp');
    
    // Only manipulate SPA elements if they exist
    if (loginSection) {
        loginSection.style.display = 'none';
    }
    if (registerSection) {
        registerSection.style.display = 'none';
    }
    if (mainApp) {
        mainApp.style.display = 'block';
    }
    
    // Update user info if element exists
    const userInfo = document.getElementById('userInfo');
    if (userInfo && currentUser) {
        userInfo.textContent = `Olá, ${currentUser.username}`;
    }
    
    // Show navbar in main app
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        navbar.style.display = 'flex';
    }
    
    // Show/hide admin menu items (only if elements exist)
    const adminUsersNav = document.getElementById('adminUsersNav');
    const adminGroupsNav = document.getElementById('adminGroupsNav');
    if (adminUsersNav && adminGroupsNav && currentUser) {
        if (currentUser.is_admin) {
            adminUsersNav.style.display = 'block';
            adminGroupsNav.style.display = 'block';
        } else {
            adminUsersNav.style.display = 'none';
            adminGroupsNav.style.display = 'none';
        }
    }
    
    // Check if this is first login (no section in URL)
    const currentPath = window.location.pathname;
    const hasSection = ['/conexoes', '/projetos', '/comparacao', '/dashboard', '/tabelas', '/relatorios', '/usuarios', '/grupos'].some(path => currentPath.includes(path));

    if (!hasSection) {
        // Show welcome screen on first login
        showWelcomeScreen();
    } else {
        // Navigate to the section in URL
        const section = getSectionFromPath(currentPath);
        if (section) {
            navigateToSection(section, false);
        }
    }
}

// Show welcome screen
function showWelcomeScreen() {
    // Hide all sections
    document.querySelectorAll('[id$="Section"]').forEach(section => {
        if (section.id !== 'welcomeSection') {
            section.style.display = 'none';
        }
    });
    
    // Show welcome section
    const welcomeSection = document.getElementById('welcomeSection');
    if (welcomeSection) {
        welcomeSection.style.display = 'block';
    }
    
    // Update URL to home
    window.history.pushState({ section: 'welcome' }, 'Bem-vindo - DeltaScope', '/');
    document.title = 'Bem-vindo - DeltaScope';
}

// Navigate to section with URL update
function navigateToSection(section, updateHistory = true) {
    // Don't run on template pages
    if (isTemplatePage()) {
        return;
    }
    
    // Hide welcome screen
    const welcomeSection = document.getElementById('welcomeSection');
    if (welcomeSection) {
        welcomeSection.style.display = 'none';
    }
    
    // Show the selected section
    showSection(section);
    
    // Scroll to top of page when navigating to users or groups sections
    if (section === 'users' || section === 'groups') {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
    
    // Map section names to URL paths
    const sectionPaths = {
        'connections': '/conexoes',
        'projects': '/projetos',
        'comparison': '/comparacao',
        'dashboard': '/dashboard',
        'tables': '/tabelas',
        'reports': '/relatorios',
        'users': '/usuarios',
        'groups': '/grupos'
    };
    
    const sectionTitles = {
        'connections': 'Conexões - DeltaScope',
        'projects': 'Projetos - DeltaScope',
        'comparison': 'Comparação - DeltaScope',
        'dashboard': 'Dashboard - DeltaScope',
        'tables': 'Tabelas - DeltaScope',
        'reports': 'Relatórios - DeltaScope',
        'users': 'Usuários - DeltaScope',
        'groups': 'Grupos - DeltaScope'
    };
    
    const path = sectionPaths[section] || '/';
    const title = sectionTitles[section] || 'DeltaScope';
    
    if (updateHistory) {
        window.history.pushState({ section: section }, title, path);
        document.title = title;
    }
}

// Get section from path
function getSectionFromPath(path) {
    const pathMap = {
        '/conexoes': 'connections',
        '/projetos': 'projects',
        '/comparacao': 'comparison',
        '/dashboard': 'dashboard',
        '/tabelas': 'tables',
        '/relatorios': 'reports',
        '/usuarios': 'users',
        '/grupos': 'groups'
    };
    
    for (const [urlPath, section] of Object.entries(pathMap)) {
        if (path.includes(urlPath)) {
            return section;
        }
    }
    
    return null;
}

// Handle browser back/forward buttons (only for SPA page)
window.addEventListener('popstate', function(event) {
    // Don't interfere with template pages
    if (isTemplatePage()) {
        return;
    }
    
    if (event.state && event.state.section) {
        if (event.state.section === 'welcome') {
            showWelcomeScreen();
        } else {
            navigateToSection(event.state.section, false);
        }
    } else {
        const section = getSectionFromPath(window.location.pathname);
        if (section) {
            navigateToSection(section, false);
        } else {
            showWelcomeScreen();
        }
    }
});

// Handle login
async function handleLogin(e) {
    e.preventDefault();
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;
    
    if (!username || !password) {
        showError('Por favor, preencha usuário e senha.');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            authToken = data.token;
            currentUser = data.user;
            try {
                localStorage.setItem('authToken', authToken);
                localStorage.setItem('currentUser', JSON.stringify(currentUser));
            } catch (storageError) {
                console.error('Error saving to localStorage:', storageError);
                // Continue anyway - session-based auth will handle it
            }
            showMainApp();
            loadConnections();
            loadProjects();
            // Load users and groups if user is admin
            if (currentUser && currentUser.is_admin) {
                loadUsers();
                loadGroups();
            }
            // Show welcome screen on first login
            showWelcomeScreen();
        } else {
            showError(data.message || 'Erro ao fazer login');
        }
    } catch (error) {
        showError('Erro ao fazer login: ' + error.message);
    }
}

// Handle register
async function handleRegister(e) {
    e.preventDefault();
    const username = document.getElementById('regUsername').value;
    const email = document.getElementById('regEmail').value;
    const password = document.getElementById('regPassword').value;
    
    try {
        const response = await fetch(`${API_BASE}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, email, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showSuccess('Registro realizado com sucesso! Faça login.');
            showLogin();
        } else {
            showError(data.message);
        }
    } catch (error) {
        showError('Erro ao registrar: ' + error.message);
    }
}

// Logout
function logout() {
    try {
        localStorage.removeItem('authToken');
        localStorage.removeItem('currentUser');
    } catch (error) {
        console.error('Error clearing localStorage:', error);
    }
    authToken = null;
    currentUser = null;
    // Redirect to login page
    window.location.href = '/login';
}

// Handle logout from template pages
function handleLogout(e) {
    e.preventDefault();
    fetch('/api/auth/logout', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(() => {
        // Clear any localStorage
        try {
            localStorage.clear();
            sessionStorage.clear();
        } catch (error) {
            console.error('Error clearing storage:', error);
        }
        // Redirect to login
        window.location.href = '/login';
    }).catch(error => {
        console.error('Error logging out:', error);
        // Redirect anyway
        window.location.href = '/login';
    });
}

// Show section
function showSection(section) {
    // Remove active class from all nav links
    document.querySelectorAll('.navbar-nav .nav-link').forEach(link => {
        link.classList.remove('active');
    });
    
    // Add active class to clicked nav link
    const sectionMap = {
        'connections': 0,
        'projects': 1,
        'comparison': 2,
        'dashboard': 3,
        'tables': 4,
        'reports': 5,
        'users': 6,
        'groups': 7
    };
    
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    if (sectionMap.hasOwnProperty(section) && navLinks[sectionMap[section]]) {
        navLinks[sectionMap[section]].classList.add('active');
    }
    
    // Hide welcome section
    const welcomeSection = document.getElementById('welcomeSection');
    if (welcomeSection) {
        welcomeSection.style.display = 'none';
    }
    
    // Only manipulate sections if we're on the SPA page (not template pages)
    const mainApp = document.getElementById('mainApp');
    if (!mainApp) {
        // We're on a template page, don't manipulate sections
        return;
    }
    
    // Hide all sections (only on SPA page)
    const sectionsToHide = [
        'connectionsSection',
        'projectsSection',
        'comparisonSection',
        'dashboardSection',
        'tablesSection',
        'reportsSection',
        'usersSection',
        'groupsSection'
    ];
    
    sectionsToHide.forEach(sectionId => {
        const element = document.getElementById(sectionId);
        if (element) {
            element.style.display = 'none';
        }
    });
    
    // Show selected section
    if (section === 'connections') {
        document.getElementById('connectionsSection').style.display = 'block';
        loadConnections();
    } else if (section === 'projects') {
        document.getElementById('projectsSection').style.display = 'block';
        loadProjects();
    } else if (section === 'comparison') {
        document.getElementById('comparisonSection').style.display = 'block';
        populateComparisonProjectSelect();
        // Clear selection when entering comparison section
        document.querySelectorAll('.comparison-project-card').forEach(card => {
            card.classList.remove('border-primary', 'border-3');
        });
        document.getElementById('projectComparisonInfo').style.display = 'none';
    } else if (section === 'dashboard') {
        document.getElementById('dashboardSection').style.display = 'block';
        // Set default dates to today
        const today = new Date();
        const startDateInput = document.getElementById('dashboardStartDate');
        const endDateInput = document.getElementById('dashboardEndDate');
        
        if (startDateInput && !startDateInput.value) {
            today.setHours(0, 0, 0, 0);
            startDateInput.value = today.toISOString().slice(0, 16);
        }
        
        if (endDateInput && !endDateInput.value) {
            const todayEnd = new Date();
            todayEnd.setHours(23, 59, 59, 999);
            endDateInput.value = todayEnd.toISOString().slice(0, 16);
        }
        
        if (currentProject) {
            loadDashboard();
        }
    } else if (section === 'tables') {
        document.getElementById('tablesSection').style.display = 'block';
        populateTableConnectionSelect();
    } else if (section === 'reports') {
        document.getElementById('reportsSection').style.display = 'block';
        populateReportsProjectSelect();
        loadReports();
    } else if (section === 'users') {
        // Check if user is admin
        if (!currentUser || !currentUser.is_admin) {
            showError('Acesso negado. Apenas administradores podem gerenciar usuários.');
            return;
        }
        document.getElementById('usersSection').style.display = 'block';
        loadUsers();
    } else if (section === 'groups') {
        // Check if user is admin
        if (!currentUser || !currentUser.is_admin) {
            showError('Acesso negado. Apenas administradores podem gerenciar grupos.');
            return;
        }
        if (document.getElementById('groupsSection')) {
            document.getElementById('groupsSection').style.display = 'block';
            loadGroups();
        }
    }
}

// Load projects
async function loadProjects() {
    try {
        const response = await fetch(`${API_BASE}/projects`, {
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'X-User-Id': currentUser.id
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            projects = data.projects;
            renderProjects();
            populateComparisonProjectSelect();
            populateDashboardProjectSelect();
            populateReportsProjectSelect();
        }
    } catch (error) {
        console.error('Error loading projects:', error);
    }
}

// Populate comparison project select (now renders as cards)
function populateComparisonProjectSelect() {
    const container = document.getElementById('comparisonProjectsList');
    if (!container) return;
    
    if (projects.length === 0) {
        container.innerHTML = '<div class="col-12"><div class="alert alert-info">Nenhum projeto encontrado. Crie um novo projeto para começar.</div></div>';
        return;
    }
    
    container.innerHTML = projects.map(project => `
        <div class="col-md-4 mb-3">
            <div class="card project-card comparison-project-card" onclick="selectProjectForComparison(${project.id})" id="comparisonProjectCard_${project.id}">
                <div class="card-body">
                    <h5 class="card-title">${project.name}</h5>
                    <p class="card-text text-muted small">${project.description || 'Sem descrição'}</p>
                    <div class="d-flex justify-content-between align-items-center">
                        <small class="text-muted">
                            <i class="fas fa-table me-1"></i>${project.source_table} → ${project.target_table}
                        </small>
                        <i class="fas fa-chevron-right text-primary"></i>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

// Select project for comparison
function selectProjectForComparison(projectId) {
    // Show loading modal
    const loadingModalEl = document.getElementById('loadingModal');
    let loadingModal = bootstrap.Modal.getInstance(loadingModalEl);
    if (!loadingModal) {
        loadingModal = new bootstrap.Modal(loadingModalEl);
    }
    
    document.getElementById('loadingMessage').textContent = 'Carregando informações do projeto...';
    document.getElementById('loadingDetails').textContent = 'Aguarde enquanto carregamos as informações das tabelas.';
    loadingModal.show();
    
    // Remove active class from all cards
    document.querySelectorAll('.comparison-project-card').forEach(card => {
        card.classList.remove('border-primary', 'border-3');
    });
    
    // Add active class to selected card
    const selectedCard = document.getElementById(`comparisonProjectCard_${projectId}`);
    if (selectedCard) {
        selectedCard.classList.add('border-primary', 'border-3');
    }
    
    // Load project for comparison - modal will be hidden inside loadProjectForComparison
    loadProjectForComparison(projectId, loadingModal);
}

// Render projects
function renderProjects() {
    const container = document.getElementById('projectsList');
    
    if (projects.length === 0) {
        container.innerHTML = '<div class="col-12"><div class="alert alert-info">Nenhum projeto encontrado. Crie um novo projeto para começar.</div></div>';
        return;
    }
    
    container.innerHTML = projects.map(project => `
        <div class="col-md-4">
            <div class="card project-card" onclick="selectProject(${project.id})">
                <div class="card-body">
                    <h5 class="card-title">${project.name}</h5>
                    <p class="card-text text-muted">${project.description || 'Sem descrição'}</p>
                    <div class="d-flex justify-content-between align-items-center">
                        <small class="text-muted">
                            <i class="fas fa-table me-1"></i>${project.source_table} → ${project.target_table}
                        </small>
                        <div>
                            <button class="btn btn-sm btn-outline-primary" onclick="event.stopPropagation(); editProject(${project.id})">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-danger" onclick="event.stopPropagation(); deleteProject(${project.id})">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

// Show create project modal
function showCreateProjectModal() {
    updateSourceDbConfig();
    updateTargetDbConfig();
    // Reset modal state
    document.getElementById('projectConfigStep').style.display = 'block';
    document.getElementById('tableSelectionStep').style.display = 'none';
    document.getElementById('backToConfigBtn').style.display = 'none';
    document.getElementById('nextToTablesBtn').style.display = 'inline-block';
    document.getElementById('createProjectBtn').style.display = 'none';
    new bootstrap.Modal(document.getElementById('createProjectModal')).show();
}

// Test database connection
async function testConnection(type) {
    const dbType = document.getElementById(`${type}DbType`).value;
    let dbConfig = { type: dbType };
    
    if (dbType === 'sqlite') {
        const path = document.getElementById(`${type}DbPath`).value;
        if (!path) {
            showWarning('Informe o caminho do arquivo SQLite');
            return;
        }
        dbConfig.path = path;
    } else {
        dbConfig.host = document.getElementById(`${type}DbHost`).value;
        dbConfig.port = document.getElementById(`${type}DbPort`).value;
        dbConfig.user = document.getElementById(`${type}DbUser`).value;
        dbConfig.password = document.getElementById(`${type}DbPassword`).value;
        dbConfig.database = document.getElementById(`${type}DbName`).value;
    }
    
    try {
        const response = await fetch(`${API_BASE}/tables/test-connection`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`,
                'X-User-Id': currentUser.id
            },
            body: JSON.stringify({ db_config: dbConfig })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showSuccess('Conexão bem-sucedida!');
        } else {
            showError('Erro na conexão: ' + data.message);
        }
    } catch (error) {
        showError('Erro ao testar conexão: ' + error.message);
    }
}

// Load tables for project creation
async function loadTablesForProject() {
    const sourceType = document.getElementById('sourceDbType').value;
    const targetType = document.getElementById('targetDbType').value;
    
    let sourceConfig = { type: sourceType };
    let targetConfig = { type: targetType };
    
    if (sourceType === 'sqlite') {
        sourceConfig.path = document.getElementById('sourceDbPath').value;
    } else {
        sourceConfig.host = document.getElementById('sourceDbHost').value;
        sourceConfig.port = document.getElementById('sourceDbPort').value;
        sourceConfig.user = document.getElementById('sourceDbUser').value;
        sourceConfig.password = document.getElementById('sourceDbPassword').value;
        sourceConfig.database = document.getElementById('sourceDbName').value;
    }
    
    if (targetType === 'sqlite') {
        targetConfig.path = document.getElementById('targetDbPath').value;
    } else {
        targetConfig.host = document.getElementById('targetDbHost').value;
        targetConfig.port = document.getElementById('targetDbPort').value;
        targetConfig.user = document.getElementById('targetDbUser').value;
        targetConfig.password = document.getElementById('targetDbPassword').value;
        targetConfig.database = document.getElementById('targetDbName').value;
    }
    
    try {
        // Test connections first
        const sourceTest = await fetch(`${API_BASE}/tables/test-connection`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`,
                'X-User-Id': currentUser.id
            },
            body: JSON.stringify({ db_config: sourceConfig })
        });
        
        const targetTest = await fetch(`${API_BASE}/tables/test-connection`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`,
                'X-User-Id': currentUser.id
            },
            body: JSON.stringify({ db_config: targetConfig })
        });
        
        const sourceTestData = await sourceTest.json();
        const targetTestData = await targetTest.json();
        
        if (!sourceTestData.success) {
            showError('Erro na conexão origem: ' + sourceTestData.message);
            return;
        }
        
        if (!targetTestData.success) {
            showError('Erro na conexão destino: ' + targetTestData.message);
            return;
        }
        
        // Load tables
        const sourceTables = await listTables(sourceConfig);
        const targetTables = await listTables(targetConfig);
        
        if (sourceTables.length === 0) {
            showWarning('Nenhuma tabela encontrada no banco origem.');
            return;
        }
        
        if (targetTables.length === 0) {
            showWarning('Nenhuma tabela encontrada no banco destino.');
            return;
        }
        
        // Populate table selects
        const sourceSelect = document.getElementById('modalSourceTableSelect');
        const targetSelect = document.getElementById('modalTargetTableSelect');
        
        sourceSelect.innerHTML = sourceTables.map(t => `<option value="${t}">${t}</option>`).join('');
        targetSelect.innerHTML = targetTables.map(t => `<option value="${t}">${t}</option>`).join('');
        
        // Store configs for later use
        window.tempSourceConfig = sourceConfig;
        window.tempTargetConfig = targetConfig;
        
        // Show table selection step
        document.getElementById('projectConfigStep').style.display = 'none';
        document.getElementById('tableSelectionStep').style.display = 'block';
        document.getElementById('backToConfigBtn').style.display = 'inline-block';
        document.getElementById('nextToTablesBtn').style.display = 'none';
        document.getElementById('createProjectBtn').style.display = 'inline-block';
        
        // Add event listeners for table selection
        sourceSelect.addEventListener('change', () => updateModalTableInfo('source', sourceSelect.value, sourceConfig));
        targetSelect.addEventListener('change', () => updateModalTableInfo('target', targetSelect.value, targetConfig));
        
    } catch (error) {
        showError('Erro ao carregar tabelas: ' + error.message);
    }
}

// Update table info in modal
async function updateModalTableInfo(type, tableName, dbConfig) {
    if (!tableName) return;
    
    const info = await getTableInfo(dbConfig, tableName);
    const infoDiv = document.getElementById(`modal${type.charAt(0).toUpperCase() + type.slice(1)}TableInfo`);
    
    infoDiv.innerHTML = `
        <strong>Colunas:</strong> ${info.columns.length}<br>
        <strong>Linhas:</strong> ${info.row_count}<br>
        <strong>Chaves Primárias:</strong> ${info.primary_keys.join(', ') || 'Nenhuma'}
    `;
}

// Back to config step
function backToConfig() {
    document.getElementById('projectConfigStep').style.display = 'block';
    document.getElementById('tableSelectionStep').style.display = 'none';
    document.getElementById('backToConfigBtn').style.display = 'none';
    document.getElementById('nextToTablesBtn').style.display = 'inline-block';
    document.getElementById('nextToTablesBtn').disabled = true;
    document.getElementById('createProjectBtn').style.display = 'none';
}

// Update database config fields
function updateSourceDbConfig() {
    const type = document.getElementById('sourceDbType').value;
    const container = document.getElementById('sourceDbConfig');
    
    if (type === 'sqlite') {
        container.innerHTML = `
            <div class="mb-2">
                <label class="form-label">Caminho do arquivo</label>
                <input type="text" class="form-control" id="sourceDbPath" placeholder="instance/deltascope.db">
            </div>
        `;
    } else {
        container.innerHTML = `
            <div class="mb-2">
                <label class="form-label">Host</label>
                <input type="text" class="form-control" id="sourceDbHost" value="localhost">
            </div>
            <div class="mb-2">
                <label class="form-label">Porta</label>
                <input type="number" class="form-control" id="sourceDbPort" value="3306">
            </div>
            <div class="mb-2">
                <label class="form-label">Usuário</label>
                <input type="text" class="form-control" id="sourceDbUser" value="root">
            </div>
            <div class="mb-2">
                <label class="form-label">Senha</label>
                <input type="password" class="form-control" id="sourceDbPassword">
            </div>
            <div class="mb-2">
                <label class="form-label">Database</label>
                <input type="text" class="form-control" id="sourceDbName">
            </div>
        `;
    }
}

function updateTargetDbConfig() {
    const type = document.getElementById('targetDbType').value;
    const container = document.getElementById('targetDbConfig');
    
    if (type === 'sqlite') {
        container.innerHTML = `
            <div class="mb-2">
                <label class="form-label">Caminho do arquivo</label>
                <input type="text" class="form-control" id="targetDbPath" placeholder="instance/deltascope.db">
            </div>
        `;
    } else {
        container.innerHTML = `
            <div class="mb-2">
                <label class="form-label">Host</label>
                <input type="text" class="form-control" id="targetDbHost" value="localhost">
            </div>
            <div class="mb-2">
                <label class="form-label">Porta</label>
                <input type="number" class="form-control" id="targetDbPort" value="3306">
            </div>
            <div class="mb-2">
                <label class="form-label">Usuário</label>
                <input type="text" class="form-control" id="targetDbUser" value="root">
            </div>
            <div class="mb-2">
                <label class="form-label">Senha</label>
                <input type="password" class="form-control" id="targetDbPassword">
            </div>
            <div class="mb-2">
                <label class="form-label">Database</label>
                <input type="text" class="form-control" id="targetDbName">
            </div>
        `;
    }
}

// Create project
async function createProject() {
    const name = document.getElementById('projectName').value;
    const description = document.getElementById('projectDescription').value;
    const sourceTable = document.getElementById('modalSourceTableSelect').value;
    const targetTable = document.getElementById('modalTargetTableSelect').value;
    
    if (!sourceTable || !targetTable) {
        showWarning('Selecione ambas as tabelas antes de criar o projeto.');
        return;
    }
    
    if (!window.tempSourceConfig || !window.tempTargetConfig) {
        showError('Configurações de banco não encontradas. Volte e configure novamente.');
        return;
    }
    
    const projectData = {
        name,
        description,
        source_table: sourceTable,
        target_table: targetTable,
        source_db_config: window.tempSourceConfig,
        target_db_config: window.tempTargetConfig
    };
    
    try {
        const response = await fetch(`${API_BASE}/projects`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`,
                'X-User-Id': currentUser.id
            },
            body: JSON.stringify(projectData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            bootstrap.Modal.getInstance(document.getElementById('createProjectModal')).hide();
            loadProjects();
            showSuccess('Projeto criado com sucesso!');
            // Clear temp configs
            window.tempSourceConfig = null;
            window.tempTargetConfig = null;
        } else {
            showError(data.message);
        }
    } catch (error) {
        showError('Erro ao criar projeto: ' + error.message);
    }
}

// List tables
async function listTables(dbConfig) {
    const response = await fetch(`${API_BASE}/tables/list`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${authToken}`,
            'X-User-Id': currentUser.id
        },
        body: JSON.stringify({ db_config: dbConfig })
    });
    
    const data = await response.json();
    return response.ok ? data.tables : [];
}

// Select project (for project list)
function selectProject(projectId) {
    currentProject = projects.find(p => p.id === projectId);
    showSection('comparison');
    // Select project card in comparison section
    selectProjectForComparison(projectId);
}

// Load project for comparison
async function loadProjectForComparison(projectId, loadingModalInstance = null) {
    // If projectId is not provided, try to get from selected card
    if (!projectId) {
        const selectedCard = document.querySelector('.comparison-project-card.border-primary');
        if (selectedCard) {
            const cardId = selectedCard.id;
            projectId = parseInt(cardId.replace('comparisonProjectCard_', ''));
        }
    }
    
    const loadingModalEl = document.getElementById('loadingModal');
    let loadingModal = loadingModalInstance || bootstrap.Modal.getInstance(loadingModalEl);
    
    if (!projectId) {
        document.getElementById('projectComparisonInfo').style.display = 'none';
        if (loadingModal) {
            loadingModal.hide();
        }
        return;
    }
    
    currentProject = projects.find(p => p.id == projectId);
    
    if (!currentProject) {
        showError('Projeto não encontrado.');
        if (loadingModal) {
            loadingModal.hide();
        }
        return;
    }
    
    try {
        const sourceConnId = currentProject.source_connection_id;
        const targetConnId = currentProject.target_connection_id;
        const sourceTable = currentProject.source_table;
        const targetTable = currentProject.target_table;
        
        // Update loading message
        const isModalShown = loadingModalEl && loadingModalEl.classList.contains('show');
        
        if (isModalShown) {
            document.getElementById('loadingDetails').textContent = `Carregando informações da tabela ${sourceTable}...`;
        }
        
        // Update project info display immediately
        document.getElementById('selectedProjectName').textContent = currentProject.name;
        document.getElementById('selectedSourceTable').textContent = sourceTable;
        document.getElementById('selectedTargetTable').textContent = targetTable;
        
        // Display table info - load both in parallel for faster loading
        const [sourceInfo, targetInfo] = await Promise.all([
            updateTableInfoForComparison('source', sourceConnId, sourceTable).catch(err => {
                console.error('Error loading source table info:', err);
                return null;
            }),
            updateTableInfoForComparison('target', targetConnId, targetTable).catch(err => {
                console.error('Error loading target table info:', err);
                return null;
            })
        ]);
        
        // Hide loading modal immediately after data is loaded
        if (loadingModal) {
            loadingModal.hide();
            // Force cleanup of backdrop
            setTimeout(() => {
                const backdrops = document.querySelectorAll('.modal-backdrop');
                backdrops.forEach(backdrop => {
                    if (!document.querySelector('.modal.show')) {
                        backdrop.remove();
                    }
                });
            }, 150);
        }
        
        // Show project comparison info
        document.getElementById('projectComparisonInfo').style.display = 'block';
        
        // Enable compare button
        document.getElementById('compareBtn').disabled = false;
        
        // Scroll to comparison info smoothly
        setTimeout(() => {
            document.getElementById('projectComparisonInfo').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }, 100);
        
    } catch (error) {
        console.error('Error loading project for comparison:', error);
        showError('Erro ao carregar informações do projeto: ' + error.message);
        // Hide loading modal on error
        if (loadingModal) {
            loadingModal.hide();
            setTimeout(() => {
                const backdrops = document.querySelectorAll('.modal-backdrop');
                backdrops.forEach(backdrop => {
                    if (!document.querySelector('.modal.show')) {
                        backdrop.remove();
                    }
                });
            }, 150);
        }
    }
}

// Load tables for comparison (deprecated - kept for compatibility)
async function loadTablesForComparison() {
    // This function is now handled by loadProjectForComparison
    // But we keep it for compatibility
    const selectedCard = document.querySelector('.comparison-project-card.border-primary');
    if (selectedCard) {
        const cardId = selectedCard.id;
        const projectId = parseInt(cardId.replace('comparisonProjectCard_', ''));
        if (projectId) {
            await loadProjectForComparison(projectId);
        }
    }
}

// Update table info for comparison
async function updateTableInfoForComparison(type, connectionId, tableName) {
    if (!tableName) {
        document.getElementById(`${type}TableInfo`).innerHTML = '';
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/connections/${connectionId}/tables/${tableName}/info`, {
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'X-User-Id': currentUser.id
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            const infoDiv = document.getElementById(`${type}TableInfo`);
            infoDiv.innerHTML = `
                <div class="table-info">
                    <p><strong>Tabela:</strong> ${tableName}</p>
                    <p><strong>Colunas:</strong> ${data.columns.length}</p>
                    <p><strong>Linhas:</strong> ${data.row_count.toLocaleString('pt-BR')}</p>
                    <p><strong>Chaves Primárias:</strong> ${data.primary_keys.join(', ') || 'Nenhuma'}</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading table info:', error);
        const infoDiv = document.getElementById(`${type}TableInfo`);
        infoDiv.innerHTML = `<div class="alert alert-warning">Erro ao carregar informações da tabela</div>`;
    }
}


// Get table info
async function getTableInfo(dbConfig, tableName) {
    const response = await fetch(`${API_BASE}/tables/columns`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${authToken}`,
            'X-User-Id': currentUser.id
        },
        body: JSON.stringify({ db_config: dbConfig, table_name: tableName })
    });
    
    const data = await response.json();
    return response.ok ? data : {};
}

// Store selected primary key mappings
let selectedPrimaryKeyMappings = [];

// Clear all checkboxes in primary key modal
function clearAllPrimaryKeyCheckboxes() {
    // Clear all source checkboxes
    document.querySelectorAll('.source-column-checkbox').forEach(checkbox => {
        checkbox.checked = false;
    });
    
    // Clear all target checkboxes
    document.querySelectorAll('.target-column-checkbox').forEach(checkbox => {
        checkbox.checked = false;
    });
    
    // Clear mappings
    selectedPrimaryKeyMappings = [];
    document.getElementById('keyMappingsList').innerHTML = '<p class="text-muted text-center mb-0">Nenhum mapeamento selecionado ainda.</p>';
    document.getElementById('primaryKeyWarning').style.display = 'none';
}

// Show primary key mapping modal
async function showPrimaryKeySelection() {
    if (!currentProject) {
        showError('Selecione um projeto primeiro.');
        return;
    }
    
    const sourceTable = currentProject.source_table;
    const targetTable = currentProject.target_table;
    
    if (!sourceTable || !targetTable) {
        showError('Projeto não possui tabelas configuradas.');
        return;
    }
    
    // Clear all checkboxes and mappings first
    clearAllPrimaryKeyCheckboxes();
    
    try {
        // Get table columns from both connections
        const sourceConnId = currentProject.source_connection_id;
        const targetConnId = currentProject.target_connection_id;
        
        const [sourceInfoResponse, targetInfoResponse] = await Promise.all([
            fetch(`${API_BASE}/connections/${sourceConnId}/tables/${sourceTable}/info`, {
                headers: {
                    'Authorization': `Bearer ${authToken}`,
                    'X-User-Id': currentUser.id
                }
            }),
            fetch(`${API_BASE}/connections/${targetConnId}/tables/${targetTable}/info`, {
                headers: {
                    'Authorization': `Bearer ${authToken}`,
                    'X-User-Id': currentUser.id
                }
            })
        ]);
        
        const sourceInfo = await sourceInfoResponse.json();
        const targetInfo = await targetInfoResponse.json();
        
        if (!sourceInfo.columns || sourceInfo.columns.length === 0) {
            showError('Não foi possível carregar as colunas da tabela origem.');
            return;
        }
        
        if (!targetInfo.columns || targetInfo.columns.length === 0) {
            showError('Não foi possível carregar as colunas da tabela destino.');
            return;
        }
        
        // Update table names
        document.getElementById('sourceTableNameModal').textContent = sourceTable;
        document.getElementById('targetTableNameModal').textContent = targetTable;
        
        // Populate source columns
        const sourceContainer = document.getElementById('sourceColumnsList');
        sourceContainer.innerHTML = '';
        sourceInfo.columns.forEach(column => {
            const checkbox = `
                <div class="form-check mb-2 source-column-item" data-column="${column.name}">
                    <input class="form-check-input source-column-checkbox" type="checkbox" value="${column.name}" 
                           id="src_${column.name}" onchange="updateKeyMappings()">
                    <label class="form-check-label" for="src_${column.name}">
                        <strong>${column.name}</strong> <span class="text-muted">(${column.type})</span>
                    </label>
                </div>
            `;
            sourceContainer.insertAdjacentHTML('beforeend', checkbox);
        });
        
        // Populate target columns
        const targetContainer = document.getElementById('targetColumnsList');
        targetContainer.innerHTML = '';
        targetInfo.columns.forEach(column => {
            const checkbox = `
                <div class="form-check mb-2 target-column-item" data-column="${column.name}">
                    <input class="form-check-input target-column-checkbox" type="checkbox" value="${column.name}" 
                           id="tgt_${column.name}" onchange="updateKeyMappings()">
                    <label class="form-check-label" for="tgt_${column.name}">
                        <strong>${column.name}</strong> <span class="text-muted">(${column.type})</span>
                    </label>
                </div>
            `;
            targetContainer.insertAdjacentHTML('beforeend', checkbox);
        });
        
        // Don't auto-map - let user select manually
        // All checkboxes start unchecked
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('primaryKeyModal'));
        
        // Clear checkboxes when modal is hidden
        const modalElement = document.getElementById('primaryKeyModal');
        modalElement.addEventListener('hidden.bs.modal', function() {
            clearAllPrimaryKeyCheckboxes();
        }, { once: true });
        
        modal.show();
        
        // Hide warning initially
        document.getElementById('primaryKeyWarning').style.display = 'none';
        selectedPrimaryKeyMappings = [];
        
        // Ensure all checkboxes are unchecked after modal is shown
        setTimeout(() => {
            clearAllPrimaryKeyCheckboxes();
        }, 100);
    } catch (error) {
        showError('Erro ao carregar informações das tabelas: ' + error.message);
    }
}

// Update key mappings display
function updateKeyMappings() {
    const sourceChecked = Array.from(document.querySelectorAll('.source-column-checkbox:checked')).map(cb => cb.value);
    const targetChecked = Array.from(document.querySelectorAll('.target-column-checkbox:checked')).map(cb => cb.value);
    
    const mappingsContainer = document.getElementById('keyMappingsList');
    
    if (sourceChecked.length === 0 || targetChecked.length === 0) {
        mappingsContainer.innerHTML = '<p class="text-muted text-center mb-0">Selecione campos em ambas as tabelas para criar mapeamentos.</p>';
        selectedPrimaryKeyMappings = [];
        return;
    }
    
    // Create mappings - match by order (first selected source with first selected target, etc.)
    const mappings = [];
    const minLength = Math.min(sourceChecked.length, targetChecked.length);
    
    // Try to match by name first (exact or case-insensitive)
    const matchedSources = [];
    const matchedTargets = [];
    
    sourceChecked.forEach(srcCol => {
        const exactMatch = targetChecked.find(tgtCol => tgtCol === srcCol);
        const caseMatch = targetChecked.find(tgtCol => !exactMatch && tgtCol.toLowerCase() === srcCol.toLowerCase());
        const matchingTarget = exactMatch || caseMatch;
        
        if (matchingTarget && !matchedTargets.includes(matchingTarget)) {
            mappings.push({ source: srcCol, target: matchingTarget });
            matchedSources.push(srcCol);
            matchedTargets.push(matchingTarget);
        }
    });
    
    // Add remaining unmatched columns in order
    let targetIndex = 0;
    sourceChecked.forEach(srcCol => {
        if (!matchedSources.includes(srcCol)) {
            // Find next unmatched target
            while (targetIndex < targetChecked.length && matchedTargets.includes(targetChecked[targetIndex])) {
                targetIndex++;
            }
            if (targetIndex < targetChecked.length) {
                mappings.push({ source: srcCol, target: targetChecked[targetIndex] });
                matchedSources.push(srcCol);
                matchedTargets.push(targetChecked[targetIndex]);
                targetIndex++;
            }
        }
    });
    
    // Display mappings
    if (mappings.length === 0) {
        mappingsContainer.innerHTML = '<p class="text-muted text-center mb-0">Nenhum mapeamento válido. Selecione campos correspondentes.</p>';
        selectedPrimaryKeyMappings = [];
    } else {
        mappingsContainer.innerHTML = mappings.map((mapping, index) => `
            <div class="d-flex justify-content-between align-items-center mb-2 p-2 bg-white rounded border" data-mapping-index="${index}">
                <div class="d-flex align-items-center">
                    <span class="badge bg-primary me-2">${mapping.source}</span>
                    <i class="fas fa-arrow-right mx-2 text-muted"></i>
                    <span class="badge bg-success">${mapping.target}</span>
                </div>
                <button class="btn btn-sm btn-outline-danger" onclick="removeMapping(${index})" title="Remover mapeamento">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `).join('');
        
        selectedPrimaryKeyMappings = mappings;
    }
}

// Remove a mapping
function removeMapping(index) {
    if (selectedPrimaryKeyMappings[index]) {
        const mapping = selectedPrimaryKeyMappings[index];
        // Uncheck checkboxes
        const sourceCheckbox = document.getElementById(`src_${mapping.source}`);
        const targetCheckbox = document.getElementById(`tgt_${mapping.target}`);
        if (sourceCheckbox) sourceCheckbox.checked = false;
        if (targetCheckbox) targetCheckbox.checked = false;
        
        // Update mappings
        updateKeyMappings();
    }
}

// Confirm primary keys and run comparison
function confirmPrimaryKeysAndRun() {
    if (selectedPrimaryKeyMappings.length === 0) {
        document.getElementById('primaryKeyWarning').style.display = 'block';
        return;
    }
    
    // Show loading modal before closing primary key modal
    const loadingModal = new bootstrap.Modal(document.getElementById('loadingModal'));
    document.getElementById('loadingMessage').textContent = 'Preparando comparação...';
    document.getElementById('loadingDetails').textContent = 'Aguarde enquanto preparamos a execução da comparação.';
    loadingModal.show();
    
    // Hide primary key modal
    const modal = bootstrap.Modal.getInstance(document.getElementById('primaryKeyModal'));
    modal.hide();
    
    // Clear checkboxes after modal is hidden
    setTimeout(() => {
        clearAllPrimaryKeyCheckboxes();
        // Now run comparison (loading modal is already showing)
        runComparison();
    }, 300);
}

// Run comparison
async function runComparison() {
    if (!currentProject) {
        // Hide loading if showing
        const loadingModal = bootstrap.Modal.getInstance(document.getElementById('loadingModal'));
        if (loadingModal) {
            loadingModal.hide();
        }
        showError('Selecione um projeto primeiro.');
        return;
    }
    
    // Use project's configured tables
    const sourceTable = currentProject.source_table;
    const targetTable = currentProject.target_table;
    
    if (!sourceTable || !targetTable) {
        // Hide loading if showing
        const loadingModal = bootstrap.Modal.getInstance(document.getElementById('loadingModal'));
        if (loadingModal) {
            loadingModal.hide();
        }
        showError('Projeto não possui tabelas configuradas.');
        return;
    }
    
    // Use selected primary key mappings
    if (selectedPrimaryKeyMappings.length === 0) {
        // Hide loading if showing
        const loadingModal = bootstrap.Modal.getInstance(document.getElementById('loadingModal'));
        if (loadingModal) {
            loadingModal.hide();
        }
        showError('Nenhuma chave primária mapeada.');
        return;
    }
    
    // Extract source keys for API (backend will handle mapping)
    const sourceKeys = selectedPrimaryKeyMappings.map(m => m.source);
    const keyMappings = selectedPrimaryKeyMappings.reduce((acc, m) => {
        acc[m.source] = m.target;
        return acc;
    }, {});
    
    // Hide previous results
    document.getElementById('comparisonResults').style.display = 'none';
    currentComparisonResults = null;
    
    // Get or create loading modal
    let loadingModal = bootstrap.Modal.getInstance(document.getElementById('loadingModal'));
    if (!loadingModal) {
        loadingModal = new bootstrap.Modal(document.getElementById('loadingModal'));
    }
    
    // Update loading message
    document.getElementById('loadingMessage').textContent = 'Executando comparação...';
    const mappingsText = selectedPrimaryKeyMappings.map(m => `${m.source} ↔ ${m.target}`).join(', ');
    document.getElementById('loadingDetails').textContent = `Comparando ${sourceTable} com ${targetTable} usando chaves: ${mappingsText}`;
    
    // Show loading modal if not already showing
    const loadingModalEl = document.getElementById('loadingModal');
    if (!loadingModalEl.classList.contains('show')) {
        loadingModal.show();
    }
    
    const btn = document.getElementById('compareBtn');
    btn.disabled = true;
    
    try {
        // Update loading message
        document.getElementById('loadingDetails').textContent = 'Processando dados e identificando diferenças...';
        
        const response = await fetch(`${API_BASE}/comparisons/project/${currentProject.id}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`,
                'X-User-Id': currentUser.id
            },
            body: JSON.stringify({
                source_table: sourceTable,
                target_table: targetTable,
                primary_keys: sourceKeys,
                key_mappings: keyMappings
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Update loading message
            document.getElementById('loadingDetails').textContent = 'Carregando resultados detalhados...';
            
            // Load detailed results
            try {
                await loadComparisonResults(data.comparison.id);
                
                // Scroll to results
                setTimeout(() => {
                    document.getElementById('comparisonResults').scrollIntoView({ behavior: 'smooth' });
                }, 100);
            } catch (loadError) {
                console.error('Error loading comparison results:', loadError);
                showError('Erro ao carregar resultados detalhados: ' + loadError.message);
            }
        } else {
            showError(data.message || 'Erro ao executar comparação');
        }
    } catch (error) {
        console.error('Error running comparison:', error);
        showError('Erro ao executar comparação: ' + error.message);
    } finally {
        // Always hide loading modal when done
        if (loadingModal) {
            loadingModal.hide();
            // Clean up backdrop
            setTimeout(() => {
                const backdrops = document.querySelectorAll('.modal-backdrop');
                backdrops.forEach(backdrop => {
                    if (!document.querySelector('.modal.show')) {
                        backdrop.remove();
                    }
                });
            }, 150);
        }
        
        btn.disabled = false;
        // Reset selected mappings and clear checkboxes
        selectedPrimaryKeyMappings = [];
        clearAllPrimaryKeyCheckboxes();
    }
}

// Store current comparison results globally
let currentComparisonResults = null;

// Load detailed comparison results
async function loadComparisonResults(comparisonId) {
    try {
        const response = await fetch(`${API_BASE}/comparisons/${comparisonId}/results`, {
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'X-User-Id': currentUser.id
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentComparisonResults = data;
            displayComparisonResults(data);
        } else {
            showError(data.message);
        }
    } catch (error) {
        showError('Erro ao carregar resultados: ' + error.message);
    }
}

// Display comparison results
function displayComparisonResults(data) {
    const container = document.getElementById('comparisonResults');
    const results = data.results || [];
    
    // Calculate statistics
    const totalDifferences = results.length;
    const modified = results.filter(r => r.change_type === 'modified').length;
    const added = results.filter(r => r.change_type === 'added').length;
    const deleted = results.filter(r => r.change_type === 'deleted').length;
    
    // Update statistics cards
    document.getElementById('totalDifferences').textContent = totalDifferences;
    document.getElementById('totalModified').textContent = modified;
    document.getElementById('totalAdded').textContent = added;
    document.getElementById('totalDeleted').textContent = deleted;
    
    // Populate table
    const tbody = document.getElementById('resultsTableBody');
    tbody.innerHTML = '';
    
    if (results.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center">Nenhuma diferença encontrada!</td></tr>';
    } else {
        results.forEach(result => {
            const changeTypeBadge = getChangeTypeBadge(result.change_type);
            const row = `
                <tr>
                    <td>${result.record_id || 'N/A'}</td>
                    <td><strong>${result.field_name}</strong></td>
                    <td>${formatValue(result.source_value)}</td>
                    <td>${formatValue(result.target_value)}</td>
                    <td>${changeTypeBadge}</td>
                </tr>
            `;
            tbody.insertAdjacentHTML('beforeend', row);
        });
    }
    
    // Show results section
    container.style.display = 'block';
}

// Format value for display
function formatValue(value) {
    if (value === null || value === undefined) {
        return '<span class="text-muted fst-italic">(vazio)</span>';
    }
    if (typeof value === 'string' && value.length > 50) {
        return `<span title="${value}">${value.substring(0, 50)}...</span>`;
    }
    return String(value);
}

// Get badge for change type
function getChangeTypeBadge(type) {
    const badges = {
        'modified': '<span class="badge bg-warning">Modificado</span>',
        'added': '<span class="badge bg-success">Adicionado</span>',
        'deleted': '<span class="badge bg-danger">Removido</span>'
    };
    return badges[type] || `<span class="badge bg-secondary">${type}</span>`;
}

// Export results
function exportResults(format) {
    if (!currentComparisonResults || !currentComparisonResults.results) {
        showError('Nenhum resultado disponível para exportar.');
        return;
    }
    
    const results = currentComparisonResults.results;
    const comparison = currentComparisonResults.comparison;
    const projectName = currentProject ? currentProject.name : 'comparison';
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `${projectName}_comparison_${timestamp}`;
    
    let content = '';
    let mimeType = '';
    let extension = '';
    
    switch(format) {
        case 'csv':
            content = exportToCSV(results);
            mimeType = 'text/csv';
            extension = 'csv';
            break;
        case 'json':
            content = exportToJSON(currentComparisonResults);
            mimeType = 'application/json';
            extension = 'json';
            break;
        case 'txt':
            content = exportToTXT(results, comparison);
            mimeType = 'text/plain';
            extension = 'txt';
            break;
        default:
            showError('Formato de exportação não suportado.');
            return;
    }
    
    // Create download link
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${filename}.${extension}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    showSuccess(`Arquivo ${extension.toUpperCase()} exportado com sucesso!`);
}

// Export to CSV
function exportToCSV(results) {
    const headers = ['ID do Registro', 'Campo', 'Valor Origem', 'Valor Destino', 'Tipo de Mudança'];
    const rows = results.map(r => [
        r.record_id || '',
        r.field_name || '',
        r.source_value || '',
        r.target_value || '',
        r.change_type || ''
    ]);
    
    const csvContent = [
        headers.join(','),
        ...rows.map(row => row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(','))
    ].join('\n');
    
    // Add BOM for Excel compatibility
    return '\uFEFF' + csvContent;
}

// Export to JSON
function exportToJSON(data) {
    return JSON.stringify(data, null, 2);
}

// Export to TXT
function exportToTXT(results, comparison) {
    let txt = '='.repeat(80) + '\n';
    txt += 'RELATÓRIO DE COMPARAÇÃO\n';
    txt += '='.repeat(80) + '\n\n';
    txt += `Data/Hora: ${new Date(comparison.executed_at).toLocaleString('pt-BR')}\n`;
    txt += `Total de Diferenças: ${results.length}\n`;
    txt += `\n${'='.repeat(80)}\n\n`;
    
    results.forEach((result, index) => {
        txt += `Diferença ${index + 1}:\n`;
        txt += `  ID do Registro: ${result.record_id || 'N/A'}\n`;
        txt += `  Campo: ${result.field_name}\n`;
        txt += `  Valor Origem: ${result.source_value || '(vazio)'}\n`;
        txt += `  Valor Destino: ${result.target_value || '(vazio)'}\n`;
        txt += `  Tipo de Mudança: ${result.change_type}\n`;
        txt += `\n${'-'.repeat(80)}\n\n`;
    });
    
    return txt;
}

// Populate dashboard project select
function populateDashboardProjectSelect() {
    const select = document.getElementById('dashboardProjectSelect');
    if (!select) return;
    
    const options = projects.map(p => `<option value="${p.id}">${p.name}</option>`).join('');
    select.innerHTML = '<option value="">Selecione um projeto...</option>' + options;
    
    // Set current project if available
    if (currentProject) {
        select.value = currentProject.id;
    }
}

// Load dashboard
async function loadDashboard() {
    const projectId = document.getElementById('dashboardProjectSelect')?.value;
    
    if (!projectId) {
        // Clear stats if no project selected
        document.getElementById('statTotalComparisons').textContent = '0';
        document.getElementById('statCompletedComparisons').textContent = '0';
        document.getElementById('statTotalDifferences').textContent = '0';
        document.getElementById('statModifiedFields').textContent = '0';
        document.getElementById('changesOverTimeChart').innerHTML = '';
        document.getElementById('fieldChangesChart').innerHTML = '';
        return;
    }
    
    // Set current project
    currentProject = projects.find(p => p.id == projectId);
    
    try {
        // Set today as default date if not set
        const startDateInput = document.getElementById('dashboardStartDate');
        const endDateInput = document.getElementById('dashboardEndDate');
        
        if (!startDateInput.value) {
            const today = new Date();
            today.setHours(0, 0, 0, 0);
            startDateInput.value = today.toISOString().slice(0, 16);
        }
        
        if (!endDateInput.value) {
            const today = new Date();
            today.setHours(23, 59, 59, 999);
            endDateInput.value = today.toISOString().slice(0, 16);
        }
        
        const startDate = startDateInput.value;
        const endDate = endDateInput.value;
        
        let url = `${API_BASE}/dashboard/project/${projectId}/stats`;
        if (startDate) url += `?start_date=${startDate}`;
        if (endDate) url += `${startDate ? '&' : '?'}end_date=${endDate}`;
        
        const response = await fetch(url, {
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'X-User-Id': currentUser.id
            }
        });
        
        if (!response.ok) {
            // Try to get error message
            let errorMsg = 'Erro ao carregar dashboard';
            try {
                const errorData = await response.json();
                errorMsg = errorData.message || errorMsg;
            } catch {
                errorMsg = `Erro ${response.status}: ${response.statusText}`;
            }
            showError(errorMsg);
            return;
        }
        
        const data = await response.json();
        
        document.getElementById('statTotalComparisons').textContent = data.total_comparisons || 0;
        document.getElementById('statCompletedComparisons').textContent = data.completed_comparisons || 0;
        document.getElementById('statTotalDifferences').textContent = data.total_differences || 0;
        document.getElementById('statModifiedFields').textContent = data.modified_fields_count || 0;
        
        loadCharts(projectId, null, startDate, endDate);
    } catch (error) {
        console.error('Error loading dashboard:', error);
        showError('Erro ao carregar dashboard: ' + error.message);
    }
}

// Load charts
async function loadCharts(projectId, period = null, startDate = null, endDate = null) {
    if (!projectId) return;
    
    try {
        let changesUrl = `${API_BASE}/dashboard/project/${projectId}/changes-over-time`;
        const params = [];
        if (startDate) params.push(`start_date=${startDate}`);
        if (endDate) params.push(`end_date=${endDate}`);
        if (params.length > 0) {
            changesUrl += '?' + params.join('&');
        }
        
        const changesResponse = await fetch(changesUrl, {
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'X-User-Id': currentUser.id
            }
        });
        
        const changesData = await changesResponse.json();
        
        if (changesResponse.ok) {
            renderChangesOverTimeChart(changesData.data);
        }
        
        const fieldsResponse = await fetch(`${API_BASE}/dashboard/project/${projectId}/field-changes`, {
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'X-User-Id': currentUser.id
            }
        });
        
        const fieldsData = await fieldsResponse.json();
        
        if (fieldsResponse.ok) {
            renderFieldChangesChart(fieldsData.data);
        }
    } catch (error) {
        console.error('Error loading charts:', error);
    }
}

// Render changes over time chart
function renderChangesOverTimeChart(data) {
    if (!data || Object.keys(data).length === 0) {
        document.getElementById('changesOverTimeChart').innerHTML = '<p class="text-muted text-center">Nenhum dado disponível</p>';
        return;
    }
    
    const dates = Object.keys(data).sort();
    const changeTypes = ['modified', 'added', 'deleted'];
    const traces = [];
    
    changeTypes.forEach(type => {
        const values = dates.map(d => data[d][type] || 0);
        if (values.some(v => v > 0)) {
            traces.push({
                x: dates,
                y: values,
                type: 'scatter',
                mode: 'lines+markers',
                name: type === 'modified' ? 'Modificados' : type === 'added' ? 'Adicionados' : 'Removidos',
                line: { width: 2 }
            });
        }
    });
    
    if (traces.length === 0) {
        document.getElementById('changesOverTimeChart').innerHTML = '<p class="text-muted text-center">Nenhum dado disponível</p>';
        return;
    }
    
    Plotly.newPlot('changesOverTimeChart', traces, {
        title: 'Mudanças ao Longo do Tempo',
        xaxis: { title: 'Data' },
        yaxis: { title: 'Número de Mudanças' },
        hovermode: 'x unified'
    }, {responsive: true});
}

// Render field changes chart (pie chart)
function renderFieldChangesChart(data) {
    if (!data || data.length === 0) {
        document.getElementById('fieldChangesChart').innerHTML = '<p class="text-muted text-center">Nenhum dado disponível</p>';
        return;
    }
    
    const fields = data.map(d => d.field);
    const counts = data.map(d => d.count);
    
    const trace = {
        labels: fields,
        values: counts,
        type: 'pie',
        textinfo: 'label+percent',
        textposition: 'outside',
        hovertemplate: '<b>%{label}</b><br>Quantidade: %{value}<br>Percentual: %{percent}<extra></extra>'
    };
    
    Plotly.newPlot('fieldChangesChart', [trace], {
        title: 'Campos Mais Modificados',
        showlegend: true
    }, {responsive: true});
}

// Populate reports project select
function populateReportsProjectSelect() {
    const select = document.getElementById('reportsProjectSelect');
    if (!select) return;
    
    const options = projects.map(p => `<option value="${p.id}">${p.name}</option>`).join('');
    select.innerHTML = '<option value="">Todos os projetos...</option>' + options;
}

// Load reports
async function loadReports() {
    const projectId = document.getElementById('reportsProjectSelect')?.value;
    const container = document.getElementById('reportsList');
    
    if (!container) return;
    
    try {
        let url = `${API_BASE}/comparisons`;
        if (projectId) {
            url = `${API_BASE}/comparisons/project/${projectId}`;
        }
        
        const response = await fetch(url, {
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'X-User-Id': currentUser.id
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            const comparisons = data.comparisons || [];
            
            if (comparisons.length === 0) {
                container.innerHTML = '<p class="text-muted text-center">Nenhum relatório encontrado.</p>';
                return;
            }
            
            container.innerHTML = comparisons.map(comp => {
                const executedDate = comp.executed_at ? new Date(comp.executed_at).toLocaleString('pt-BR') : 'N/A';
                const projectName = comp.project_name || 'Projeto desconhecido';
                const sourceTable = comp.project_source_table || 'N/A';
                const targetTable = comp.project_target_table || 'N/A';
                
                return `
                    <div class="card mb-3">
                        <div class="card-body">
                            <div class="row align-items-center">
                                <div class="col-md-4">
                                    <h6 class="mb-1"><strong>${projectName}</strong></h6>
                                    <small class="text-muted">${sourceTable} → ${targetTable}</small>
                                </div>
                                <div class="col-md-3">
                                    <small class="text-muted">Data de Execução:</small><br>
                                    <strong>${executedDate}</strong>
                                </div>
                                <div class="col-md-2">
                                    <small class="text-muted">Status:</small><br>
                                    <span class="badge bg-${comp.status === 'completed' ? 'success' : 'warning'}">${comp.status}</span>
                                </div>
                                <div class="col-md-2">
                                    <small class="text-muted">Diferenças:</small><br>
                                    <strong>${comp.total_differences || 0}</strong>
                                </div>
                                <div class="col-md-1 text-end">
                                    <div class="btn-group-vertical">
                                        <button class="btn btn-sm btn-outline-primary" onclick="exportReport(${comp.id}, 'csv')" title="Exportar CSV">
                                            <i class="fas fa-file-csv"></i>
                                        </button>
                                        <button class="btn btn-sm btn-outline-success" onclick="exportReport(${comp.id}, 'json')" title="Exportar JSON">
                                            <i class="fas fa-file-code"></i>
                                        </button>
                                        <button class="btn btn-sm btn-outline-info" onclick="exportReport(${comp.id}, 'txt')" title="Exportar TXT">
                                            <i class="fas fa-file-alt"></i>
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            }).join('');
        }
    } catch (error) {
        console.error('Error loading reports:', error);
        showError('Erro ao carregar relatórios: ' + error.message);
    }
}

// Export report
async function exportReport(comparisonId, format) {
    try {
        const response = await fetch(`${API_BASE}/comparisons/${comparisonId}/results`, {
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'X-User-Id': currentUser.id
            }
        });
        
        const data = await response.json();
        
        if (response.ok && data.results) {
            const comparison = data.comparison;
            const results = data.results;
            
            let content, filename, mimeType;
            
            if (format === 'csv') {
                content = exportToCSV(results, comparison);
                filename = `relatorio_${comparisonId}_${new Date().toISOString().split('T')[0]}.csv`;
                mimeType = 'text/csv';
            } else if (format === 'json') {
                content = exportToJSON(results, comparison);
                filename = `relatorio_${comparisonId}_${new Date().toISOString().split('T')[0]}.json`;
                mimeType = 'application/json';
            } else if (format === 'txt') {
                content = exportToTXT(results, comparison);
                filename = `relatorio_${comparisonId}_${new Date().toISOString().split('T')[0]}.txt`;
                mimeType = 'text/plain';
            }
            
            const blob = new Blob([content], { type: mimeType });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
            showSuccess('Relatório exportado com sucesso!');
        } else {
            showError('Erro ao exportar relatório: ' + (data.message || 'Erro desconhecido'));
        }
    } catch (error) {
        showError('Erro ao exportar relatório: ' + error.message);
    }
}

// Send changes to API
async function sendChangesToAPI() {
    if (!currentProject) {
        showError('Nenhum projeto selecionado.');
        return;
    }
    
    const confirmed = await showConfirmation('Confirmação', 'Deseja enviar todas as mudanças para a API externa?');
    if (confirmed) {
        try {
            const response = await fetch(`${API_BASE}/comparisons/project/${currentProject.id}/send-changes`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${authToken}`,
                    'X-User-Id': currentUser.id
                }
            });
            
            const data = await response.json();
            
            if (response.ok) {
                const successCount = data.results.success.length;
                const failedCount = data.results.failed.length;
                if (failedCount === 0) {
                    showSuccess(`Todas as ${successCount} mudanças foram enviadas com sucesso!`);
                } else {
                    showWarning(`${successCount} mudanças enviadas com sucesso, ${failedCount} falharam.`);
                }
            } else {
                showError(data.message);
            }
        } catch (error) {
            showError('Erro ao enviar mudanças: ' + error.message);
        }
    }
}

// Edit project
async function editProject(projectId) {
    const project = projects.find(p => p.id === projectId);
    if (!project) {
        showError('Projeto não encontrado.');
        return;
    }
    
    // Store current project being edited
    window.editingProjectId = projectId;
    
    // Populate form with project data
    document.getElementById('editProjectId').value = project.id;
    document.getElementById('editProjectName').value = project.name;
    document.getElementById('editProjectDescription').value = project.description || '';
    
    // Populate connection selects
    populateConnectionSelects();
    
    // Set selected connections
    document.getElementById('editSourceConnectionSelect').value = project.source_connection_id;
    document.getElementById('editTargetConnectionSelect').value = project.target_connection_id;
    
    // Store connection IDs for later use
    window.editSourceConnectionId = project.source_connection_id;
    window.editTargetConnectionId = project.target_connection_id;
    
    // Load tables for selected connections
    await loadEditConnectionTables('source');
    await loadEditConnectionTables('target');
    
    // Set selected tables
    setTimeout(() => {
        const sourceSelect = document.getElementById('editModalSourceTableSelect');
        const targetSelect = document.getElementById('editModalTargetTableSelect');
        
        if (sourceSelect) {
            sourceSelect.value = project.source_table;
            if (project.source_table) {
                updateEditModalTableInfo('source', project.source_table);
            }
        }
        
        if (targetSelect) {
            targetSelect.value = project.target_table;
            if (project.target_table) {
                updateEditModalTableInfo('target', project.target_table);
            }
        }
        
        // Show config step initially
        document.getElementById('editProjectConfigStep').style.display = 'block';
        document.getElementById('editTableSelectionStep').style.display = 'none';
        document.getElementById('editBackToConfigBtn').style.display = 'none';
        document.getElementById('editNextToTablesBtn').style.display = 'inline-block';
        document.getElementById('updateProjectBtn').style.display = 'none';
        
        // Enable next button if connections are selected
        if (project.source_connection_id && project.target_connection_id) {
            document.getElementById('editNextToTablesBtn').disabled = false;
        }
    }, 300);
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('editProjectModal'));
    modal.show();
}

// Load tables for edit modal connections
async function loadEditConnectionTables(type) {
    const connectionId = document.getElementById(`edit${type.charAt(0).toUpperCase() + type.slice(1)}ConnectionSelect`).value;
    
    if (!connectionId) {
        document.getElementById(`editModal${type.charAt(0).toUpperCase() + type.slice(1)}TableSelect`).innerHTML = '<option value="">Selecione uma conexão primeiro...</option>';
        return;
    }
    
    // Store connection ID
    window[`edit${type}ConnectionId`] = connectionId;
    
    try {
        const response = await fetch(`${API_BASE}/connections/${connectionId}/tables`, {
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'X-User-Id': currentUser.id
            }
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            showError('Erro ao carregar tabelas: ' + (errorData.message || 'Erro desconhecido'));
            return;
        }
        
        const data = await response.json();
        const select = document.getElementById(`editModal${type.charAt(0).toUpperCase() + type.slice(1)}TableSelect`);
        
        if (data.tables && data.tables.length > 0) {
            select.innerHTML = data.tables.map(table => 
                `<option value="${table}">${table}</option>`
            ).join('');
        } else {
            select.innerHTML = '<option value="">Nenhuma tabela encontrada</option>';
        }
    } catch (error) {
        console.error('Error loading tables:', error);
        showError('Erro ao carregar tabelas: ' + error.message);
    }
}

// Update table info for edit modal
async function updateEditModalTableInfo(type, tableName) {
    if (!tableName) return;
    
    const connectionId = window[`edit${type}ConnectionId`];
    if (!connectionId) return;
    
    try {
        const response = await fetch(`${API_BASE}/connections/${connectionId}/tables/${encodeURIComponent(tableName)}/info`, {
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'X-User-Id': currentUser.id
            }
        });
        
        if (!response.ok) return;
        
        const data = await response.json();
        const infoDiv = document.getElementById(`editModal${type.charAt(0).toUpperCase() + type.slice(1)}TableInfo`);
        infoDiv.innerHTML = `
            <strong>Colunas:</strong> ${data.columns.length}<br>
            <strong>Linhas:</strong> ${data.row_count}<br>
            <strong>Chaves Primárias:</strong> ${data.primary_keys.join(', ') || 'Nenhuma'}
        `;
    } catch (error) {
        console.error('Error loading table info:', error);
    }
}

// Load tables for edit project (step 2)
async function loadEditTablesForProject() {
    const sourceConn = document.getElementById('editSourceConnectionSelect').value;
    const targetConn = document.getElementById('editTargetConnectionSelect').value;
    
    if (!sourceConn || !targetConn) {
        showWarning('Selecione ambas as conexões antes de continuar.');
        return;
    }
    
    // Load tables for both connections
    await loadEditConnectionTables('source');
    await loadEditConnectionTables('target');
    
    // Show table selection step
    document.getElementById('editProjectConfigStep').style.display = 'none';
    document.getElementById('editTableSelectionStep').style.display = 'block';
    document.getElementById('editBackToConfigBtn').style.display = 'inline-block';
    document.getElementById('editNextToTablesBtn').style.display = 'none';
    document.getElementById('updateProjectBtn').style.display = 'inline-block';
}

// Back to config step in edit modal
function editBackToConfig() {
    document.getElementById('editProjectConfigStep').style.display = 'block';
    document.getElementById('editTableSelectionStep').style.display = 'none';
    document.getElementById('editBackToConfigBtn').style.display = 'none';
    document.getElementById('editNextToTablesBtn').style.display = 'inline-block';
    document.getElementById('updateProjectBtn').style.display = 'none';
}

// Update project
async function updateProject() {
    const projectId = document.getElementById('editProjectId').value;
    const name = document.getElementById('editProjectName').value;
    const description = document.getElementById('editProjectDescription').value;
    const sourceTable = document.getElementById('editModalSourceTableSelect').value;
    const targetTable = document.getElementById('editModalTargetTableSelect').value;
    const sourceConnectionId = window.editSourceConnectionId;
    const targetConnectionId = window.editTargetConnectionId;
    
    if (!name) {
        showError('Nome do projeto é obrigatório.');
        return;
    }
    
    if (!sourceTable || !targetTable) {
        showWarning('Selecione ambas as tabelas antes de salvar.');
        return;
    }
    
    if (!sourceConnectionId || !targetConnectionId) {
        showError('Conexões não encontradas.');
        return;
    }
    
    const projectData = {
        name,
        description,
        source_table: sourceTable,
        target_table: targetTable,
        source_connection_id: parseInt(sourceConnectionId),
        target_connection_id: parseInt(targetConnectionId)
    };
    
    try {
        const response = await fetch(`${API_BASE}/projects/${projectId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`,
                'X-User-Id': currentUser.id
            },
            body: JSON.stringify(projectData)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            showError(errorData.message || 'Erro ao atualizar projeto');
            return;
        }
        
        const data = await response.json();
        
        bootstrap.Modal.getInstance(document.getElementById('editProjectModal')).hide();
        loadProjects();
        showSuccess('Projeto atualizado com sucesso!');
        
        // Clear temp data
        window.editingProjectId = null;
        window.editSourceConnectionId = null;
        window.editTargetConnectionId = null;
    } catch (error) {
        console.error('Error updating project:', error);
        showError('Erro ao atualizar projeto: ' + error.message);
    }
}

// Delete project
async function deleteProject(projectId) {
    showConfirmation('Tem certeza que deseja excluir este projeto?', async () => {
        try {
            const response = await fetch(`${API_BASE}/projects/${projectId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${authToken}`,
                    'X-User-Id': currentUser.id
                }
            });
            
            const data = await response.json();
            
            if (response.ok) {
                loadProjects();
                showSuccess('Projeto excluído com sucesso!');
            } else {
                showError(data.message);
            }
        } catch (error) {
            showError('Erro ao excluir projeto: ' + error.message);
        }
    });
}

// ========== CONNECTION MANAGEMENT ==========

// Load connections
async function loadConnections() {
    try {
        const response = await fetch(`${API_BASE}/connections`, {
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'X-User-Id': currentUser.id
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            connections = data.connections;
            renderConnections();
            populateConnectionSelects();
            populateTableConnectionSelect(); // Also update tables management select
        }
    } catch (error) {
        console.error('Error loading connections:', error);
    }
}

// Render connections
function renderConnections() {
    const container = document.getElementById('connectionsList');
    
    if (connections.length === 0) {
        container.innerHTML = '<div class="col-12"><div class="alert alert-info">Nenhuma conexão encontrada. Crie uma nova conexão para começar.</div></div>';
        return;
    }
    
    container.innerHTML = connections.map(conn => `
        <div class="col-md-4">
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">${conn.name}</h5>
                    <p class="card-text text-muted">${conn.description || 'Sem descrição'}</p>
                    <p class="card-text">
                        <small class="text-muted">
                            <i class="fas fa-database me-1"></i>${conn.db_type.toUpperCase()}
                        </small>
                    </p>
                    <div class="d-flex justify-content-between">
                        <button class="btn btn-sm btn-outline-primary" onclick="testConnectionById(${conn.id})">
                            <i class="fas fa-plug"></i> Testar
                        </button>
                        <div>
                            <button class="btn btn-sm btn-outline-secondary" onclick="editConnection(${conn.id})">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-danger" onclick="deleteConnection(${conn.id})">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

// Populate connection selects in project modal
function populateConnectionSelects() {
    const sourceSelect = document.getElementById('sourceConnectionSelect');
    const targetSelect = document.getElementById('targetConnectionSelect');
    const editSourceSelect = document.getElementById('editSourceConnectionSelect');
    const editTargetSelect = document.getElementById('editTargetConnectionSelect');
    
    const options = connections.map(c => `<option value="${c.id}">${c.name} (${c.db_type})</option>`).join('');
    const defaultOption = '<option value="">Selecione uma conexão...</option>';
    
    if (sourceSelect && targetSelect) {
        sourceSelect.innerHTML = defaultOption + options;
        targetSelect.innerHTML = defaultOption + options;
    }
    
    // Also populate edit modal selects
    if (editSourceSelect && editTargetSelect) {
        editSourceSelect.innerHTML = defaultOption + options;
        editTargetSelect.innerHTML = defaultOption + options;
    }
}

// Show create connection modal
function showCreateConnectionModal() {
    updateConnectionDbConfig();
    new bootstrap.Modal(document.getElementById('createConnectionModal')).show();
}

// Update connection DB config fields
function updateConnectionDbConfig() {
    const type = document.getElementById('connectionDbType').value;
    const container = document.getElementById('connectionDbConfig');
    
    if (type === 'sqlite') {
        container.innerHTML = `
            <div class="mb-2">
                <label class="form-label">Caminho do arquivo</label>
                <input type="text" class="form-control" id="connectionDbPath" placeholder="instance/deltascope.db" required>
            </div>
        `;
    } else {
        container.innerHTML = `
            <div class="mb-2">
                <label class="form-label">Host</label>
                <input type="text" class="form-control" id="connectionDbHost" value="localhost" required>
            </div>
            <div class="mb-2">
                <label class="form-label">Porta</label>
                <input type="number" class="form-control" id="connectionDbPort" value="3306" required>
            </div>
            <div class="mb-2">
                <label class="form-label">Usuário</label>
                <input type="text" class="form-control" id="connectionDbUser" value="root" required>
            </div>
            <div class="mb-2">
                <label class="form-label">Senha</label>
                <input type="password" class="form-control" id="connectionDbPassword" required>
            </div>
            <div class="mb-2">
                <label class="form-label">Database</label>
                <input type="text" class="form-control" id="connectionDbName" required>
            </div>
        `;
    }
}

// Test connection for new connection
async function testConnectionForNew() {
    const dbType = document.getElementById('connectionDbType').value;
    let dbConfig = { type: dbType };
    
    if (dbType === 'sqlite') {
        dbConfig.path = document.getElementById('connectionDbPath').value;
    } else {
        dbConfig.host = document.getElementById('connectionDbHost').value;
        dbConfig.port = document.getElementById('connectionDbPort').value;
        dbConfig.user = document.getElementById('connectionDbUser').value;
        dbConfig.password = document.getElementById('connectionDbPassword').value;
        dbConfig.database = document.getElementById('connectionDbName').value;
    }
    
    try {
        const response = await fetch(`${API_BASE}/tables/test-connection`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`,
                'X-User-Id': currentUser.id
            },
            body: JSON.stringify({ db_config: dbConfig })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showSuccess('Conexão bem-sucedida!');
        } else {
            showError('Erro na conexão: ' + data.message);
        }
    } catch (error) {
        showError('Erro ao testar conexão: ' + error.message);
    }
}

// Create connection
async function createConnection() {
    const name = document.getElementById('connectionName').value;
    const description = document.getElementById('connectionDescription').value;
    const dbType = document.getElementById('connectionDbType').value;
    
    let dbConfig = { type: dbType };
    
    if (dbType === 'sqlite') {
        dbConfig.path = document.getElementById('connectionDbPath').value;
    } else {
        dbConfig.host = document.getElementById('connectionDbHost').value;
        dbConfig.port = document.getElementById('connectionDbPort').value;
        dbConfig.user = document.getElementById('connectionDbUser').value;
        dbConfig.password = document.getElementById('connectionDbPassword').value;
        dbConfig.database = document.getElementById('connectionDbName').value;
    }
    
    try {
        const response = await fetch(`${API_BASE}/connections`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`,
                'X-User-Id': currentUser.id
            },
            body: JSON.stringify({
                name,
                description,
                db_type: dbType,
                db_config: dbConfig
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            bootstrap.Modal.getInstance(document.getElementById('createConnectionModal')).hide();
            // Clear form
            document.getElementById('connectionName').value = '';
            document.getElementById('connectionDescription').value = '';
            document.getElementById('connectionDbType').value = 'sqlite';
            updateConnectionDbConfig();
            // Reload connections and update selects
            await loadConnections();
            showSuccess('Conexão criada com sucesso!');
        } else {
            showError(data.message);
        }
    } catch (error) {
        showError('Erro ao criar conexão: ' + error.message);
    }
}

// Test connection by ID
async function testConnectionById(connectionId) {
    try {
        const response = await fetch(`${API_BASE}/connections/${connectionId}/test`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'X-User-Id': currentUser.id
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            showSuccess('Conexão bem-sucedida!');
        } else {
            showError('Erro na conexão: ' + data.message);
        }
    } catch (error) {
        showError('Erro ao testar conexão: ' + error.message);
    }
}

// Edit connection
async function editConnection(connectionId) {
    const connection = connections.find(c => c.id === connectionId);
    if (!connection) {
        showError('Conexão não encontrada.');
        return;
    }
    
    try {
        // Fetch full connection details (including decrypted config)
        const response = await fetch(`${API_BASE}/connections/${connectionId}`, {
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'X-User-Id': currentUser.id
            }
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            showError('Erro ao carregar conexão: ' + (errorData.message || 'Erro desconhecido'));
            return;
        }
        
        const data = await response.json();
        const conn = data.connection;
        
        // Populate form with connection data
        document.getElementById('editConnectionId').value = conn.id;
        document.getElementById('editConnectionName').value = conn.name;
        document.getElementById('editConnectionDescription').value = conn.description || '';
        document.getElementById('editConnectionDbType').value = conn.db_type;
        
        // Update config fields based on type
        updateEditConnectionDbConfig();
        
        // Wait a bit for DOM to update, then populate config fields
        setTimeout(() => {
            if (conn.db_type === 'sqlite') {
                const pathInput = document.getElementById('editConnectionDbPath');
                if (pathInput && conn.db_config && conn.db_config.path) {
                    pathInput.value = conn.db_config.path;
                }
            } else {
                // MariaDB/MySQL
                if (conn.db_config) {
                    const hostInput = document.getElementById('editConnectionDbHost');
                    const portInput = document.getElementById('editConnectionDbPort');
                    const userInput = document.getElementById('editConnectionDbUser');
                    const passwordInput = document.getElementById('editConnectionDbPassword');
                    const dbNameInput = document.getElementById('editConnectionDbName');
                    
                    if (hostInput && conn.db_config.host) hostInput.value = conn.db_config.host;
                    if (portInput && conn.db_config.port) portInput.value = conn.db_config.port;
                    if (userInput && conn.db_config.user) userInput.value = conn.db_config.user;
                    // Don't populate password for security - user needs to re-enter
                    if (passwordInput) passwordInput.value = '';
                    if (dbNameInput && conn.db_config.database) dbNameInput.value = conn.db_config.database;
                }
            }
        }, 100);
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('editConnectionModal'));
        modal.show();
    } catch (error) {
        console.error('Error loading connection:', error);
        showError('Erro ao carregar conexão: ' + error.message);
    }
}

// Update edit connection DB config fields
function updateEditConnectionDbConfig() {
    const type = document.getElementById('editConnectionDbType').value;
    const container = document.getElementById('editConnectionDbConfig');
    
    if (type === 'sqlite') {
        container.innerHTML = `
            <div class="mb-2">
                <label class="form-label">Caminho do arquivo</label>
                <input type="text" class="form-control" id="editConnectionDbPath" placeholder="instance/deltascope.db" required>
            </div>
        `;
    } else {
        container.innerHTML = `
            <div class="mb-2">
                <label class="form-label">Host</label>
                <input type="text" class="form-control" id="editConnectionDbHost" value="localhost" required>
            </div>
            <div class="mb-2">
                <label class="form-label">Porta</label>
                <input type="number" class="form-control" id="editConnectionDbPort" value="3306" required>
            </div>
            <div class="mb-2">
                <label class="form-label">Usuário</label>
                <input type="text" class="form-control" id="editConnectionDbUser" value="root" required>
            </div>
            <div class="mb-2">
                <label class="form-label">Senha</label>
                <input type="password" class="form-control" id="editConnectionDbPassword" placeholder="Deixe em branco para manter a senha atual">
            </div>
            <div class="mb-2">
                <label class="form-label">Database</label>
                <input type="text" class="form-control" id="editConnectionDbName" required>
            </div>
        `;
    }
}

// Test edit connection
async function testEditConnection() {
    const dbType = document.getElementById('editConnectionDbType').value;
    let dbConfig = { type: dbType };
    
    if (dbType === 'sqlite') {
        dbConfig.path = document.getElementById('editConnectionDbPath').value;
    } else {
        dbConfig.host = document.getElementById('editConnectionDbHost').value;
        dbConfig.port = document.getElementById('editConnectionDbPort').value;
        dbConfig.user = document.getElementById('editConnectionDbUser').value;
        dbConfig.password = document.getElementById('editConnectionDbPassword').value;
        dbConfig.database = document.getElementById('editConnectionDbName').value;
    }
    
    try {
        const response = await fetch(`${API_BASE}/tables/test-connection`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`,
                'X-User-Id': currentUser.id
            },
            body: JSON.stringify({ db_config: dbConfig })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showSuccess('Conexão bem-sucedida!');
        } else {
            showError('Erro na conexão: ' + data.message);
        }
    } catch (error) {
        showError('Erro ao testar conexão: ' + error.message);
    }
}

// Update connection
async function updateConnection() {
    const connectionId = document.getElementById('editConnectionId').value;
    const name = document.getElementById('editConnectionName').value;
    const description = document.getElementById('editConnectionDescription').value;
    const dbType = document.getElementById('editConnectionDbType').value;
    
    if (!name) {
        showError('Nome da conexão é obrigatório.');
        return;
    }
    
    // Get current connection to check if password should be kept
    const currentConnection = connections.find(c => c.id === parseInt(connectionId));
    
    let dbConfig = { type: dbType };
    
    if (dbType === 'sqlite') {
        const path = document.getElementById('editConnectionDbPath').value;
        if (!path) {
            showError('Caminho do arquivo SQLite é obrigatório.');
            return;
        }
        dbConfig.path = path;
    } else {
        dbConfig.host = document.getElementById('editConnectionDbHost').value;
        dbConfig.port = document.getElementById('editConnectionDbPort').value;
        dbConfig.user = document.getElementById('editConnectionDbUser').value;
        const password = document.getElementById('editConnectionDbPassword').value;
        
        // If password is empty, backend will keep the existing password
        // So we can send empty string and backend will handle it
        dbConfig.password = password || '';
        dbConfig.database = document.getElementById('editConnectionDbName').value;
        
        if (!dbConfig.host || !dbConfig.user || !dbConfig.database) {
            showError('Preencha todos os campos obrigatórios.');
            return;
        }
    }
    
    try {
        const response = await fetch(`${API_BASE}/connections/${connectionId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`,
                'X-User-Id': currentUser.id
            },
            body: JSON.stringify({
                name,
                description,
                db_type: dbType,
                db_config: dbConfig
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            showError(errorData.message || 'Erro ao atualizar conexão');
            return;
        }
        
        const data = await response.json();
        
        bootstrap.Modal.getInstance(document.getElementById('editConnectionModal')).hide();
        await loadConnections();
        showSuccess('Conexão atualizada com sucesso!');
    } catch (error) {
        console.error('Error updating connection:', error);
        showError('Erro ao atualizar conexão: ' + error.message);
    }
}

// Delete connection
async function deleteConnection(connectionId) {
    showConfirmation('Tem certeza que deseja excluir esta conexão?', async () => {
        try {
            const response = await fetch(`${API_BASE}/connections/${connectionId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${authToken}`,
                    'X-User-Id': currentUser.id
                }
            });
            
            const data = await response.json();
            
            if (response.ok) {
                loadConnections();
                showSuccess('Conexão excluída com sucesso!');
            } else {
                showError(data.message);
            }
        } catch (error) {
            showError('Erro ao excluir conexão: ' + error.message);
        }
    });
}

// Load tables for a connection
async function loadConnectionTables(type) {
    const connectionId = document.getElementById(`${type}ConnectionSelect`).value;
    
    if (!connectionId) {
        document.getElementById(`modal${type.charAt(0).toUpperCase() + type.slice(1)}TableSelect`).innerHTML = '<option value="">Selecione uma conexão primeiro...</option>';
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/connections/${connectionId}/tables`, {
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'X-User-Id': currentUser.id
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            const select = document.getElementById(`modal${type.charAt(0).toUpperCase() + type.slice(1)}TableSelect`);
            select.innerHTML = data.tables.map(t => `<option value="${t}">${t}</option>`).join('');
            
            // Store connection ID for later use
            window[`${type}ConnectionId`] = connectionId;
            
            // Enable next button if both connections are selected
            checkProjectReady();
        } else {
            showError('Erro ao carregar tabelas: ' + data.message);
        }
    } catch (error) {
        showError('Erro ao carregar tabelas: ' + error.message);
    }
}

// Check if project is ready to proceed
function checkProjectReady() {
    const sourceConn = document.getElementById('sourceConnectionSelect').value;
    const targetConn = document.getElementById('targetConnectionSelect').value;
    const nextBtn = document.getElementById('nextToTablesBtn');
    
    if (sourceConn && targetConn) {
        nextBtn.disabled = false;
    } else {
        nextBtn.disabled = true;
    }
}

// Update modal table info
async function updateModalTableInfo(type, tableName) {
    if (!tableName) return;
    
    const connectionId = window[`${type}ConnectionId`];
    if (!connectionId) return;
    
    try {
        const response = await fetch(`${API_BASE}/connections/${connectionId}/tables/${tableName}/info`, {
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'X-User-Id': currentUser.id
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            const infoDiv = document.getElementById(`modal${type.charAt(0).toUpperCase() + type.slice(1)}TableInfo`);
            infoDiv.innerHTML = `
                <strong>Colunas:</strong> ${data.columns.length}<br>
                <strong>Linhas:</strong> ${data.row_count}<br>
                <strong>Chaves Primárias:</strong> ${data.primary_keys.join(', ') || 'Nenhuma'}
            `;
        }
    } catch (error) {
        console.error('Error loading table info:', error);
    }
}

// Updated loadTablesForProject
async function loadTablesForProject() {
    const sourceConn = document.getElementById('sourceConnectionSelect').value;
    const targetConn = document.getElementById('targetConnectionSelect').value;
    
    if (!sourceConn || !targetConn) {
        showWarning('Selecione ambas as conexões antes de continuar.');
        return;
    }
    
    // Load tables for both connections
    await loadConnectionTables('source');
    await loadConnectionTables('target');
    
    // Show table selection step
    document.getElementById('projectConfigStep').style.display = 'none';
    document.getElementById('tableSelectionStep').style.display = 'block';
    document.getElementById('backToConfigBtn').style.display = 'inline-block';
    document.getElementById('nextToTablesBtn').style.display = 'none';
    document.getElementById('createProjectBtn').style.display = 'inline-block';
}

// Updated createProject
async function createProject() {
    const name = document.getElementById('projectName').value;
    const description = document.getElementById('projectDescription').value;
    const sourceTable = document.getElementById('modalSourceTableSelect').value;
    const targetTable = document.getElementById('modalTargetTableSelect').value;
    const sourceConnectionId = window.sourceConnectionId;
    const targetConnectionId = window.targetConnectionId;
    
    if (!sourceTable || !targetTable) {
        showWarning('Selecione ambas as tabelas antes de criar o projeto.');
        return;
    }
    
    if (!sourceConnectionId || !targetConnectionId) {
        showError('Conexões não encontradas.');
        return;
    }
    
    const projectData = {
        name,
        description,
        source_table: sourceTable,
        target_table: targetTable,
        source_connection_id: parseInt(sourceConnectionId),
        target_connection_id: parseInt(targetConnectionId)
    };
    
    try {
        const response = await fetch(`${API_BASE}/projects`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`,
                'X-User-Id': currentUser.id
            },
            body: JSON.stringify(projectData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            bootstrap.Modal.getInstance(document.getElementById('createProjectModal')).hide();
            loadProjects();
            showSuccess('Projeto criado com sucesso!');
            // Clear temp data
            window.sourceConnectionId = null;
            window.targetConnectionId = null;
        } else {
            showError(data.message);
        }
    } catch (error) {
        showError('Erro ao criar projeto: ' + error.message);
    }
}

// ========== TABLES MANAGEMENT ==========

// Populate connection select for tables management
function populateTableConnectionSelect() {
    const select = document.getElementById('tableConnectionSelect');
    if (!select) return;
    
    const options = connections.map(c => `<option value="${c.id}">${c.name} (${c.db_type})</option>`).join('');
    select.innerHTML = '<option value="">Selecione uma conexão...</option>' + options;
    
    // Restore last selected connection if available
    if (lastSelectedConnectionId) {
        select.value = lastSelectedConnectionId;
        // Auto-load tables if connection is restored
        if (select.value) {
            loadTablesForManagement();
        }
    }
}

// Store last selected connection for tables management
let lastSelectedConnectionId = null;

// Handle table connection change
function onTableConnectionChange(connectionId) {
    lastSelectedConnectionId = connectionId;
    loadTablesForManagement();
}

// Load tables for management
async function loadTablesForManagement() {
    const connectionSelect = document.getElementById('tableConnectionSelect');
    const connectionId = connectionSelect?.value || lastSelectedConnectionId;
    
    if (!connectionId) {
        document.getElementById('tablesListContainer').innerHTML = '';
        return;
    }
    
    // Store the connection ID for future use
    lastSelectedConnectionId = connectionId;
    
    // Show loading state
    const container = document.getElementById('tablesListContainer');
    container.innerHTML = '<div class="text-center p-4"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Carregando...</span></div><p class="mt-2">Carregando tabelas...</p></div>';
    
    try {
        // Verify auth token and user are still available
        if (!authToken || !currentUser) {
            console.error('Auth token or user not available');
            container.innerHTML = '<div class="alert alert-warning">Sessão expirada. Por favor, faça login novamente.</div>';
            return;
        }
        
        const response = await fetch(`${API_BASE}/connections/${connectionId}/tables`, {
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'X-User-Id': currentUser.id
            }
        });
        
        if (!response.ok) {
            // Try to get error message
            let errorMsg = 'Erro ao carregar tabelas';
            try {
                const errorData = await response.json();
                errorMsg = errorData.message || errorMsg;
            } catch (parseError) {
                // If response is not JSON, try to get text
                try {
                    const textData = await response.text();
                    console.error('Non-JSON response:', textData);
                    errorMsg = `Erro ${response.status}: ${response.statusText}`;
                } catch {
                    errorMsg = `Erro ${response.status}: ${response.statusText}`;
                }
            }
            
            // Don't show error modal if it's just a network issue - show inline
            console.error('Error loading tables:', errorMsg);
            // Keep the connection selected even on error
            if (connectionSelect) {
                connectionSelect.value = connectionId;
            }
            container.innerHTML = `<div class="alert alert-warning"><i class="fas fa-exclamation-triangle me-2"></i>${errorMsg}</div>`;
            return;
        }
        
        const data = await response.json();
        
        if (data && data.tables) {
            renderTablesList(data.tables, connectionId);
        } else {
            console.error('Invalid response data:', data);
            // Keep the connection selected even on error
            if (connectionSelect) {
                connectionSelect.value = connectionId;
            }
            container.innerHTML = '<div class="alert alert-danger">Resposta inválida do servidor</div>';
        }
    } catch (error) {
        console.error('Error loading tables:', error);
        const errorMsg = 'Erro ao carregar tabelas: ' + (error.message || 'Erro desconhecido');
        // Keep the connection selected even on error
        if (connectionSelect) {
            connectionSelect.value = connectionId;
        }
        container.innerHTML = `<div class="alert alert-danger"><i class="fas fa-exclamation-circle me-2"></i>${errorMsg}</div>`;
    }
}

// Render tables list
function renderTablesList(tables, connectionId) {
    const container = document.getElementById('tablesListContainer');
    
    if (tables.length === 0) {
        container.innerHTML = '<div class="alert alert-info">Nenhuma tabela encontrada nesta conexão.</div>';
        return;
    }
    
    container.innerHTML = `
        <div class="list-group">
            ${tables.map(table => `
                <div class="list-group-item">
                    <div class="d-flex justify-content-between align-items-center">
                        <h5 class="mb-1">${table}</h5>
                        <button class="btn btn-sm btn-primary" onclick="viewTableDetails('${table}', ${connectionId})">
                            <i class="fas fa-eye me-1"></i>Visualizar
                        </button>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

// View table details
async function viewTableDetails(tableName, connectionId) {
    // Store connection ID for later use
    lastSelectedConnectionId = connectionId;
    
    // Ensure connection is selected in the dropdown
    const connectionSelect = document.getElementById('tableConnectionSelect');
    if (connectionSelect) {
        connectionSelect.value = connectionId;
    }
    
    try {
        const response = await fetch(`${API_BASE}/connections/${connectionId}/tables/${encodeURIComponent(tableName)}/info`, {
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'X-User-Id': currentUser.id
            }
        });
        
        if (!response.ok) {
            let errorMsg = 'Erro ao carregar detalhes da tabela';
            try {
                const errorData = await response.json();
                errorMsg = errorData.message || errorMsg;
            } catch {
                errorMsg = `Erro ${response.status}: ${response.statusText}`;
            }
            showError(errorMsg);
            return;
        }
        
        const data = await response.json();
        showTableDetailsModal(tableName, connectionId, data);
    } catch (error) {
        console.error('Error loading table details:', error);
        showError('Erro ao carregar detalhes da tabela: ' + error.message);
    }
}

// Show table details modal
// Edit column type
async function editColumnType(connectionId, tableName, columnName, currentType, nullable, primaryKey) {
    // Load data types
    try {
        const typesResponse = await fetch(`${API_BASE}/tables/data-types`, {
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'X-User-Id': currentUser.id
            }
        });
        
        const typesData = await typesResponse.json();
        
        if (typesResponse.ok) {
            // Populate form
            document.getElementById('columnTypeConnectionId').value = connectionId;
            document.getElementById('editTableName').value = tableName;
            document.getElementById('editColumnName').value = columnName;
            document.getElementById('editColumnDisplay').textContent = columnName;
            document.getElementById('editColumnNullable').checked = nullable;
            document.getElementById('editColumnPrimaryKey').checked = primaryKey;
            
            // Populate type select
            const typeSelect = document.getElementById('editColumnType');
            typeSelect.innerHTML = '<option value="">Selecione um tipo...</option>';
            
            const groupedTypes = {};
            typesData.data_types.forEach(dt => {
                if (!groupedTypes[dt.category]) {
                    groupedTypes[dt.category] = [];
                }
                groupedTypes[dt.category].push(dt);
            });
            
            Object.keys(groupedTypes).forEach(category => {
                const optgroup = document.createElement('optgroup');
                optgroup.label = category;
                groupedTypes[category].forEach(dt => {
                    const option = document.createElement('option');
                    option.value = dt.value;
                    option.textContent = dt.label;
                    if (dt.value === currentType) {
                        option.selected = true;
                    }
                    optgroup.appendChild(option);
                });
                typeSelect.appendChild(optgroup);
            });
            
            // Show modal
            const modal = new bootstrap.Modal(document.getElementById('columnTypeModal'));
            modal.show();
        }
    } catch (error) {
        showError('Erro ao carregar tipos de dados: ' + error.message);
    }
}

// Save column type
async function saveColumnType() {
    const connectionId = document.getElementById('columnTypeConnectionId').value;
    const tableName = document.getElementById('editTableName').value;
    const columnName = document.getElementById('editColumnName').value;
    const newType = document.getElementById('editColumnType').value;
    const nullable = document.getElementById('editColumnNullable').checked;
    const primaryKey = document.getElementById('editColumnPrimaryKey').checked;
    
    if (!newType) {
        showError('Selecione um tipo de dado.');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/tables/update-column-type`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`,
                'X-User-Id': currentUser.id
            },
            body: JSON.stringify({
                connection_id: parseInt(connectionId),
                table_name: tableName,
                column_name: columnName,
                new_type: newType,
                nullable: nullable,
                primary_key: primaryKey
            })
        });
        
        if (!response.ok) {
            // Try to get error message
            let errorMsg = 'Erro ao salvar tipo de dado';
            try {
                const errorData = await response.json();
                errorMsg = errorData.message || errorMsg;
            } catch {
                errorMsg = `Erro ${response.status}: ${response.statusText}`;
            }
            showError(errorMsg);
            return;
        }
        
        const data = await response.json();
        
        // Show success message first
        showSuccess(data.message);
        
        // Close column type modal
        const columnTypeModalEl = document.getElementById('columnTypeModal');
        if (columnTypeModalEl) {
            const columnTypeModal = bootstrap.Modal.getInstance(columnTypeModalEl);
            if (columnTypeModal) {
                columnTypeModal.hide();
            }
        }
        
        // Store connection ID before closing modals
        const savedConnectionId = connectionId;
        
        // Close table details modal after a short delay
        setTimeout(() => {
            const tableDetailsModalEl = document.getElementById('tableDetailsModal');
            if (tableDetailsModalEl && tableDetailsModalEl.classList.contains('show')) {
                const tableDetailsModal = bootstrap.Modal.getInstance(tableDetailsModalEl);
                if (tableDetailsModal) {
                    tableDetailsModal.hide();
                }
            }
            
            // Wait for modals to fully close before reloading
            setTimeout(() => {
                // Reload tables list - use the same connection that was being edited
                if (savedConnectionId) {
                    // Set the connection select to the same connection
                    const connectionSelect = document.getElementById('tableConnectionSelect');
                    if (connectionSelect) {
                        connectionSelect.value = savedConnectionId;
                    }
                    // Store for future use
                    lastSelectedConnectionId = savedConnectionId;
                }
                
                // Reload tables
                loadTablesForManagement();
            }, 600); // Increased delay to ensure modals are fully closed
        }, 300);
    } catch (error) {
        console.error('Error saving column type:', error);
        showError('Erro ao salvar tipo de dado: ' + error.message);
    }
}

// View model code
async function viewModelCode(connectionId, tableName) {
    try {
        const response = await fetch(`${API_BASE}/tables/model/${connectionId}/${encodeURIComponent(tableName)}`, {
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'X-User-Id': currentUser.id
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            document.getElementById('modelTableName').textContent = data.table_name;
            document.getElementById('modelConnectionName').textContent = data.connection_name;
            document.getElementById('modelFilePath').textContent = data.file_path;
            document.getElementById('modelCodeContent').textContent = data.model_code;
            
            // Show modal
            const modal = new bootstrap.Modal(document.getElementById('modelViewerModal'));
            modal.show();
        } else {
            showError(data.message);
        }
    } catch (error) {
        showError('Erro ao carregar modelo: ' + error.message);
    }
}

// Copy model code to clipboard
function copyModelCode() {
    const codeContent = document.getElementById('modelCodeContent').textContent;
    navigator.clipboard.writeText(codeContent).then(() => {
        showSuccess('Código copiado para a área de transferência!');
    }).catch(() => {
        showError('Erro ao copiar código.');
    });
}

function showTableDetailsModal(tableName, connectionId, tableInfo) {
    const modalHtml = `
        <div class="modal fade" id="tableDetailsModal" tabindex="-1">
            <div class="modal-dialog modal-xl">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Detalhes da Tabela: ${tableName}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="mb-3">
                            <strong>Total de linhas:</strong> ${tableInfo.row_count}
                        </div>
                        <h6>Colunas:</h6>
                        <div class="table-responsive">
                            <table class="table table-striped">
                                <thead>
                                    <tr>
                                        <th>Nome</th>
                                        <th>Tipo</th>
                                        <th>Nullable</th>
                                        <th>Chave Primária</th>
                                        <th>Ações</th>
                                    </tr>
                                </thead>
                                <tbody id="tableColumnsBody">
                                    ${tableInfo.columns.map(col => {
                                        const colType = col.type.split('(')[0].trim(); // Extract base type
                                        return `
                                        <tr>
                                            <td>${col.name}</td>
                                            <td>${col.type}</td>
                                            <td>${col.nullable ? 'Sim' : 'Não'}</td>
                                            <td>${tableInfo.primary_keys.includes(col.name) ? '<span class="badge bg-primary">Sim</span>' : '<span class="badge bg-secondary">Não</span>'}</td>
                                            <td>
                                                <button class="btn btn-sm btn-warning" onclick="editColumnType(${connectionId}, '${tableName}', '${col.name}', '${colType}', ${col.nullable}, ${tableInfo.primary_keys.includes(col.name)})" title="Editar tipo">
                                                    <i class="fas fa-edit"></i>
                                                </button>
                                            </td>
                                        </tr>
                                    `;
                                    }).join('')}
                                </tbody>
                            </table>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-info" onclick="viewModelCode(${connectionId}, '${tableName}')">
                            <i class="fas fa-code me-2"></i>Ver Modelo SQLAlchemy
                        </button>
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Fechar</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remove existing modal if any
    const existingModal = document.getElementById('tableDetailsModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Add modal to body
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('tableDetailsModal'));
    modal.show();
    
    // Store connectionId and tableName for update function
    window.currentTableDetails = { tableName, connectionId };
}

// Update primary keys
async function updatePrimaryKeys(tableName, connectionId) {
    const checkboxes = document.querySelectorAll('.primary-key-checkbox:checked');
    const primaryKeys = Array.from(checkboxes).map(cb => cb.dataset.column);
    
    try {
        // Update primary keys in projects that use this table
        const response = await fetch(`${API_BASE}/tables/update-primary-keys`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`,
                'X-User-Id': currentUser.id
            },
            body: JSON.stringify({
                connection_id: connectionId,
                table_name: tableName,
                primary_keys: primaryKeys
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            bootstrap.Modal.getInstance(document.getElementById('tableDetailsModal')).hide();
            showSuccess('Chaves primárias atualizadas com sucesso! Os modelos do projeto serão atualizados.');
        } else {
            showError(data.message);
        }
    } catch (error) {
        showError('Erro ao atualizar chaves primárias: ' + error.message);
    }
}

// Updated showCreateProjectModal
function showCreateProjectModal() {
    populateConnectionSelects();
    // Reset modal state
    document.getElementById('projectConfigStep').style.display = 'block';
    document.getElementById('tableSelectionStep').style.display = 'none';
    document.getElementById('backToConfigBtn').style.display = 'none';
    document.getElementById('nextToTablesBtn').style.display = 'inline-block';
    document.getElementById('nextToTablesBtn').disabled = true;
    document.getElementById('createProjectBtn').style.display = 'none';
    
    // Add change listeners
    document.getElementById('sourceConnectionSelect').addEventListener('change', () => {
        loadConnectionTables('source');
        checkProjectReady();
    });
    document.getElementById('targetConnectionSelect').addEventListener('change', () => {
        loadConnectionTables('target');
        checkProjectReady();
    });
    
    new bootstrap.Modal(document.getElementById('createProjectModal')).show();
}

// ==================== USER MANAGEMENT FUNCTIONS ====================

// Load all users
async function loadUsers() {
    const container = document.getElementById('usersListContainer');
    
    if (!currentUser || !currentUser.is_admin) {
        container.innerHTML = '<div class="alert alert-danger">Acesso negado. Apenas administradores podem gerenciar usuários.</div>';
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/users/`, {
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'X-User-Id': currentUser.id
            }
        });
        
        if (!response.ok) {
            if (response.status === 403) {
                showError('Acesso negado. Apenas administradores podem gerenciar usuários.');
                return;
            }
            const data = await response.json();
            throw new Error(data.message || 'Erro ao carregar usuários');
        }
        
        const data = await response.json();
        renderUsersList(data.users);
    } catch (error) {
        container.innerHTML = `<div class="alert alert-danger">Erro ao carregar usuários: ${error.message}</div>`;
    }
}

// Render users list
function renderUsersList(users) {
    const container = document.getElementById('usersListContainer');
    
    if (!users || users.length === 0) {
        container.innerHTML = '<div class="alert alert-info">Nenhum usuário encontrado.</div>';
        return;
    }
    
    container.innerHTML = users.map(user => `
        <div class="card mb-3">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <h5 class="card-title mb-1">
                            ${user.username}
                            ${user.is_admin ? '<span class="badge bg-danger ms-2">Admin</span>' : ''}
                            ${!user.is_active ? '<span class="badge bg-secondary ms-2">Inativo</span>' : '<span class="badge bg-success ms-2">Ativo</span>'}
                        </h5>
                        <p class="card-text text-muted mb-1">
                            <i class="fas fa-envelope me-1"></i>${user.email}
                        </p>
                        <p class="card-text text-muted small mb-0">
                            <i class="fas fa-calendar me-1"></i>Criado em: ${new Date(user.created_at).toLocaleString('pt-BR')}
                        </p>
                    </div>
                    <div class="btn-group" role="group">
                        ${currentUser.id !== user.id ? `
                            <button class="btn btn-sm ${user.is_active ? 'btn-secondary' : 'btn-success'}" onclick="toggleUserActive(${user.id}, ${user.is_active})" title="${user.is_active ? 'Desativar' : 'Ativar'} Usuário">
                                <i class="fas fa-${user.is_active ? 'ban' : 'check'}"></i>
                            </button>
                        ` : ''}
                        <button class="btn btn-sm btn-warning" onclick="showChangePasswordModal(${user.id})" title="Alterar Senha">
                            <i class="fas fa-key"></i>
                        </button>
                        ${currentUser.id !== user.id ? `
                            <button class="btn btn-sm btn-danger" onclick="deleteUser(${user.id}, '${user.username.replace(/'/g, "\\'")}')" title="Deletar Usuário">
                                <i class="fas fa-trash"></i>
                            </button>
                        ` : `
                            <button class="btn btn-sm btn-secondary" disabled title="Não é possível deletar seu próprio usuário">
                                <i class="fas fa-trash"></i>
                            </button>
                        `}
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

// Show create user modal
function showCreateUserModal() {
    document.getElementById('createUserForm').reset();
    document.getElementById('newIsActive').checked = true;
    document.getElementById('newIsAdmin').checked = false;
    new bootstrap.Modal(document.getElementById('createUserModal')).show();
}

// Create new user
async function createUser() {
    const username = document.getElementById('newUsername').value.trim();
    const email = document.getElementById('newEmail').value.trim();
    const password = document.getElementById('newPassword').value;
    const isAdmin = document.getElementById('newIsAdmin').checked;
    const isActive = document.getElementById('newIsActive').checked;
    
    if (!username || !email || !password) {
        showError('Preencha todos os campos obrigatórios.');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/users/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`,
                'X-User-Id': currentUser.id
            },
            body: JSON.stringify({
                username,
                email,
                password,
                is_admin: isAdmin,
                is_active: isActive
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            bootstrap.Modal.getInstance(document.getElementById('createUserModal')).hide();
            showSuccess('Usuário criado com sucesso!');
            loadUsers();
        } else {
            showError(data.message || 'Erro ao criar usuário');
        }
    } catch (error) {
        showError('Erro ao criar usuário: ' + error.message);
    }
}

// Show change password modal
function showChangePasswordModal(userId) {
    document.getElementById('passwordUserId').value = userId;
    document.getElementById('changePasswordForm').reset();
    new bootstrap.Modal(document.getElementById('changePasswordModal')).show();
}

// Save password change
async function savePasswordChange() {
    const userId = parseInt(document.getElementById('passwordUserId').value);
    const password = document.getElementById('newUserPassword').value;
    const confirmPassword = document.getElementById('confirmUserPassword').value;
    
    if (!password || !confirmPassword) {
        showError('Preencha todos os campos.');
        return;
    }
    
    if (password !== confirmPassword) {
        showError('As senhas não coincidem.');
        return;
    }
    
    if (password.length < 6) {
        showError('A senha deve ter pelo menos 6 caracteres.');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/users/${userId}/password`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`,
                'X-User-Id': currentUser.id
            },
            body: JSON.stringify({ password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            bootstrap.Modal.getInstance(document.getElementById('changePasswordModal')).hide();
            showSuccess('Senha alterada com sucesso!');
        } else {
            showError(data.message || 'Erro ao alterar senha');
        }
    } catch (error) {
        showError('Erro ao alterar senha: ' + error.message);
    }
}

// Delete user
async function deleteUser(userId, username) {
    if (currentUser.id === userId) {
        showError('Não é possível deletar seu próprio usuário.');
        return;
    }
    
    const confirmed = await showConfirmation(
        'Confirmar Exclusão',
        `Tem certeza que deseja deletar o usuário "${username}"? O usuário será removido de todos os grupos e esta ação não pode ser desfeita.`
    );
    
    if (!confirmed) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/users/${userId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'X-User-Id': currentUser.id
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showSuccess('Usuário deletado com sucesso! O usuário foi removido de todos os grupos.');
            loadUsers();
        } else {
            showError(data.message || 'Erro ao deletar usuário');
        }
    } catch (error) {
        showError('Erro ao deletar usuário: ' + error.message);
    }
}

// Toggle user active status
async function toggleUserActive(userId, isCurrentlyActive) {
    if (currentUser.id === userId) {
        showError('Não é possível desativar seu próprio usuário.');
        return;
    }
    
    const action = isCurrentlyActive ? 'desativar' : 'ativar';
    const confirmed = await showConfirmation(
        `Confirmar ${action.charAt(0).toUpperCase() + action.slice(1)}`,
        `Tem certeza que deseja ${action} este usuário? ${isCurrentlyActive ? 'O usuário não poderá mais fazer login ou usar a API.' : 'O usuário poderá fazer login e usar a API novamente.'}`
    );
    
    if (!confirmed) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/users/${userId}/toggle-active`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'X-User-Id': currentUser.id
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showSuccess(`Usuário ${action}do com sucesso!`);
            loadUsers();
        } else {
            showError(data.message || `Erro ao ${action} usuário`);
        }
    } catch (error) {
        showError(`Erro ao ${action} usuário: ` + error.message);
    }
}


// ==================== GROUP MANAGEMENT FUNCTIONS ====================

// Load all groups
async function loadGroups() {
    const container = document.getElementById('groupsListContainer');
    
    if (!currentUser || !currentUser.is_admin) {
        container.innerHTML = '<div class="alert alert-danger">Acesso negado. Apenas administradores podem gerenciar grupos.</div>';
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/groups/`, {
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'X-User-Id': currentUser.id
            }
        });
        
        if (!response.ok) {
            if (response.status === 403) {
                showError('Acesso negado. Apenas administradores podem gerenciar grupos.');
                return;
            }
            const data = await response.json();
            throw new Error(data.message || 'Erro ao carregar grupos');
        }
        
        const data = await response.json();
        renderGroupsList(data.groups);
    } catch (error) {
        container.innerHTML = `<div class="alert alert-danger">Erro ao carregar grupos: ${error.message}</div>`;
    }
}

// Render groups list
function renderGroupsList(groups) {
    const container = document.getElementById('groupsListContainer');
    
    if (!groups || groups.length === 0) {
        container.innerHTML = '<div class="alert alert-info">Nenhum grupo encontrado.</div>';
        return;
    }
    
    container.innerHTML = groups.map(group => {
        const permissions = [];
        if (group.can_create_connections) permissions.push('Criar Conexões');
        if (group.can_create_projects) permissions.push('Criar Projetos');
        if (group.can_view_dashboards) permissions.push('Ver Dashboards');
        if (group.can_edit_tables) permissions.push('Editar Tabelas');
        if (group.can_view_tables) permissions.push('Ver Tabelas');
        if (group.can_view_reports) permissions.push('Ver Relatórios');
        if (group.can_download_reports) permissions.push('Baixar Relatórios');
        
        return `
        <div class="card mb-3">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-start">
                    <div class="flex-grow-1">
                        <h5 class="card-title mb-1">${group.name}</h5>
                        <p class="card-text text-muted mb-2">${group.description || 'Sem descrição'}</p>
                        <div class="mb-2">
                            <small class="text-muted">
                                <strong>Permissões:</strong> ${permissions.length > 0 ? permissions.join(', ') : 'Nenhuma'}
                            </small>
                        </div>
                        <div>
                            <small class="text-muted">
                                <i class="fas fa-users me-1"></i>${group.user_count || 0} usuário(s) | 
                                <i class="fas fa-calendar me-1"></i>Criado em: ${new Date(group.created_at).toLocaleString('pt-BR')}
                            </small>
                        </div>
                    </div>
                    <div class="btn-group ms-3" role="group">
                        <button class="btn btn-sm btn-info" onclick="viewGroupUsers(${group.id})" title="Ver Usuários">
                            <i class="fas fa-users"></i>
                        </button>
                        <button class="btn btn-sm btn-primary" onclick="editGroup(${group.id})" title="Editar Grupo">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="deleteGroup(${group.id}, '${group.name.replace(/'/g, "\\'")}')" title="Deletar Grupo">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    }).join('');
}

// Show create group modal
function showCreateGroupModal() {
    document.getElementById('groupForm').reset();
    document.getElementById('groupId').value = '';
    document.getElementById('groupModalTitle').innerHTML = '<i class="fas fa-user-friends me-2"></i>Criar Novo Grupo';
    
    // Uncheck all permissions
    ['permCreateConnections', 'permCreateProjects', 'permViewDashboards', 
     'permEditTables', 'permViewTables', 'permViewReports', 'permDownloadReports'].forEach(id => {
        document.getElementById(id).checked = false;
    });
    
    new bootstrap.Modal(document.getElementById('groupModal')).show();
}

// Edit group
async function editGroup(groupId) {
    try {
        const response = await fetch(`${API_BASE}/groups/${groupId}`, {
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'X-User-Id': currentUser.id
            }
        });
        
        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.message || 'Erro ao carregar grupo');
        }
        
        const data = await response.json();
        const group = data.group;
        
        // Populate form
        document.getElementById('groupId').value = group.id;
        document.getElementById('groupName').value = group.name;
        document.getElementById('groupDescription').value = group.description || '';
        document.getElementById('groupModalTitle').innerHTML = '<i class="fas fa-user-friends me-2"></i>Editar Grupo';
        
        // Set permissions
        document.getElementById('permCreateConnections').checked = group.can_create_connections;
        document.getElementById('permCreateProjects').checked = group.can_create_projects;
        document.getElementById('permViewDashboards').checked = group.can_view_dashboards;
        document.getElementById('permEditTables').checked = group.can_edit_tables;
        document.getElementById('permViewTables').checked = group.can_view_tables;
        document.getElementById('permViewReports').checked = group.can_view_reports;
        document.getElementById('permDownloadReports').checked = group.can_download_reports;
        
        new bootstrap.Modal(document.getElementById('groupModal')).show();
    } catch (error) {
        showError('Erro ao carregar grupo: ' + error.message);
    }
}

// Save group (create or update)
async function saveGroup() {
    const groupId = document.getElementById('groupId').value;
    const name = document.getElementById('groupName').value.trim();
    const description = document.getElementById('groupDescription').value.trim();
    
    if (!name) {
        showError('O nome do grupo é obrigatório.');
        return;
    }
    
    const groupData = {
        name,
        description,
        can_create_connections: document.getElementById('permCreateConnections').checked,
        can_create_projects: document.getElementById('permCreateProjects').checked,
        can_view_dashboards: document.getElementById('permViewDashboards').checked,
        can_edit_tables: document.getElementById('permEditTables').checked,
        can_view_tables: document.getElementById('permViewTables').checked,
        can_view_reports: document.getElementById('permViewReports').checked,
        can_download_reports: document.getElementById('permDownloadReports').checked
    };
    
    try {
        const url = groupId ? `${API_BASE}/groups/${groupId}` : `${API_BASE}/groups/`;
        const method = groupId ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`,
                'X-User-Id': currentUser.id
            },
            body: JSON.stringify(groupData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            bootstrap.Modal.getInstance(document.getElementById('groupModal')).hide();
            showSuccess(groupId ? 'Grupo atualizado com sucesso!' : 'Grupo criado com sucesso!');
            loadGroups();
        } else {
            showError(data.message || 'Erro ao salvar grupo');
        }
    } catch (error) {
        showError('Erro ao salvar grupo: ' + error.message);
    }
}

// Delete group
async function deleteGroup(groupId, groupName) {
    const confirmed = await showConfirmation(
        'Confirmar Exclusão',
        `Tem certeza que deseja deletar o grupo "${groupName}"? Todos os usuários serão removidos deste grupo. Esta ação não pode ser desfeita.`
    );
    
    if (!confirmed) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/groups/${groupId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'X-User-Id': currentUser.id
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showSuccess('Grupo deletado com sucesso!');
            loadGroups();
        } else {
            showError(data.message || 'Erro ao deletar grupo');
        }
    } catch (error) {
        showError('Erro ao deletar grupo: ' + error.message);
    }
}

// Store current group users for filtering
let currentGroupUsers = [];
let allAvailableUsers = [];

// View group users
async function viewGroupUsers(groupId) {
    document.getElementById('groupUsersGroupId').value = groupId;
    
    try {
        const response = await fetch(`${API_BASE}/groups/${groupId}/users`, {
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'X-User-Id': currentUser.id
            }
        });
        
        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.message || 'Erro ao carregar usuários do grupo');
        }
        
        const data = await response.json();
        currentGroupUsers = data.users.map(u => u.id);
        renderGroupUsers(data.users, groupId);
        
        // Ensure no lingering backdrops before opening modal
        cleanupModalBackdrops();
        
        const groupUsersModalEl = document.getElementById('groupUsersModal');
        const existingModal = bootstrap.Modal.getInstance(groupUsersModalEl);
        if (existingModal) {
            existingModal.show();
        } else {
            new bootstrap.Modal(groupUsersModalEl).show();
        }
    } catch (error) {
        showError('Erro ao carregar usuários do grupo: ' + error.message);
    }
}

// Render group users
function renderGroupUsers(users, groupId) {
    const container = document.getElementById('groupUsersListContainer');
    
    if (!users || users.length === 0) {
        container.innerHTML = '<div class="alert alert-info">Nenhum usuário neste grupo.</div>';
        return;
    }
    
    container.innerHTML = users.map(user => `
        <div class="card mb-2">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <h6 class="mb-0">${user.username}</h6>
                        <small class="text-muted">${user.email}</small>
                    </div>
                    <button class="btn btn-sm btn-danger" onclick="removeUserFromGroup(${groupId}, ${user.id}, '${user.username.replace(/'/g, "\\'")}')">
                        <i class="fas fa-times"></i> Remover
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

// Remove user from group
async function removeUserFromGroup(groupId, userId, username) {
    const confirmed = await showConfirmation(
        'Confirmar Remoção',
        `Tem certeza que deseja remover o usuário "${username}" deste grupo?`
    );
    
    if (!confirmed) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/groups/${groupId}/users/${userId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'X-User-Id': currentUser.id
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showSuccess('Usuário removido do grupo com sucesso!');
            viewGroupUsers(groupId); // Reload users
        } else {
            showError(data.message || 'Erro ao remover usuário do grupo');
        }
    } catch (error) {
        showError('Erro ao remover usuário do grupo: ' + error.message);
    }
}

// Show add user to group modal
async function showAddUserToGroupModal() {
    const groupId = document.getElementById('groupUsersGroupId').value;
    
    if (!groupId) {
        showError('Grupo não identificado.');
        return;
    }
    
    // Clear search field
    document.getElementById('addUserSearch').value = '';
    
    try {
        // Load all users
        const response = await fetch(`${API_BASE}/users/`, {
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'X-User-Id': currentUser.id
            }
        });
        
        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.message || 'Erro ao carregar usuários');
        }
        
        const data = await response.json();
        allAvailableUsers = data.users;
        
        // Filter out users already in the group
        const availableUsers = data.users.filter(user => !currentGroupUsers.includes(user.id));
        
        renderAvailableUsers(availableUsers, groupId);
        
        const modal = new bootstrap.Modal(document.getElementById('addUserToGroupModal'));
        modal.show();
        
        // Clear search when modal is hidden
        document.getElementById('addUserToGroupModal').addEventListener('hidden.bs.modal', function() {
            document.getElementById('addUserSearch').value = '';
        }, { once: true });
    } catch (error) {
        showError('Erro ao carregar usuários: ' + error.message);
    }
}

// Render available users list
function renderAvailableUsers(users, groupId) {
    const container = document.getElementById('availableUsersList');
    
    if (!users || users.length === 0) {
        container.innerHTML = '<div class="alert alert-info">Todos os usuários já estão neste grupo ou não há usuários disponíveis.</div>';
        return;
    }
    
    container.innerHTML = users.map(user => `
        <div class="card mb-2 available-user-card" data-user-id="${user.id}">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <h6 class="mb-0">${user.username}</h6>
                        <small class="text-muted">${user.email}</small>
                        ${user.is_admin ? '<br><span class="badge bg-danger mt-1">Admin</span>' : ''}
                    </div>
                    <button class="btn btn-sm btn-success" onclick="addUserToGroup(${groupId}, ${user.id}, '${user.username.replace(/'/g, "\\'")}')">
                        <i class="fas fa-plus"></i> Adicionar
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

// Filter available users
function filterAvailableUsers() {
    const searchTerm = document.getElementById('addUserSearch').value.toLowerCase();
    const groupId = document.getElementById('groupUsersGroupId').value;
    
    const filteredUsers = allAvailableUsers.filter(user => {
        const matchesSearch = user.username.toLowerCase().includes(searchTerm) || 
                             user.email.toLowerCase().includes(searchTerm);
        const notInGroup = !currentGroupUsers.includes(user.id);
        return matchesSearch && notInGroup;
    });
    
    renderAvailableUsers(filteredUsers, groupId);
}

// Add user to group
async function addUserToGroup(groupId, userId, username) {
    try {
        const response = await fetch(`${API_BASE}/groups/${groupId}/users/${userId}`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'X-User-Id': currentUser.id
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showSuccess(`Usuário "${username}" adicionado ao grupo com sucesso!`);
            
            // Close add user modal properly
            const addUserModal = document.getElementById('addUserToGroupModal');
            const addUserModalInstance = bootstrap.Modal.getInstance(addUserModal);
            if (addUserModalInstance) {
                addUserModalInstance.hide();
            }
            
            // Remove any lingering backdrop
            setTimeout(() => {
                cleanupModalBackdrops();
            }, 300);
            
            // Reload group users after modal is fully closed
            setTimeout(() => {
                viewGroupUsers(groupId);
            }, 400);
        } else {
            showError(data.message || 'Erro ao adicionar usuário ao grupo');
        }
    } catch (error) {
        showError('Erro ao adicionar usuário ao grupo: ' + error.message);
    }
}
