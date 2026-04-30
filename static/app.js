        function app() {
            return {
                view: 'dash',
                modules: [],
                tasks: [],
                activeModule: null,
                calmMode: false,
                theme: 'light',
                sidebarCollapsed: false,
                focusFilter: 'all',
                dopamineWeekOffset: 0,
                taskScope: 'all',
                moduleOrder: [],
                dailyGoal: 5,
                taskModal: false,
                isCreatingTask: false,
                editingTask: {},
                priorityFilter: 'ALL',
                sortOrder: 'none',
                API: '',
                flowTask: null,
                flowTimer: 0,
                timerInterval: null,
                isShredding: false,
                brainDump: '',
                brainDumpTargetModuleId: '',
                noteSavedAt: '',
                brainDumpSaveTimer: null,
                brainDumpStorageKey: 'adhd-focus-brain-dump-draft-v1',
                calendarMode: 'month',
                calendarCursor: '',
                selectedDate: '',
                monthlyMonthKey: '',
                monthlyTasks: [],
                newMonthlyTaskName: '',
                newMonthlyTaskDueDay: '',
                monthlyTaskModal: false,
                debts: [],
                debtsMonthKey: '',
                debtsSummary: { count: 0, total: 0, monthly: 0, debt_total: 0, debt_monthly: 0, fixed_monthly: 0, fixed_count: 0, debt_count: 0 },
                debtModal: false,
                newDebt: {
                    name: '',
                    place: '',
                    kind: 'debt',
                    total_amount: '',
                    monthly_amount: '',
                    due_day: '',
                    note: ''
                },
                draggedTaskId: null,
                draggedModuleId: null,
                moduleNotes: {},
                moduleNoteTimers: {},
                globalLaneCollapsed: {},
                mutedModuleIds: [],
                canvasNodes: [],
                canvasLinks: [],
                selectedCanvasNodeId: null,
                selectedCanvasLinkId: null,
                canvasPointerAction: null,
                canvasLinkDraftFromId: null,
                canvasBoardWidth: 12000,
                canvasBoardHeight: 8000,
                canvasGridVisible: true,
                canvasSnapToGrid: false,
                canvasSaveTimer: null,
                canvasStorageKey: 'adhd-focus-canvas-v2',
                canvasLegacyStorageKey: 'adhd-focus-canvas-v1',
                canvasColorOptions: [
                    { id: 'slate', label: 'Szary', swatch: '#e2e8f0', bg: '#ffffff', border: '#cbd5e1', text: '#0f172a' },
                    { id: 'emerald', label: 'Zielony', swatch: '#10b981', bg: '#ecfdf5', border: '#6ee7b7', text: '#064e3b' },
                    { id: 'sky', label: 'Niebieski', swatch: '#0ea5e9', bg: '#e0f2fe', border: '#7dd3fc', text: '#082f49' },
                    { id: 'amber', label: 'Bursztyn', swatch: '#f59e0b', bg: '#fffbeb', border: '#fcd34d', text: '#78350f' },
                    { id: 'rose', label: 'Rozowy', swatch: '#f43f5e', bg: '#fff1f2', border: '#fda4af', text: '#881337' },
                    { id: 'violet', label: 'Fiolet', swatch: '#8b5cf6', bg: '#f5f3ff', border: '#c4b5fd', text: '#4c1d95' }
                ],
                canvasShapeOptions: [
                    { id: 'text', label: 'Tekst' },
                    { id: 'rect', label: 'Prostokat' },
                    { id: 'diamond', label: 'Romb' },
                    { id: 'circle', label: 'Kolo' }
                ],
                projectDoc: '',
                projectDocSavedAt: '',
                projectDocSaveTimer: null,
                projectDocStorageKey: 'adhd-focus-project-doc-v1',
                uiPrefsKey: 'adhd-focus-ui-v1',
                weekLabels: ['Pon', 'Wt', 'Sr', 'Czw', 'Pt', 'Sob', 'Nd'],
                columnsMeta: [
                    { id: 'oczekujace', name: 'Oczekujace', color: 'text-slate-500' },
                    { id: 'przygotowanie', name: 'Przygotowanie', color: 'text-amber-600' },
                    { id: 'todo', name: 'Teraz robie', color: 'text-cyan-600' },
                    { id: 'gotowe', name: 'Gotowe', color: 'text-emerald-600' }
                ],
                moduleThemes: [
                    {
                        badge: 'border-emerald-100 bg-emerald-50 text-emerald-700',
                        dot: 'bg-emerald-500',
                        bar: 'bg-emerald-500',
                        soft: 'border-emerald-100 bg-emerald-50 text-emerald-700',
                        text: 'text-emerald-700'
                    },
                    {
                        badge: 'border-sky-100 bg-sky-50 text-sky-700',
                        dot: 'bg-sky-500',
                        bar: 'bg-sky-500',
                        soft: 'border-sky-100 bg-sky-50 text-sky-700',
                        text: 'text-sky-700'
                    },
                    {
                        badge: 'border-amber-100 bg-amber-50 text-amber-700',
                        dot: 'bg-amber-500',
                        bar: 'bg-amber-500',
                        soft: 'border-amber-100 bg-amber-50 text-amber-700',
                        text: 'text-amber-700'
                    },
                    {
                        badge: 'border-rose-100 bg-rose-50 text-rose-700',
                        dot: 'bg-rose-500',
                        bar: 'bg-rose-500',
                        soft: 'border-rose-100 bg-rose-50 text-rose-700',
                        text: 'text-rose-700'
                    },
                    {
                        badge: 'border-violet-100 bg-violet-50 text-violet-700',
                        dot: 'bg-violet-500',
                        bar: 'bg-violet-500',
                        soft: 'border-violet-100 bg-violet-50 text-violet-700',
                        text: 'text-violet-700'
                    },
                    {
                        badge: 'border-cyan-100 bg-cyan-50 text-cyan-700',
                        dot: 'bg-cyan-500',
                        bar: 'bg-cyan-500',
                        soft: 'border-cyan-100 bg-cyan-50 text-cyan-700',
                        text: 'text-cyan-700'
                    }
                ],

                async init() {
                    this.loadUIPreferences();

                    if (!this.calendarCursor) this.calendarCursor = this.getTodayKey();
                    if (!this.selectedDate) this.selectedDate = this.getTodayKey();
                    if (!this.monthlyMonthKey) this.monthlyMonthKey = this.getCurrentMonthKey();

                    await Promise.all([
                        this.loadModules(),
                        this.loadAllTasks(),
                        this.loadBrainDump(),
                        this.loadCanvasBoard(),
                        this.loadProjectDoc(),
                        this.loadMonthlyTasks(),
                        this.loadDebts(this.getCurrentMonthKey())
                    ]);
                    await this.loadModuleNotes();

                    if (!this.activeModule && this.modules.length > 0) {
                        this.activeModule = this.getSidebarModules()[0] || this.modules[0];
                    }

                    if (!this.activeModule && this.view === 'kanban') {
                        this.view = 'dash';
                    }

                    if (!this.brainDumpTargetModuleId && this.modules.length > 0) {
                        const firstModule = this.getSidebarModules()[0] || this.modules[0];
                        this.brainDumpTargetModuleId = String(firstModule.id);
                    }
                },

                loadUIPreferences() {
                    try {
                        const raw = localStorage.getItem(this.uiPrefsKey);
                        if (!raw) return;
                        const parsed = JSON.parse(raw);
                        this.calmMode = false;
                        this.theme = parsed.theme === 'dark' ? 'dark' : 'light';
                        this.sidebarCollapsed = parsed.sidebarCollapsed ?? this.sidebarCollapsed;
                        this.focusFilter = parsed.focusFilter ?? this.focusFilter;
                        this.dopamineWeekOffset = Number.isFinite(Number(parsed.dopamineWeekOffset)) ? Number(parsed.dopamineWeekOffset) : this.dopamineWeekOffset;
                        this.moduleOrder = Array.isArray(parsed.moduleOrder) ? parsed.moduleOrder.map(Number).filter(Number.isFinite) : this.moduleOrder;
                        this.globalLaneCollapsed = parsed.globalLaneCollapsed && typeof parsed.globalLaneCollapsed === 'object' ? parsed.globalLaneCollapsed : this.globalLaneCollapsed;
                        this.mutedModuleIds = Array.isArray(parsed.mutedModuleIds) ? parsed.mutedModuleIds.map(Number).filter(Number.isFinite) : this.mutedModuleIds;
                        this.dailyGoal = Number.isFinite(Number(parsed.dailyGoal)) && Number(parsed.dailyGoal) > 0 ? Number(parsed.dailyGoal) : this.dailyGoal;
                    } catch (error) {
                        /* ignore broken local settings */
                    }
                },

                saveUIPreferences() {
                    try {
                        localStorage.setItem(this.uiPrefsKey, JSON.stringify({
                            theme: this.theme,
                            sidebarCollapsed: this.sidebarCollapsed,
                            focusFilter: this.focusFilter,
                            moduleOrder: this.moduleOrder,
                            globalLaneCollapsed: this.globalLaneCollapsed,
                            mutedModuleIds: this.mutedModuleIds,
                            dailyGoal: this.dailyGoal,
                            dopamineWeekOffset: this.dopamineWeekOffset
                        }));
                    } catch (error) {
                        /* ignore storage write errors */
                    }
                },

                toggleTheme() {
                    this.theme = this.theme === 'dark' ? 'light' : 'dark';
                    this.saveUIPreferences();
                },

                toggleSidebar() {
                    this.sidebarCollapsed = !this.sidebarCollapsed;
                    this.saveUIPreferences();
                },

                setFocusFilter(mode) {
                    this.focusFilter = mode;
                    this.saveUIPreferences();
                },

                setTaskScope(mode) {
                    this.taskScope = mode === 'module' ? 'module' : 'all';
                },

                openAllTasksView() {
                    this.setTaskScope('all');
                    this.view = 'kanban';
                },

                normalizeModuleCategory(category) {
                    const value = (category || 'praca').toString().trim().toLowerCase();
                    return value.startsWith('pryw') ? 'prywatne' : 'praca';
                },

                normalizeModuleOrder() {
                    const ids = this.modules.map(module => module.id);
                    const ordered = this.moduleOrder.filter(id => ids.includes(id));
                    const missing = ids.filter(id => !ordered.includes(id));
                    this.moduleOrder = [...ordered, ...missing];
                },

                getModuleOrderIndex(moduleId) {
                    const index = this.moduleOrder.indexOf(moduleId);
                    return index === -1 ? Number.MAX_SAFE_INTEGER : index;
                },

                sortModulesByManualOrder(modules) {
                    return [...modules].sort((a, b) => {
                        const orderDiff = this.getModuleOrderIndex(a.id) - this.getModuleOrderIndex(b.id);
                        if (orderDiff !== 0) return orderDiff;
                        return a.name.localeCompare(b.name, 'pl');
                    });
                },

                sortModulesForAttention(modules) {
                    return this.sortModulesByManualOrder(modules).sort((a, b) => {
                        const muteDiff = Number(this.isModuleMuted(a.id)) - Number(this.isModuleMuted(b.id));
                        if (muteDiff !== 0) return muteDiff;
                        return this.getModuleOrderIndex(a.id) - this.getModuleOrderIndex(b.id);
                    });
                },

                getSidebarModules() {
                    return this.sortModulesForAttention(this.modules);
                },

                getModulesByCategory(category) {
                    const normalized = this.normalizeModuleCategory(category);
                    return this.sortModulesForAttention(
                        this.modules.filter(module => this.normalizeModuleCategory(module.category) === normalized)
                    );
                },

                isModuleMuted(moduleId) {
                    return this.mutedModuleIds.includes(Number(moduleId));
                },

                toggleModuleMuted(moduleId) {
                    const id = Number(moduleId);
                    if (!Number.isFinite(id)) return;
                    if (this.isModuleMuted(id)) {
                        this.mutedModuleIds = this.mutedModuleIds.filter(item => item !== id);
                    } else {
                        this.mutedModuleIds = [...this.mutedModuleIds, id];
                    }
                    this.saveUIPreferences();
                },

                getSidebarSections() {
                    return [
                        { id: 'praca', label: 'Praca', modules: this.getModulesByCategory('praca') },
                        { id: 'prywatne', label: 'Prywatne', modules: this.getModulesByCategory('prywatne') }
                    ];
                },

                getModuleCategoryLabel(category) {
                    return this.normalizeModuleCategory(category) === 'prywatne' ? 'Prywatne' : 'Praca';
                },

                normalizePriorityValue(priority) {
                    const value = (priority || '').toString().trim().toUpperCase();
                    return ['P1', 'P2', 'P3'].includes(value) ? value : '';
                },

                normalizeTaskStatus(status) {
                    const value = (status || 'oczekujace').toString().trim().toLowerCase();
                    if (value === 'analiza' || value === 'wstepne') return 'przygotowanie';
                    return ['oczekujace', 'przygotowanie', 'todo', 'gotowe'].includes(value) ? value : 'oczekujace';
                },

                moveModule(moduleId, direction) {
                    const index = this.moduleOrder.indexOf(moduleId);
                    if (index === -1) return;
                    const nextIndex = index + direction;
                    if (nextIndex < 0 || nextIndex >= this.moduleOrder.length) return;
                    const swapped = [...this.moduleOrder];
                    [swapped[index], swapped[nextIndex]] = [swapped[nextIndex], swapped[index]];
                    this.moduleOrder = swapped;
                    this.saveUIPreferences();
                },

                canMoveModule(moduleId, direction) {
                    const index = this.moduleOrder.indexOf(moduleId);
                    if (index === -1) return false;
                    const nextIndex = index + direction;
                    return nextIndex >= 0 && nextIndex < this.moduleOrder.length;
                },

                startModuleDrag(module, event) {
                    if (!module) return;
                    this.draggedModuleId = module.id;
                    if (event?.dataTransfer) {
                        event.dataTransfer.effectAllowed = 'move';
                        event.dataTransfer.setData('text/plain', String(module.id));
                    }
                },

                endModuleDrag() {
                    this.draggedModuleId = null;
                },

                dropModuleOn(targetModule) {
                    if (!this.draggedModuleId || !targetModule || this.draggedModuleId === targetModule.id) {
                        this.draggedModuleId = null;
                        return;
                    }

                    const ordered = [...this.moduleOrder];
                    const fromIndex = ordered.indexOf(this.draggedModuleId);
                    const toIndex = ordered.indexOf(targetModule.id);
                    if (fromIndex === -1 || toIndex === -1) {
                        this.draggedModuleId = null;
                        return;
                    }

                    const [moved] = ordered.splice(fromIndex, 1);
                    ordered.splice(toIndex, 0, moved);
                    this.moduleOrder = ordered;
                    this.draggedModuleId = null;
                    this.saveUIPreferences();
                },

                async renameModule(module) {
                    if (!module) return;
                    const nextName = prompt('Nowa nazwa modulu:', module.name || '');
                    if (nextName === null) return;
                    const cleanName = nextName.trim();
                    if (!cleanName) {
                        alert('Nazwa modulu nie moze byc pusta.');
                        return;
                    }

                    const response = await fetch(`${this.API}/modules/${module.id}`, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ name: cleanName })
                    });

                    if (!response.ok) {
                        alert(await this.getApiErrorMessage(response, 'Nie udalo sie zmienic nazwy modulu.'));
                        return;
                    }

                    await this.init();
                    const refreshed = this.modules.find(item => item.id === module.id);
                    if (refreshed && this.activeModule?.id === module.id) {
                        this.activeModule = refreshed;
                    }
                },

                async loadModules() {
                    const res = await fetch(`${this.API}/modules`);
                    const baseModules = await res.json();
                    this.modules = await Promise.all(baseModules.map(async (module) => {
                        const progressRes = await fetch(`${this.API}/modules/${module.id}/progress`);
                        const progressData = await progressRes.json();
                        return {
                            ...module,
                            category: this.normalizeModuleCategory(module.category),
                            progress: Math.round(progressData.percent || 0)
                        };
                    }));
                    this.normalizeModuleOrder();
                    this.saveUIPreferences();
                },

                async loadAllTasks() {
                    const res = await fetch(`${this.API}/tasks`);
                    const payload = await res.json();
                    this.tasks = payload.map(task => ({
                        ...task,
                        status: this.normalizeTaskStatus(task.status),
                        priority: this.normalizePriorityValue(task.priority)
                    }));
                },

                async loadBrainDump() {
                    try {
                        const res = await fetch(`${this.API}/notes/brain-dump`);
                        if (!res.ok) throw new Error('note_load_failed');
                        const data = await res.json();
                        this.brainDump = data.content || '';
                        this.noteSavedAt = data.updated_at || '';
                        try {
                            const localDraft = localStorage.getItem(this.brainDumpStorageKey);
                            if (typeof localDraft === 'string' && localDraft.trim() && localDraft !== this.brainDump) {
                                this.brainDump = localDraft;
                            } else {
                                localStorage.removeItem(this.brainDumpStorageKey);
                            }
                        } catch (error) {
                            /* ignore storage cleanup errors */
                        }
                    } catch (error) {
                        try {
                            const localDraft = localStorage.getItem(this.brainDumpStorageKey);
                            if (typeof localDraft === 'string') {
                                this.brainDump = localDraft;
                            }
                        } catch (readError) {
                            /* ignore storage read errors */
                        }
                    }
                },

                async loadCanvasBoard() {
                    const applyPayload = (payload) => {
                        const normalized = this.normalizeCanvasBoard(payload);
                        this.canvasNodes = normalized.nodes;
                        this.canvasLinks = normalized.links;
                        this.canvasGridVisible = normalized.gridVisible;
                        this.canvasSnapToGrid = normalized.snapToGrid;
                        this.selectedCanvasNodeId = null;
                        this.selectedCanvasLinkId = null;
                        this.canvasLinkDraftFromId = null;
                    };

                    try {
                        const res = await fetch(`${this.API}/notes/process-map`);
                        if (!res.ok) throw new Error('canvas_load_failed');
                        const data = await res.json();
                        const content = data.content || '';
                        const parsed = content ? JSON.parse(content) : { version: 2, nodes: [], links: [] };
                        applyPayload(parsed);
                    } catch (error) {
                        try {
                            const localDraft = localStorage.getItem(this.canvasStorageKey) || localStorage.getItem(this.canvasLegacyStorageKey);
                            const parsed = localDraft ? JSON.parse(localDraft) : { version: 2, nodes: [], links: [] };
                            applyPayload(parsed);
                        } catch (readError) {
                            applyPayload({ version: 2, nodes: [], links: [] });
                        }
                    }
                },

                async loadProjectDoc() {
                    try {
                        const res = await fetch(`${this.API}/notes/project-doc`);
                        if (!res.ok) throw new Error('doc_load_failed');
                        const data = await res.json();
                        this.projectDoc = data.content || '';
                        this.projectDocSavedAt = data.updated_at || '';
                        try {
                            const localDraft = localStorage.getItem(this.projectDocStorageKey);
                            if (typeof localDraft === 'string' && localDraft.trim() && localDraft !== this.projectDoc) {
                                this.projectDoc = localDraft;
                            } else {
                                localStorage.removeItem(this.projectDocStorageKey);
                            }
                        } catch (error) {
                            /* ignore storage cleanup errors */
                        }
                    } catch (error) {
                        try {
                            const localDraft = localStorage.getItem(this.projectDocStorageKey);
                            this.projectDoc = typeof localDraft === 'string' ? localDraft : '';
                        } catch (readError) {
                            this.projectDoc = '';
                        }
                    }
                },

                async loadMonthlyTasks() {
                    const month = this.monthlyMonthKey || this.getCurrentMonthKey();
                    this.monthlyMonthKey = month;
                    const res = await fetch(`${this.API}/monthly-tasks?month=${encodeURIComponent(month)}`);
                    if (!res.ok) {
                        this.monthlyTasks = [];
                        return;
                    }
                    const payload = await res.json();
                    this.monthlyMonthKey = payload.month_key || month;
                    this.monthlyTasks = Array.isArray(payload.items) ? payload.items : [];
                },

                async loadDebts(monthKey = '') {
                    const cleanMonthKey = (monthKey || '').trim() || this.getCurrentMonthKey();
                    const res = await fetch(`${this.API}/debts?month=${encodeURIComponent(cleanMonthKey)}`);
                    if (!res.ok) {
                        this.debts = [];
                        this.debtsMonthKey = cleanMonthKey;
                        this.debtsSummary = { count: 0, total: 0, monthly: 0, debt_total: 0, debt_monthly: 0, fixed_monthly: 0, fixed_count: 0, debt_count: 0 };
                        return;
                    }
                    const payload = await res.json();
                    this.debts = Array.isArray(payload.items) ? payload.items : [];
                    this.debtsMonthKey = payload.month_key || cleanMonthKey;
                    this.debtsSummary = payload.summary || { count: 0, total: 0, monthly: 0, debt_total: 0, debt_monthly: 0, fixed_monthly: 0, fixed_count: 0, debt_count: 0 };
                },

                async loadModuleNotes() {
                    if (!Array.isArray(this.modules) || this.modules.length === 0) {
                        this.moduleNotes = {};
                        return;
                    }

                    const entries = await Promise.all(this.modules.map(async module => {
                        try {
                            const res = await fetch(`${this.API}/notes/module-${module.id}`);
                            if (!res.ok) return [module.id, this.moduleNotes[module.id] || ''];
                            const payload = await res.json();
                            return [module.id, payload.content || ''];
                        } catch (error) {
                            return [module.id, this.moduleNotes[module.id] || ''];
                        }
                    }));

                    this.moduleNotes = Object.fromEntries(entries);
                },

                getTodayKey() {
                    return this.dateToKey(new Date());
                },

                keyToDate(dateKey) {
                    if (!dateKey) return new Date();
                    const [year, month, day] = dateKey.split('-').map(Number);
                    return new Date(year, month - 1, day, 12, 0, 0);
                },

                dateToKey(date) {
                    const year = date.getFullYear();
                    const month = String(date.getMonth() + 1).padStart(2, '0');
                    const day = String(date.getDate()).padStart(2, '0');
                    return `${year}-${month}-${day}`;
                },

                formatCurrentDate() {
                    return new Intl.DateTimeFormat('pl-PL', {
                        weekday: 'long',
                        day: 'numeric',
                        month: 'long'
                    }).format(new Date());
                },

                formatNoteTimestamp(timestamp) {
                    if (!timestamp) return 'brak';
                    return new Intl.DateTimeFormat('pl-PL', {
                        day: 'numeric',
                        month: 'short',
                        hour: '2-digit',
                        minute: '2-digit'
                    }).format(new Date(timestamp));
                },

                getCurrentMonthKey() {
                    const today = new Date();
                    const year = today.getFullYear();
                    const month = String(today.getMonth() + 1).padStart(2, '0');
                    return `${year}-${month}`;
                },

                formatMonthLabel(monthKey) {
                    if (!monthKey) return '';
                    const [year, month] = monthKey.split('-').map(Number);
                    if (!year || !month) return monthKey;
                    return new Intl.DateTimeFormat('pl-PL', { month: 'long', year: 'numeric' }).format(
                        new Date(year, month - 1, 1, 12, 0, 0)
                    );
                },

                shiftMonthlyMonth(step) {
                    const [year, month] = (this.monthlyMonthKey || this.getCurrentMonthKey()).split('-').map(Number);
                    const nextDate = new Date(year, (month - 1) + step, 1, 12, 0, 0);
                    const nextYear = nextDate.getFullYear();
                    const nextMonth = String(nextDate.getMonth() + 1).padStart(2, '0');
                    this.monthlyMonthKey = `${nextYear}-${nextMonth}`;
                    this.loadMonthlyTasks();
                },

                formatMoney(value) {
                    return new Intl.NumberFormat('pl-PL', {
                        style: 'currency',
                        currency: 'PLN',
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2
                    }).format(Number(value || 0));
                },

                normalizeMonthlyDueDay(value) {
                    const day = Math.round(Number(value || 0));
                    if (!Number.isFinite(day) || day <= 0) return 0;
                    return Math.min(31, day);
                },

                getMonthlyDueLabel(task) {
                    const dueDay = this.normalizeMonthlyDueDay(task?.due_day);
                    if (!dueDay) return 'bez dnia';
                    return `do ${dueDay}. dnia miesiaca`;
                },

                getMonthlyDueBadgeClass(task) {
                    const dueDay = this.normalizeMonthlyDueDay(task?.due_day);
                    if (!dueDay || task?.done) return 'bg-slate-100 text-slate-500';
                    const today = new Date();
                    const currentMonth = this.getCurrentMonthKey();
                    if ((this.monthlyMonthKey || currentMonth) !== currentMonth) return 'bg-cyan-50 text-cyan-700';
                    const daysLeft = dueDay - today.getDate();
                    if (daysLeft < 0) return 'bg-red-50 text-red-600';
                    if (daysLeft <= 2) return 'bg-amber-50 text-amber-700';
                    return 'bg-cyan-50 text-cyan-700';
                },

                getDebtKindLabel(kind) {
                    return kind === 'fixed' ? 'koszt staly' : 'splata';
                },

                getDebtKindBadgeClass(kind) {
                    return kind === 'fixed'
                        ? 'bg-sky-50 text-sky-700'
                        : 'bg-emerald-50 text-emerald-700';
                },

                getDebtDueLabel(item) {
                    const dueDay = this.normalizeMonthlyDueDay(item?.due_day);
                    if (!dueDay) return 'bez dnia';
                    return `do ${dueDay}. dnia mies.`;
                },

                getDebtsByKind(kind) {
                    return this.debts.filter(item => (item.kind || 'debt') === kind);
                },

                resetMonthlyTaskDraft() {
                    this.newMonthlyTaskName = '';
                    this.newMonthlyTaskDueDay = '';
                },

                openMonthlyTaskModal() {
                    this.monthlyTaskModal = true;
                },

                closeMonthlyTaskModal() {
                    this.monthlyTaskModal = false;
                    this.resetMonthlyTaskDraft();
                },

                resetDebtDraft() {
                    this.newDebt = {
                        name: '',
                        place: '',
                        kind: 'debt',
                        total_amount: '',
                        monthly_amount: '',
                        due_day: '',
                        note: ''
                    };
                },

                openDebtModal() {
                    this.debtModal = true;
                },

                closeDebtModal() {
                    this.debtModal = false;
                    this.resetDebtDraft();
                },

                getMonthKeyFromDateKey(dateKey) {
                    const clean = (dateKey || '').toString().trim();
                    return /^\d{4}-\d{2}-\d{2}$/.test(clean) ? clean.slice(0, 7) : this.getCurrentMonthKey();
                },

                getCalendarCursorMonthKey() {
                    return this.getMonthKeyFromDateKey(this.calendarCursor || this.getTodayKey());
                },

                getDebtEstimatedMonths(item) {
                    if ((item?.kind || 'debt') !== 'debt') return 0;
                    const total = Number(item?.total_amount || 0);
                    const monthly = Number(item?.monthly_amount || 0);
                    if (total <= 0 || monthly <= 0) return 0;
                    return Math.max(1, Math.ceil(total / monthly));
                },

                getDebtRemainingAmount(item) {
                    if ((item?.kind || 'debt') !== 'debt') return 0;
                    const total = Number(item?.total_amount || 0);
                    const monthly = Number(item?.monthly_amount || 0);
                    const paidMonths = Math.max(0, Number(item?.paid_months || 0));
                    if (total <= 0 || monthly <= 0) return Math.max(0, total);
                    return Math.max(0, total - (paidMonths * monthly));
                },

                getDebtRemainingMonths(item) {
                    if ((item?.kind || 'debt') !== 'debt') return 0;
                    const remainingAmount = this.getDebtRemainingAmount(item);
                    const monthly = Number(item?.monthly_amount || 0);
                    if (remainingAmount <= 0 || monthly <= 0) return 0;
                    return Math.ceil(remainingAmount / monthly);
                },

                getDebtMonthsLabel(item) {
                    if ((item?.kind || 'debt') !== 'debt') return '';
                    const estimated = this.getDebtEstimatedMonths(item);
                    const left = this.getDebtRemainingMonths(item);
                    if (!estimated) return '';
                    if (left <= 0) return 'splacone';
                    return `${left}/${estimated} mies.`;
                },

                getMonthlyEntriesForDate(dateKey) {
                    const targetMonthKey = this.getMonthKeyFromDateKey(dateKey);
                    if (targetMonthKey !== (this.monthlyMonthKey || this.getCurrentMonthKey())) return [];
                    const day = this.keyToDate(dateKey).getDate();
                    return this.monthlyTasks
                        .filter(task => this.normalizeMonthlyDueDay(task?.due_day) === day)
                        .map(task => ({
                            type: 'monthly',
                            id: `monthly-${task.id}-${dateKey}`,
                            dateKey,
                            item: task,
                            done: !!task.done
                        }));
                },

                getDebtEntriesForDate(dateKey) {
                    const targetMonthKey = this.getMonthKeyFromDateKey(dateKey);
                    if (targetMonthKey !== (this.debtsMonthKey || this.getCurrentMonthKey())) return [];
                    const day = this.keyToDate(dateKey).getDate();
                    return this.debts
                        .filter(debt => this.normalizeMonthlyDueDay(debt?.due_day) === day)
                        .map(debt => ({
                            type: 'debt',
                            id: `debt-${debt.id}-${dateKey}`,
                            dateKey,
                            item: debt,
                            done: !!debt.month_done
                        }));
                },

                getCalendarEntriesForDate(dateKey) {
                    const taskEntries = this.getTasksForDate(dateKey).map(task => ({
                        type: 'task',
                        id: `task-${task.id}-${dateKey}`,
                        dateKey,
                        item: task
                    }));
                    const monthlyEntries = this.getMonthlyEntriesForDate(dateKey);
                    const debtEntries = this.getDebtEntriesForDate(dateKey);
                    const order = { debt: 0, monthly: 1, task: 2 };
                    return [...debtEntries, ...monthlyEntries, ...taskEntries].sort((a, b) => {
                        const typeDiff = (order[a.type] ?? 9) - (order[b.type] ?? 9);
                        if (typeDiff !== 0) return typeDiff;
                        const aName = (a.item?.name || '').toString();
                        const bName = (b.item?.name || '').toString();
                        return aName.localeCompare(bName, 'pl');
                    });
                },

                getMonthlyDoneCount() {
                    return this.monthlyTasks.filter(task => task.done).length;
                },

                getMonthlyOpenCount() {
                    return this.monthlyTasks.filter(task => !task.done).length;
                },

                sanitizeDateKey(value) {
                    const clean = (value || '').toString().trim();
                    return /^\d{4}-\d{2}-\d{2}$/.test(clean) ? clean : '';
                },

                formatSelectedDateTitle() {
                    const selected = this.selectedDate || this.getTodayKey();
                    return new Intl.DateTimeFormat('pl-PL', {
                        weekday: 'long',
                        day: 'numeric',
                        month: 'long'
                    }).format(this.keyToDate(selected));
                },

                getOpenTasks() {
                    return this.tasks.filter(task => task.status !== 'gotowe');
                },

                getInProgressCount() {
                    return this.getOpenTasks().filter(task => task.status === 'todo').length;
                },

                getUrgentOpenCount() {
                    return this.getOpenTasks().filter(task => (
                        this.normalizePriorityValue(task.priority) === 'P1' ||
                        this.isTaskOverdue(task) ||
                        this.isTaskDueToday(task)
                    )).length;
                },

                getPlannedTodayCount() {
                    return this.getTodayTasks().length;
                },

                getPlannedUpcomingCount() {
                    return this.getUpcomingTasks().length;
                },

                getPreparationCount() {
                    return this.getOpenTasks().filter(task => task.status === 'przygotowanie').length;
                },

                getStatusCount(status) {
                    const normalized = this.normalizeTaskStatus(status);
                    return this.tasks.filter(task => this.normalizeTaskStatus(task.status) === normalized).length;
                },

                getPriorityCount(priority) {
                    return this.getOpenTasks().filter(task => this.normalizePriorityValue(task.priority) === priority).length;
                },

                getActiveModulesCount() {
                    return this.modules.filter(module => this.getModuleOpenCount(module.id) > 0).length;
                },

                getWorkingModulesCount() {
                    return this.getActiveModulesCount();
                },

                getModuleTheme(moduleId) {
                    const index = this.modules.findIndex(module => module.id === moduleId);
                    const safeIndex = index >= 0 ? index : Number(moduleId || 0);
                    return this.moduleThemes[safeIndex % this.moduleThemes.length];
                },

                getModuleName(moduleId) {
                    const module = this.modules.find(item => item.id === moduleId);
                    return module ? module.name : '?';
                },

                getModuleOpenCount(moduleId) {
                    return this.tasks.filter(task => task.module_id === moduleId && task.status !== 'gotowe').length;
                },

                getModuleTodoCount(moduleId) {
                    return this.tasks.filter(task => task.module_id === moduleId && task.status === 'todo').length;
                },

                getModuleUrgentCount(moduleId) {
                    return this.tasks.filter(task => (
                        task.module_id === moduleId &&
                        task.status !== 'gotowe' &&
                        (this.normalizePriorityValue(task.priority) === 'P1' || this.isTaskOverdue(task) || this.isTaskDueToday(task))
                    )).length;
                },

                getModulesSortedByWorkload() {
                    return [...this.modules].sort((a, b) => {
                        const muteDiff = Number(this.isModuleMuted(a.id)) - Number(this.isModuleMuted(b.id));
                        if (muteDiff !== 0) return muteDiff;

                        const urgentDiff = this.getModuleUrgentCount(b.id) - this.getModuleUrgentCount(a.id);
                        if (urgentDiff !== 0) return urgentDiff;

                        const openDiff = this.getModuleOpenCount(b.id) - this.getModuleOpenCount(a.id);
                        if (openDiff !== 0) return openDiff;

                        const orderDiff = this.getModuleOrderIndex(a.id) - this.getModuleOrderIndex(b.id);
                        if (orderDiff !== 0) return orderDiff;

                        return a.name.localeCompare(b.name, 'pl');
                    });
                },

                priorityRank(priority) {
                    return { P1: 0, P2: 1, P3: 2 }[priority] ?? 4;
                },

                statusRank(status) {
                    return { todo: 0, przygotowanie: 1, oczekujace: 3, gotowe: 9 }[this.normalizeTaskStatus(status)] ?? 8;
                },

                daysUntilDue(task) {
                    if (!task?.due_date) return null;
                    const due = this.keyToDate(task.due_date);
                    const today = this.keyToDate(this.getTodayKey());
                    return Math.round((due - today) / 86400000);
                },

                isTaskOverdue(task) {
                    const days = this.daysUntilDue(task);
                    return days !== null && days < 0;
                },

                isTaskDueToday(task) {
                    return this.daysUntilDue(task) === 0;
                },

                isTaskUpcoming(task) {
                    const days = this.daysUntilDue(task);
                    return days !== null && days > 0 && days <= 7;
                },

                dueSortValue(task) {
                    const days = this.daysUntilDue(task);
                    if (days === null) return 999;
                    if (days < 0) return -100 + days;
                    return days;
                },

                sortTasksForFocus(tasks) {
                    return [...tasks].sort((a, b) => {
                        const overdueDiff = (this.isTaskOverdue(a) ? 0 : 1) - (this.isTaskOverdue(b) ? 0 : 1);
                        if (overdueDiff !== 0) return overdueDiff;

                        const todayDiff = (this.isTaskDueToday(a) ? 0 : 1) - (this.isTaskDueToday(b) ? 0 : 1);
                        if (todayDiff !== 0) return todayDiff;

                        const priorityDiff = this.priorityRank(a.priority) - this.priorityRank(b.priority);
                        if (priorityDiff !== 0) return priorityDiff;

                        const statusDiff = this.statusRank(a.status) - this.statusRank(b.status);
                        if (statusDiff !== 0) return statusDiff;

                        const dueDiff = this.dueSortValue(a) - this.dueSortValue(b);
                        if (dueDiff !== 0) return dueDiff;

                        const timeDiff = (a.estimated_time || 999) - (b.estimated_time || 999);
                        if (timeDiff !== 0) return timeDiff;

                        return a.name.localeCompare(b.name, 'pl');
                    });
                },

                getRecommendedTasks(limit = 4) {
                    return this.sortTasksForFocus(this.getOpenTasks()).slice(0, limit);
                },

                getFocusTask() {
                    const inProgress = this.sortTasksForFocus(this.getOpenTasks().filter(task => task.status === 'todo'));
                    if (inProgress.length > 0) return inProgress[0];
                    return this.getRecommendedTasks(1)[0] || null;
                },

                getUrgentTasks(limit = 5) {
                    const urgent = this.sortTasksForFocus(
                        this.getOpenTasks().filter(task => (
                            this.isTaskOverdue(task) ||
                            this.isTaskDueToday(task) ||
                            this.normalizePriorityValue(task.priority) === 'P1'
                        ))
                    );
                    return (urgent.length > 0 ? urgent : this.getRecommendedTasks(limit)).slice(0, limit);
                },

                getModulePreviewTasks(moduleId, limit = 3) {
                    return this.sortTasksForFocus(
                        this.getOpenTasks().filter(task => task.module_id === moduleId)
                    ).slice(0, limit);
                },

                getOverdueTasks(limit = null) {
                    const tasks = this.sortTasksForFocus(this.getOpenTasks().filter(task => this.isTaskOverdue(task)));
                    return limit ? tasks.slice(0, limit) : tasks;
                },

                getTodayTasks(limit = null) {
                    const tasks = this.sortTasksForFocus(this.getOpenTasks().filter(task => this.isTaskDueToday(task)));
                    return limit ? tasks.slice(0, limit) : tasks;
                },

                getUpcomingTasks(limit = null) {
                    const tasks = this.sortTasksForFocus(this.getOpenTasks().filter(task => this.isTaskUpcoming(task)));
                    return limit ? tasks.slice(0, limit) : tasks;
                },

                getPlanSlotLabel(index) {
                    return ['Teraz', 'Potem', 'Lekki finisz'][index] || `Krok ${index + 1}`;
                },

                getTopBarGuidance() {
                    return '';
                },

                shortenText(text, max = 36) {
                    if (!text) return '';
                    return text.length > max ? `${text.slice(0, max).trimEnd()}...` : text;
                },

                getFocusButtonLabel() {
                    const task = this.getFocusTask();
                    if (!task) return 'Brak zadania';
                    return `Teraz: ${this.shortenText(task.name, 34)}`;
                },

                jumpToFocusTask() {
                    const task = this.getFocusTask();
                    if (!task) return;
                    this.kickTaskOff(task);
                },

                getFocusCoach(task) {
                    if (!task) return '';
                    const moduleName = this.getModuleName(task.module_id);
                    if (task.status === 'todo') {
                        return `To masz juz napoczete w module "${moduleName}". Najlatwiej odzyskac momentum, domykajac wlasnie to.`;
                    }
                    if (this.isTaskOverdue(task)) {
                        return `To zadanie zaczelo juz wisiec za dlugo. Zdejmij z glowy najbardziej ciezacy temat z modulu "${moduleName}".`;
                    }
                    if (this.normalizePriorityValue(task.priority) === 'P1') {
                        return `Najwiekszy spokoj da Ci ruszenie tego teraz. To najmocniejszy kandydat do startu w module "${moduleName}".`;
                    }
                    return `To jest najczytelniejszy kolejny krok w module "${moduleName}" - sensowny i gotowy do ruszenia bez duzego rozpedu.`;
                },

                hasPriority(task) {
                    return ['P1', 'P2', 'P3'].includes(this.normalizePriorityValue(task?.priority));
                },

                getPriorityDotClass(priority) {
                    const normalized = this.normalizePriorityValue(priority);
                    return {
                        P1: 'bg-red-500',
                        P2: 'bg-amber-500',
                        P3: 'bg-blue-500'
                    }[normalized] || 'bg-slate-300';
                },

                getPriorityLabel(priority) {
                    const normalized = this.normalizePriorityValue(priority);
                    return {
                        P1: 'P1 pilne',
                        P2: 'P2 normalne',
                        P3: 'P3 spokojne'
                    }[normalized] || 'Bez priorytetu';
                },

                getPriorityBadgeClass(priority) {
                    const normalized = this.normalizePriorityValue(priority);
                    return {
                        P1: 'bg-red-50 text-red-600',
                        P2: 'bg-amber-50 text-amber-700',
                        P3: 'bg-blue-50 text-blue-700'
                    }[normalized] || 'bg-slate-100 text-slate-500';
                },

                getStatusLabel(status) {
                    return {
                        oczekujace: 'oczekuje',
                        przygotowanie: 'przygotowanie',
                        todo: 'w toku',
                        gotowe: 'gotowe'
                    }[this.normalizeTaskStatus(status)] || status;
                },

                getTaskTimeLabel(task) {
                    return task?.estimated_time > 0 ? `${task.estimated_time} min` : 'bez czasu';
                },

                getTaskUrgencyLabel(task) {
                    const days = this.daysUntilDue(task);
                    if (days === null) return this.hasPriority(task) ? 'priorytet' : '';
                    if (days < 0) return `${Math.abs(days)} d. po terminie`;
                    if (days === 0) return 'na dzis';
                    if (days === 1) return 'jutro';
                    if (days <= 7) return `za ${days} dni`;
                    return 'zaplanowane';
                },

                getUrgencyClass(task) {
                    const days = this.daysUntilDue(task);
                    if (days !== null && days < 0) return 'bg-red-50 text-red-600';
                    if (days === 0) return 'bg-amber-50 text-amber-700';
                    if (this.normalizePriorityValue(task?.priority) === 'P1') return 'bg-rose-50 text-rose-600';
                    if (days !== null && days <= 7) return 'bg-cyan-50 text-cyan-700';
                    return 'bg-slate-100 text-slate-500';
                },

                formatDueDate(task) {
                    const days = this.daysUntilDue(task);
                    if (days === null) return '';
                    if (days === 0) return 'dzisiaj';
                    if (days === 1) return 'jutro';
                    if (days < 0) return `${Math.abs(days)} dni temu`;
                    return new Intl.DateTimeFormat('pl-PL', { day: 'numeric', month: 'short' }).format(this.keyToDate(task.due_date));
                },

                setDailyGoalPrompt() {
                    const value = prompt('Dzienny cel (liczba zadan):', String(this.dailyGoal));
                    if (value === null) return;
                    const next = Number(value);
                    if (!Number.isFinite(next) || next <= 0) {
                        alert('Podaj liczbe wieksza od 0.');
                        return;
                    }
                    this.dailyGoal = Math.round(next);
                    this.saveUIPreferences();
                },

                shiftDateKey(dateKey, offsetDays) {
                    const date = this.keyToDate(dateKey);
                    date.setDate(date.getDate() + offsetDays);
                    return this.dateToKey(date);
                },

                getDoneCountByDate(dateKey) {
                    const stamp = `[Done: ${dateKey}]`;
                    return this.tasks.filter(task => task.status === 'gotowe' && (task.description || '').includes(stamp)).length;
                },

                getTodayDoneCount() {
                    return this.getDoneCountByDate(this.getTodayKey());
                },

                getYesterdayDoneCount() {
                    const yesterday = this.shiftDateKey(this.getTodayKey(), -1);
                    return this.getDoneCountByDate(yesterday);
                },

                getSevenDayAverage() {
                    const today = this.getTodayKey();
                    let total = 0;
                    for (let offset = 0; offset < 7; offset++) {
                        total += this.getDoneCountByDate(this.shiftDateKey(today, -offset));
                    }
                    return Number((total / 7).toFixed(1));
                },

                getDailyProgressPercent() {
                    if (this.dailyGoal <= 0) return 0;
                    return Math.min(100, Math.round((this.getTodayDoneCount() / this.dailyGoal) * 100));
                },

                getDailyRewardLabel() {
                    const done = this.getTodayDoneCount();
                    if (done <= 0) return 'Pierwszy ruch odpala dzien';
                    if (done >= this.dailyGoal) return 'Cel dnia zamkniety';
                    const left = Math.max(0, this.dailyGoal - done);
                    return left === 1 ? 'Jeszcze 1 i cel siada' : `Jeszcze ${left} do celu`;
                },

                getWeeklyDoneTotal() {
                    const today = this.shiftDateKey(this.getTodayKey(), this.dopamineWeekOffset * 7);
                    let total = 0;
                    for (let offset = 0; offset < 7; offset++) {
                        total += this.getDoneCountByDate(this.shiftDateKey(today, -offset));
                    }
                    return total;
                },

                getWeeklyGoalDots() {
                    const realToday = this.getTodayKey();
                    const today = this.shiftDateKey(realToday, this.dopamineWeekOffset * 7);
                    const dots = [];
                    for (let offset = 6; offset >= 0; offset--) {
                        const dateKey = this.shiftDateKey(today, -offset);
                        const done = this.getDoneCountByDate(dateKey);
                        const ratio = this.dailyGoal > 0 ? Math.min(1, done / this.dailyGoal) : 0;
                        const percent = Math.round(ratio * 100);
                        const date = this.keyToDate(dateKey);
                        dots.push({
                            dateKey,
                            done,
                            ratio,
                            percent,
                            isToday: dateKey === realToday,
                            weekday: new Intl.DateTimeFormat('pl-PL', { weekday: 'short' }).format(date),
                            dayNumber: date.getDate()
                        });
                    }
                    return dots;
                },

                shiftDopamineWeek(step) {
                    this.dopamineWeekOffset += step;
                    this.saveUIPreferences();
                },

                resetDopamineWeek() {
                    this.dopamineWeekOffset = 0;
                    this.saveUIPreferences();
                },

                getDopamineWeekLabel() {
                    if (this.dopamineWeekOffset === 0) return 'ten tydzien';
                    if (this.dopamineWeekOffset === -1) return 'poprzedni tydzien';
                    if (this.dopamineWeekOffset === 1) return 'nastepny tydzien';
                    return this.dopamineWeekOffset < 0
                        ? `${Math.abs(this.dopamineWeekOffset)} tyg. temu`
                        : `za ${this.dopamineWeekOffset} tyg.`;
                },

                getDopamineDotClass(done) {
                    if (done >= this.dailyGoal) return 'dopamine-dot-full';
                    if (done >= Math.max(1, Math.ceil(this.dailyGoal * 0.6))) return 'dopamine-dot-good';
                    if (done > 0) return 'dopamine-dot-low';
                    return 'dopamine-dot-empty';
                },

                getDopamineDotStyle(day) {
                    const percent = Math.max(0, Math.min(100, Number(day?.percent || 0)));
                    return `--dopamine-progress: ${percent};`;
                },

                getGoalDotRingClass(percent) {
                    if (percent >= 100) return 'kpi-ring-full';
                    if (percent >= 60) return 'kpi-ring-good';
                    if (percent > 0) return 'kpi-ring-low';
                    return 'kpi-ring-empty';
                },

                getModuleNote(moduleId) {
                    return this.moduleNotes[moduleId] || '';
                },

                setModuleNote(moduleId, value) {
                    this.moduleNotes = {
                        ...this.moduleNotes,
                        [moduleId]: value
                    };
                    this.saveModuleNote(moduleId);
                },

                saveModuleNote(moduleId) {
                    if (!moduleId) return;
                    clearTimeout(this.moduleNoteTimers[moduleId]);
                    this.moduleNoteTimers[moduleId] = setTimeout(async () => {
                        try {
                            await fetch(`${this.API}/notes/module-${moduleId}`, {
                                method: 'PUT',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ content: this.moduleNotes[moduleId] || '' })
                            });
                        } catch (error) {
                            /* keep local text if saving fails */
                        }
                    }, 450);
                },

                getTaskDescriptionPreview(task, maxWords = 8) {
                    const description = (task?.description || '')
                        .replace(/\[Done:\s*\d{4}-\d{2}-\d{2}\]/g, '')
                        .replace(/\s+/g, ' ')
                        .trim();
                    if (!description) return '';
                    const words = description.split(' ');
                    if (words.length <= maxWords) return description;
                    return `${words.slice(0, maxWords).join(' ')}...`;
                },

                getBrainDumpPreview() {
                    const trimmed = (this.brainDump || '').trim();
                    if (!trimmed) {
                        return 'Brain dump jest pusty. To dobre miejsce na wrzucenie wszystkiego, co blokuje skupienie.';
                    }
                    const lines = trimmed.split('\n').map(line => line.trim()).filter(Boolean);
                    if (lines.length === 1) return lines[0];
                    return `${lines.slice(0, 3).join(' • ')}${lines.length > 3 ? ' ...' : ''}`;
                },

                countBrainDumpLines() {
                    return (this.brainDump || '').split('\n').map(line => line.trim()).filter(Boolean).length;
                },

                taskMatchesPriority(task) {
                    return this.priorityFilter === 'ALL' || this.normalizePriorityValue(task.priority) === this.priorityFilter;
                },

                taskMatchesFocusFilter(task) {
                    if (this.focusFilter === 'all') return true;
                    return (
                        task.status === 'todo' ||
                        this.normalizePriorityValue(task.priority) === 'P1' ||
                        this.isTaskDueToday(task) ||
                        this.isTaskOverdue(task)
                    );
                },

                isTaskInScope(task) {
                    if (this.taskScope !== 'module') return true;
                    if (!this.activeModule) return true;
                    return task.module_id === this.activeModule.id;
                },

                getScopeLabel() {
                    if (this.taskScope === 'all') return 'Wszystkie zadania';
                    return this.activeModule ? this.activeModule.name : 'Modul';
                },

                getScopedTasks() {
                    return this.tasks.filter(task => (
                        this.isTaskInScope(task) &&
                        this.taskMatchesPriority(task) &&
                        this.taskMatchesFocusFilter(task)
                    ));
                },

                getDisplayTaskGroups(status) {
                    const tasks = this.getFilteredAndSortedTasks(status);
                    if (this.taskScope === 'module' && this.activeModule) {
                        return [{
                            moduleId: this.activeModule ? this.activeModule.id : 0,
                            moduleName: this.activeModule ? this.activeModule.name : 'Modul',
                            tasks
                        }];
                    }

                    const grouped = new Map();
                    for (const task of tasks) {
                        if (!grouped.has(task.module_id)) {
                            grouped.set(task.module_id, {
                                moduleId: task.module_id,
                                moduleName: this.getModuleName(task.module_id),
                                tasks: []
                            });
                        }
                        grouped.get(task.module_id).tasks.push(task);
                    }

                    return [...grouped.values()].sort((a, b) => {
                        const orderDiff = this.getModuleOrderIndex(a.moduleId) - this.getModuleOrderIndex(b.moduleId);
                        if (orderDiff !== 0) return orderDiff;
                        return a.moduleName.localeCompare(b.moduleName, 'pl');
                    });
                },

                getFilteredAndSortedTasks(status) {
                    let filtered = this.tasks.filter(task => (
                        task.status === status &&
                        this.isTaskInScope(task) &&
                        this.taskMatchesPriority(task) &&
                        this.taskMatchesFocusFilter(task)
                    ));

                    if (status === 'oczekujace' && this.sortOrder !== 'none') {
                        filtered = [...filtered].sort((a, b) => {
                            return this.sortOrder === 'asc'
                                ? (a.estimated_time || 0) - (b.estimated_time || 0)
                                : (b.estimated_time || 0) - (a.estimated_time || 0);
                        });
                    } else {
                        filtered = this.sortTasksForFocus(filtered);
                    }

                    return filtered;
                },

                getFilteredTaskCountForModule() {
                    return this.columnsMeta
                        .filter(column => column.id !== 'gotowe')
                        .reduce((total, column) => total + this.getFilteredAndSortedTasks(column.id).length, 0);
                },

                getFilteredPriorityCountForModule(priority) {
                    return this.tasks.filter(task => (
                        task.status !== 'gotowe' &&
                        this.isTaskInScope(task) &&
                        this.normalizePriorityValue(task.priority) === priority &&
                        this.taskMatchesFocusFilter(task)
                    )).length;
                },

                getModuleTasksByStatus(moduleId, status) {
                    return this.sortTasksForFocus(
                        this.tasks.filter(task => (
                            task.module_id === moduleId &&
                            task.status === status &&
                            this.taskMatchesPriority(task) &&
                            this.taskMatchesFocusFilter(task)
                        ))
                    );
                },

                getModuleVisibleCount(moduleId) {
                    return this.tasks.filter(task => (
                        task.module_id === moduleId &&
                        this.taskMatchesPriority(task) &&
                        this.taskMatchesFocusFilter(task)
                    )).length;
                },

                getGlobalModules() {
                    const categoryRank = { praca: 0, prywatne: 1 };
                    return this.sortModulesByManualOrder(this.modules).sort((a, b) => {
                        const muteDiff = Number(this.isModuleMuted(a.id)) - Number(this.isModuleMuted(b.id));
                        if (muteDiff !== 0) return muteDiff;

                        const catDiff =
                            (categoryRank[this.normalizeModuleCategory(a.category)] ?? 0) -
                            (categoryRank[this.normalizeModuleCategory(b.category)] ?? 0);
                        if (catDiff !== 0) return catDiff;

                        const orderDiff = this.getModuleOrderIndex(a.id) - this.getModuleOrderIndex(b.id);
                        if (orderDiff !== 0) return orderDiff;
                        return a.name.localeCompare(b.name, 'pl');
                    });
                },

                toggleGlobalLane(moduleId) {
                    this.globalLaneCollapsed[moduleId] = !this.globalLaneCollapsed[moduleId];
                    this.saveUIPreferences();
                },

                isGlobalLaneCollapsed(moduleId) {
                    return !!this.globalLaneCollapsed[moduleId];
                },

                getTaskById(taskId) {
                    return this.tasks.find(task => task.id === taskId) || null;
                },

                buildDoneDescription(description = '') {
                    const stamp = `[Done: ${this.getTodayKey()}]`;
                    if ((description || '').includes(stamp)) return description || stamp;
                    const clean = (description || '').trimEnd();
                    return clean ? `${clean}\n${stamp}` : stamp;
                },

                pickTaskPayload(task) {
                    return {
                        name: task.name,
                        module_id: Number(task.module_id) || 0,
                        priority: this.normalizePriorityValue(task.priority),
                        description: task.description || '',
                        due_date: this.sanitizeDateKey(task.due_date),
                        estimated_time: Math.max(0, Number(task.estimated_time) || 0),
                        status: this.normalizeTaskStatus(task.status)
                    };
                },

                async patchTask(taskId, payload) {
                    await fetch(`${this.API}/tasks/${taskId}`, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });
                },

                async changeTaskStatus(task, nextStatus) {
                    if (!task) return;
                    const payload = { status: nextStatus };
                    if (nextStatus === 'gotowe') {
                        payload.description = this.buildDoneDescription(task.description);
                    }
                    await this.patchTask(task.id, payload);
                    await this.init();
                },

                openModule(module) {
                    this.activeModule = module;
                    this.setTaskScope('module');
                    this.view = 'kanban';
                },

                goToTask(task) {
                    if (!task) return;
                    const module = this.modules.find(item => item.id === task.module_id);
                    if (module) {
                        this.activeModule = module;
                        this.setTaskScope('module');
                    }
                    this.view = 'kanban';
                    this.openTaskModal(task);
                },

                async kickTaskOff(task) {
                    if (!task) return;
                    let currentTask = task;
                    if (task.status !== 'todo') {
                        await this.changeTaskStatus(task, 'todo');
                        currentTask = this.getTaskById(task.id) || { ...task, status: 'todo' };
                    }
                    this.goToTask(currentTask);
                },

                async deleteTask(taskId) {
                    if (!confirm('Na pewno usunac to zadanie?')) return false;
                    await fetch(`${this.API}/tasks/${taskId}`, { method: 'DELETE' });
                    await this.init();
                    return true;
                },

                async deleteModule(module) {
                    if (!module) return false;
                    const taskCount = this.tasks.filter(task => task.module_id === module.id).length;
                    const suffix = taskCount === 1 ? 'zadanie' : (taskCount >= 2 && taskCount <= 4 ? 'zadania' : 'zadan');
                    if (!confirm(`Usunac modul "${module.name}" razem z ${taskCount} ${suffix}?`)) return false;

                    const response = await fetch(`${this.API}/modules/${module.id}`, { method: 'DELETE' });
                    if (!response.ok) {
                        alert('Nie udalo sie usunac modulu.');
                        return false;
                    }

                    if (this.activeModule?.id === module.id) {
                        this.activeModule = null;
                        this.setTaskScope('all');
                    }

                    await this.init();
                    if (!this.activeModule && this.modules.length > 0) {
                        this.activeModule = this.getSidebarModules()[0] || this.modules[0];
                    }
                    return true;
                },

                async quickMove(task, direction) {
                    const columns = this.columnsMeta.map(column => column.id);
                    const nextIndex = columns.indexOf(task.status) + direction;
                    if (nextIndex < 0 || nextIndex >= columns.length) return;
                    await this.changeTaskStatus(task, columns[nextIndex]);
                },

                startTaskDrag(task, event) {
                    if (!task) return;
                    this.draggedTaskId = task.id;
                    if (event?.dataTransfer) {
                        event.dataTransfer.effectAllowed = 'move';
                        event.dataTransfer.setData('text/plain', String(task.id));
                    }
                },

                endTaskDrag() {
                    this.draggedTaskId = null;
                },

                async dropTaskToColumn(status) {
                    if (!this.draggedTaskId) return;
                    const task = this.getTaskById(this.draggedTaskId);
                    this.draggedTaskId = null;
                    if (!task || task.status === status) return;
                    await this.changeTaskStatus(task, status);
                },

                handleKeydown(event) {
                    const targetTag = event?.target?.tagName?.toLowerCase();
                    const isTypingField = ['input', 'textarea', 'select'].includes(targetTag) || event?.target?.isContentEditable;
                    if (this.view === 'canvas' && event.key === 'Escape') {
                        this.clearCanvasSelection();
                        return;
                    }

                    if (isTypingField) return;

                    if (this.view === 'canvas' && (event.key === 'Delete' || event.key === 'Backspace')) {
                        if (this.selectedCanvasLinkId) {
                            event.preventDefault();
                            this.deleteCanvasLink(this.selectedCanvasLinkId);
                            return;
                        }
                        if (this.selectedCanvasNodeId) {
                            event.preventDefault();
                            this.deleteCanvasNode(this.selectedCanvasNodeId);
                            return;
                        }
                    }

                    if (this.view === 'canvas' && (event.key === 'd' || event.key === 'D') && (event.metaKey || event.ctrlKey)) {
                        if (!this.selectedCanvasNodeId) return;
                        event.preventDefault();
                        this.duplicateCanvasNode(this.selectedCanvasNodeId);
                        return;
                    }

                    if ((event.key === 'f' || event.key === 'F') && event.altKey) {
                        event.preventDefault();
                        this.startFlow();
                    }
                },

                openNewTaskModal(preferredModuleId = null) {
                    const fallbackModule = this.activeModule || this.getSidebarModules()[0];
                    const targetModuleId = Number(preferredModuleId || fallbackModule?.id || 0);
                    if (!targetModuleId) {
                        alert('Najpierw dodaj modul.');
                        return;
                    }

                    this.isCreatingTask = true;
                    this.editingTask = {
                        id: null,
                        name: '',
                        module_id: targetModuleId,
                        description: '',
                        due_date: '',
                        estimated_time: 0,
                        priority: '',
                        status: 'oczekujace'
                    };
                    this.taskModal = true;
                },

                openTaskModal(task) {
                    this.isCreatingTask = false;
                    this.editingTask = {
                        description: '',
                        due_date: '',
                        estimated_time: 0,
                        priority: '',
                        status: 'oczekujace',
                        ...task,
                        status: this.normalizeTaskStatus(task?.status),
                        priority: this.normalizePriorityValue(task?.priority)
                    };
                    this.taskModal = true;
                },

                async saveTask() {
                    const pickedDueDate = this.$refs?.taskDueDateInput?.value || this.editingTask.due_date;
                    this.editingTask.due_date = this.sanitizeDateKey(pickedDueDate);
                    const payload = this.pickTaskPayload(this.editingTask);
                    payload.name = (payload.name || '').trim();
                    if (!payload.name) {
                        alert('Podaj nazwe zadania.');
                        return;
                    }

                    if (!payload.module_id) {
                        alert('Wybierz modul.');
                        return;
                    }

                    if (payload.status === 'gotowe') {
                        payload.description = this.buildDoneDescription(payload.description);
                    }

                    if (this.isCreatingTask || !this.editingTask.id) {
                        await fetch(`${this.API}/tasks`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(payload)
                        });
                    } else {
                        await this.patchTask(this.editingTask.id, payload);
                    }

                    this.taskModal = false;
                    this.isCreatingTask = false;
                    await this.init();
                },

                async removeEditingTask() {
                    if (!this.editingTask.id) {
                        this.taskModal = false;
                        this.isCreatingTask = false;
                        return;
                    }
                    const deleted = await this.deleteTask(this.editingTask.id);
                    if (deleted) {
                        this.taskModal = false;
                        this.isCreatingTask = false;
                    }
                },

                async addModulePrompt(categoryHint = '') {
                    const name = prompt('Nazwa modulu:');
                    if (!name) return;
                    const cleanName = name.trim();
                    if (!cleanName) return;
                    const category = this.normalizeModuleCategory(categoryHint || 'praca');
                    await fetch(`${this.API}/modules`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            name: cleanName,
                            category
                        })
                    });
                    await this.init();
                },

                async saveBrainDump(quiet = false) {
                    clearTimeout(this.brainDumpSaveTimer);
                    try {
                        const response = await fetch(`${this.API}/notes/brain-dump`, {
                            method: 'PUT',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ content: this.brainDump })
                        });
                        if (!response.ok) throw new Error('note_save_failed');
                        const payload = await response.json();
                        this.noteSavedAt = payload.updated_at || new Date().toISOString();
                        try {
                            localStorage.removeItem(this.brainDumpStorageKey);
                        } catch (error) {
                            /* ignore storage cleanup errors */
                        }
                        return true;
                    } catch (error) {
                        try {
                            localStorage.setItem(this.brainDumpStorageKey, this.brainDump || '');
                        } catch (writeError) {
                            /* ignore storage write errors */
                        }
                        if (!quiet) {
                            alert('Nie udalo sie zapisac notatki na serwerze. Zostala zabezpieczona lokalnie.');
                        }
                        return false;
                    }
                },

                async saveBrainDumpQuiet() {
                    await this.saveBrainDump(true);
                },

                handleBrainDumpInput() {
                    try {
                        localStorage.setItem(this.brainDumpStorageKey, this.brainDump || '');
                    } catch (error) {
                        /* ignore storage write errors */
                    }
                    clearTimeout(this.brainDumpSaveTimer);
                    this.brainDumpSaveTimer = setTimeout(() => {
                        this.saveBrainDumpQuiet();
                    }, 700);
                },

                async sendBrainDumpToModule() {
                    if (!this.brainDumpTargetModuleId) {
                        alert('Najpierw wybierz modul.');
                        return;
                    }

                    const lines = (this.brainDump || '').split('\n').map(line => line.trim()).filter(Boolean);
                    if (lines.length === 0) {
                        alert('Brain dump jest pusty.');
                        return;
                    }

                    if (!confirm(`Stworzyc ${lines.length} zadan z brain dump?`)) return;

                    for (const line of lines) {
                        await fetch(`${this.API}/tasks`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                name: line,
                                module_id: Number(this.brainDumpTargetModuleId),
                                estimated_time: 15,
                                priority: ''
                            })
                        });
                    }

                    this.brainDump = '';
                    await this.saveBrainDump();
                    await this.init();

                    const module = this.modules.find(item => item.id === Number(this.brainDumpTargetModuleId));
                    if (module) this.activeModule = module;
                    this.view = module ? 'kanban' : 'dash';
                },

                clampCanvasValue(value, min, max) {
                    return Math.min(max, Math.max(min, value));
                },

                makeCanvasItemId(prefix = 'node') {
                    return `${prefix}-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
                },

                getCanvasShapeBounds(shape = 'rect') {
                    if (shape === 'circle') {
                        return { minWidth: 130, maxWidth: 320, minHeight: 130, maxHeight: 320, defaultWidth: 190, defaultHeight: 190, square: true };
                    }
                    if (shape === 'diamond') {
                        return { minWidth: 180, maxWidth: 420, minHeight: 180, maxHeight: 420, defaultWidth: 220, defaultHeight: 220, square: true };
                    }
                    if (shape === 'text') {
                        return { minWidth: 180, maxWidth: 560, minHeight: 110, maxHeight: 440, defaultWidth: 320, defaultHeight: 170, square: false };
                    }
                    return { minWidth: 160, maxWidth: 560, minHeight: 110, maxHeight: 440, defaultWidth: 260, defaultHeight: 170, square: false };
                },

                coerceCanvasDimensions(shape, width, height) {
                    const bounds = this.getCanvasShapeBounds(shape);
                    let nextWidth = this.clampCanvasValue(Number(width) || bounds.defaultWidth, bounds.minWidth, bounds.maxWidth);
                    let nextHeight = this.clampCanvasValue(Number(height) || bounds.defaultHeight, bounds.minHeight, bounds.maxHeight);
                    if (bounds.square) {
                        const squareSize = this.clampCanvasValue(Math.max(nextWidth, nextHeight), bounds.minWidth, bounds.maxWidth);
                        nextWidth = squareSize;
                        nextHeight = squareSize;
                    }
                    return { width: Math.round(nextWidth), height: Math.round(nextHeight) };
                },

                getCanvasColorMeta(colorId) {
                    return this.canvasColorOptions.find(color => color.id === colorId) || this.canvasColorOptions[0];
                },

                getCanvasShapeLabel(shape) {
                    return this.canvasShapeOptions.find(option => option.id === shape)?.label || 'Prostokat';
                },

                getCanvasShapeSymbol(shape) {
                    return {
                        text: 'T',
                        rect: '▭',
                        diamond: '◇',
                        circle: '○'
                    }[shape || 'rect'] || '▭';
                },

                normalizeCanvasNode(node, index, usedIds) {
                    if (!node || typeof node !== 'object') return null;
                    const allowedShapes = this.canvasShapeOptions.map(shape => shape.id);
                    const shape = allowedShapes.includes(node.shape) ? node.shape : 'rect';
                    const bounds = this.getCanvasShapeBounds(shape);
                    const dimensions = this.coerceCanvasDimensions(shape, node.width ?? bounds.defaultWidth, node.height ?? bounds.defaultHeight);
                    const normalizedColor = node.color === 'white' ? 'slate' : node.color;
                    const color = this.canvasColorOptions.some(option => option.id === normalizedColor) ? normalizedColor : 'slate';

                    let id = node.id === 0 || node.id ? String(node.id) : this.makeCanvasItemId('node');
                    while (usedIds.has(id)) {
                        id = this.makeCanvasItemId('node');
                    }
                    usedIds.add(id);

                    const maxX = Math.max(0, this.canvasBoardWidth - dimensions.width - 10);
                    const maxY = Math.max(0, this.canvasBoardHeight - dimensions.height - 10);
                    const x = this.clampCanvasValue(Number(node.x) || 60, 0, maxX);
                    const y = this.clampCanvasValue(Number(node.y) || 60, 0, maxY);
                    const z = Number.isFinite(Number(node.z)) ? Number(node.z) : (index + 1);

                    return {
                        id,
                        shape,
                        color,
                        text: typeof node.text === 'string' ? node.text : '',
                        x,
                        y,
                        width: dimensions.width,
                        height: dimensions.height,
                        z
                    };
                },

                normalizeCanvasLink(link, validNodeIds, usedLinks) {
                    if (!link || typeof link !== 'object') return null;
                    const fromId = link.fromId === 0 || link.fromId ? String(link.fromId) : '';
                    const toId = link.toId === 0 || link.toId ? String(link.toId) : '';
                    if (!fromId || !toId || fromId === toId || !validNodeIds.has(fromId) || !validNodeIds.has(toId)) return null;

                    const key = `${fromId}->${toId}`;
                    if (usedLinks.has(key)) return null;
                    usedLinks.add(key);

                    const color = this.canvasColorOptions.some(option => option.id === link.color) ? link.color : 'slate';
                    return {
                        id: link.id === 0 || link.id ? String(link.id) : this.makeCanvasItemId('link'),
                        fromId,
                        toId,
                        color
                    };
                },

                normalizeCanvasBoard(payload) {
                    const board = payload && typeof payload === 'object' ? payload : {};
                    const rawNodes = Array.isArray(payload) ? payload : (Array.isArray(board.nodes) ? board.nodes : []);
                    const usedIds = new Set();
                    const nodes = rawNodes
                        .map((node, index) => this.normalizeCanvasNode(node, index, usedIds))
                        .filter(Boolean)
                        .sort((a, b) => (Number(a.z) || 0) - (Number(b.z) || 0))
                        .map((node, index) => ({ ...node, z: index + 1 }));

                    const validNodeIds = new Set(nodes.map(node => node.id));
                    const usedLinks = new Set();
                    const rawLinks = Array.isArray(payload) ? [] : (Array.isArray(board.links) ? board.links : []);
                    const links = rawLinks
                        .map(link => this.normalizeCanvasLink(link, validNodeIds, usedLinks))
                        .filter(Boolean);

                    return {
                        nodes,
                        links,
                        gridVisible: typeof board.gridVisible === 'boolean' ? board.gridVisible : true,
                        snapToGrid: typeof board.snapToGrid === 'boolean' ? board.snapToGrid : false
                    };
                },

                getCanvasNodeById(nodeId) {
                    if (nodeId === null || nodeId === undefined) return null;
                    const id = String(nodeId);
                    return this.canvasNodes.find(node => node.id === id) || null;
                },

                getCanvasNodesSorted() {
                    return [...this.canvasNodes].sort((a, b) => (Number(a.z) || 0) - (Number(b.z) || 0));
                },

                getCanvasNodeStyle(node) {
                    const color = this.getCanvasColorMeta(node?.color);
                    const shape = node?.shape || 'rect';
                    const dimensions = this.coerceCanvasDimensions(shape, node?.width, node?.height);
                    const maxX = Math.max(0, this.canvasBoardWidth - dimensions.width - 10);
                    const maxY = Math.max(0, this.canvasBoardHeight - dimensions.height - 10);
                    const x = this.clampCanvasValue(Number(node?.x) || 0, 0, maxX);
                    const y = this.clampCanvasValue(Number(node?.y) || 0, 0, maxY);
                    const z = Number.isFinite(Number(node?.z)) ? Number(node.z) : 1;
                    return `left:${x}px;top:${y}px;width:${dimensions.width}px;height:${dimensions.height}px;z-index:${z};--canvas-node-bg:${color.bg};--canvas-node-border:${color.border};--canvas-node-text:${color.text};`;
                },

                getCanvasNodeClass(node) {
                    const shape = node?.shape || 'rect';
                    return `canvas-node-${shape}`;
                },

                getCanvasNodeShortLabel(node) {
                    if (!node) return 'Element';
                    const firstLine = (node.text || '').split('\n').map(line => line.trim()).find(Boolean);
                    if (firstLine) return firstLine.slice(0, 34);
                    return this.getCanvasShapeLabel(node.shape);
                },

                getCanvasLinksLayout() {
                    return this.canvasLinks.map(link => {
                        const fromNode = this.getCanvasNodeById(link.fromId);
                        const toNode = this.getCanvasNodeById(link.toId);
                        if (!fromNode || !toNode) return null;

                        const fromCenterX = Number(fromNode.x) + (Number(fromNode.width) / 2);
                        const fromCenterY = Number(fromNode.y) + (Number(fromNode.height) / 2);
                        const toCenterX = Number(toNode.x) + (Number(toNode.width) / 2);
                        const toCenterY = Number(toNode.y) + (Number(toNode.height) / 2);

                        const dx = toCenterX - fromCenterX;
                        const dy = toCenterY - fromCenterY;
                        const length = Math.max(1, Math.hypot(dx, dy));
                        const offsetFrom = Math.max(22, Math.min(Number(fromNode.width), Number(fromNode.height)) / 2.6);
                        const offsetTo = Math.max(20, Math.min(Number(toNode.width), Number(toNode.height)) / 2.8);

                        const x1 = fromCenterX + ((dx / length) * offsetFrom);
                        const y1 = fromCenterY + ((dy / length) * offsetFrom);
                        const x2 = toCenterX - ((dx / length) * offsetTo);
                        const y2 = toCenterY - ((dy / length) * offsetTo);
                        const color = this.getCanvasColorMeta(link.color).swatch;

                        return { ...link, x1, y1, x2, y2, color };
                    }).filter(Boolean);
                },

                getCanvasNodeLinks(nodeId) {
                    const id = String(nodeId || '');
                    return this.canvasLinks
                        .filter(link => link.fromId === id || link.toId === id)
                        .map(link => {
                            const outbound = link.fromId === id;
                            const otherNode = this.getCanvasNodeById(outbound ? link.toId : link.fromId);
                            return {
                                ...link,
                                outbound,
                                label: this.getCanvasNodeShortLabel(otherNode)
                            };
                        });
                },

                getSelectedCanvasNode() {
                    return this.getCanvasNodeById(this.selectedCanvasNodeId);
                },

                setCanvasNodeShape(nodeId, shape) {
                    if (!this.canvasShapeOptions.some(option => option.id === shape)) return;
                    this.canvasNodes = this.canvasNodes.map(node => {
                        if (node.id !== String(nodeId)) return node;
                        const bounds = this.getCanvasShapeBounds(shape);
                        const dimensions = this.coerceCanvasDimensions(shape, node.width || bounds.defaultWidth, node.height || bounds.defaultHeight);
                        return { ...node, shape, width: dimensions.width, height: dimensions.height };
                    });
                    this.saveCanvasBoard();
                },

                setCanvasNodeWidth(nodeId, width) {
                    this.canvasNodes = this.canvasNodes.map(node => {
                        if (node.id !== String(nodeId)) return node;
                        const dimensions = this.coerceCanvasDimensions(node.shape, width, node.height);
                        return { ...node, width: dimensions.width, height: dimensions.height };
                    });
                    this.saveCanvasBoard();
                },

                setCanvasNodeHeight(nodeId, height) {
                    this.canvasNodes = this.canvasNodes.map(node => {
                        if (node.id !== String(nodeId)) return node;
                        const dimensions = this.coerceCanvasDimensions(node.shape, node.width, height);
                        return { ...node, width: dimensions.width, height: dimensions.height };
                    });
                    this.saveCanvasBoard();
                },

                updateCanvasNodeText(nodeId, value) {
                    this.canvasNodes = this.canvasNodes.map(node => (
                        node.id === String(nodeId) ? { ...node, text: value } : node
                    ));
                    this.saveCanvasBoard();
                },

                setCanvasNodeColor(nodeId, color) {
                    if (!this.canvasColorOptions.some(option => option.id === color)) return;
                    this.canvasNodes = this.canvasNodes.map(node => (
                        node.id === String(nodeId) ? { ...node, color } : node
                    ));
                    this.canvasLinks = this.canvasLinks.map(link => (
                        link.fromId === String(nodeId) ? { ...link, color } : link
                    ));
                    this.saveCanvasBoard();
                },

                addCanvasNode(shape = 'rect') {
                    const allowedShapes = this.canvasShapeOptions.map(option => option.id);
                    const cleanShape = allowedShapes.includes(shape) ? shape : 'rect';
                    const bounds = this.getCanvasShapeBounds(cleanShape);
                    const dimensions = this.coerceCanvasDimensions(cleanShape, bounds.defaultWidth, bounds.defaultHeight);
                    const viewport = this.$refs?.canvasViewport;
                    const baseX = viewport ? (viewport.scrollLeft + (viewport.clientWidth * 0.28)) : 120;
                    const baseY = viewport ? (viewport.scrollTop + (viewport.clientHeight * 0.24)) : 120;
                    const offset = (this.canvasNodes.length * 26) % 220;
                    const maxX = Math.max(0, this.canvasBoardWidth - dimensions.width - 10);
                    const maxY = Math.max(0, this.canvasBoardHeight - dimensions.height - 10);
                    const node = {
                        id: this.makeCanvasItemId('node'),
                        shape: cleanShape,
                        color: cleanShape === 'diamond' ? 'amber' : (cleanShape === 'circle' ? 'sky' : 'slate'),
                        text: cleanShape === 'text' ? 'Nowa notatka' : '',
                        x: this.clampCanvasValue(baseX + offset, 0, maxX),
                        y: this.clampCanvasValue(baseY + offset, 0, maxY),
                        width: dimensions.width,
                        height: dimensions.height,
                        z: this.canvasNodes.reduce((max, item) => Math.max(max, Number(item.z) || 0), 0) + 1
                    };

                    this.canvasNodes = [...this.canvasNodes, node];
                    this.selectedCanvasNodeId = node.id;
                    this.selectedCanvasLinkId = null;
                    this.canvasLinkDraftFromId = null;
                    this.saveCanvasBoard();
                },

                duplicateCanvasNode(nodeId) {
                    const sourceNode = this.getCanvasNodeById(nodeId);
                    if (!sourceNode) return;
                    const maxX = Math.max(0, this.canvasBoardWidth - Number(sourceNode.width) - 10);
                    const maxY = Math.max(0, this.canvasBoardHeight - Number(sourceNode.height) - 10);
                    const duplicated = {
                        ...sourceNode,
                        id: this.makeCanvasItemId('node'),
                        x: this.clampCanvasValue(Number(sourceNode.x) + 36, 0, maxX),
                        y: this.clampCanvasValue(Number(sourceNode.y) + 32, 0, maxY),
                        z: this.canvasNodes.reduce((max, item) => Math.max(max, Number(item.z) || 0), 0) + 1
                    };
                    this.canvasNodes = [...this.canvasNodes, duplicated];
                    this.selectedCanvasNodeId = duplicated.id;
                    this.selectedCanvasLinkId = null;
                    this.saveCanvasBoard();
                },

                deleteCanvasNode(nodeId) {
                    const id = String(nodeId || '');
                    if (!id) return;
                    this.canvasNodes = this.canvasNodes.filter(node => node.id !== id);
                    this.canvasLinks = this.canvasLinks.filter(link => link.fromId !== id && link.toId !== id);
                    if (this.selectedCanvasNodeId === id) this.selectedCanvasNodeId = null;
                    if (this.canvasLinkDraftFromId === id) this.canvasLinkDraftFromId = null;
                    if (this.selectedCanvasLinkId && !this.canvasLinks.some(link => link.id === this.selectedCanvasLinkId)) {
                        this.selectedCanvasLinkId = null;
                    }
                    this.saveCanvasBoard();
                },

                selectCanvasNode(nodeId) {
                    const node = this.getCanvasNodeById(nodeId);
                    if (!node) return;
                    this.selectedCanvasNodeId = node.id;
                    this.selectedCanvasLinkId = null;
                },

                selectCanvasLink(linkId) {
                    if (!linkId) return;
                    this.selectedCanvasLinkId = String(linkId);
                    this.selectedCanvasNodeId = null;
                    this.canvasLinkDraftFromId = null;
                },

                clearCanvasSelection() {
                    this.selectedCanvasNodeId = null;
                    this.selectedCanvasLinkId = null;
                    this.canvasLinkDraftFromId = null;
                },

                toggleCanvasLinkMode() {
                    if (!this.selectedCanvasNodeId) {
                        alert('Najpierw wybierz element, od ktorego chcesz poprowadzic strzalke.');
                        return;
                    }
                    if (this.canvasLinkDraftFromId) {
                        this.canvasLinkDraftFromId = null;
                        return;
                    }
                    this.canvasLinkDraftFromId = this.selectedCanvasNodeId;
                    this.selectedCanvasLinkId = null;
                },

                cancelCanvasLinkMode() {
                    this.canvasLinkDraftFromId = null;
                },

                connectCanvasNodes(fromId, toId) {
                    const sourceId = String(fromId || '');
                    const targetId = String(toId || '');
                    if (!sourceId || !targetId || sourceId === targetId) return false;
                    if (!this.getCanvasNodeById(sourceId) || !this.getCanvasNodeById(targetId)) return false;

                    const duplicateExists = this.canvasLinks.some(link => link.fromId === sourceId && link.toId === targetId);
                    if (duplicateExists) return false;

                    const sourceNode = this.getCanvasNodeById(sourceId);
                    const color = sourceNode?.color || 'slate';
                    const link = {
                        id: this.makeCanvasItemId('link'),
                        fromId: sourceId,
                        toId: targetId,
                        color
                    };
                    this.canvasLinks = [...this.canvasLinks, link];
                    this.selectedCanvasLinkId = link.id;
                    this.saveCanvasBoard();
                    return true;
                },

                deleteCanvasLink(linkId) {
                    const id = String(linkId || '');
                    if (!id) return;
                    this.canvasLinks = this.canvasLinks.filter(link => link.id !== id);
                    if (this.selectedCanvasLinkId === id) this.selectedCanvasLinkId = null;
                    this.saveCanvasBoard();
                },

                startCanvasDrag(node, event) {
                    if (!node || !event || event.button !== 0) return;
                    if (this.canvasLinkDraftFromId) return;
                    const id = String(node.id);
                    const topLayer = this.canvasNodes.reduce((max, item) => Math.max(max, Number(item.z) || 0), 0) + 1;
                    this.canvasNodes = this.canvasNodes.map(item => (
                        item.id === id ? { ...item, z: topLayer } : item
                    ));
                    this.selectedCanvasNodeId = id;
                    this.selectedCanvasLinkId = null;
                    this.canvasPointerAction = {
                        mode: 'drag',
                        id,
                        startX: event.clientX,
                        startY: event.clientY,
                        nodeX: Number(node.x) || 0,
                        nodeY: Number(node.y) || 0
                    };
                    event.preventDefault();
                },

                startCanvasResize(node, event) {
                    if (!node || !event || event.button !== 0) return;
                    const id = String(node.id);
                    this.selectedCanvasNodeId = id;
                    this.selectedCanvasLinkId = null;
                    this.canvasPointerAction = {
                        mode: 'resize',
                        id,
                        startX: event.clientX,
                        startY: event.clientY,
                        width: Number(node.width) || 220,
                        height: Number(node.height) || 160
                    };
                    event.preventDefault();
                },

                handleCanvasNodeClick(node) {
                    if (!node) return;
                    if (this.canvasLinkDraftFromId) {
                        if (this.canvasLinkDraftFromId === String(node.id)) {
                            this.canvasLinkDraftFromId = null;
                            return;
                        }
                        this.connectCanvasNodes(this.canvasLinkDraftFromId, node.id);
                        this.canvasLinkDraftFromId = null;
                        this.selectedCanvasNodeId = String(node.id);
                        return;
                    }
                    this.selectCanvasNode(node.id);
                },

                handleCanvasBoardPointerDown(event) {
                    const tagName = event?.target?.tagName?.toLowerCase();
                    if (event?.target === event?.currentTarget || tagName === 'svg') {
                        this.clearCanvasSelection();
                    }
                },

                moveCanvasDrag(event) {
                    if (!this.canvasPointerAction || !event) return;
                    const action = this.canvasPointerAction;
                    const node = this.getCanvasNodeById(action.id);
                    if (!node) return;

                    if (action.mode === 'drag') {
                        let nextX = action.nodeX + (event.clientX - action.startX);
                        let nextY = action.nodeY + (event.clientY - action.startY);
                        if (this.canvasSnapToGrid) {
                            nextX = Math.round(nextX / 28) * 28;
                            nextY = Math.round(nextY / 28) * 28;
                        }
                        const maxX = Math.max(0, this.canvasBoardWidth - Number(node.width) - 10);
                        const maxY = Math.max(0, this.canvasBoardHeight - Number(node.height) - 10);
                        nextX = this.clampCanvasValue(nextX, 0, maxX);
                        nextY = this.clampCanvasValue(nextY, 0, maxY);
                        this.canvasNodes = this.canvasNodes.map(item => (
                            item.id === action.id ? { ...item, x: nextX, y: nextY } : item
                        ));
                        return;
                    }

                    if (action.mode === 'resize') {
                        const bounds = this.getCanvasShapeBounds(node.shape);
                        let nextWidth = action.width + (event.clientX - action.startX);
                        let nextHeight = action.height + (event.clientY - action.startY);
                        if (this.canvasSnapToGrid) {
                            nextWidth = Math.round(nextWidth / 14) * 14;
                            nextHeight = Math.round(nextHeight / 14) * 14;
                        }
                        const maxWidthByBoard = Math.max(bounds.minWidth, this.canvasBoardWidth - Number(node.x) - 10);
                        const maxHeightByBoard = Math.max(bounds.minHeight, this.canvasBoardHeight - Number(node.y) - 10);
                        nextWidth = this.clampCanvasValue(nextWidth, bounds.minWidth, Math.min(bounds.maxWidth, maxWidthByBoard));
                        nextHeight = this.clampCanvasValue(nextHeight, bounds.minHeight, Math.min(bounds.maxHeight, maxHeightByBoard));
                        const dimensions = this.coerceCanvasDimensions(node.shape, nextWidth, nextHeight);
                        this.canvasNodes = this.canvasNodes.map(item => (
                            item.id === action.id ? { ...item, width: dimensions.width, height: dimensions.height } : item
                        ));
                    }
                },

                endCanvasDrag() {
                    if (!this.canvasPointerAction) return;
                    this.canvasPointerAction = null;
                    this.saveCanvasBoard();
                },

                clearCanvasBoard() {
                    if (!confirm('Wyczysc cala tablice robocza?')) return;
                    this.canvasNodes = [];
                    this.canvasLinks = [];
                    this.selectedCanvasNodeId = null;
                    this.selectedCanvasLinkId = null;
                    this.canvasLinkDraftFromId = null;
                    this.saveCanvasBoard();
                },

                serializeCanvasBoard() {
                    return JSON.stringify({
                        version: 2,
                        nodes: this.canvasNodes,
                        links: this.canvasLinks,
                        gridVisible: this.canvasGridVisible,
                        snapToGrid: this.canvasSnapToGrid
                    });
                },

                async saveCanvasBoard() {
                    clearTimeout(this.canvasSaveTimer);
                    this.canvasSaveTimer = setTimeout(async () => {
                        const content = this.serializeCanvasBoard();
                        try {
                            const response = await fetch(`${this.API}/notes/process-map`, {
                                method: 'PUT',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ content })
                            });
                            if (!response.ok) throw new Error('canvas_save_failed');
                            localStorage.removeItem(this.canvasStorageKey);
                            localStorage.removeItem(this.canvasLegacyStorageKey);
                        } catch (error) {
                            try {
                                localStorage.setItem(this.canvasStorageKey, content);
                            } catch (writeError) {
                                /* ignore storage write errors */
                            }
                        }
                    }, 350);
                },

                execDocCommand(command, value = null) {
                    document.execCommand(command, false, value);
                    this.projectDoc = this.$refs?.projectDocEditor?.innerHTML || this.projectDoc;
                    this.handleProjectDocInput();
                },

                handleProjectDocInput() {
                    this.projectDoc = this.$refs?.projectDocEditor?.innerHTML || '';
                    try {
                        localStorage.setItem(this.projectDocStorageKey, this.projectDoc);
                    } catch (error) {
                        /* ignore storage write errors */
                    }
                    clearTimeout(this.projectDocSaveTimer);
                    this.projectDocSaveTimer = setTimeout(() => {
                        this.saveProjectDoc(true);
                    }, 700);
                },

                async saveProjectDoc(quiet = false) {
                    clearTimeout(this.projectDocSaveTimer);
                    try {
                        const response = await fetch(`${this.API}/notes/project-doc`, {
                            method: 'PUT',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ content: this.projectDoc })
                        });
                        if (!response.ok) throw new Error('doc_save_failed');
                        const payload = await response.json();
                        this.projectDocSavedAt = payload.updated_at || new Date().toISOString();
                        localStorage.removeItem(this.projectDocStorageKey);
                        return true;
                    } catch (error) {
                        try {
                            localStorage.setItem(this.projectDocStorageKey, this.projectDoc || '');
                        } catch (writeError) {
                            /* ignore storage write errors */
                        }
                        if (!quiet) alert('Nie udalo sie zapisac dokumentu na serwerze. Kopia zostala lokalnie.');
                        return false;
                    }
                },

                async getApiErrorMessage(response, fallback) {
                    if (response.status === 404) {
                        return 'Endpoint nie znaleziony. Otworz aplikacje przez backend (http://127.0.0.1:8000) i odswiez strone, zeby formularze trafialy do API.';
                    }
                    try {
                        const payload = await response.json();
                        if (payload?.detail && payload.detail !== 'Not Found') return payload.detail;
                    } catch (error) {
                        /* response was not JSON */
                    }
                    return fallback;
                },

                async addMonthlyTask() {
                    const name = (this.newMonthlyTaskName || '').trim();
                    if (!name) {
                        alert('Podaj nazwe zadania miesiecznego.');
                        return;
                    }

                    const response = await fetch(`${this.API}/monthly-tasks`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            name,
                            due_day: this.normalizeMonthlyDueDay(this.newMonthlyTaskDueDay)
                        })
                    });

                    if (!response.ok) {
                        alert(await this.getApiErrorMessage(response, 'Nie udalo sie dodac zadania miesiecznego.'));
                        return;
                    }

                    this.closeMonthlyTaskModal();
                    await this.loadMonthlyTasks();
                },

                async saveMonthlyTaskDetails(task) {
                    if (!task) return;
                    const name = (task.name || '').trim();
                    if (!name) {
                        alert('Nazwa zadania miesiecznego nie moze byc pusta.');
                        await this.loadMonthlyTasks();
                        return;
                    }

                    const response = await fetch(`${this.API}/monthly-tasks/${task.id}`, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            name,
                            due_day: this.normalizeMonthlyDueDay(task.due_day)
                        })
                    });

                    if (!response.ok) {
                        alert(await this.getApiErrorMessage(response, 'Nie udalo sie zapisac zadania miesiecznego.'));
                    }

                    await this.loadMonthlyTasks();
                },

                async toggleMonthlyTaskDone(task) {
                    if (!task) return;
                    const response = await fetch(`${this.API}/monthly-tasks/${task.id}/state`, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            month_key: this.monthlyMonthKey || this.getCurrentMonthKey(),
                            done: !task.done,
                            note: task.note || ''
                        })
                    });

                    if (!response.ok) {
                        alert('Nie udalo sie zaktualizowac statusu.');
                        return;
                    }

                    await this.loadMonthlyTasks();
                },

                async saveMonthlyTaskNote(task) {
                    if (!task) return;
                    const response = await fetch(`${this.API}/monthly-tasks/${task.id}/state`, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            month_key: this.monthlyMonthKey || this.getCurrentMonthKey(),
                            done: !!task.done,
                            note: task.note || ''
                        })
                    });

                    if (!response.ok) {
                        alert('Nie udalo sie zapisac notatki.');
                        return;
                    }

                    await this.loadMonthlyTasks();
                },

                async deleteMonthlyTask(taskId) {
                    if (!confirm('Usunac to zadanie miesieczne?')) return;
                    const response = await fetch(`${this.API}/monthly-tasks/${taskId}`, { method: 'DELETE' });
                    if (!response.ok) {
                        alert('Nie udalo sie usunac zadania miesiecznego.');
                        return;
                    }
                    await this.loadMonthlyTasks();
                },

                async addDebt() {
                    const name = (this.newDebt.name || '').trim();
                    if (!name) {
                        alert('Podaj nazwe pozycji splaty.');
                        return;
                    }

                    const payload = {
                        name,
                        place: (this.newDebt.place || '').trim(),
                        kind: this.newDebt.kind === 'fixed' ? 'fixed' : 'debt',
                        total_amount: Number(this.newDebt.total_amount || 0),
                        monthly_amount: Number(this.newDebt.monthly_amount || 0),
                        due_day: this.normalizeMonthlyDueDay(this.newDebt.due_day),
                        note: (this.newDebt.note || '').trim()
                    };

                    const response = await fetch(`${this.API}/debts`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });

                    if (!response.ok) {
                        alert(await this.getApiErrorMessage(response, 'Nie udalo sie dodac pozycji splaty.'));
                        return;
                    }

                    this.closeDebtModal();
                    await this.loadDebts(this.debtsMonthKey || this.getCurrentMonthKey());
                },

                async deleteDebt(debtId) {
                    if (!confirm('Usunac te pozycje splaty?')) return;
                    const response = await fetch(`${this.API}/debts/${debtId}`, { method: 'DELETE' });
                    if (!response.ok) {
                        alert('Nie udalo sie usunac pozycji splaty.');
                        return;
                    }
                    await this.loadDebts(this.debtsMonthKey || this.getCurrentMonthKey());
                },

                async toggleDebtDoneForMonth(debt, dateKey, forceDone = null) {
                    if (!debt) return;
                    const monthKey = this.getMonthKeyFromDateKey(dateKey || this.getTodayKey());
                    const nextDone = forceDone === null ? !debt.month_done : !!forceDone;
                    const response = await fetch(`${this.API}/debts/${debt.id}/state`, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            month_key: monthKey,
                            done: nextDone
                        })
                    });
                    if (!response.ok) {
                        alert('Nie udalo sie zapisac statusu splaty.');
                        return;
                    }
                    await this.loadDebts(monthKey);
                },

                async shredTask() {
                    this.isShredding = true;
                    try {
                        const res = await fetch(`${this.API}/tasks/${this.editingTask.id}/shred`, { method: 'POST' });
                        const data = await res.json();
                        if (data.error) {
                            alert(`Blad AI: ${data.error}`);
                        } else {
                            this.taskModal = false;
                            await this.init();
                        }
                    } catch (error) {
                        alert('Blad polaczenia z Ollama.');
                    }
                    this.isShredding = false;
                },

                formatTime(seconds) {
                    return `${Math.floor(seconds / 60).toString().padStart(2, '0')}:${(seconds % 60).toString().padStart(2, '0')}`;
                },

                clearFlowState() {
                    clearInterval(this.timerInterval);
                    this.timerInterval = null;
                    this.flowTask = null;
                    this.flowTimer = 0;
                },

                async startFlow() {
                    const candidate = this.getFocusTask();
                    if (!candidate) {
                        alert('Najpierw dodaj zadanie do planera.');
                        return;
                    }

                    let task = candidate;
                    if (task.status !== 'todo') {
                        await this.changeTaskStatus(task, 'todo');
                        task = this.getTaskById(task.id) || { ...task, status: 'todo' };
                    }

                    this.flowTask = task;
                    this.flowTimer = (task.estimated_time || 15) * 60;
                    clearInterval(this.timerInterval);
                    this.timerInterval = setInterval(() => {
                        if (this.flowTimer > 0) this.flowTimer--;
                    }, 1000);
                    this.view = 'flow';
                },

                async completeFlowTask() {
                    const currentTask = this.flowTask;
                    this.clearFlowState();
                    if (currentTask) {
                        await this.changeTaskStatus(currentTask, 'gotowe');
                    }
                    this.view = this.activeModule ? 'kanban' : 'dash';
                },

                skipFlowTask() {
                    this.clearFlowState();
                    this.view = this.activeModule ? 'kanban' : 'dash';
                },

                async syncCalendarMonthData() {
                    const monthKey = this.getCalendarCursorMonthKey();
                    this.monthlyMonthKey = monthKey;
                    await Promise.all([
                        this.loadMonthlyTasks(),
                        this.loadDebts(monthKey)
                    ]);
                },

                async setCalendarMode(mode) {
                    this.calendarMode = mode;
                    this.calendarCursor = this.selectedDate || this.getTodayKey();
                    await this.syncCalendarMonthData();
                },

                async openCalendarView() {
                    this.view = 'calendar';
                    if (!this.calendarCursor) this.calendarCursor = this.getTodayKey();
                    if (!this.selectedDate) this.selectedDate = this.calendarCursor;
                    await this.syncCalendarMonthData();
                },

                async shiftCalendar(step) {
                    const cursor = this.keyToDate(this.calendarCursor || this.getTodayKey());
                    if (this.calendarMode === 'month') {
                        cursor.setDate(1);
                        cursor.setMonth(cursor.getMonth() + step);
                    } else {
                        cursor.setDate(cursor.getDate() + (step * 7));
                    }
                    this.calendarCursor = this.dateToKey(cursor);
                    this.selectedDate = this.dateToKey(cursor);
                    await this.syncCalendarMonthData();
                },

                async goToToday() {
                    this.calendarCursor = this.getTodayKey();
                    this.selectedDate = this.getTodayKey();
                    await this.syncCalendarMonthData();
                },

                getTasksForDate(dateKey) {
                    return this.sortTasksForFocus(
                        this.getOpenTasks().filter(task => task.due_date === dateKey)
                    );
                },

                getSelectedDateTasks() {
                    return this.getTasksForDate(this.selectedDate || this.getTodayKey());
                },

                getStartOfWeek(date) {
                    const start = new Date(date);
                    const day = (start.getDay() + 6) % 7;
                    start.setDate(start.getDate() - day);
                    return start;
                },

                getWeekDays() {
                    const start = this.getStartOfWeek(this.keyToDate(this.calendarCursor || this.getTodayKey()));
                    const days = [];
                    for (let index = 0; index < 7; index++) {
                        const date = new Date(start);
                        date.setDate(start.getDate() + index);
                        const dateKey = this.dateToKey(date);
                        days.push({
                            dateKey,
                            dayNumber: date.getDate(),
                            monthShort: new Intl.DateTimeFormat('pl-PL', { month: 'short' }).format(date),
                            weekdayLong: new Intl.DateTimeFormat('pl-PL', { weekday: 'short' }).format(date),
                            isToday: dateKey === this.getTodayKey(),
                            tasks: this.getTasksForDate(dateKey)
                        });
                    }
                    return days;
                },

                getMonthDays() {
                    const cursor = this.keyToDate(this.calendarCursor || this.getTodayKey());
                    const monthStart = new Date(cursor.getFullYear(), cursor.getMonth(), 1, 12, 0, 0);
                    const gridStart = this.getStartOfWeek(monthStart);
                    const days = [];

                    for (let index = 0; index < 42; index++) {
                        const date = new Date(gridStart);
                        date.setDate(gridStart.getDate() + index);
                        const dateKey = this.dateToKey(date);
                        const entries = this.getCalendarEntriesForDate(dateKey);
                        days.push({
                            dateKey,
                            dayNumber: date.getDate(),
                            weekdayShort: new Intl.DateTimeFormat('pl-PL', { weekday: 'short' }).format(date),
                            isCurrentMonth: date.getMonth() === cursor.getMonth(),
                            isToday: dateKey === this.getTodayKey(),
                            isSelected: dateKey === this.selectedDate,
                            entries,
                            total: entries.length
                        });
                    }

                    return days;
                },

                getCalendarVisibleEntriesCount() {
                    return this.getMonthDays()
                        .filter(day => day.isCurrentMonth)
                        .reduce((sum, day) => sum + (day.entries?.length || 0), 0);
                },

                getCalendarLabel() {
                    const cursor = this.keyToDate(this.calendarCursor || this.getTodayKey());
                    if (this.calendarMode === 'month') {
                        return new Intl.DateTimeFormat('pl-PL', {
                            month: 'long',
                            year: 'numeric'
                        }).format(cursor);
                    }

                    const start = this.getStartOfWeek(cursor);
                    const end = new Date(start);
                    end.setDate(start.getDate() + 6);

                    const startLabel = new Intl.DateTimeFormat('pl-PL', { day: 'numeric', month: 'short' }).format(start);
                    const endLabel = new Intl.DateTimeFormat('pl-PL', { day: 'numeric', month: 'short', year: 'numeric' }).format(end);
                    return `${startLabel} - ${endLabel}`;
                }
            };
        }
