// FastAPI Todo App - Frontend JavaScript
class TodoApp {
    constructor() {
        this.token = localStorage.getItem('token');
        this.user = JSON.parse(localStorage.getItem('user') || 'null');
        this.todos = [];
        this.currentFilter = 'all';
        this.currentTodoId = null;
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.checkAuth();
    }

    // Authentication Methods
    checkAuth() {
        if (this.token && this.user) {
            this.showMainApp();
            this.loadUserData();
            this.loadTodos();
        } else {
            this.showAuthSection();
        }
        this.hideLoading();
    }

    async login(username, password) {
        try {
            const formData = new FormData();
            formData.append('username', username);
            formData.append('password', password);

            const response = await fetch('/auth/token', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const data = await response.json();
                this.token = data.access_token;
                this.user = { username: username }; // Store basic user info
                
                localStorage.setItem('token', this.token);
                localStorage.setItem('user', JSON.stringify(this.user));
                
                this.showNotification('Login successful!', 'success');
                this.showMainApp();
                this.loadUserData();
                this.loadTodos();
            } else {
                const error = await response.json();
                throw new Error(error.detail || 'Login failed');
            }
        } catch (error) {
            this.showNotification(error.message, 'error');
        }
    }

    async register(userData) {
        try {
            const response = await fetch('/auth/new-user', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(userData)
            });

            if (response.ok) {
                this.showNotification('Registration successful! Please login.', 'success');
                this.showLoginForm();
            } else {
                const error = await response.json();
                throw new Error(error.detail || 'Registration failed');
            }
        } catch (error) {
            this.showNotification(error.message, 'error');
        }
    }

    logout() {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        this.token = null;
        this.user = null;
        this.todos = [];
        this.showAuthSection();
        this.showNotification('Logged out successfully', 'success');
    }

    // API Helper Methods
    async makeAuthenticatedRequest(url, options = {}) {
        const headers = {
            'Authorization': `Bearer ${this.token}`,
            'Content-Type': 'application/json',
            ...options.headers
        };

        const response = await fetch(url, {
            ...options,
            headers
        });

        if (response.status === 401) {
            this.logout();
            throw new Error('Session expired. Please login again.');
        }

        return response;
    }

    // User Data Methods
    async loadUserData() {
        try {
            const response = await this.makeAuthenticatedRequest('/users/user-info');
            if (response.ok) {
                const userData = await response.json();
                this.user = { ...this.user, ...userData };
                localStorage.setItem('user', JSON.stringify(this.user));
                this.updateUserDisplay();
                
                // Show admin features if user is admin
                if (this.user.role === 'admin') {
                    this.showAdminFeatures();
                }
            }
        } catch (error) {
            console.error('Error loading user data:', error);
        }
    }

    updateUserDisplay() {
        const usernameDisplay = document.getElementById('username-display');
        const profileName = document.getElementById('profile-name');
        const profileEmail = document.getElementById('profile-email');
        const profilePhone = document.getElementById('profile-phone');

        if (usernameDisplay) usernameDisplay.textContent = this.user.username;
        if (profileName) profileName.textContent = `${this.user.first_name} ${this.user.last_name}`;
        if (profileEmail) profileEmail.textContent = this.user.email;
        if (profilePhone) profilePhone.textContent = this.user.phone_number;
    }

    async changePassword(oldPassword, newPassword) {
        try {
            const response = await this.makeAuthenticatedRequest(`/users/change-password?old_password=${oldPassword}&new_password=${newPassword}`, {
                method: 'POST'
            });

            if (response.ok) {
                this.showNotification('Password updated successfully!', 'success');
                this.closeModal('password-modal');
            } else {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to update password');
            }
        } catch (error) {
            this.showNotification(error.message, 'error');
        }
    }

    async changePhoneNumber(newPhone) {
        try {
            const response = await this.makeAuthenticatedRequest(`/users/change-phone-number?new_phone_number=${newPhone}`, {
                method: 'POST'
            });

            if (response.ok) {
                this.user.phone_number = newPhone;
                localStorage.setItem('user', JSON.stringify(this.user));
                this.updateUserDisplay();
                this.showNotification('Phone number updated successfully!', 'success');
                this.closeModal('phone-modal');
            } else {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to update phone number');
            }
        } catch (error) {
            this.showNotification(error.message, 'error');
        }
    }

    // Todo Methods
    async loadTodos() {
        try {
            const response = await this.makeAuthenticatedRequest('/todos/');
            if (response.ok) {
                this.todos = await response.json();
                this.renderTodos();
                this.updateStats();
            }
        } catch (error) {
            this.showNotification(error.message, 'error');
        }
    }

    async createTodo(todoData) {
        try {
            const response = await this.makeAuthenticatedRequest('/todos/', {
                method: 'POST',
                body: JSON.stringify(todoData)
            });

            if (response.ok) {
                this.showNotification('Todo created successfully!', 'success');
                this.loadTodos();
                this.closeModal('todo-modal');
            } else {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to create todo');
            }
        } catch (error) {
            this.showNotification(error.message, 'error');
        }
    }

    async updateTodo(todoId, todoData) {
        try {
            const response = await this.makeAuthenticatedRequest(`/todos/${todoId}`, {
                method: 'PUT',
                body: JSON.stringify(todoData)
            });

            if (response.ok) {
                this.showNotification('Todo updated successfully!', 'success');
                this.loadTodos();
                this.closeModal('todo-modal');
            } else {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to update todo');
            }
        } catch (error) {
            this.showNotification(error.message, 'error');
        }
    }

    async deleteTodo(todoId) {
        if (!confirm('Are you sure you want to delete this todo?')) return;

        try {
            const response = await this.makeAuthenticatedRequest(`/todos/${todoId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                this.showNotification('Todo deleted successfully!', 'success');
                this.loadTodos();
            } else {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to delete todo');
            }
        } catch (error) {
            this.showNotification(error.message, 'error');
        }
    }

    async toggleTodoComplete(todoId, completed) {
        const todo = this.todos.find(t => t.id === todoId);
        if (!todo) return;

        const updatedTodo = { ...todo, complete: completed };
        delete updatedTodo.id;
        delete updatedTodo.owner_id;

        await this.updateTodo(todoId, updatedTodo);
    }

    // Admin Methods
    async loadAdminTodos() {
        try {
            const response = await this.makeAuthenticatedRequest('/admin/todos');
            if (response.ok) {
                const adminTodos = await response.json();
                this.renderAdminTodos(adminTodos);
                document.getElementById('admin-total-todos').textContent = adminTodos.length;
            }
        } catch (error) {
            this.showNotification(error.message, 'error');
        }
    }

    async adminDeleteTodo(todoId) {
        if (!confirm('Are you sure you want to delete this todo? (Admin action)')) return;

        try {
            const response = await this.makeAuthenticatedRequest(`/admin/todos/${todoId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                this.showNotification('Todo deleted successfully! (Admin)', 'success');
                this.loadAdminTodos();
            } else {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to delete todo');
            }
        } catch (error) {
            this.showNotification(error.message, 'error');
        }
    }

    // Rendering Methods
    renderTodos() {
        const todoList = document.getElementById('todo-list');
        const emptyState = document.getElementById('empty-todos');

        let filteredTodos = this.todos;

        // Apply filters
        switch (this.currentFilter) {
            case 'pending':
                filteredTodos = this.todos.filter(todo => !todo.complete);
                break;
            case 'completed':
                filteredTodos = this.todos.filter(todo => todo.complete);
                break;
            case 'high':
                filteredTodos = this.todos.filter(todo => todo.priority >= 4);
                break;
        }

        if (filteredTodos.length === 0) {
            emptyState.style.display = 'block';
            todoList.innerHTML = '';
            todoList.appendChild(emptyState);
            return;
        }

        emptyState.style.display = 'none';
        todoList.innerHTML = '';

        filteredTodos.forEach(todo => {
            const todoElement = this.createTodoElement(todo);
            todoList.appendChild(todoElement);
        });
    }

    createTodoElement(todo) {
        const todoDiv = document.createElement('div');
        todoDiv.className = `todo-item priority-${todo.priority} ${todo.complete ? 'completed' : ''}`;
        todoDiv.innerHTML = `
            <div class="todo-header">
                <div>
                    <h3 class="todo-title">${this.escapeHtml(todo.title)}</h3>
                    <span class="todo-priority">${this.getPriorityText(todo.priority)}</span>
                </div>
            </div>
            <p class="todo-description">${this.escapeHtml(todo.description)}</p>
            <div class="todo-actions">
                <button class="complete-btn" onclick="app.toggleTodoComplete(${todo.id}, ${!todo.complete})">
                    <i class="fas fa-${todo.complete ? 'undo' : 'check'}"></i>
                    ${todo.complete ? 'Undo' : 'Complete'}
                </button>
                <button class="edit-btn" onclick="app.openEditTodo(${todo.id})">
                    <i class="fas fa-edit"></i> Edit
                </button>
                <button class="delete-btn" onclick="app.deleteTodo(${todo.id})">
                    <i class="fas fa-trash"></i> Delete
                </button>
            </div>
        `;
        return todoDiv;
    }

    renderAdminTodos(todos) {
        const todoList = document.getElementById('admin-todo-list');
        const emptyState = document.getElementById('empty-admin-todos');

        if (todos.length === 0) {
            emptyState.style.display = 'block';
            todoList.innerHTML = '';
            todoList.appendChild(emptyState);
            return;
        }

        emptyState.style.display = 'none';
        todoList.innerHTML = '';

        todos.forEach(todo => {
            const todoElement = this.createAdminTodoElement(todo);
            todoList.appendChild(todoElement);
        });
    }

    createAdminTodoElement(todo) {
        const todoDiv = document.createElement('div');
        todoDiv.className = `todo-item priority-${todo.priority} ${todo.complete ? 'completed' : ''}`;
        todoDiv.innerHTML = `
            <div class="todo-header">
                <div>
                    <h3 class="todo-title">${this.escapeHtml(todo.title)}</h3>
                    <span class="todo-priority">${this.getPriorityText(todo.priority)}</span>
                </div>
            </div>
            <p class="todo-description">${this.escapeHtml(todo.description)}</p>
            <p><strong>Owner ID:</strong> ${todo.owner_id}</p>
            <div class="todo-actions">
                <button class="delete-btn" onclick="app.adminDeleteTodo(${todo.id})">
                    <i class="fas fa-trash"></i> Delete (Admin)
                </button>
            </div>
        `;
        return todoDiv;
    }

    updateStats() {
        const total = this.todos.length;
        const completed = this.todos.filter(todo => todo.complete).length;
        const pending = total - completed;

        document.getElementById('total-todos').textContent = total;
        document.getElementById('completed-todos').textContent = completed;
        document.getElementById('pending-todos').textContent = pending;
    }

    // UI Helper Methods
    showAuthSection() {
        document.getElementById('auth-section').style.display = 'flex';
        document.getElementById('main-app').classList.remove('active');
    }

    showMainApp() {
        document.getElementById('auth-section').style.display = 'none';
        document.getElementById('main-app').classList.add('active');
    }

    hideLoading() {
        document.getElementById('loading-screen').style.display = 'none';
    }

    showLoginForm() {
        document.getElementById('login-form').classList.add('active');
        document.getElementById('register-form').classList.remove('active');
    }

    showRegisterForm() {
        document.getElementById('login-form').classList.remove('active');
        document.getElementById('register-form').classList.add('active');
    }

    showAdminFeatures() {
        document.getElementById('admin-panel-btn').style.display = 'block';
        document.getElementById('admin-nav-btn').style.display = 'flex';
    }

    showSection(sectionId) {
        // Hide all sections
        document.querySelectorAll('.section').forEach(section => {
            section.classList.remove('active');
        });

        // Show selected section
        document.getElementById(sectionId).classList.add('active');

        // Update navigation
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-section="${sectionId}"]`).classList.add('active');

        // Load section-specific data
        if (sectionId === 'admin-section' && this.user.role === 'admin') {
            this.loadAdminTodos();
        }
    }

    openModal(modalId) {
        document.getElementById(modalId).classList.add('active');
    }

    closeModal(modalId) {
        document.getElementById(modalId).classList.remove('active');
        // Clear forms
        document.querySelectorAll(`#${modalId} form`).forEach(form => form.reset());
        this.currentTodoId = null;
    }

    openAddTodo() {
        this.currentTodoId = null;
        document.getElementById('todo-modal-title').textContent = 'Add New Task';
        document.getElementById('todo-form').reset();
        this.openModal('todo-modal');
    }

    openEditTodo(todoId) {
        const todo = this.todos.find(t => t.id === todoId);
        if (!todo) return;

        this.currentTodoId = todoId;
        document.getElementById('todo-modal-title').textContent = 'Edit Task';
        document.getElementById('todoTitle').value = todo.title;
        document.getElementById('todoDescription').value = todo.description;
        document.getElementById('todoPriority').value = todo.priority;
        this.openModal('todo-modal');
    }

    showNotification(message, type = 'info') {
        const container = document.getElementById('notification-container');
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <p>${this.escapeHtml(message)}</p>
        `;

        container.appendChild(notification);

        // Show notification
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);

        // Hide and remove notification
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                container.removeChild(notification);
            }, 300);
        }, 5000);
    }

    // Event Listeners Setup
    setupEventListeners() {
        // Auth form switching
        document.getElementById('showRegister').addEventListener('click', (e) => {
            e.preventDefault();
            this.showRegisterForm();
        });

        document.getElementById('showLogin').addEventListener('click', (e) => {
            e.preventDefault();
            this.showLoginForm();
        });

        // Login form
        document.getElementById('loginForm').addEventListener('submit', (e) => {
            e.preventDefault();
            const username = document.getElementById('loginUsername').value;
            const password = document.getElementById('loginPassword').value;
            this.login(username, password);
        });

        // Register form
        document.getElementById('registerForm').addEventListener('submit', (e) => {
            e.preventDefault();
            const userData = {
                username: document.getElementById('regUsername').value,
                email: document.getElementById('regEmail').value,
                first_name: document.getElementById('regFirstName').value,
                last_name: document.getElementById('regLastName').value,
                phone_number: document.getElementById('regPhone').value,
                password: document.getElementById('regPassword').value,
                role: 'user'
            };
            this.register(userData);
        });

        // Logout
        document.getElementById('logout-btn').addEventListener('click', (e) => {
            e.preventDefault();
            this.logout();
        });

        // Navigation
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const sectionId = btn.dataset.section;
                this.showSection(sectionId);
            });
        });

        // Profile navigation
        document.getElementById('profile-btn').addEventListener('click', (e) => {
            e.preventDefault();
            this.showSection('profile-section');
        });

        document.getElementById('admin-panel-btn').addEventListener('click', (e) => {
            e.preventDefault();
            this.showSection('admin-section');
        });

        // Todo actions
        document.getElementById('add-todo-btn').addEventListener('click', () => {
            this.openAddTodo();
        });

        // Todo form
        document.getElementById('todo-form').addEventListener('submit', (e) => {
            e.preventDefault();
            const todoData = {
                title: document.getElementById('todoTitle').value,
                description: document.getElementById('todoDescription').value,
                priority: parseInt(document.getElementById('todoPriority').value)
            };

            if (this.currentTodoId) {
                // For updates, we need to include the complete status
                const currentTodo = this.todos.find(t => t.id === this.currentTodoId);
                todoData.complete = currentTodo ? currentTodo.complete : false;
                this.updateTodo(this.currentTodoId, todoData);
            } else {
                // For creation, don't send complete field - let database default handle it
                this.createTodo(todoData);
            }
        });

        // Todo filters
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                this.currentFilter = btn.dataset.filter;
                this.renderTodos();
            });
        });

        // Profile actions
        document.getElementById('change-password-btn').addEventListener('click', () => {
            this.openModal('password-modal');
        });

        document.getElementById('change-phone-btn').addEventListener('click', () => {
            this.openModal('phone-modal');
        });

        // Password form
        document.getElementById('password-form').addEventListener('submit', (e) => {
            e.preventDefault();
            const oldPassword = document.getElementById('oldPassword').value;
            const newPassword = document.getElementById('newPassword').value;
            this.changePassword(oldPassword, newPassword);
        });

        // Phone form
        document.getElementById('phone-form').addEventListener('submit', (e) => {
            e.preventDefault();
            const newPhone = document.getElementById('newPhone').value;
            this.changePhoneNumber(newPhone);
        });

        // Modal close buttons
        document.querySelectorAll('.modal-close').forEach(btn => {
            btn.addEventListener('click', () => {
                const modal = btn.closest('.modal');
                this.closeModal(modal.id);
            });
        });

        // Cancel buttons
        document.getElementById('cancel-todo').addEventListener('click', () => {
            this.closeModal('todo-modal');
        });

        document.getElementById('cancel-password').addEventListener('click', () => {
            this.closeModal('password-modal');
        });

        document.getElementById('cancel-phone').addEventListener('click', () => {
            this.closeModal('phone-modal');
        });

        // Modal background click
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.closeModal(modal.id);
                }
            });
        });
    }

    // Utility Methods
    getPriorityText(priority) {
        const priorities = {
            1: 'Low Priority',
            2: 'Medium Priority',
            3: 'High Priority',
            4: 'Urgent',
            5: 'Critical'
        };
        return priorities[priority] || 'Unknown';
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new TodoApp();
});
