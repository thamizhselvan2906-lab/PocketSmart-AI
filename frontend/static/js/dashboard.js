// PocketSmart AI - Dashboard Analytics & Saved Plans

const Dashboard = {
  currentModalPlan: null,

  async init() {
    await this.loadStats();
    await this.loadPlans();
  },

  async loadStats() {
    try {
      const stats = await API.getDashboardStats();
      
      const totalBudgetEl = document.getElementById('dash-total-budget');
      const totalSpendingEl = document.getElementById('dash-total-spending');
      const totalRemainingEl = document.getElementById('dash-total-remaining');
      const totalPlansEl = document.getElementById('dash-total-plans');
      const totalRecsEl = document.getElementById('dash-total-recs');

      if (totalBudgetEl) totalBudgetEl.textContent = `$${stats.total_budget.toLocaleString()}`;
      if (totalSpendingEl) totalSpendingEl.textContent = `$${stats.total_spending.toLocaleString()}`;
      if (totalRemainingEl) totalRemainingEl.textContent = `$${stats.total_remaining.toLocaleString()}`;
      if (totalPlansEl) totalPlansEl.textContent = stats.total_plans;
      if (totalRecsEl) totalRecsEl.textContent = stats.total_recommendations;

      // Type counts
      const homeCount = document.getElementById('count-home');
      const partyCount = document.getElementById('count-party');
      const jewelryCount = document.getElementById('count-jewelry');

      if (homeCount) homeCount.textContent = stats.type_counts?.home || 0;
      if (partyCount) partyCount.textContent = stats.type_counts?.party || 0;
      if (jewelryCount) jewelryCount.textContent = stats.type_counts?.jewelry || 0;

      // Budget Utilization Bar
      const total = stats.total_budget || 1;
      const spent = stats.total_spending || 0;
      const pct = Math.min(100, Math.round((spent / total) * 100));

      const bar = document.getElementById('dash-budget-bar');
      const pctText = document.getElementById('dash-budget-pct');

      if (bar) {
        bar.style.width = `${pct}%`;
        bar.className = `budget-progress-bar h-full rounded-full ${pct > 95 ? 'bg-rose-500' : pct > 80 ? 'bg-amber-400' : 'bg-emerald-400'}`;
      }
      if (pctText) pctText.textContent = `${pct}% utilized`;

    } catch (err) {
      console.error('Failed to load dashboard stats:', err);
    }
  },

  async loadPlans() {
    const container = document.getElementById('saved-plans-container');
    if (!container) return;

    try {
      const plans = await API.getPlans();
      if (!plans || plans.length === 0) {
        container.innerHTML = `
          <div class="col-span-full text-center py-12 p-6 glass-panel border-dashed border-gray-700">
            <span class="text-4xl block mb-2">📋</span>
            <h3 class="text-lg font-semibold text-white mb-1">No plans generated yet</h3>
            <p class="text-sm text-gray-400 mb-4">Choose a planner above to create your first AI-guided budget plan.</p>
            <div class="flex items-center justify-center gap-3">
              <button onclick="App.switchTab('home')" class="px-4 py-2 rounded-xl bg-indigo-600/30 hover:bg-indigo-600 text-indigo-200 hover:text-white border border-indigo-500/40 text-xs font-semibold transition">
                🛋️ Home Interior
              </button>
              <button onclick="App.switchTab('party')" class="px-4 py-2 rounded-xl bg-indigo-600/30 hover:bg-indigo-600 text-indigo-200 hover:text-white border border-indigo-500/40 text-xs font-semibold transition">
                🎉 Party Planner
              </button>
              <button onclick="App.switchTab('jewelry')" class="px-4 py-2 rounded-xl bg-indigo-600/30 hover:bg-indigo-600 text-indigo-200 hover:text-white border border-indigo-500/40 text-xs font-semibold transition">
                💎 Jewelry Planner
              </button>
            </div>
          </div>
        `;
        return;
      }

      container.innerHTML = plans.map(p => {
        const typeEmoji = p.planner_type === 'home' ? '🛋️' : p.planner_type === 'party' ? '🎉' : '💎';
        const typeName = p.planner_type === 'home' ? 'Home Interior' : p.planner_type === 'party' ? 'Party Planner' : 'Jewelry';
        const pct = p.total_budget > 0 ? ((p.estimated_spending / p.total_budget) * 100).toFixed(0) : 0;

        return `
          <div class="glass-panel-interactive p-5 flex flex-col justify-between">
            <div>
              <div class="flex items-start justify-between gap-2 mb-2">
                <span class="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                  ${typeEmoji} ${typeName}
                </span>
                <span class="text-xs text-gray-400">${p.created_at ? p.created_at.split(' ')[0] : 'Recent'}</span>
              </div>

              <h4 class="text-base font-bold text-white mb-2 line-clamp-1">${p.title}</h4>

              <div class="grid grid-cols-2 gap-2 p-2.5 rounded-lg bg-gray-900/60 border border-gray-800 text-xs mb-3">
                <div>
                  <span class="text-gray-400 block">Budget:</span>
                  <span class="font-bold text-white">${p.currency}${p.total_budget.toLocaleString()}</span>
                </div>
                <div>
                  <span class="text-gray-400 block">Est. Cost:</span>
                  <span class="font-bold text-indigo-300">${p.currency}${p.estimated_spending.toLocaleString()}</span>
                </div>
              </div>

              <div class="w-full bg-gray-800 rounded-full h-1.5 overflow-hidden mb-1">
                <div class="bg-indigo-500 h-full rounded-full" style="width: ${Math.min(100, pct)}%"></div>
              </div>
              <div class="flex justify-between items-center text-[10px] text-gray-400 mb-4">
                <span>Utilization</span>
                <span>${pct}% (${p.currency}${p.remaining_budget.toLocaleString()} saved)</span>
              </div>
            </div>

            <div class="pt-3 border-t border-gray-800 flex items-center justify-between gap-2">
              <button onclick="Dashboard.viewPlanDetails(${p.id})" class="px-3 py-1.5 rounded-lg bg-indigo-600/30 hover:bg-indigo-600 text-indigo-200 hover:text-white border border-indigo-500/40 text-xs font-medium transition flex items-center gap-1">
                <span>View Details</span>
                <span>→</span>
              </button>
              
              <button onclick="Dashboard.deletePlan(${p.id})" class="p-1.5 rounded-lg hover:bg-rose-500/20 text-gray-400 hover:text-rose-400 transition" title="Delete Plan">
                🗑️
              </button>
            </div>
          </div>
        `;
      }).join('');

    } catch (err) {
      console.error('Failed to load plans:', err);
    }
  },

  async viewPlanDetails(planId) {
    try {
      const plan = await API.getPlanById(planId);
      this.currentModalPlan = plan;
      
      const modal = document.getElementById('plan-detail-modal');
      const content = document.getElementById('modal-plan-content');
      if (!modal || !content) return;

      const currency = plan.currency || '$';
      const pct = plan.total_budget > 0 ? (plan.estimated_spending / plan.total_budget) * 100 : 0;

      content.innerHTML = `
        <div class="mb-4">
          <div class="flex items-center gap-2 mb-1">
            <span class="text-xs font-bold text-indigo-400 uppercase tracking-wider">${plan.planner_type} Planner</span>
            <span class="text-gray-500">•</span>
            <span class="text-xs text-gray-400">${plan.created_at || ''}</span>
          </div>
          <h2 class="text-2xl font-bold text-white">${plan.title}</h2>
        </div>

        <div class="grid grid-cols-3 gap-3 p-3.5 rounded-xl bg-gray-900/70 border border-gray-800 mb-4">
          <div>
            <span class="text-xs text-gray-400 block">Total Budget</span>
            <span class="text-lg font-bold text-white">${currency}${plan.total_budget.toLocaleString()}</span>
          </div>
          <div>
            <span class="text-xs text-gray-400 block">Estimated Cost</span>
            <span class="text-lg font-bold text-indigo-400" id="modal-spent">${currency}${plan.estimated_spending.toLocaleString()}</span>
          </div>
          <div>
            <span class="text-xs text-gray-400 block">Remaining</span>
            <span class="text-lg font-bold text-emerald-400" id="modal-remaining">${currency}${plan.remaining_budget.toLocaleString()}</span>
          </div>
        </div>

        <div class="p-3.5 rounded-xl bg-indigo-950/20 border border-indigo-800/30 text-xs text-gray-300 leading-relaxed mb-4">
          <strong class="text-indigo-300 block mb-1">AI Recommendation Rationale:</strong>
          ${plan.ai_summary}
        </div>

        <h4 class="text-sm font-bold text-white mb-2">Recommended Items (${plan.recommendations.length})</h4>
        <div class="space-y-3 max-h-96 overflow-y-auto pr-1">
          ${plan.recommendations.map(r => `
            <div class="p-3 rounded-xl bg-gray-900/60 border border-gray-800 flex items-center justify-between gap-3 ${r.is_selected === false ? 'opacity-50' : ''}" id="modal-item-${r.id}">
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2 mb-0.5">
                  <span class="text-xs font-semibold text-gray-300 truncate">${r.name}</span>
                  <span class="px-2 py-0.2 rounded text-[10px] bg-gray-800 text-gray-400 border border-gray-700">${r.platform_name}</span>
                </div>
                <p class="text-[11px] text-gray-400 line-clamp-1">${r.why_recommended}</p>
              </div>

              <div class="text-right flex items-center gap-3">
                <span class="text-sm font-bold text-indigo-300">${currency}${r.estimated_price}</span>
                <label class="cursor-pointer" title="Toggle item in budget">
                  <input type="checkbox" class="w-4 h-4 rounded text-indigo-600 bg-gray-900 border-gray-700" 
                         ${r.is_selected !== false ? 'checked' : ''} 
                         onchange="Dashboard.toggleModalItem(${plan.id}, ${r.id}, this.checked)">
                </label>
                <a href="${r.shopping_link}" target="_blank" rel="noopener noreferrer" class="px-2.5 py-1 rounded bg-indigo-600/30 hover:bg-indigo-600 text-indigo-200 text-xs border border-indigo-500/40 transition">
                  Shop ↗
                </a>
              </div>
            </div>
          `).join('')}
        </div>
      `;

      modal.classList.remove('hidden');
    } catch (err) {
      showToast('Failed to load plan details', 'error');
    }
  },

  async toggleModalItem(planId, itemId, isChecked) {
    try {
      const res = await API.togglePlanItem(planId, itemId, isChecked);
      const currency = this.currentModalPlan?.currency || '$';
      
      const spentEl = document.getElementById('modal-spent');
      const remainingEl = document.getElementById('modal-remaining');
      const itemEl = document.getElementById(`modal-item-${itemId}`);

      if (spentEl) spentEl.textContent = `${currency}${res.estimated_spending.toLocaleString()}`;
      if (remainingEl) remainingEl.textContent = `${currency}${res.remaining_budget.toLocaleString()}`;
      if (itemEl) {
        if (isChecked) itemEl.classList.remove('opacity-50');
        else itemEl.classList.add('opacity-50');
      }

      showToast(isChecked ? 'Item included in plan' : 'Item excluded from plan', 'info');
      // Refresh dashboard list behind modal
      this.loadPlans();
      this.loadStats();
    } catch (err) {
      showToast('Failed to update item status', 'error');
    }
  },

  closeModal() {
    const modal = document.getElementById('plan-detail-modal');
    if (modal) modal.classList.add('hidden');
  },

  async deletePlan(planId) {
    if (!confirm('Are you sure you want to delete this plan?')) return;

    try {
      await API.deletePlan(planId);
      showToast('Plan deleted successfully');
      await this.loadStats();
      await this.loadPlans();
    } catch (err) {
      showToast('Failed to delete plan', 'error');
    }
  }
};
