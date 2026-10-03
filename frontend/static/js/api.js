// PocketSmart AI - API Service Layer

const API = {
  baseUrl: '',

  // System & Health
  async getSystemStatus() {
    const res = await fetch(`${this.baseUrl}/api/system/status`);
    return await res.json();
  },

  async updateApiKey(apiKey) {
    const res = await fetch(`${this.baseUrl}/api/system/key`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ api_key: apiKey })
    });
    return await res.json();
  },

  // Planners
  async planHomeInterior(payload) {
    const res = await fetch(`${this.baseUrl}/api/planners/home-interior`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.error || 'Failed to generate interior plan');
    }
    return await res.json();
  },

  async planParty(payload) {
    const res = await fetch(`${this.baseUrl}/api/planners/party`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.error || 'Failed to generate party plan');
    }
    return await res.json();
  },

  async planJewelry(formDataOrJson) {
    let options = {};
    if (formDataOrJson instanceof FormData) {
      options = {
        method: 'POST',
        body: formDataOrJson
      };
    } else {
      options = {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formDataOrJson)
      };
    }

    const res = await fetch(`${this.baseUrl}/api/planners/jewelry`, options);
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.error || 'Failed to generate jewelry plan');
    }
    return await res.json();
  },

  // Plans Management
  async getPlans(type = null) {
    const url = type ? `${this.baseUrl}/api/plans?type=${type}` : `${this.baseUrl}/api/plans`;
    const res = await fetch(url);
    return await res.json();
  },

  async getPlanById(planId) {
    const res = await fetch(`${this.baseUrl}/api/plans/${planId}`);
    if (!res.ok) throw new Error('Plan not found');
    return await res.json();
  },

  async savePlan(planData) {
    const res = await fetch(`${this.baseUrl}/api/plans/save`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(planData)
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.error || 'Failed to save plan');
    }
    return await res.json();
  },

  async deletePlan(planId) {
    const res = await fetch(`${this.baseUrl}/api/plans/${planId}`, {
      method: 'DELETE'
    });
    return await res.json();
  },

  async togglePlanItem(planId, itemId, isSelected, quantity = 1) {
    const res = await fetch(`${this.baseUrl}/api/plans/${planId}/items/${itemId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ is_selected: isSelected, quantity: quantity })
    });
    return await res.json();
  },

  // Dashboard Stats
  async getDashboardStats() {
    const res = await fetch(`${this.baseUrl}/api/dashboard/stats`);
    return await res.json();
  }
};

// Global Toast Notification Helper
function showToast(message, type = 'success') {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  const bgClass = type === 'success' ? 'bg-emerald-500/20 border-emerald-500/40 text-emerald-300' :
                  type === 'warning' ? 'bg-amber-500/20 border-amber-500/40 text-amber-300' :
                  type === 'error' ? 'bg-rose-500/20 border-rose-500/40 text-rose-300' :
                  'bg-indigo-500/20 border-indigo-500/40 text-indigo-300';
  
  const icon = type === 'success' ? '✓' : type === 'error' ? '✕' : type === 'warning' ? '⚠' : 'ℹ';

  toast.className = `flex items-center gap-3 px-4 py-3 rounded-xl border backdrop-blur-md shadow-2xl transition-all duration-300 transform translate-y-2 opacity-0 text-sm font-medium ${bgClass}`;
  toast.innerHTML = `<span class="text-base font-bold">${icon}</span> <span>${message}</span>`;

  container.appendChild(toast);

  // Trigger animation
  requestAnimationFrame(() => {
    toast.classList.remove('translate-y-2', 'opacity-0');
  });

  setTimeout(() => {
    toast.classList.add('translate-y-2', 'opacity-0');
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}
