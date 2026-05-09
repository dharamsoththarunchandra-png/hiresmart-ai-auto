document.addEventListener('DOMContentLoaded', () => {
    // Mobile Menu Toggle
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const navList = document.querySelector('.nav-list');
    const headerActions = document.querySelector('.header-actions');

    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', () => {
            navList.classList.toggle('active');
            if (headerActions) headerActions.classList.toggle('active');

            const icon = mobileMenuBtn.querySelector('i');
            if (navList.classList.contains('active')) {
                icon.classList.remove('fa-bars');
                icon.classList.add('fa-times');
            } else {
                icon.classList.remove('fa-times');
                icon.classList.add('fa-bars');
            }
        });
    }

    // Smooth Scroll for Anchor Links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
                if (navList) navList.classList.remove('active');
                if (headerActions) headerActions.classList.remove('active');
                const icon = mobileMenuBtn ? mobileMenuBtn.querySelector('i') : null;
                if (icon) {
                    icon.classList.remove('fa-times');
                    icon.classList.add('fa-bars');
                }
            }
        });
    });

    // Dashboard Upload Logic
    if (window.location.pathname.includes('dashboard.html')) {
        const resumeInput = document.getElementById('resume-input');
        const batchInput = document.getElementById('batch-input');

        const handleFiles = async (files, type) => {
            if (!files.length) return;
            console.log(`Handling ${files.length} ${type} files:`, files);

            const file = files[0];
            const formData = new FormData();
            formData.append('file', file);

            const endpoint = type === 'resume' ? '/upload/resume' : '/upload/batch';

            try {
                alert(`Uploading ${type} file... Please wait.`); // Simple loading indicator
                
                const response = await fetch(endpoint, {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    console.log('Upload Result:', result);
                    alert(`Success: ${result.message}\n` + JSON.stringify(result.data || result, null, 2));
                } else {
                    console.error('Upload Error:', result);
                    alert(`Error: ${result.message || 'Upload failed'}`);
                }
            } catch (error) {
                console.error('Network Error:', error);
                alert('Network error while uploading file. Ensure backend is running on port 5000.');
            }
        };

        if (resumeInput) {
            resumeInput.addEventListener('change', (e) => handleFiles(e.target.files, 'resume'));
        }

        if (batchInput) {
            batchInput.addEventListener('change', (e) => handleFiles(e.target.files, 'batch'));
        }

        // Drag and Drop
        const uploadCards = document.querySelectorAll('.upload-card');
        uploadCards.forEach(card => {
            card.addEventListener('dragover', (e) => {
                e.preventDefault();
                card.style.borderColor = 'var(--primary)';
            });

            card.addEventListener('dragleave', () => {
                card.style.borderColor = 'rgba(79, 70, 229, 0.1)';
            });

            card.addEventListener('drop', (e) => {
                e.preventDefault();
                card.style.borderColor = 'rgba(79, 70, 229, 0.1)';
                const files = e.dataTransfer.files;
                const type = card.id === 'resume-upload' ? 'resume' : 'batch';
                handleFiles(files, type);
            });
        });
    }

    // Intersection Observer for Reveal on Scroll
    const revealElements = document.querySelectorAll('.reveal');
    const revealObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('active');
            }
        });
    }, { threshold: 0.15 });

    revealElements.forEach(el => revealObserver.observe(el));

    // Marquee duplication
    const marqueeLogos = document.querySelector('.marquee-logos');
    if (marqueeLogos) {
        marqueeLogos.innerHTML += marqueeLogos.innerHTML;
    }

    // Sidebar Toggle
    const menuToggle = document.querySelector('.menu-toggle');
    const sidebar = document.querySelector('.sidebar');

    if (menuToggle && sidebar) {
        menuToggle.addEventListener('click', () => {
            sidebar.classList.toggle('active');
            if (window.innerWidth <= 992) {
                sidebar.style.transform = sidebar.classList.contains('active') ? 'translateX(0)' : 'translateX(-100%)';
            }
        });
    }

    // Login Form Handling
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        // Real-time validation
        const emailInput = document.getElementById('email');
        const passwordInput = document.getElementById('password');
        
        const validateEmail = (email) => {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            return emailRegex.test(email);
        };
        
        const showError = (input, message) => {
            const formGroup = input.closest('.form-group');
            formGroup.classList.add('error');
            const errorMsg = formGroup.querySelector('.error-message') || document.createElement('div');
            errorMsg.className = 'error-message';
            errorMsg.textContent = message;
            if (!formGroup.querySelector('.error-message')) {
                formGroup.appendChild(errorMsg);
            }
        };
        
        const clearError = (input) => {
            const formGroup = input.closest('.form-group');
            formGroup.classList.remove('error');
            const errorMsg = formGroup.querySelector('.error-message');
            if (errorMsg) {
                errorMsg.remove();
            }
        };
        
        emailInput.addEventListener('blur', () => {
            if (emailInput.value && !validateEmail(emailInput.value)) {
                showError(emailInput, 'Please enter a valid email address');
            } else {
                clearError(emailInput);
            }
        });
        
        passwordInput.addEventListener('blur', () => {
            if (passwordInput.value && passwordInput.value.length < 6) {
                showError(passwordInput, 'Password must be at least 6 characters');
            } else {
                clearError(passwordInput);
            }
        });
        
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const email = emailInput.value.trim();
            const password = passwordInput.value;
            const userType = document.querySelector('input[name="userType"]:checked').value;
            
            // Clear previous errors
            clearError(emailInput);
            clearError(passwordInput);
            
            // Validation
            let hasErrors = false;
            
            if (!email) {
                showError(emailInput, 'Email is required');
                hasErrors = true;
            } else if (!validateEmail(email)) {
                showError(emailInput, 'Please enter a valid email address');
                hasErrors = true;
            }
            
            if (!password) {
                showError(passwordInput, 'Password is required');
                hasErrors = true;
            } else if (password.length < 6) {
                showError(passwordInput, 'Password must be at least 6 characters');
                hasErrors = true;
            }
            
            if (hasErrors) return;
            
            // Show loading state
            const submitBtn = loginForm.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            submitBtn.textContent = 'Signing in...';
            submitBtn.disabled = true;
            
            try {
                // For now, simulate login - replace with actual API call
                const response = await fetch('/auth/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        email,
                        password,
                        userType
                    })
                });
                
                if (response.ok) {
                    const data = await response.json();
                    // Store user info in localStorage
                    localStorage.setItem('user', JSON.stringify({
                        email: data.email,
                        userType: data.userType,
                        name: data.name
                    }));
                    
                    // Redirect based on user type
                    if (userType === 'recruiter') {
                        window.location.href = 'dashboard.html';
                    } else {
                        window.location.href = 'dashboard.html'; // or user-specific dashboard
                    }
                } else {
                    const error = await response.json();
                    alert(error.message || 'Login failed');
                }
            } catch (error) {
                console.error('Login error:', error);
                alert('Network error. Please try again.');
            } finally {
                // Reset button state
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
            }
        });
    }
});
