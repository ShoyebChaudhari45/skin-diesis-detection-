/**
 * Authentication Module
 * ======================
 * Handles login and signup form submissions.
 */

// ──── Login Handler ────
async function handleLogin(event) {
    event.preventDefault();
    hideAlert('authAlert');

    const email = document.getElementById('loginEmail').value.trim();
    const password = document.getElementById('loginPassword').value;

    if (!email || !password) {
        showAlert('authAlert', 'Please fill in all fields', 'error');
        return;
    }

    const btn = event.target.querySelector('button[type="submit"]');
    const originalText = btn.textContent;
    btn.textContent = 'Logging in...';
    btn.disabled = true;

    try {
        const data = await apiRequest('/api/login', {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });

        // Store token and user data
        setToken(data.token);
        setUser(data.user);

        showAlert('authAlert', 'Login successful! Redirecting...', 'success');

        // Redirect to dashboard
        setTimeout(() => {
            window.location.href = '/dashboard';
        }, 500);

    } catch (error) {
        showAlert('authAlert', error.message || 'Login failed', 'error');
        btn.textContent = originalText;
        btn.disabled = false;
    }
}

// ──── Signup Handler ────
async function handleSignup(event) {
    event.preventDefault();
    hideAlert('authAlert');

    const name = document.getElementById('signupName').value.trim();
    const email = document.getElementById('signupEmail').value.trim();
    const password = document.getElementById('signupPassword').value;
    const confirmPassword = document.getElementById('signupConfirmPassword').value;

    // Validation
    if (!name || !email || !password || !confirmPassword) {
        showAlert('authAlert', 'Please fill in all fields', 'error');
        return;
    }

    if (password.length < 6) {
        showAlert('authAlert', 'Password must be at least 6 characters', 'error');
        return;
    }

    if (password !== confirmPassword) {
        showAlert('authAlert', 'Passwords do not match', 'error');
        return;
    }

    const btn = event.target.querySelector('button[type="submit"]');
    const originalText = btn.textContent;
    btn.textContent = 'Creating account...';
    btn.disabled = true;

    try {
        const data = await apiRequest('/api/signup', {
            method: 'POST',
            body: JSON.stringify({ name, email, password })
        });

        // Store token and user data
        setToken(data.token);
        setUser(data.user);

        showAlert('authAlert', 'Account created! Redirecting...', 'success');

        // Redirect to dashboard
        setTimeout(() => {
            window.location.href = '/dashboard';
        }, 500);

    } catch (error) {
        showAlert('authAlert', error.message || 'Signup failed', 'error');
        btn.textContent = originalText;
        btn.disabled = false;
    }
}
