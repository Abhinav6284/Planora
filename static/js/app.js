// Planora - Professional Project Management Application
// Main application state and functionality with demo mode

class PlanoraApp {
    constructor() {
        this.api = new APIClient();
        this.demoMode = true; // Enable demo mode for testing
        this.state = {
            user: null,
            tasks: [],
            projects: [],
            notes: [],
            currentNote: null,
            filters: {
                status: '',
                priority: '',
                search: ''
            }
        };
        this.init();
    }

    async init() {
        this.setupEventListeners();
        
        // Check authentication
        const token = localStorage.getItem('planora_token');
        if (token || this.demoMode) {
            try {
                await this.loadUserData();
                this.showApp();
            } catch (error) {
                this.showLogin();
            }
        } else {
            this.showLogin();
        }

        this.hideLoading();
    }

    setupEventListeners() {
        // Login form
        document.getElementById('login-form').addEventListener('submit', this.handleLogin.bind(this));
        
        // Navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', this.handleNavigation.bind(this));
        });
        
        // Sidebar toggle
        document.getElementById('sidebar-toggle').addEventListener('click', this.toggleSidebar.bind(this));
        
        // User menu
        document.getElementById('user-menu-btn').addEventListener('click', this.toggleUserMenu.bind(this));
        document.getElementById('logout-btn').addEventListener('click', this.handleLogout.bind(this));
        
        // Global search
        document.getElementById('global-search').addEventListener('input', this.handleGlobalSearch.bind(this));
        
        // Refresh data
        document.getElementById('refresh-data').addEventListener('click', this.refreshDashboard.bind(this));
        
        // Task management
        document.getElementById('create-task-btn').addEventListener('click', () => this.showTaskModal());
        document.getElementById('task-form').addEventListener('submit', this.handleTaskSubmit.bind(this));
        document.getElementById('task-modal-close').addEventListener('click', () => this.hideModal('task-modal'));
        document.getElementById('task-modal-cancel').addEventListener('click', () => this.hideModal('task-modal'));
        
        // Task filters
        document.getElementById('task-status-filter').addEventListener('change', this.handleTaskFilter.bind(this));
        document.getElementById('task-priority-filter').addEventListener('change', this.handleTaskFilter.bind(this));
        document.getElementById('task-search').addEventListener('input', this.handleTaskFilter.bind(this));
        
        // Project management
        document.getElementById('create-project-btn').addEventListener('click', () => this.showProjectModal());
        document.getElementById('ai-generate-project').addEventListener('click', this.handleAIProjectGeneration.bind(this));
        document.getElementById('project-form').addEventListener('submit', this.handleProjectSubmit.bind(this));
        document.getElementById('project-modal-close').addEventListener('click', () => this.hideModal('project-modal'));
        document.getElementById('project-modal-cancel').addEventListener('click', () => this.hideModal('project-modal'));
        
        // Notes management
        document.getElementById('create-note-btn').addEventListener('click', this.createNewNote.bind(this));
        document.getElementById('notes-search').addEventListener('input', this.handleNotesSearch.bind(this));
        document.getElementById('save-note').addEventListener('click', this.saveCurrentNote.bind(this));
        document.getElementById('delete-note').addEventListener('click', this.deleteCurrentNote.bind(this));
        
        // AI Chat
        document.getElementById('ai-fab').addEventListener('click', this.toggleAIChat.bind(this));
        document.getElementById('chat-toggle').addEventListener('click', this.toggleAIChat.bind(this));
        document.getElementById('chat-form').addEventListener('submit', this.handleChatSubmit.bind(this));
        
        // Click outside to close dropdowns/modals
        document.addEventListener('click', this.handleOutsideClick.bind(this));
        
        // Keyboard shortcuts
        document.addEventListener('keydown', this.handleKeyboardShortcuts.bind(this));
    }

    hideLoading() {
        document.getElementById('loading-spinner').classList.add('hidden');
    }

    showLogin() {
        document.getElementById('login-screen').classList.remove('hidden');
        document.getElementById('app').classList.add('hidden');
    }

    showApp() {
        document.getElementById('login-screen').classList.add('hidden');
        document.getElementById('app').classList.remove('hidden');
        this.loadDashboard();
    }

    async handleLogin(e) {
        e.preventDefault();
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        
        // Demo mode - accept any credentials
        if (this.demoMode) {
            if (!email || !password) {
                this.showToast('Please enter email and password', 'error');
                return;
            }
            
            // Simulate loading
            const submitBtn = e.target.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Signing In...';
            submitBtn.disabled = true;
            
            setTimeout(() => {
                localStorage.setItem('planora_token', 'demo-token');
                this.state.user = { name: 'Demo User', email: email };
                this.showToast('Welcome to Planora Demo!', 'success');
                this.showApp();
                
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
            }, 1500);
            return;
        }
        
        try {
            const response = await this.api.login(email, password);
            localStorage.setItem('planora_token', response.token);
            this.state.user = response.user;
            this.showToast('Login successful!', 'success');
            this.showApp();
        } catch (error) {
            this.showToast('Login failed: ' + error.message, 'error');
        }
    }

    handleLogout() {
        localStorage.removeItem('planora_token');
        this.state.user = null;
        this.hideUserMenu();
        this.showLogin();
        this.showToast('Logged out successfully', 'success');
    }

    async loadUserData() {
        if (this.demoMode) {
            const savedUser = { name: 'Demo User', email: 'demo@planora.com' };
            this.state.user = savedUser;
            document.getElementById('user-name').textContent = savedUser.name;
            return;
        }
        
        try {
            const userData = await this.api.getCurrentUser();
            this.state.user = userData;
            document.getElementById('user-name').textContent = userData.name || userData.email;
        } catch (error) {
            throw new Error('Failed to load user data');
        }
    }

    toggleSidebar() {
        const sidebar = document.getElementById('sidebar');
        sidebar.classList.toggle('open');
    }

    toggleUserMenu() {
        const dropdown = document.getElementById('user-dropdown');
        dropdown.classList.toggle('hidden');
    }

    hideUserMenu() {
        document.getElementById('user-dropdown').classList.add('hidden');
    }

    handleNavigation(e) {
        e.preventDefault();
        const section = e.currentTarget.getAttribute('data-section');
        this.showSection(section);
        
        // Update active nav item
        document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));
        e.currentTarget.classList.add('active');
        
        // Close sidebar on mobile
        if (window.innerWidth <= 768) {
            document.getElementById('sidebar').classList.remove('open');
        }
    }

    showSection(sectionName) {
        document.querySelectorAll('.content-section').forEach(section => {
            section.classList.remove('active');
        });
        
        const targetSection = document.getElementById(`${sectionName}-section`);
        if (targetSection) {
            targetSection.classList.add('active');
            this.loadSectionData(sectionName);
        }
    }

    async loadSectionData(section) {
        switch (section) {
            case 'overview':
                await this.loadDashboard();
                break;
            case 'tasks':
                await this.loadTasks();
                break;
            case 'projects':
                await this.loadProjects();
                break;
            case 'notes':
                await this.loadNotes();
                break;
            case 'calendar':
                await this.loadCalendar();
                break;
            case 'analytics':
                await this.loadAnalytics();
                break;
        }
    }

    async loadDashboard() {
        try {
            let statsData, dashboardData;
            
            if (this.demoMode) {
                // Demo data
                statsData = {
                    totalTasks: 24,
                    completedTasks: 18,
                    activeProjects: 5,
                    overdueTasks: 3
                };
                
                dashboardData = {
                    recentTasks: [
                        { id: 1, title: 'Update user interface', status: 'in-progress', priority: 'high', due_date: '2025-09-20' },
                        { id: 2, title: 'Review code changes', status: 'todo', priority: 'medium', due_date: '2025-09-21' },
                        { id: 3, title: 'Deploy to production', status: 'completed', priority: 'high', due_date: '2025-09-19' },
                        { id: 4, title: 'Update documentation', status: 'todo', priority: 'low', due_date: '2025-09-22' },
                        { id: 5, title: 'Client meeting preparation', status: 'in-progress', priority: 'high', due_date: '2025-09-20' }
                    ],
                    activeProjects: [
                        { id: 1, name: 'Planora Dashboard', task_count: 8 },
                        { id: 2, name: 'Mobile App Development', task_count: 12 },
                        { id: 3, name: 'API Integration', task_count: 4 }
                    ]
                };
            } else {
                [statsData, dashboardData] = await Promise.all([
                    this.api.getDashboardStats(),
                    this.api.getDashboardData()
                ]);
            }

            // Update stats cards
            document.getElementById('total-tasks').textContent = statsData.totalTasks || 0;
            document.getElementById('completed-tasks').textContent = statsData.completedTasks || 0;
            document.getElementById('active-projects').textContent = statsData.activeProjects || 0;
            document.getElementById('overdue-tasks').textContent = statsData.overdueTasks || 0;
            
            // Update task badge in sidebar
            document.getElementById('tasks-count').textContent = statsData.totalTasks || 0;

            // Load recent tasks
            this.renderRecentTasks(dashboardData.recentTasks || []);
            
            // Load active projects
            this.renderActiveProjects(dashboardData.activeProjects || []);
            
        } catch (error) {
            console.error('Failed to load dashboard:', error);
            this.showToast('Failed to load dashboard data', 'error');
        }
    }

    async refreshDashboard() {
        const refreshBtn = document.getElementById('refresh-data');
        const icon = refreshBtn.querySelector('i');
        icon.style.animation = 'spin 1s linear infinite';
        
        try {
            await this.loadDashboard();
            this.showToast('Dashboard refreshed', 'success');
        } catch (error) {
            this.showToast('Failed to refresh dashboard', 'error');
        } finally {
            setTimeout(() => {
                icon.style.animation = '';
            }, 1000);
        }
    }

    renderRecentTasks(tasks) {
        const container = document.getElementById('recent-tasks');
        
        if (tasks.length === 0) {
            container.innerHTML = '<p class="text-muted">No recent tasks found</p>';
            return;
        }
        
        container.innerHTML = tasks.slice(0, 5).map(task => `
            <div class="task-item" data-task-id="${task.id}">
                <div class="task-checkbox ${task.status === 'completed' ? 'completed' : ''}" 
                     onclick="app.toggleTaskStatus(${task.id})">
                    ${task.status === 'completed' ? '<i class="fas fa-check"></i>' : ''}
                </div>
                <div class="task-content">
                    <div class="task-title ${task.status === 'completed' ? 'completed' : ''}">${task.title}</div>
                    <div class="task-meta">
                        <span class="task-priority ${task.priority}">${task.priority}</span>
                        ${task.due_date ? `<span>Due: ${new Date(task.due_date).toLocaleDateString()}</span>` : ''}
                    </div>
                </div>
            </div>
        `).join('');
    }

    renderActiveProjects(projects) {
        const container = document.getElementById('active-projects-list');
        
        if (projects.length === 0) {
            container.innerHTML = '<p class="text-muted">No active projects found</p>';
            return;
        }
        
        container.innerHTML = projects.slice(0, 3).map(project => `
            <div class="project-item">
                <div class="project-title">${project.name}</div>
                <div class="project-meta text-muted">
                    ${project.task_count || 0} tasks
                </div>
            </div>
        `).join('');
    }

    async loadTasks() {
        try {
            let tasks;
            
            if (this.demoMode) {
                // Demo tasks data
                tasks = [
                    { id: 1, title: 'Update user interface', description: 'Modernize the dashboard UI with new components', status: 'in-progress', priority: 'high', due_date: '2025-09-20', created_at: '2025-09-15' },
                    { id: 2, title: 'Review code changes', description: 'Review pull requests from team members', status: 'todo', priority: 'medium', due_date: '2025-09-21', created_at: '2025-09-16' },
                    { id: 3, title: 'Deploy to production', description: 'Deploy latest version to production servers', status: 'completed', priority: 'high', due_date: '2025-09-19', created_at: '2025-09-14' },
                    { id: 4, title: 'Update documentation', description: 'Update API documentation with new endpoints', status: 'todo', priority: 'low', due_date: '2025-09-22', created_at: '2025-09-17' },
                    { id: 5, title: 'Client meeting preparation', description: 'Prepare presentation for client demo', status: 'in-progress', priority: 'high', due_date: '2025-09-20', created_at: '2025-09-18' },
                    { id: 6, title: 'Database optimization', description: 'Optimize database queries for better performance', status: 'todo', priority: 'medium', due_date: '2025-09-23', created_at: '2025-09-18' },
                    { id: 7, title: 'Security audit', description: 'Conduct security audit of the application', status: 'todo', priority: 'high', due_date: '2025-09-25', created_at: '2025-09-19' },
                    { id: 8, title: 'User feedback analysis', description: 'Analyze user feedback and create improvement plan', status: 'completed', priority: 'medium', due_date: '2025-09-18', created_at: '2025-09-13' }
                ];
            } else {
                tasks = await this.api.getTasks();
            }
            
            this.state.tasks = tasks;
            this.renderTasks();
        } catch (error) {
            console.error('Failed to load tasks:', error);
            this.showToast('Failed to load tasks', 'error');
        }
    }

    renderTasks() {
        const container = document.getElementById('tasks-container');
        let filteredTasks = this.filterTasks();
        
        if (filteredTasks.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-tasks"></i>
                    <h3>No tasks found</h3>
                    <p>Create your first task to get started</p>
                    <button class="btn btn--primary" onclick="app.showTaskModal()">
                        <i class="fas fa-plus"></i> Create Task
                    </button>
                </div>
            `;
            return;
        }
        
        container.innerHTML = filteredTasks.map(task => `
            <div class="task-item" data-task-id="${task.id}">
                <div class="task-checkbox ${task.status === 'completed' ? 'completed' : ''}" 
                     onclick="app.toggleTaskStatus(${task.id})">
                    ${task.status === 'completed' ? '<i class="fas fa-check"></i>' : ''}
                </div>
                <div class="task-content">
                    <div class="task-title ${task.status === 'completed' ? 'completed' : ''}">${task.title}</div>
                    <div class="task-description text-muted">${task.description || ''}</div>
                    <div class="task-meta">
                        <span class="task-priority ${task.priority}">${task.priority}</span>
                        <span class="task-status">${task.status.replace('-', ' ')}</span>
                        ${task.due_date ? `<span>Due: ${new Date(task.due_date).toLocaleDateString()}</span>` : ''}
                    </div>
                </div>
                <div class="task-actions">
                    <button class="btn btn--outline btn--sm" onclick="app.editTask(${task.id})">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn--outline btn--sm" onclick="app.deleteTask(${task.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `).join('');
    }

    filterTasks() {
        return this.state.tasks.filter(task => {
            const statusMatch = !this.state.filters.status || task.status === this.state.filters.status;
            const priorityMatch = !this.state.filters.priority || task.priority === this.state.filters.priority;
            const searchMatch = !this.state.filters.search || 
                task.title.toLowerCase().includes(this.state.filters.search.toLowerCase()) ||
                (task.description && task.description.toLowerCase().includes(this.state.filters.search.toLowerCase()));
            
            return statusMatch && priorityMatch && searchMatch;
        });
    }

    handleTaskFilter() {
        this.state.filters.status = document.getElementById('task-status-filter').value;
        this.state.filters.priority = document.getElementById('task-priority-filter').value;
        this.state.filters.search = document.getElementById('task-search').value;
        this.renderTasks();
    }

    showTaskModal(task = null) {
        const modal = document.getElementById('task-modal');
        const title = document.getElementById('task-modal-title');
        const form = document.getElementById('task-form');
        
        if (task) {
            title.textContent = 'Edit Task';
            document.getElementById('task-title').value = task.title;
            document.getElementById('task-description').value = task.description || '';
            document.getElementById('task-priority').value = task.priority;
            document.getElementById('task-status').value = task.status;
            document.getElementById('task-due-date').value = task.due_date ? task.due_date.split('T')[0] : '';
            form.dataset.taskId = task.id;
        } else {
            title.textContent = 'Create Task';
            form.reset();
            delete form.dataset.taskId;
        }
        
        modal.classList.remove('hidden');
    }

    async handleTaskSubmit(e) {
        e.preventDefault();
        
        const taskData = {
            title: document.getElementById('task-title').value,
            description: document.getElementById('task-description').value,
            priority: document.getElementById('task-priority').value,
            status: document.getElementById('task-status').value,
            due_date: document.getElementById('task-due-date').value || null
        };
        
        try {
            const taskId = e.target.dataset.taskId;
            
            if (this.demoMode) {
                if (taskId) {
                    // Update existing task
                    const taskIndex = this.state.tasks.findIndex(t => t.id == taskId);
                    if (taskIndex !== -1) {
                        this.state.tasks[taskIndex] = { ...this.state.tasks[taskIndex], ...taskData };
                    }
                    this.showToast('Task updated successfully', 'success');
                } else {
                    // Create new task
                    const newTask = {
                        id: Date.now(),
                        ...taskData,
                        created_at: new Date().toISOString()
                    };
                    this.state.tasks.unshift(newTask);
                    this.showToast('Task created successfully', 'success');
                }
            } else {
                if (taskId) {
                    await this.api.updateTask(taskId, taskData);
                    this.showToast('Task updated successfully', 'success');
                } else {
                    await this.api.createTask(taskData);
                    this.showToast('Task created successfully', 'success');
                }
            }
            
            this.hideModal('task-modal');
            if (!this.demoMode) await this.loadTasks();
            else this.renderTasks();
        } catch (error) {
            this.showToast('Failed to save task: ' + error.message, 'error');
        }
    }

    async toggleTaskStatus(taskId) {
        try {
            const task = this.state.tasks.find(t => t.id == taskId);
            if (!task) return;
            
            const newStatus = task.status === 'completed' ? 'todo' : 'completed';
            
            if (this.demoMode) {
                task.status = newStatus;
                this.renderTasks();
                this.renderRecentTasks(this.state.tasks.slice(0, 5));
            } else {
                await this.api.updateTask(taskId, { status: newStatus });
                task.status = newStatus;
                this.renderTasks();
            }
            
            this.showToast(`Task marked as ${newStatus === 'completed' ? 'completed' : 'todo'}`, 'success');
        } catch (error) {
            this.showToast('Failed to update task status', 'error');
        }
    }

    async editTask(taskId) {
        const task = this.state.tasks.find(t => t.id == taskId);
        if (task) {
            this.showTaskModal(task);
        }
    }

    async deleteTask(taskId) {
        if (!confirm('Are you sure you want to delete this task?')) return;
        
        try {
            if (this.demoMode) {
                this.state.tasks = this.state.tasks.filter(t => t.id != taskId);
                this.renderTasks();
            } else {
                await this.api.deleteTask(taskId);
                this.state.tasks = this.state.tasks.filter(t => t.id !== taskId);
                this.renderTasks();
            }
            this.showToast('Task deleted successfully', 'success');
        } catch (error) {
            this.showToast('Failed to delete task', 'error');
        }
    }

    async loadProjects() {
        try {
            let projects;
            
            if (this.demoMode) {
                projects = [
                    { id: 1, name: 'Planora Dashboard', description: 'Professional project management dashboard with modern UI/UX', task_count: 8, created_at: '2025-09-10' },
                    { id: 2, name: 'Mobile App Development', description: 'React Native mobile application for iOS and Android', task_count: 12, created_at: '2025-09-05' },
                    { id: 3, name: 'API Integration', description: 'RESTful API integration with third-party services', task_count: 4, created_at: '2025-09-12' },
                    { id: 4, name: 'Database Migration', description: 'Migration from MySQL to PostgreSQL for better performance', task_count: 6, created_at: '2025-09-08' },
                    { id: 5, name: 'Security Audit', description: 'Comprehensive security audit and penetration testing', task_count: 3, created_at: '2025-09-15' }
                ];
            } else {
                projects = await this.api.getProjects();
            }
            
            this.state.projects = projects;
            this.renderProjects();
        } catch (error) {
            console.error('Failed to load projects:', error);
            this.showToast('Failed to load projects', 'error');
        }
    }

    renderProjects() {
        const container = document.getElementById('projects-container');
        
        if (this.state.projects.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-folder-open"></i>
                    <h3>No projects found</h3>
                    <p>Create your first project to organize your tasks</p>
                    <button class="btn btn--primary" onclick="app.showProjectModal()">
                        <i class="fas fa-plus"></i> Create Project
                    </button>
                </div>
            `;
            return;
        }
        
        container.innerHTML = this.state.projects.map(project => `
            <div class="project-card">
                <div class="project-header">
                    <h3 class="project-title">${project.name}</h3>
                    <button class="project-menu" onclick="app.deleteProject(${project.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
                <p class="project-description">${project.description || 'No description'}</p>
                <div class="project-stats">
                    <span>${project.task_count || 0} tasks</span>
                    <span>Created ${new Date(project.created_at).toLocaleDateString()}</span>
                </div>
            </div>
        `).join('');
    }

    showProjectModal() {
        document.getElementById('project-modal').classList.remove('hidden');
        document.getElementById('project-form').reset();
    }

    async handleProjectSubmit(e) {
        e.preventDefault();
        
        const projectData = {
            name: document.getElementById('project-name').value,
            description: document.getElementById('project-description').value
        };
        
        try {
            if (this.demoMode) {
                const newProject = {
                    id: Date.now(),
                    ...projectData,
                    task_count: 0,
                    created_at: new Date().toISOString()
                };
                this.state.projects.unshift(newProject);
                this.renderProjects();
            } else {
                await this.api.createProject(projectData);
                await this.loadProjects();
            }
            
            this.hideModal('project-modal');
            this.showToast('Project created successfully', 'success');
        } catch (error) {
            this.showToast('Failed to create project: ' + error.message, 'error');
        }
    }

    async deleteProject(projectId) {
        if (!confirm('Are you sure you want to delete this project?')) return;
        
        try {
            if (this.demoMode) {
                this.state.projects = this.state.projects.filter(p => p.id != projectId);
                this.renderProjects();
            } else {
                await this.api.deleteProject(projectId);
                this.state.projects = this.state.projects.filter(p => p.id !== projectId);
                this.renderProjects();
            }
            this.showToast('Project deleted successfully', 'success');
        } catch (error) {
            this.showToast('Failed to delete project', 'error');
        }
    }

    async handleAIProjectGeneration() {
        const prompt = prompt('Describe the project you want to create:', 'e.g., Create a mobile app for food delivery with user authentication and payment integration');
        if (!prompt) return;
        
        try {
            // Show loading toast
            this.showToast('Generating project with AI...', 'info');
            
            // Show loading on button
            const aiBtn = document.getElementById('ai-generate-project');
            const originalContent = aiBtn.innerHTML;
            aiBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
            aiBtn.disabled = true;
            
            setTimeout(() => {
                let project;
                if (this.demoMode) {
                    // Demo AI generation with different project types
                    const projectTypes = [
                        {
                            name: `E-commerce Platform`,
                            description: `Comprehensive e-commerce solution with user authentication, product catalog, shopping cart, payment processing, order management, and admin dashboard. Features include product search, filtering, reviews, wishlist functionality, and mobile-responsive design.`
                        },
                        {
                            name: `Social Media Analytics Dashboard`,
                            description: `Advanced analytics platform for social media management with real-time data visualization, engagement metrics, audience insights, content scheduling, performance tracking, and automated reporting capabilities.`
                        },
                        {
                            name: `Learning Management System`,
                            description: `Educational platform with course creation tools, student progress tracking, interactive assignments, video streaming, discussion forums, grade management, and certification generation.`
                        },
                        {
                            name: `Healthcare Management System`,
                            description: `Digital health solution with patient records management, appointment scheduling, telemedicine integration, prescription tracking, billing system, and HIPAA-compliant data security.`
                        },
                        {
                            name: `Project Collaboration Tool`,
                            description: `Team productivity platform with task management, file sharing, real-time collaboration, video conferencing integration, time tracking, project templates, and progress reporting.`
                        }
                    ];
                    
                    const randomProject = projectTypes[Math.floor(Math.random() * projectTypes.length)];
                    
                    // Customize based on prompt keywords
                    if (prompt.toLowerCase().includes('mobile') || prompt.toLowerCase().includes('app')) {
                        project = {
                            name: `Mobile ${randomProject.name}`,
                            description: `${randomProject.description} Optimized for mobile devices with native iOS and Android applications, offline functionality, push notifications, and seamless cross-platform synchronization.`
                        };
                    } else if (prompt.toLowerCase().includes('ai') || prompt.toLowerCase().includes('machine learning')) {
                        project = {
                            name: `AI-Powered ${randomProject.name}`,
                            description: `${randomProject.description} Enhanced with artificial intelligence features including predictive analytics, natural language processing, automated insights, smart recommendations, and machine learning algorithms.`
                        };
                    } else {
                        project = randomProject;
                    }
                    
                    // Add prompt-specific customization
                    if (prompt.length > 20) {
                        const keywords = prompt.toLowerCase().match(/\b\w{4,}\b/g) || [];
                        if (keywords.length > 0) {
                            const keyword = keywords[0];
                            project.name = `${keyword.charAt(0).toUpperCase() + keyword.slice(1)} ${project.name}`;
                        }
                    }
                } else {
                    project = await this.api.generateAIProject(prompt);
                }
                
                // Fill the project form with AI-generated data
                document.getElementById('project-name').value = project.name;
                document.getElementById('project-description').value = project.description;
                
                // Show the modal
                this.showProjectModal();
                
                // Reset button
                aiBtn.innerHTML = originalContent;
                aiBtn.disabled = false;
                
                this.showToast('✨ AI project generated successfully! Review and save.', 'success');
            }, 2000);
            
        } catch (error) {
            this.showToast('Failed to generate project: ' + error.message, 'error');
            
            // Reset button on error
            const aiBtn = document.getElementById('ai-generate-project');
            aiBtn.innerHTML = '<i class="fas fa-robot"></i> AI Generate';
            aiBtn.disabled = false;
        }
    }

    async loadNotes() {
        try {
            let notes;
            
            if (this.demoMode) {
                notes = [
                    { id: 1, title: 'Project Meeting Notes', content: 'Discussed project timeline and deliverables. Key points:\n\n• Launch date: October 15th\n• Team size: 5 developers\n• Budget approved: $50,000\n• Weekly status meetings on Mondays at 10 AM\n• Use Agile methodology with 2-week sprints\n• Primary stakeholders: John (PM), Sarah (Designer), Mike (CTO)\n\nAction Items:\n- Set up project repository\n- Create initial wireframes\n- Schedule kick-off meeting', created_at: '2025-09-18' },
                    { id: 2, title: 'Technical Architecture', content: 'System architecture decisions:\n\n**Frontend:**\n- React 18 with TypeScript\n- Tailwind CSS for styling\n- React Router for navigation\n- Zustand for state management\n\n**Backend:**\n- Node.js with Express framework\n- PostgreSQL database\n- JWT authentication\n- REST API architecture\n\n**DevOps:**\n- Docker containerization\n- AWS deployment (EC2 + RDS)\n- GitHub Actions for CI/CD\n- Nginx reverse proxy\n\n**Security:**\n- HTTPS encryption\n- Input validation\n- Rate limiting\n- SQL injection prevention', created_at: '2025-09-17' },
                    { id: 3, title: 'Client Requirements', content: 'Client specific requirements gathered from initial consultation:\n\n**Core Features:**\n✓ Mobile responsive design\n✓ Dark/light theme toggle\n✓ Multi-language support (EN, ES, FR)\n✓ Advanced analytics dashboard\n✓ Real-time notifications\n✓ Export functionality (PDF, Excel)\n\n**User Management:**\n- Role-based access control\n- Single sign-on (SSO) integration\n- User activity tracking\n- Password policy enforcement\n\n**Performance:**\n- Page load time < 3 seconds\n- Support for 10,000+ concurrent users\n- 99.9% uptime requirement\n- Automated backups\n\n**Integration:**\n- Slack notifications\n- Calendar sync (Google, Outlook)\n- Third-party API integrations', created_at: '2025-09-16' },
                    { id: 4, title: 'Code Review Guidelines', content: 'Development standards and review process:\n\n**Review Requirements:**\n• All PRs require 2 approvals minimum\n• Unit tests required for new features\n• Code coverage must be > 80%\n• ESLint and Prettier enforcement\n• Documentation updates mandatory\n\n**Performance Standards:**\n- Bundle size optimization\n- Image compression required\n- Lazy loading implementation\n- Database query optimization\n- Caching strategy implementation\n\n**Security Checklist:**\n□ Input sanitization\n□ Authentication checks\n□ Authorization validation\n□ Secure headers\n□ Dependency vulnerability scan\n\n**Code Quality:**\n- Meaningful variable names\n- Function complexity < 10\n- DRY principles\n- SOLID principles\n- Proper error handling', created_at: '2025-09-15' },
                    { id: 5, title: 'Marketing Strategy', content: 'Product launch marketing strategy:\n\n**Phase 1: Pre-Launch (4 weeks)**\n- Build landing page with email signup\n- Create teaser content for social media\n- Reach out to industry influencers\n- Develop press kit and media assets\n\n**Phase 2: Launch Week**\n- Product Hunt launch\n- Social media campaign rollout\n- Email announcement to subscribers\n- Press release distribution\n- Partner announcements\n\n**Content Marketing:**\n📝 Weekly blog posts on industry topics\n🎥 Product demo videos\n📊 Case studies and success stories\n🎙️ Podcast interviews\n📧 Newsletter with tips and updates\n\n**Channels:**\n- LinkedIn: B2B audience targeting\n- Twitter: Tech community engagement\n- YouTube: Tutorial and demo content\n- Medium: Thought leadership articles\n\n**Budget Allocation:**\n- Paid ads: 40% ($20,000)\n- Content creation: 30% ($15,000)\n- Influencer partnerships: 20% ($10,000)\n- Events/conferences: 10% ($5,000)', created_at: '2025-09-14' }
                ];
            } else {
                notes = await this.api.getNotes();
            }
            
            this.state.notes = notes;
            this.renderNotesList();
        } catch (error) {
            console.error('Failed to load notes:', error);
            this.showToast('Failed to load notes', 'error');
        }
    }

    renderNotesList() {
        const container = document.getElementById('notes-list');
        
        if (this.state.notes.length === 0) {
            container.innerHTML = '<p class="text-muted p-16">No notes found</p>';
            return;
        }
        
        container.innerHTML = this.state.notes.map(note => `
            <div class="note-item ${note.id === (this.state.currentNote?.id) ? 'active' : ''}" 
                 onclick="app.selectNote(${note.id})">
                <div class="note-item-title">${note.title}</div>
                <div class="note-item-preview">${(note.content || '').substring(0, 100)}${note.content && note.content.length > 100 ? '...' : ''}</div>
            </div>
        `).join('');
    }

    selectNote(noteId) {
        const note = this.state.notes.find(n => n.id == noteId);
        if (!note) return;
        
        this.state.currentNote = note;
        
        // Update UI
        document.getElementById('note-editor-placeholder').classList.add('hidden');
        document.getElementById('note-editor-content').classList.remove('hidden');
        
        document.getElementById('note-title').value = note.title;
        document.getElementById('note-content').value = note.content || '';
        
        // Update active state
        document.querySelectorAll('.note-item').forEach(item => item.classList.remove('active'));
        document.querySelector(`[onclick="app.selectNote(${noteId})"]`)?.classList.add('active');
    }

    async createNewNote() {
        try {
            let newNote;
            
            if (this.demoMode) {
                newNote = {
                    id: Date.now(),
                    title: 'Untitled Note',
                    content: '',
                    created_at: new Date().toISOString()
                };
                this.state.notes.unshift(newNote);
            } else {
                newNote = await this.api.createNote({
                    title: 'Untitled Note',
                    content: ''
                });
                this.state.notes.unshift(newNote);
            }
            
            this.renderNotesList();
            this.selectNote(newNote.id);
            this.showToast('New note created', 'success');
        } catch (error) {
            this.showToast('Failed to create note', 'error');
        }
    }

    async saveCurrentNote() {
        if (!this.state.currentNote) return;
        
        try {
            const noteData = {
                title: document.getElementById('note-title').value,
                content: document.getElementById('note-content').value
            };
            
            if (this.demoMode) {
                // Update local state
                this.state.currentNote.title = noteData.title;
                this.state.currentNote.content = noteData.content;
                
                const noteIndex = this.state.notes.findIndex(n => n.id == this.state.currentNote.id);
                if (noteIndex !== -1) {
                    this.state.notes[noteIndex] = { ...this.state.currentNote };
                }
            } else {
                await this.api.updateNote(this.state.currentNote.id, noteData);
                
                // Update local state
                this.state.currentNote.title = noteData.title;
                this.state.currentNote.content = noteData.content;
                
                const noteIndex = this.state.notes.findIndex(n => n.id === this.state.currentNote.id);
                if (noteIndex !== -1) {
                    this.state.notes[noteIndex] = { ...this.state.currentNote };
                }
            }
            
            this.renderNotesList();
            this.showToast('Note saved successfully', 'success');
        } catch (error) {
            this.showToast('Failed to save note', 'error');
        }
    }

    async deleteCurrentNote() {
        if (!this.state.currentNote) return;
        if (!confirm('Are you sure you want to delete this note?')) return;
        
        try {
            if (this.demoMode) {
                this.state.notes = this.state.notes.filter(n => n.id != this.state.currentNote.id);
            } else {
                await this.api.deleteNote(this.state.currentNote.id);
                this.state.notes = this.state.notes.filter(n => n.id !== this.state.currentNote.id);
            }
            
            this.state.currentNote = null;
            
            document.getElementById('note-editor-placeholder').classList.remove('hidden');
            document.getElementById('note-editor-content').classList.add('hidden');
            
            this.renderNotesList();
            this.showToast('Note deleted successfully', 'success');
        } catch (error) {
            this.showToast('Failed to delete note', 'error');
        }
    }

    handleNotesSearch(e) {
        const searchTerm = e.target.value.toLowerCase();
        const filteredNotes = this.state.notes.filter(note => 
            note.title.toLowerCase().includes(searchTerm) ||
            (note.content && note.content.toLowerCase().includes(searchTerm))
        );
        
        // Render filtered notes
        const container = document.getElementById('notes-list');
        if (filteredNotes.length === 0) {
            container.innerHTML = '<p class="text-muted p-16">No notes match your search</p>';
            return;
        }
        
        container.innerHTML = filteredNotes.map(note => `
            <div class="note-item ${note.id === (this.state.currentNote?.id) ? 'active' : ''}" 
                 onclick="app.selectNote(${note.id})">
                <div class="note-item-title">${note.title}</div>
                <div class="note-item-preview">${(note.content || '').substring(0, 100)}${note.content && note.content.length > 100 ? '...' : ''}</div>
            </div>
        `).join('');
    }

    async loadCalendar() {
        try {
            // Create a functional calendar view
            const container = document.getElementById('calendar-container');
            
            // Clear existing content
            container.innerHTML = '';
            
            // Calendar header
            const calendarHeader = document.createElement('div');
            calendarHeader.className = 'calendar-header';
            calendarHeader.innerHTML = `
                <div class="calendar-nav">
                    <button class="btn btn--outline btn--sm" onclick="app.previousMonth()">
                        <i class="fas fa-chevron-left"></i>
                    </button>
                    <h3 id="calendar-month">${this.getCurrentMonthYear()}</h3>
                    <button class="btn btn--outline btn--sm" onclick="app.nextMonth()">
                        <i class="fas fa-chevron-right"></i>
                    </button>
                </div>
                <div class="calendar-legend">
                    <span class="legend-item">
                        <span class="legend-dot high"></span>
                        High Priority
                    </span>
                    <span class="legend-item">
                        <span class="legend-dot medium"></span>
                        Medium Priority
                    </span>
                    <span class="legend-item">
                        <span class="legend-dot low"></span>
                        Low Priority
                    </span>
                </div>
            `;
            
            // Calendar grid
            const calendarGrid = document.createElement('div');
            calendarGrid.className = 'calendar-grid';
            calendarGrid.id = 'calendar-grid';
            
            container.appendChild(calendarHeader);
            container.appendChild(calendarGrid);
            
            this.currentDate = new Date();
            this.renderCalendar();
            
        } catch (error) {
            console.error('Failed to load calendar:', error);
            this.showToast('Failed to load calendar', 'error');
        }
    }

    getCurrentMonthYear() {
        const months = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ];
        return `${months[this.currentDate.getMonth()]} ${this.currentDate.getFullYear()}`;
    }

    previousMonth() {
        this.currentDate.setMonth(this.currentDate.getMonth() - 1);
        document.getElementById('calendar-month').textContent = this.getCurrentMonthYear();
        this.renderCalendar();
    }

    nextMonth() {
        this.currentDate.setMonth(this.currentDate.getMonth() + 1);
        document.getElementById('calendar-month').textContent = this.getCurrentMonthYear();
        this.renderCalendar();
    }

    renderCalendar() {
        const grid = document.getElementById('calendar-grid');
        if (!grid) return;
        
        // Clear grid
        grid.innerHTML = '';
        
        // Day headers
        const dayHeaders = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
        dayHeaders.forEach(day => {
            const dayHeader = document.createElement('div');
            dayHeader.className = 'calendar-day-header';
            dayHeader.textContent = day;
            grid.appendChild(dayHeader);
        });
        
        // Get calendar data
        const year = this.currentDate.getFullYear();
        const month = this.currentDate.getMonth();
        const firstDay = new Date(year, month, 1);
        const lastDay = new Date(year, month + 1, 0);
        const startDate = new Date(firstDay);
        startDate.setDate(startDate.getDate() - firstDay.getDay());
        
        // Get tasks for the current month
        const tasksThisMonth = this.state.tasks.filter(task => {
            if (!task.due_date) return false;
            const taskDate = new Date(task.due_date);
            return taskDate.getMonth() === month && taskDate.getFullYear() === year;
        });
        
        // Render 42 days (6 weeks)
        for (let i = 0; i < 42; i++) {
            const currentDay = new Date(startDate);
            currentDay.setDate(startDate.getDate() + i);
            
            const dayElement = document.createElement('div');
            dayElement.className = `calendar-day ${currentDay.getMonth() !== month ? 'other-month' : ''}`;
            
            const dayNumber = document.createElement('div');
            dayNumber.className = 'day-number';
            dayNumber.textContent = currentDay.getDate();
            dayElement.appendChild(dayNumber);
            
            // Add tasks for this day
            const dayTasks = tasksThisMonth.filter(task => {
                const taskDate = new Date(task.due_date);
                return taskDate.getDate() === currentDay.getDate() &&
                       taskDate.getMonth() === currentDay.getMonth() &&
                       taskDate.getFullYear() === currentDay.getFullYear();
            });
            
            if (dayTasks.length > 0) {
                const tasksContainer = document.createElement('div');
                tasksContainer.className = 'day-tasks';
                
                dayTasks.slice(0, 3).forEach(task => {
                    const taskElement = document.createElement('div');
                    taskElement.className = `task-dot ${task.priority} ${task.status === 'completed' ? 'completed' : ''}`;
                    taskElement.title = `${task.title} (${task.priority} priority)`;
                    taskElement.textContent = task.title.substring(0, 15) + (task.title.length > 15 ? '...' : '');
                    tasksContainer.appendChild(taskElement);
                });
                
                if (dayTasks.length > 3) {
                    const moreElement = document.createElement('div');
                    moreElement.className = 'task-more';
                    moreElement.textContent = `+${dayTasks.length - 3} more`;
                    tasksContainer.appendChild(moreElement);
                }
                
                dayElement.appendChild(tasksContainer);
            }
            
            // Mark today
            const today = new Date();
            if (currentDay.toDateString() === today.toDateString()) {
                dayElement.classList.add('today');
            }
            
            grid.appendChild(dayElement);
        }
    }

    async loadAnalytics() {
        try {
            let stats;
            
            if (this.demoMode) {
                stats = {
                    weeklyCompletion: [2, 5, 3, 8, 6, 4, 7],
                    highPriority: 5,
                    mediumPriority: 10,
                    lowPriority: 8
                };
            } else {
                stats = await this.api.getTaskStats();
            }
            
            this.renderCharts(stats);
        } catch (error) {
            console.error('Failed to load analytics:', error);
            this.showToast('Failed to load analytics', 'error');
        }
    }

    renderCharts(stats) {
        // Completion trend chart
        const completionCtx = document.getElementById('completion-chart');
        if (completionCtx && !completionCtx.chart) {
            completionCtx.chart = new Chart(completionCtx, {
                type: 'line',
                data: {
                    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                    datasets: [{
                        label: 'Completed Tasks',
                        data: stats.weeklyCompletion || [2, 5, 3, 8, 6, 4, 7],
                        borderColor: '#1FB8CD',
                        backgroundColor: 'rgba(31, 184, 205, 0.1)',
                        tension: 0.4,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            labels: {
                                color: '#f0f6fc'
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                color: '#8b949e'
                            },
                            grid: {
                                color: 'rgba(240, 246, 252, 0.1)'
                            }
                        },
                        x: {
                            ticks: {
                                color: '#8b949e'
                            },
                            grid: {
                                color: 'rgba(240, 246, 252, 0.1)'
                            }
                        }
                    }
                }
            });
        }

        // Priority distribution chart
        const priorityCtx = document.getElementById('priority-chart');
        if (priorityCtx && !priorityCtx.chart) {
            priorityCtx.chart = new Chart(priorityCtx, {
                type: 'doughnut',
                data: {
                    labels: ['High', 'Medium', 'Low'],
                    datasets: [{
                        data: [
                            stats.highPriority || 5,
                            stats.mediumPriority || 10,
                            stats.lowPriority || 8
                        ],
                        backgroundColor: ['#1FB8CD', '#FFC185', '#B4413C'],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                color: '#f0f6fc',
                                padding: 20
                            }
                        }
                    }
                }
            });
        }
    }

    toggleAIChat() {
        const chatWidget = document.getElementById('ai-chat');
        chatWidget.classList.toggle('hidden');
        
        if (!chatWidget.classList.contains('hidden')) {
            document.getElementById('chat-input').focus();
        }
    }

    async handleChatSubmit(e) {
        e.preventDefault();
        const input = document.getElementById('chat-input');
        const message = input.value.trim();
        if (!message) return;
        
        // Add user message
        this.addChatMessage(message, false);
        input.value = '';
        
        try {
            let response;
            if (this.demoMode) {
                // Demo AI responses
                const responses = [
                    "I can help you create tasks, manage projects, and organize your workflow. What would you like to do?",
                    "Great question! For better task management, try organizing tasks by priority and setting realistic deadlines.",
                    "I'd suggest breaking down large projects into smaller, manageable tasks. This makes tracking progress easier.",
                    "You can use the search functionality to quickly find specific tasks or projects. Try the search bar at the top!",
                    "Consider using the Analytics section to track your productivity trends and identify areas for improvement.",
                    "Pro tip: Use keyboard shortcuts like Ctrl+N to quickly create new tasks!",
                    "The Calendar view helps you visualize your deadlines and plan your schedule effectively.",
                    "For better organization, try creating projects first, then add related tasks to keep everything structured."
                ];
                const randomResponse = responses[Math.floor(Math.random() * responses.length)];
                
                setTimeout(() => {
                    this.addChatMessage(randomResponse, true);
                }, 1000);
            } else {
                response = await this.api.chatWithAI(message);
                this.addChatMessage(response.message, true);
            }
        } catch (error) {
            this.addChatMessage('Sorry, I encountered an error. Please try again.', true);
        }
    }

    addChatMessage(message, isAI) {
        const messagesContainer = document.getElementById('chat-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${isAI ? 'ai-message' : 'user-message'}`;
        messageDiv.innerHTML = `
            <i class="fas ${isAI ? 'fa-robot' : 'fa-user'}"></i>
            <p>${message}</p>
        `;
        
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    handleGlobalSearch(e) {
        const searchTerm = e.target.value.toLowerCase();
        if (!searchTerm) return;
        
        // Search across tasks, projects, and notes
        const results = {
            tasks: this.state.tasks.filter(task => 
                task.title.toLowerCase().includes(searchTerm) ||
                (task.description && task.description.toLowerCase().includes(searchTerm))
            ),
            projects: this.state.projects.filter(project =>
                project.name.toLowerCase().includes(searchTerm) ||
                (project.description && project.description.toLowerCase().includes(searchTerm))
            ),
            notes: this.state.notes.filter(note =>
                note.title.toLowerCase().includes(searchTerm) ||
                (note.content && note.content.toLowerCase().includes(searchTerm))
            )
        };
        
        console.log('Global search results:', results);
        // You could implement a search results dropdown here
    }

    hideModal(modalId) {
        document.getElementById(modalId).classList.add('hidden');
    }

    handleOutsideClick(e) {
        // Close user dropdown if clicking outside
        if (!e.target.closest('.user-menu')) {
            this.hideUserMenu();
        }
        
        // Close modals if clicking on overlay
        if (e.target.classList.contains('modal')) {
            e.target.classList.add('hidden');
        }
    }

    handleKeyboardShortcuts(e) {
        // Ctrl+N for new task
        if (e.ctrlKey && e.key === 'n') {
            e.preventDefault();
            this.showTaskModal();
        }
        
        // Escape to close modals
        if (e.key === 'Escape') {
            document.querySelectorAll('.modal:not(.hidden)').forEach(modal => {
                modal.classList.add('hidden');
            });
            
            // Close AI chat
            document.getElementById('ai-chat').classList.add('hidden');
        }
    }

    showToast(message, type = 'info') {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <div class="toast-content">
                <p>${message}</p>
            </div>
        `;
        
        container.appendChild(toast);
        
        // Remove toast after 3 seconds
        setTimeout(() => {
            toast.style.animation = 'slideOut 0.3s ease-out forwards';
            setTimeout(() => {
                if (container.contains(toast)) {
                    container.removeChild(toast);
                }
            }, 300);
        }, 3000);
    }
}

// API Client Class
class APIClient {
    constructor() {
        this.baseURL = '/api';
        this.token = localStorage.getItem('planora_token');
    }

    getHeaders() {
        const headers = {
            'Content-Type': 'application/json'
        };
        
        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }
        
        return headers;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: this.getHeaders(),
            ...options
        };

        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.message || `HTTP ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error(`API request failed: ${endpoint}`, error);
            throw error;
        }
    }

    // Authentication
    async login(email, password) {
        return this.request('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });
    }

    async getCurrentUser() {
        return this.request('/auth/me');
    }

    // Dashboard
    async getDashboardStats() {
        return this.request('/dashboard/stats');
    }

    async getDashboardData() {
        return this.request('/dashboard/data');
    }

    // Tasks
    async getTasks() {
        return this.request('/tasks');
    }

    async createTask(taskData) {
        return this.request('/tasks', {
            method: 'POST',
            body: JSON.stringify(taskData)
        });
    }

    async updateTask(taskId, taskData) {
        return this.request(`/tasks/${taskId}`, {
            method: 'PUT',
            body: JSON.stringify(taskData)
        });
    }

    async deleteTask(taskId) {
        return this.request(`/tasks/${taskId}`, {
            method: 'DELETE'
        });
    }

    async getTaskStats() {
        return this.request('/tasks/stats');
    }

    // Projects
    async getProjects() {
        return this.request('/projects');
    }

    async createProject(projectData) {
        return this.request('/projects', {
            method: 'POST',
            body: JSON.stringify(projectData)
        });
    }

    async deleteProject(projectId) {
        return this.request(`/projects/${projectId}`, {
            method: 'DELETE'
        });
    }

    // Notes
    async getNotes() {
        return this.request('/notes');
    }

    async createNote(noteData) {
        return this.request('/notes', {
            method: 'POST',
            body: JSON.stringify(noteData)
        });
    }

    async updateNote(noteId, noteData) {
        return this.request(`/notes/${noteId}`, {
            method: 'PUT',
            body: JSON.stringify(noteData)
        });
    }

    async deleteNote(noteId) {
        return this.request(`/notes/${noteId}`, {
            method: 'DELETE'
        });
    }

    // AI
    async generateAIProject(prompt) {
        return this.request('/ai/generate-project', {
            method: 'POST',
            body: JSON.stringify({ prompt })
        });
    }

    async chatWithAI(message) {
        return this.request('/roadmap/chat', {
            method: 'POST',
            body: JSON.stringify({ message })
        });
    }
}

// Initialize application
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new PlanoraApp();
});

// Add additional CSS for calendar and enhanced features
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOut {
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
    
    .empty-state {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: var(--space-32);
        text-align: center;
        color: var(--planora-text-secondary);
        min-height: 400px;
    }
    
    .empty-state i {
        font-size: 64px;
        margin-bottom: var(--space-20);
        opacity: 0.5;
    }
    
    .empty-state h3 {
        margin: 0 0 var(--space-8) 0;
        color: var(--planora-text);
    }
    
    .empty-state p {
        margin: 0 0 var(--space-20) 0;
    }
    
    .task-actions {
        display: flex;
        gap: var(--space-8);
        margin-left: auto;
    }
    
    .project-item {
        padding: var(--space-12) 0;
        border-bottom: 1px solid var(--planora-border);
    }
    
    .project-item:last-child {
        border-bottom: none;
    }
    
    .project-title {
        font-weight: var(--font-weight-medium);
        color: var(--planora-text);
        margin-bottom: var(--space-4);
    }
    
    .toast-content p {
        margin: 0;
        color: var(--planora-text);
    }
    
    .task-description {
        margin: var(--space-4) 0;
        font-size: var(--font-size-sm);
    }
    
    /* Calendar Styles */
    .calendar-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: var(--space-24);
        padding-bottom: var(--space-16);
        border-bottom: 1px solid var(--planora-border);
    }
    
    .calendar-nav {
        display: flex;
        align-items: center;
        gap: var(--space-16);
    }
    
    .calendar-nav h3 {
        margin: 0;
        min-width: 200px;
        text-align: center;
        font-size: var(--font-size-xl);
        color: var(--planora-text);
    }
    
    .calendar-legend {
        display: flex;
        gap: var(--space-20);
    }
    
    .legend-item {
        display: flex;
        align-items: center;
        gap: var(--space-8);
        font-size: var(--font-size-sm);
        color: var(--planora-text-secondary);
    }
    
    .legend-dot {
        width: 12px;
        height: 12px;
        border-radius: 50%;
    }
    
    .legend-dot.high { background: #da3633; }
    .legend-dot.medium { background: #d29922; }
    .legend-dot.low { background: #238636; }
    
    .calendar-grid {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 1px;
        background: var(--planora-border);
        border: 1px solid var(--planora-border);
        border-radius: var(--radius-base);
        overflow: hidden;
    }
    
    .calendar-day-header {
        background: var(--planora-surface);
        padding: var(--space-12);
        text-align: center;
        font-weight: var(--font-weight-semibold);
        color: var(--planora-text-secondary);
        font-size: var(--font-size-sm);
    }
    
    .calendar-day {
        background: var(--planora-surface);
        min-height: 100px;
        padding: var(--space-8);
        position: relative;
        transition: all var(--duration-fast) var(--ease-standard);
    }
    
    .calendar-day:hover {
        background: var(--planora-hover);
    }
    
    .calendar-day.today {
        background: rgba(31, 184, 205, 0.1);
        border: 2px solid var(--planora-primary);
    }
    
    .calendar-day.other-month {
        opacity: 0.3;
    }
    
    .day-number {
        font-weight: var(--font-weight-medium);
        color: var(--planora-text);
        margin-bottom: var(--space-4);
    }
    
    .day-tasks {
        display: flex;
        flex-direction: column;
        gap: var(--space-2);
    }
    
    .task-dot {
        font-size: 10px;
        padding: var(--space-2) var(--space-4);
        border-radius: var(--radius-sm);
        color: white;
        font-weight: var(--font-weight-medium);
        cursor: pointer;
        transition: all var(--duration-fast) var(--ease-standard);
    }
    
    .task-dot.high { background: #da3633; }
    .task-dot.medium { background: #d29922; }
    .task-dot.low { background: #238636; }
    
    .task-dot.completed {
        opacity: 0.6;
        text-decoration: line-through;
    }
    
    .task-dot:hover {
        transform: translateY(-1px);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    }
    
    .task-more {
        font-size: 10px;
        color: var(--planora-text-secondary);
        font-style: italic;
        margin-top: var(--space-2);
    }
    
    @media (max-width: 768px) {
        .calendar-header {
            flex-direction: column;
            gap: var(--space-16);
        }
        
        .calendar-legend {
            flex-wrap: wrap;
            justify-content: center;
        }
        
        .calendar-day {
            min-height: 80px;
            font-size: var(--font-size-sm);
        }
        
        .task-dot {
            font-size: 8px;
        }
    }
`;
document.head.appendChild(style);