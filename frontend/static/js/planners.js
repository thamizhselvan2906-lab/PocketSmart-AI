// PocketSmart AI - Planners & Recommendation Logic

const Planners = {
  currentPlanData: null,
  uploadedOutfitFile: null,

  roomDefaultItems: {
    "Living Room": [
      { name: "3-Seater Sofa / Couch", qty: 1, checked: true },
      { name: "Coffee Table", qty: 1, checked: true },
      { name: "Area Rug", qty: 1, checked: true },
      { name: "Floor Arc Lamp", qty: 1, checked: true },
      { name: "TV Media Console", qty: 1, checked: false },
      { name: "Accent Armchair", qty: 1, checked: false },
      { name: "Blackout Curtains", qty: 2, checked: false },
      { name: "Wall Art / Decor Trio", qty: 1, checked: false }
    ],
    "Bedroom": [
      { name: "Queen Bed Frame", qty: 1, checked: true },
      { name: "Cooling Memory Foam Mattress", qty: 1, checked: true },
      { name: "Bedside Nightstands", qty: 2, checked: true },
      { name: "Washed Cotton Duvet Set", qty: 1, checked: true },
      { name: "Touch Bedside Lamps", qty: 2, checked: false },
      { name: "Arch Floor Mirror", qty: 1, checked: false },
      { name: "6-Drawer Dresser", qty: 1, checked: false }
    ],
    "Kitchen": [
      { name: "Extendable Dining Table", qty: 1, checked: true },
      { name: "Ergonomic Dining Chairs", qty: 4, checked: true },
      { name: "Pendant Island Lights", qty: 2, checked: true },
      { name: "Microwave Cart & Baker Rack", qty: 1, checked: false },
      { name: "Anti-Fatigue Floor Mats", qty: 2, checked: false }
    ]
  },

  init() {
    this.initHomeInterior();
    this.initPartyPlanner();
    this.initJewelryPlanner();
  },

  // -----------------------------------------------------------
  // Home Interior Planner Setup
  // -----------------------------------------------------------
  initHomeInterior() {
    const roomSelect = document.getElementById('home-room-select');
    if (roomSelect) {
      roomSelect.addEventListener('change', (e) => {
        this.renderHomeRoomItems(e.target.value);
      });
      // Initial render for default room
      this.renderHomeRoomItems(roomSelect.value);
    }

    const form = document.getElementById('home-planner-form');
    if (form) {
      form.addEventListener('submit', (e) => {
        e.preventDefault();
        this.submitHomeInterior();
      });
    }
  },

  renderHomeRoomItems(room) {
    const container = document.getElementById('home-items-container');
    if (!container) return;

    const items = this.roomDefaultItems[room] || this.roomDefaultItems["Living Room"];
    container.innerHTML = items.map((item, idx) => `
      <div class="flex items-center justify-between p-3 rounded-xl bg-gray-800/40 border border-gray-700/50 hover:border-indigo-500/30 transition-all">
        <label class="flex items-center gap-3 cursor-pointer select-none text-sm text-gray-200">
          <input type="checkbox" class="home-item-checkbox w-4 h-4 rounded text-indigo-500 focus:ring-0 bg-gray-900 border-gray-600" data-index="${idx}" ${item.checked ? 'checked' : ''}>
          <span>${item.name}</span>
        </label>
        <div class="flex items-center gap-2">
          <span class="text-xs text-gray-400">Qty:</span>
          <button type="button" class="w-6 h-6 rounded bg-gray-700 hover:bg-gray-600 flex items-center justify-center text-xs font-bold text-gray-200 transition" onclick="Planners.updateItemQty('${room}', ${idx}, -1)">-</button>
          <span class="w-6 text-center text-sm font-semibold text-indigo-300" id="home-qty-${idx}">${item.qty}</span>
          <button type="button" class="w-6 h-6 rounded bg-gray-700 hover:bg-gray-600 flex items-center justify-center text-xs font-bold text-gray-200 transition" onclick="Planners.updateItemQty('${room}', ${idx}, 1)">+</button>
        </div>
      </div>
    `).join('');
  },

  updateItemQty(room, idx, delta) {
    const items = this.roomDefaultItems[room];
    if (items && items[idx]) {
      items[idx].qty = Math.max(1, (items[idx].qty || 1) + delta);
      const span = document.getElementById(`home-qty-${idx}`);
      if (span) span.textContent = items[idx].qty;
    }
  },

  async submitHomeInterior() {
    const budget = parseFloat(document.getElementById('home-budget').value);
    const currency = document.getElementById('home-currency').value;
    const room = document.getElementById('home-room-select').value;
    const style = document.getElementById('home-style').value;
    const notes = document.getElementById('home-notes').value;

    if (!budget || budget <= 0) {
      showToast('Please enter a valid budget amount greater than 0', 'warning');
      return;
    }

    const items = [];
    const checkboxes = document.querySelectorAll('.home-item-checkbox:checked');
    const roomItems = this.roomDefaultItems[room] || [];
    checkboxes.forEach(cb => {
      const idx = parseInt(cb.dataset.index);
      if (roomItems[idx]) {
        items.push({
          name: roomItems[idx].name,
          qty: roomItems[idx].qty || 1
        });
      }
    });

    const payload = {
      budget,
      currency,
      room,
      style,
      items,
      notes
    };

    App.showLoading("Designing Your Interior...", [
      "Analyzing space and architectural dimensions...",
      `Calculating budget limits for ${room}...`,
      "Curating aesthetic furniture & decor combinations...",
      "Matching shopping links within budget..."
    ]);

    try {
      const result = await API.planHomeInterior(payload);
      result.planner_type = 'home';
      result.user_inputs = payload;
      this.currentPlanData = result;
      this.renderPlanResults(result);
      showToast('Home interior plan generated successfully!');
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      App.hideLoading();
    }
  },

  // -----------------------------------------------------------
  // Party Planner Setup
  // -----------------------------------------------------------
  initPartyPlanner() {
    const guestSlider = document.getElementById('party-guest-slider');
    const guestInput = document.getElementById('party-guest-count');
    const budgetInput = document.getElementById('party-budget');
    const perGuestDisplay = document.getElementById('party-per-guest-calc');

    const updatePerGuest = () => {
      const budget = parseFloat(budgetInput.value) || 0;
      const guests = parseInt(guestInput.value) || 1;
      const perGuest = (budget / guests).toFixed(2);
      const currency = document.getElementById('party-currency')?.value || '$';
      if (perGuestDisplay) {
        perGuestDisplay.textContent = `${currency}${perGuest} / guest`;
      }
    };

    if (guestSlider && guestInput) {
      guestSlider.addEventListener('input', (e) => {
        guestInput.value = e.target.value;
        updatePerGuest();
      });
      guestInput.addEventListener('input', (e) => {
        guestSlider.value = e.target.value;
        updatePerGuest();
      });
    }

    if (budgetInput) {
      budgetInput.addEventListener('input', updatePerGuest);
    }

    const form = document.getElementById('party-planner-form');
    if (form) {
      form.addEventListener('submit', (e) => {
        e.preventDefault();
        this.submitParty();
      });
    }
  },

  async submitParty() {
    const budget = parseFloat(document.getElementById('party-budget').value);
    const currency = document.getElementById('party-currency').value;
    const event_type = document.getElementById('party-event-type').value;
    const guest_count = parseInt(document.getElementById('party-guest-count').value);
    const notes = document.getElementById('party-notes').value;

    const requirements = [];
    document.querySelectorAll('.party-req-checkbox:checked').forEach(cb => {
      requirements.push(cb.value);
    });

    if (!budget || budget <= 0) {
      showToast('Please enter a valid event budget', 'warning');
      return;
    }

    const payload = {
      budget,
      currency,
      event_type,
      guest_count,
      requirements,
      notes
    };

    App.showLoading("Calculating Event Blueprint...", [
      `Allocating budget across venue, catering, and decor...`,
      `Balancing per-guest catering for ${guest_count} attendees...`,
      "Selecting trusted vendors and party equipment...",
      "Locking total estimates under your budget ceiling..."
    ]);

    try {
      const result = await API.planParty(payload);
      result.planner_type = 'party';
      result.user_inputs = payload;
      this.currentPlanData = result;
      this.renderPlanResults(result);
      showToast('Party plan and budget division ready!');
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      App.hideLoading();
    }
  },

  // -----------------------------------------------------------
  // Jewelry Planner Setup
  // -----------------------------------------------------------
  initJewelryPlanner() {
    const dropzone = document.getElementById('outfit-dropzone');
    const fileInput = document.getElementById('outfit-file-input');
    const previewContainer = document.getElementById('outfit-preview-container');
    const previewImg = document.getElementById('outfit-preview-img');
    const removeBtn = document.getElementById('remove-outfit-btn');

    if (dropzone && fileInput) {
      dropzone.addEventListener('click', () => fileInput.click());

      dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.classList.add('dragover');
      });

      dropzone.addEventListener('dragleave', () => {
        dropzone.classList.remove('dragover');
      });

      dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.classList.remove('dragover');
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
          this.handleOutfitFile(e.dataTransfer.files[0]);
        }
      });

      fileInput.addEventListener('change', (e) => {
        if (e.target.files && e.target.files[0]) {
          this.handleOutfitFile(e.target.files[0]);
        }
      });
    }

    if (removeBtn) {
      removeBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        this.uploadedOutfitFile = null;
        if (fileInput) fileInput.value = '';
        if (previewContainer) previewContainer.classList.add('hidden');
        if (dropzone) dropzone.classList.remove('hidden');
      });
    }

    const form = document.getElementById('jewelry-planner-form');
    if (form) {
      form.addEventListener('submit', (e) => {
        e.preventDefault();
        this.submitJewelry();
      });
    }
  },

  handleOutfitFile(file) {
    if (!file.type.startsWith('image/')) {
      showToast('Please upload an image file (JPG, PNG, WebP)', 'warning');
      return;
    }
    this.uploadedOutfitFile = file;
    const reader = new FileReader();
    reader.onload = (e) => {
      const previewImg = document.getElementById('outfit-preview-img');
      const previewContainer = document.getElementById('outfit-preview-container');
      const dropzone = document.getElementById('outfit-dropzone');

      if (previewImg) previewImg.src = e.target.result;
      if (previewContainer) previewContainer.classList.remove('hidden');
      if (dropzone) dropzone.classList.add('hidden');
      showToast('Outfit image attached for AI vision styling!');
    };
    reader.readAsDataURL(file);
  },

  async submitJewelry() {
    const budget = parseFloat(document.getElementById('jewelry-budget').value);
    const currency = document.getElementById('jewelry-currency').value;
    const occasion = document.getElementById('jewelry-occasion').value;
    const style = document.getElementById('jewelry-style').value;
    const material = document.getElementById('jewelry-material').value;
    const notes = document.getElementById('jewelry-notes').value;

    if (!budget || budget <= 0) {
      showToast('Please enter a valid jewelry budget', 'warning');
      return;
    }

    let payload;
    if (this.uploadedOutfitFile) {
      const fd = new FormData();
      fd.append('budget', budget);
      fd.append('currency', currency);
      fd.append('occasion', occasion);
      fd.append('style', style);
      fd.append('material', material);
      fd.append('notes', notes);
      fd.append('outfit_image', this.uploadedOutfitFile);
      payload = fd;
    } else {
      payload = {
        budget,
        currency,
        occasion,
        style,
        material,
        notes
      };
    }

    const visionStep = this.uploadedOutfitFile ? "Analyzing outfit neckline, silhouette & colors via Gemini Vision..." : "Evaluating neckline and occasion pairings...";
    App.showLoading("Styling Jewelry Collection...", [
      visionStep,
      `Selecting matching ${material} pieces...`,
      "Optimizing piece allocation within budget...",
      "Connecting verified retailer links..."
    ]);

    try {
      const result = await API.planJewelry(payload);
      result.planner_type = 'jewelry';
      result.user_inputs = { budget, currency, occasion, style, material, notes };
      this.currentPlanData = result;
      this.renderPlanResults(result);
      showToast('Matching jewelry ensemble ready!');
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      App.hideLoading();
    }
  },

  // -----------------------------------------------------------
  // Render Plan Results & Live Checkbox Recalculations
  // -----------------------------------------------------------
  renderPlanResults(plan) {
    const resultsContainer = document.getElementById('plan-results-section');
    if (!resultsContainer) return;

    const currency = plan.currency || '$';
    const totalBudget = plan.total_budget;
    const spent = plan.estimated_spending;
    const remaining = plan.remaining_budget;

    // Badges & Status
    const spentPct = totalBudget > 0 ? (spent / totalBudget) * 100 : 0;
    const isOver = spent > totalBudget;
    const isNear = spentPct > 85 && !isOver;

    const statusBadge = isOver ?
      `<span class="px-3 py-1 rounded-full text-xs font-bold bg-rose-500/20 text-rose-300 border border-rose-500/40">⚠ Over Budget (${spentPct.toFixed(0)}%)</span>` :
      isNear ?
      `<span class="px-3 py-1 rounded-full text-xs font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40">⚡ Optimized (${spentPct.toFixed(0)}%)</span>` :
      `<span class="px-3 py-1 rounded-full text-xs font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">✓ Within Budget (${spentPct.toFixed(0)}%)</span>`;

    const progressColor = isOver ? 'bg-rose-500' : isNear ? 'bg-amber-400' : 'bg-emerald-400';

    // Type badge
    const typeLabel = plan.planner_type === 'home' ? '🛋️ Home Interior' :
                      plan.planner_type === 'party' ? '🎉 Party Planner' : '💎 Jewelry Ensemble';

    // Outfits preview thumbnail if available
    const outfitThumb = plan.uploaded_image_url ? `
      <div class="flex items-center gap-3 p-3 bg-indigo-950/30 rounded-xl border border-indigo-800/40 mb-4">
        <img src="${plan.uploaded_image_url}" class="w-16 h-16 object-cover rounded-lg border border-indigo-500/40 shadow-md">
        <div>
          <span class="text-xs font-semibold text-indigo-300 uppercase tracking-wider block">Outfit Analyzed</span>
          <span class="text-sm text-gray-300">Styling tailored to neckline & fabric color harmony</span>
        </div>
      </div>
    ` : '';

    // Budget Allocation categories
    const allocationsHtml = (plan.allocations && plan.allocations.length > 0) ? `
      <div class="mb-6 p-4 rounded-xl bg-gray-900/60 border border-gray-800">
        <h4 class="text-xs font-semibold uppercase tracking-wider text-gray-400 mb-3">Budget Allocation Breakdown</h4>
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
          ${plan.allocations.map(al => `
            <div class="p-3 rounded-lg bg-gray-800/50 border border-gray-700/40">
              <div class="flex justify-between items-center text-xs mb-1">
                <span class="text-gray-300 font-medium truncate">${al.category_name}</span>
                <span class="text-indigo-400 font-bold">${al.percentage}%</span>
              </div>
              <div class="text-sm font-semibold text-white">${currency}${al.allocated_amount}</div>
              <div class="w-full bg-gray-700/60 h-1.5 rounded-full overflow-hidden mt-2">
                <div class="bg-indigo-500 h-full rounded-full" style="width: ${Math.min(100, al.percentage)}%"></div>
              </div>
            </div>
          `).join('')}
        </div>
      </div>
    ` : '';

    // Recommendation Cards
    const recsHtml = plan.recommendations.map((rec, idx) => {
      const platformClass = this.getPlatformBadgeClass(rec.platform_name);
      return `
        <div class="recommendation-card glass-panel p-5 relative flex flex-col justify-between ${rec.is_selected === false ? 'excluded' : ''}" id="rec-card-${idx}">
          <div>
            <div class="flex items-start justify-between gap-3 mb-2">
              <span class="px-2.5 py-0.5 rounded-md text-xs font-medium bg-gray-800 text-gray-300 border border-gray-700/60">${rec.category}</span>
              <span class="px-2.5 py-0.5 rounded-md text-xs font-semibold ${platformClass}">
                ${rec.platform_name}
              </span>
            </div>

            <h3 class="text-base font-semibold text-white mb-1 group-hover:text-indigo-300 transition">${rec.name}</h3>
            
            <div class="flex items-baseline gap-2 mb-3">
              <span class="text-xl font-bold text-gradient">${currency}${rec.estimated_price}</span>
              ${rec.quantity > 1 ? `<span class="text-xs text-gray-400">(${rec.quantity} × ${currency}${rec.estimated_price} = ${currency}${rec.total_price})</span>` : ''}
            </div>

            <div class="p-3 rounded-lg bg-gray-900/50 border border-gray-800/80 mb-4 text-xs text-gray-300 leading-relaxed">
              <strong class="text-indigo-300 block mb-0.5">Why Recommended:</strong>
              ${rec.why_recommended}
            </div>
          </div>

          <div class="pt-3 border-t border-gray-800/80 flex items-center justify-between gap-3">
            <label class="flex items-center gap-2 cursor-pointer select-none text-xs text-gray-300">
              <input type="checkbox" class="rec-toggle-checkbox w-4 h-4 rounded text-indigo-600 bg-gray-900 border-gray-700" 
                     ${rec.is_selected !== false ? 'checked' : ''} 
                     onchange="Planners.toggleRecommendationItem(${idx}, this.checked)">
              <span>In Budget</span>
            </label>

            <a href="${rec.shopping_link}" target="_blank" rel="noopener noreferrer" 
               class="px-3 py-1.5 rounded-lg bg-indigo-600/30 hover:bg-indigo-600 text-indigo-200 hover:text-white border border-indigo-500/40 text-xs font-medium flex items-center gap-1.5 transition">
              <span>View / Shop</span>
              <span>↗</span>
            </a>
          </div>
        </div>
      `;
    }).join('');

    resultsContainer.innerHTML = `
      <div class="glass-panel p-6 sm:p-8 mb-8 border-indigo-500/30 shadow-2xl">
        <!-- Header -->
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-gray-800">
          <div>
            <div class="flex items-center gap-2 mb-1">
              <span class="text-xs font-semibold text-indigo-400 uppercase tracking-wider">${typeLabel}</span>
              <span class="text-gray-600">•</span>
              ${statusBadge}
            </div>
            <h2 class="text-2xl sm:text-3xl font-bold text-white tracking-tight">${plan.title}</h2>
          </div>

          <div class="flex items-center gap-3">
            <button onclick="Planners.saveCurrentPlan()" class="px-4 py-2 rounded-xl bg-gradient-btn text-white text-sm font-semibold shadow-lg hover:shadow-indigo-500/25 transition flex items-center gap-2">
              <span>💾</span>
              <span>Save Plan</span>
            </button>
            <button onclick="window.print()" class="px-4 py-2 rounded-xl bg-gray-800 hover:bg-gray-700 text-gray-300 text-sm font-medium border border-gray-700 transition flex items-center gap-2">
              <span>🖨️</span>
              <span class="hidden sm:inline">Export</span>
            </button>
          </div>
        </div>

        <!-- Budget Progress Banner -->
        <div class="py-6">
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-4">
            <div class="p-3.5 rounded-xl bg-gray-900/50 border border-gray-800">
              <span class="text-xs text-gray-400 block mb-0.5">Total Budget</span>
              <span class="text-xl sm:text-2xl font-bold text-white">${currency}${totalBudget.toLocaleString()}</span>
            </div>
            <div class="p-3.5 rounded-xl bg-gray-900/50 border border-gray-800">
              <span class="text-xs text-gray-400 block mb-0.5">Estimated Cost</span>
              <span class="text-xl sm:text-2xl font-bold text-indigo-400" id="results-spent">${currency}${spent.toLocaleString()}</span>
            </div>
            <div class="p-3.5 rounded-xl bg-gray-900/50 border border-gray-800">
              <span class="text-xs text-gray-400 block mb-0.5">Remaining Surplus</span>
              <span class="text-xl sm:text-2xl font-bold text-emerald-400" id="results-remaining">${currency}${remaining.toLocaleString()}</span>
            </div>
            <div class="p-3.5 rounded-xl bg-gray-900/50 border border-gray-800">
              <span class="text-xs text-gray-400 block mb-0.5">Budget Health</span>
              <span class="text-xl sm:text-2xl font-bold text-white" id="results-pct">${Math.min(100, spentPct).toFixed(0)}%</span>
            </div>
          </div>

          <!-- Dynamic Progress Bar -->
          <div class="w-full bg-gray-800/80 rounded-full h-3 p-0.5 overflow-hidden border border-gray-700/60">
            <div id="results-progress-bar" class="budget-progress-bar h-full rounded-full ${progressColor}" style="width: ${Math.min(100, spentPct)}%"></div>
          </div>
        </div>

        ${outfitThumb}

        <!-- AI Explanation Card -->
        <div class="mb-6 p-4 rounded-xl bg-indigo-950/20 border border-indigo-800/30 flex items-start gap-3">
          <span class="text-2xl">✨</span>
          <div>
            <h4 class="text-sm font-semibold text-indigo-300 mb-1">AI Recommendation Intelligence</h4>
            <p class="text-sm text-gray-300 leading-relaxed">${plan.ai_summary}</p>
          </div>
        </div>

        ${allocationsHtml}

        <!-- Recommendations Grid -->
        <div class="mt-8">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-bold text-white flex items-center gap-2">
              <span>Curated Recommendations</span>
              <span class="text-xs px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 font-semibold" id="recs-count-badge">${plan.recommendations.length} items</span>
            </h3>
            <span class="text-xs text-gray-400">Toggle items to update budget dynamically</span>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            ${recsHtml}
          </div>
        </div>
      </div>
    `;

    resultsContainer.classList.remove('hidden');
    resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
  },

  toggleRecommendationItem(index, isChecked) {
    if (!this.currentPlanData || !this.currentPlanData.recommendations[index]) return;
    
    this.currentPlanData.recommendations[index].is_selected = isChecked;

    const card = document.getElementById(`rec-card-${index}`);
    if (card) {
      if (isChecked) {
        card.classList.remove('excluded');
      } else {
        card.classList.add('excluded');
      }
    }

    // Recalculate spending
    const currency = this.currentPlanData.currency || '$';
    const totalBudget = this.currentPlanData.total_budget;
    
    let newSpent = 0;
    this.currentPlanData.recommendations.forEach(r => {
      if (r.is_selected !== false) {
        newSpent += (r.estimated_price * (r.quantity || 1));
      }
    });

    newSpent = Math.round(newSpent * 100) / 100;
    const newRemaining = Math.max(0, Math.round((totalBudget - newSpent) * 100) / 100);

    this.currentPlanData.estimated_spending = newSpent;
    this.currentPlanData.remaining_budget = newRemaining;

    // Update DOM
    const spentEl = document.getElementById('results-spent');
    const remainingEl = document.getElementById('results-remaining');
    const pctEl = document.getElementById('results-pct');
    const progressBar = document.getElementById('results-progress-bar');

    if (spentEl) spentEl.textContent = `${currency}${newSpent.toLocaleString()}`;
    if (remainingEl) remainingEl.textContent = `${currency}${newRemaining.toLocaleString()}`;
    
    const spentPct = totalBudget > 0 ? (newSpent / totalBudget) * 100 : 0;
    if (pctEl) pctEl.textContent = `${Math.min(100, spentPct).toFixed(0)}%`;

    if (progressBar) {
      progressBar.style.width = `${Math.min(100, spentPct)}%`;
      progressBar.className = `budget-progress-bar h-full rounded-full ${spentPct > 100 ? 'bg-rose-500' : spentPct > 85 ? 'bg-amber-400' : 'bg-emerald-400'}`;
    }

    showToast(isChecked ? 'Item included in budget' : 'Item excluded from budget calculation', 'info');
  },

  async saveCurrentPlan() {
    if (!this.currentPlanData) return;

    try {
      const res = await API.savePlan(this.currentPlanData);
      showToast('Plan saved to your Dashboard!');
      Dashboard.loadStats();
    } catch (err) {
      showToast(err.message, 'error');
    }
  },

  getPlatformBadgeClass(platform) {
    const p = (platform || '').toLowerCase();
    if (p.includes('amazon')) return 'badge-amazon';
    if (p.includes('ikea')) return 'badge-ikea';
    if (p.includes('etsy')) return 'badge-etsy';
    if (p.includes('target')) return 'badge-target';
    if (p.includes('tanishq')) return 'badge-tanishq';
    if (p.includes('blue nile')) return 'badge-bluenile';
    return 'badge-default';
  }
};
