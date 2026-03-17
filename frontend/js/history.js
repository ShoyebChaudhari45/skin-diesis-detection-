/**
 * History Module
 * ===============
 * Fetches and displays user's prediction history.
 */

async function loadHistory() {
    if (!requireAuth()) return;

    const tbody = document.getElementById('historyTableBody');
    const emptyState = document.getElementById('emptyState');
    const countEl = document.getElementById('historyCount');

    if (!tbody) return;

    try {
        const data = await apiRequest('/api/history');

        if (countEl) countEl.textContent = data.count;

        if (data.predictions.length === 0) {
            if (emptyState) emptyState.style.display = 'block';
            return;
        }

        if (emptyState) emptyState.style.display = 'none';

        tbody.innerHTML = data.predictions.map((pred, idx) => {
            const severityClass = getSeverityClass(pred.disease_info?.severity || 'Low');
            return `
                <tr class="animate-in animate-delay-${Math.min(idx + 1, 4)}">
                    <td>
                        <img src="/uploads/${pred.image_filename}" 
                             alt="Skin Image" class="table-image"
                             onerror="this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 width=%2248%22 height=%2248%22><rect width=%2248%22 height=%2248%22 fill=%22%23334155%22/><text x=%2224%22 y=%2228%22 text-anchor=%22middle%22 fill=%22%2394a3b8%22 font-size=%2212%22>IMG</text></svg>'">
                    </td>
                    <td><strong>${pred.predicted_class}</strong></td>
                    <td>
                        <span class="font-mono">${pred.confidence.toFixed(1)}%</span>
                    </td>
                    <td>
                        <span class="result-badge ${severityClass}">
                            ${pred.disease_info?.severity || 'N/A'}
                        </span>
                    </td>
                    <td>${formatDate(pred.created_at)}</td>
                </tr>
            `;
        }).join('');

    } catch (error) {
        showAlert('historyAlert', error.message || 'Failed to load history', 'error');
    }
}

function getSeverityClass(severity) {
    const s = severity.toLowerCase();
    if (s.includes('critical')) return 'severity-critical';
    if (s.includes('high')) return 'severity-high';
    if (s.includes('moderate')) return 'severity-moderate';
    return 'severity-low';
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', loadHistory);
