// PocketSmart AI - Main App Coordinator & Navigation

const App = {
  currentTab: 'dashboard',
  loadingTimer: null,

  async init() {
    this.setupNavigation();
    this.setupApiKeyModal();
    this.checkSystemStatus();

    // Initialize submodules
    Planners.init();
    Dashboard.init();
  },

  setupNavigation() {
    const tabs = document.querySelectorAll('.nav-tab');
    tabs.forEach(tab => {
      tab.addEventListener('click', (e) => {
        const target = tab.dataset.tab;
        this.switchTab(target);
      });
    });
  },

  switchTab(tabId) {
    this.currentTab = tabId;

    // Update nav button classes
    document.querySelectorAll('.nav-tab').forEach(t => {
      if (t.dataset.tab === tabId) {
        t.classList.add('active');
      } else {
        t.classList.remove('active');
      }
    });

    // Update view panels
    const views = ['dashboard', 'home', 'party', 'jewelry'];
    views.forEach(v => {
      const el = document.getElementById(`view-${v}`);
      if (el) {
        if (v === tabId) {
          el.classList.remove('hidden');
        } else {
          el.classList.add('hidden');
        }
      }
    });

    // If switching to dashboard, refresh stats
    if (tabId === 'dashboard') {
      Dashboard.loadStats();
      Dashboard.loadPlans();
    }

    // Scroll to planner view
    window.scrollTo({ top: 0, behavior: 'smooth' });
  },

  async checkSystemStatus() {
    try {
      const status = await API.getSystemStatus();
      const badge = document.getElementById('engine-status-badge');
      const text = document.getElementById('engine-status-text');
      
      if (badge && text) {
        if (status.has_gemini_key) {
          badge.className = 'w-2 h-2 rounded-full bg-emerald-400 animate-ping';
          text.textContent = 'Gemini Live AI';
          text.className = 'text-xs font-semibold text-emerald-400';
        } else {
          badge.className = 'w-2 h-2 rounded-full bg-indigo-400';
          text.textContent = 'Demo Engine';
          text.className = 'text-xs font-semibold text-indigo-300';
        }
      }
    } catch (err) {
      console.warn('Could not reach health check endpoint:', err);
    }
  },

  setupApiKeyModal() {
    const trigger = document.getElementById('api-key-modal-trigger');
    const modal = document.getElementById('api-key-modal');
    const closeBtn = document.getElementById('close-key-modal-btn');
    const saveBtn = document.getElementById('save-api-key-btn');
    const input = document.getElementById('gemini-api-key-input');

    if (trigger && modal) {
      trigger.addEventListener('click', () => modal.classList.remove('hidden'));
    }
    if (closeBtn && modal) {
      closeBtn.addEventListener('click', () => modal.classList.add('hidden'));
    }
    if (saveBtn && input) {
      saveBtn.addEventListener('click', async () => {
        const val = input.value.trim();
        if (!val) {
          showToast('Please enter an API key', 'warning');
          return;
        }
        try {
          const res = await API.updateApiKey(val);
          showToast('Gemini API key updated!');
          modal.classList.add('hidden');
          this.checkSystemStatus();
        } catch (err) {
          showToast('Failed to update API key', 'error');
        }
      });
    }
  },

  showLoading(title = "AI Generating Plan...", steps = []) {
    const overlay = document.getElementById('loading-overlay');
    const titleEl = document.getElementById('loading-title');
    const stepEl = document.getElementById('loading-step-text');
    
    if (!overlay) return;

    if (titleEl) titleEl.textContent = title;
    overlay.classList.remove('hidden');

    if (steps.length > 0 && stepEl) {
      let stepIdx = 0;
      stepEl.textContent = steps[0];
      if (this.loadingTimer) clearInterval(this.loadingTimer);
      
      this.loadingTimer = setInterval(() => {
        stepIdx = (stepIdx + 1) % steps.length;
        stepEl.textContent = steps[stepIdx];
      }, 1200);
    }
  },

  hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) overlay.classList.add('hidden');
    if (this.loadingTimer) {
      clearInterval(this.loadingTimer);
      this.loadingTimer = null;
    }
  }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  App.init();
});
