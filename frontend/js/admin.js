/**
 * Admin Panel Module
 * ===================
 * Fetches and displays admin data: users, prediction logs, and stats.
 */

async function loadAdminData() {
    if (!requireAuth()) return;

    await Promise.all([
        loadStats(),
        loadUsers(),
        loadLogs()
    ]);
}

// ──── Load System Statistics ────
async function loadStats() {
    try {
        const data = await apiRequest('/api/admin/stats');
        const stats = data.stats;

        const totalUsers = document.getElementById('totalUsers');
        const totalPredictions = document.getElementById('totalPredictions');

        if (totalUsers) totalUsers.textContent = stats.total_users;
        if (totalPredictions) totalPredictions.textContent = stats.total_predictions;

        // Disease distribution
        const distContainer = document.getElementById('diseaseDistribution');
        if (distContainer && stats.disease_distribution) {
            const entries = Object.entries(stats.disease_distribution);
            const total = entries.reduce((sum, [, count]) => sum + count, 0);

            distContainer.innerHTML = entries.map(([name, count]) => {
                const pct = total > 0 ? ((count / total) * 100).toFixed(1) : 0;
                return `
                    <div class="prediction-bar-item">
                        <span class="prediction-bar-label">${name}</span>
                        <div class="prediction-bar-track">
                            <div class="prediction-bar-fill top" style="width: ${pct}%"></div>
                        </div>
                        <span class="prediction-bar-value">${count}</span>
                    </div>
                `;
            }).join('');
        }

    } catch (error) {
        console.error('Stats error:', error);
    }
}

// ──── Load Users ────
async function loadUsers() {
    try {
        const data = await apiRequest('/api/admin/users');
        const tbody = document.getElementById('usersTableBody');
        const countEl = document.getElementById('usersCount');

        if (countEl) countEl.textContent = data.count;

        if (tbody) {
            tbody.innerHTML = data.users.map((user, idx) => `
                <tr class="animate-in animate-delay-${Math.min(idx + 1, 4)}">
                    <td><strong>${user.name}</strong></td>
                    <td>${user.email}</td>
                    <td>
                        <span class="result-badge ${user.role === 'admin' ? 'severity-high' : 'severity-low'}">
                            ${user.role || 'user'}
                        </span>
                    </td>
                    <td>${user.predictions_count || 0}</td>
                    <td>${formatDate(user.created_at)}</td>
                </tr>
            `).join('');
        }

    } catch (error) {
        console.error('Users error:', error);
    }
}

// ──── Load Prediction Logs ────
async function loadLogs() {
    try {
        const data = await apiRequest('/api/admin/logs');
        const tbody = document.getElementById('logsTableBody');
        const countEl = document.getElementById('logsCount');

        if (countEl) countEl.textContent = data.count;

        if (tbody) {
            tbody.innerHTML = data.logs.map((log, idx) => `
                <tr class="animate-in animate-delay-${Math.min(idx + 1, 4)}">
                    <td>${log.user_name || log.user_email}</td>
                    <td><strong>${log.predicted_class}</strong></td>
                    <td class="font-mono">${log.confidence.toFixed(1)}%</td>
                    <td>${log.original_filename || 'N/A'}</td>
                    <td>${formatDate(log.created_at)}</td>
                </tr>
            `).join('');
        }

    } catch (error) {
        console.error('Logs error:', error);
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', loadAdminData);
