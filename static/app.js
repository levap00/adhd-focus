        function app() {
            return {
                view: 'dash',
                modules: [],
                tasks: [],
                activeModule: null,
                calmMode: false,
                theme: 'light',
                settingsMenuOpen: false,
                toasts: [],
                toastTimers: {},
                toastSequence: 0,
                undoTimers: {},
                notificationHistory: [],
                notificationHistoryLoading: false,
                notificationSettings: {
                    enabled: true,
                    quiet_hours_enabled: true,
                    quiet_hours_start: '22:00',
                    quiet_hours_end: '07:00',
                    opening_enabled: true,
                    opening_time: '08:00',
                    day_summary_enabled: true,
                    day_summary_time: '20:30',
                    medication_enabled: true,
                    medication_repeat_enabled: false,
                    medication_repeat_minutes: 5,
                    medication_repeat_window_minutes: 120,
                    task_due_enabled: true,
                    task_reminder_enabled: true,
                    task_reminder_repeat_minutes: 120,
                    task_reminder_window_minutes: 480,
                    timezone: 'Europe/Warsaw'
                },
                notificationSettingsSaving: false,
                pushState: {
                    supported: false,
                    serviceWorkerReady: false,
                    permission: typeof Notification === 'undefined' ? 'unsupported' : Notification.permission,
                    subscribed: false,
                    subscriptionCount: 0,
                    vapidConfigured: false,
                    publicKey: '',
                    message: ''
                },
                zoomGuardsInstalled: false,
                viewportGuardsInstalled: false,
                keyboardOpen: false,
                fabOpen: false,
                sidebarCollapsed: false,
                focusFilter: 'all',
                dopamineWeekOffset: 0,
                taskScope: 'all',
                moduleOrder: [],
                dailyGoal: 5,
                workdayLimitMinutes: 8 * 60,
                taskModal: false,
                isCreatingTask: false,
                editingTask: {},
                taskFormError: '',
                doneTasksExpanded: false,
                sharingConnections: [],
                incomingSharingInvitations: [],
                outgoingSharingInvitations: [],
                sharingInviteUsername: '',
                sharingLoading: false,
                securityProfileLoaded: false,
                securitySaving: false,
                securityAwaitingCode: false,
                securityEmailDraft: '',
                securityEmailCode: '',
                securityProfile: {
                    username: '',
                    email: '',
                    email_masked: '',
                    email_verified: false,
                    mailer_configured: false,
                    pending_email: '',
                    pending_email_masked: '',
                    devices: [],
                    dev_code: ''
                },
                shareTaskModal: false,
                sharingTaskId: null,
                shareTaskDueTime: '',
                priorityFilter: 'ALL',
                sortOrder: 'none',
                API: '',
                flowTask: null,
                flowTimer: 0,
                timerInterval: null,
                isShredding: false,
                brainDumpNotes: [],
                activeBrainDumpNoteId: null,
                brainDumpNoteTitle: '',
                brainDump: '',
                brainDumpTargetModuleId: '',
                noteSavedAt: '',
                brainDumpSaveTimer: null,
                brainDumpStorageKey: 'adhd-focus-brain-dump-draft-v1',
                calendarMode: 'month',
                calendarCursor: '',
                selectedDate: '',
                isMobileLayout: false,
                mobileModulesOpen: false,
                calendarMobileSection: 'preview',
                monthlyMonthKey: '',
                monthlyTasks: [],
                medicationsDate: '',
                medications: [],
                medicationsSummary: { total: 0, active: 0, paused: 0, scheduled: 0, done: 0, open: 0 },
                editingMedicationId: null,
                newMedication: {
                    name: '',
                    schedule_type: 'daily',
                    reminder_time: '08:00'
                },
                newMonthlyTaskName: '',
                newMonthlyTaskDueDay: '',
                newMonthlyTaskDueTime: '23:59',
                newMonthlyTaskRepeatType: 'monthly',
                newMonthlyTaskRepeatWeekday: 1,
                editingMonthlyTaskId: null,
                monthlyTaskModal: false,
                debts: [],
                debtsMonthKey: '',
                debtsSummary: { count: 0, total: 0, monthly: 0, debt_total: 0, debt_monthly: 0, fixed_monthly: 0, fixed_count: 0, debt_count: 0 },
                rewardSummary: {
                    earned_points: 0,
                    spent_points: 0,
                    available_points: 0,
                    available_budget_pln: 0,
                    point_value_pln: 1
                },
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
                draggedTaskTargetId: null,
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
                canvasZoom: 1,
                canvasMinZoom: 0.35,
                canvasMaxZoom: 2.5,
                canvasGridVisible: true,
                canvasSnapToGrid: false,
                canvasSaveTimer: null,
                canvasStorageKey: 'adhd-focus-canvas-v2',
                canvasLegacyStorageKey: 'adhd-focus-canvas-v1',
                canvasColorOptions: [
                    { id: 'slate', label: 'Szary', swatch: '#e2e8f0', line: '#64748b', bg: '#ffffff', border: '#cbd5e1', text: '#0f172a' },
                    { id: 'emerald', label: 'Zielony', swatch: '#10b981', line: '#059669', bg: '#ecfdf5', border: '#6ee7b7', text: '#064e3b' },
                    { id: 'sky', label: 'Niebieski', swatch: '#0ea5e9', line: '#0284c7', bg: '#e0f2fe', border: '#7dd3fc', text: '#082f49' },
                    { id: 'amber', label: 'Bursztyn', swatch: '#f59e0b', line: '#d97706', bg: '#fffbeb', border: '#fcd34d', text: '#78350f' },
                    { id: 'rose', label: 'Rozowy', swatch: '#f43f5e', line: '#e11d48', bg: '#fff1f2', border: '#fda4af', text: '#881337' },
                    { id: 'violet', label: 'Fiolet', swatch: '#8b5cf6', line: '#7c3aed', bg: '#f5f3ff', border: '#c4b5fd', text: '#4c1d95' }
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
                    { id: 'przygotowanie', name: 'Review / Hold', color: 'text-amber-600' },
                    { id: 'todo', name: 'Teraz robie', color: 'text-cyan-600' },
                    { id: 'obserwacja', name: 'Watchlist', color: 'text-violet-600' }
                ],
                taskReminderOptions: [
                    { value: -1, label: 'Nie powiadamiaj' },
                    { value: 0, label: 'O czasie' },
                    { value: 5, label: '5 min przed' },
                    { value: 10, label: '10 min przed' },
                    { value: 15, label: '15 min przed' },
                    { value: 30, label: '30 min przed' },
                    { value: 60, label: '1 godz. przed' },
                    { value: 120, label: '2 godz. przed' },
                    { value: 1440, label: '1 dzien przed' }
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

                detectMobileLayout() {
                    return window.matchMedia('(max-width: 1279px)').matches;
                },

                handleViewportResize() {
                    const isMobile = this.detectMobileLayout();
                    this.isMobileLayout = isMobile;
                    if (isMobile && this.view === 'combined') {
                        this.view = 'calendar';
                    }
                    if (!isMobile) {
                        this.mobileModulesOpen = true;
                    }
                    this.updateKeyboardState();
                },

                updateKeyboardState() {
                    if (typeof window === 'undefined' || typeof document === 'undefined') return;
                    if (!window.matchMedia('(max-width: 767px)').matches) {
                        this.keyboardOpen = false;
                        return;
                    }
                    const active = document.activeElement;
                    const formFieldFocused = !!active && (
                        active.matches?.('input, textarea, select, [contenteditable="true"]')
                    );
                    const viewport = window.visualViewport;
                    const viewportReduced = !!viewport && (window.innerHeight - viewport.height) > 120;
                    this.keyboardOpen = formFieldFocused || viewportReduced;
                },

                installViewportGuards() {
                    if (this.viewportGuardsInstalled || typeof window === 'undefined' || typeof document === 'undefined') return;
                    this.viewportGuardsInstalled = true;
                    const update = () => window.requestAnimationFrame(() => this.updateKeyboardState());
                    document.addEventListener('focusin', update);
                    document.addEventListener('focusout', () => window.setTimeout(update, 120));
                    window.visualViewport?.addEventListener('resize', update);
                    window.visualViewport?.addEventListener('scroll', update);
                },

                installZoomGuards() {
                    if (this.zoomGuardsInstalled || typeof document === 'undefined') return;
                    this.zoomGuardsInstalled = true;

                    document.addEventListener('gesturestart', event => {
                        event.preventDefault();
                    }, { passive: false });

                    let lastTouchEnd = 0;
                    document.addEventListener('touchend', event => {
                        const now = Date.now();
                        if (now - lastTouchEnd <= 300) {
                            event.preventDefault();
                        }
                        lastTouchEnd = now;
                    }, { passive: false });
                },

                showToast(message, type = 'info', options = {}) {
                    const id = ++this.toastSequence;
                    const toast = {
                        id,
                        message: String(message || ''),
                        type,
                        actionLabel: options.actionLabel || '',
                        cancelLabel: options.cancelLabel || '',
                        onAction: typeof options.onAction === 'function' ? options.onAction : null,
                        onDismiss: typeof options.onDismiss === 'function' ? options.onDismiss : null,
                        closable: options.closable !== false
                    };
                    this.toasts.push(toast);
                    const duration = Number(options.duration ?? (toast.actionLabel ? 0 : 4500));
                    if (duration > 0) {
                        this.toastTimers[id] = window.setTimeout(() => this.dismissToast(id), duration);
                    }
                    return id;
                },

                removeToast(id) {
                    window.clearTimeout(this.toastTimers[id]);
                    delete this.toastTimers[id];
                    this.toasts = this.toasts.filter(item => item.id !== id);
                },

                dismissToast(id) {
                    const toast = this.toasts.find(item => item.id === id);
                    this.removeToast(id);
                    if (toast?.onDismiss) toast.onDismiss();
                },

                runToastAction(id) {
                    const toast = this.toasts.find(item => item.id === id);
                    if (!toast) return;
                    this.removeToast(id);
                    if (toast.onAction) toast.onAction();
                },

                askConfirmation(message, confirmLabel = 'Kontynuuj') {
                    return new Promise(resolve => {
                        let settled = false;
                        const finish = value => {
                            if (settled) return;
                            settled = true;
                            resolve(value);
                        };
                        this.showToast(message, 'warning', {
                            duration: 0,
                            actionLabel: confirmLabel,
                            cancelLabel: 'Anuluj',
                            onAction: () => finish(true),
                            onDismiss: () => finish(false)
                        });
                    });
                },

                queueUndoableAction(message, action) {
                    let toastId = 0;
                    const cancel = () => {
                        window.clearTimeout(this.undoTimers[toastId]);
                        delete this.undoTimers[toastId];
                        this.showToast('Anulowano. Nic nie zostało usunięte.', 'success');
                    };
                    toastId = this.showToast(message, 'warning', {
                        duration: 0,
                        actionLabel: 'Cofnij',
                        onAction: cancel,
                        closable: false
                    });
                    this.undoTimers[toastId] = window.setTimeout(async () => {
                        delete this.undoTimers[toastId];
                        this.removeToast(toastId);
                        try {
                            await action();
                        } catch (error) {
                            this.showToast(error?.message || 'Nie udało się wykonać operacji.', 'error');
                        }
                    }, 6500);
                    return true;
                },

                applyRouteFromUrl() {
                    if (typeof window === 'undefined') return;
                    const params = new URLSearchParams(window.location.search || '');
                    if (!params.toString()) return;

                    let consumed = false;
                    const requestedView = (params.get('view') || '').trim().toLowerCase();
                    const medicationDate = this.sanitizeDateKey(params.get('med_date') || params.get('medication_date') || '');
                    const calendarDate = this.sanitizeDateKey(params.get('date') || params.get('calendar_date') || '');

                    if (requestedView === 'meds' || medicationDate) {
                        this.view = 'meds';
                        if (medicationDate) {
                            this.medicationsDate = medicationDate;
                        }
                        consumed = true;
                    } else if (requestedView === 'calendar' || calendarDate) {
                        this.view = 'calendar';
                        if (calendarDate) {
                            this.selectedDate = calendarDate;
                            this.calendarCursor = calendarDate;
                        }
                        consumed = true;
                    } else if (requestedView === 'combined') {
                        this.view = this.isMobileLayout ? 'calendar' : 'combined';
                        this.setTaskScope('all');
                        consumed = true;
                    } else if (['dash', 'kanban', 'global', 'calendar', 'brain', 'canvas', 'docs', 'monthly', 'debts', 'notifications', 'sharing', 'security'].includes(requestedView)) {
                        this.view = requestedView;
                        consumed = true;
                    }

                    if (!consumed || !window.history?.replaceState) return;
                    params.delete('view');
                    params.delete('med_date');
                    params.delete('medication_date');
                    params.delete('date');
                    params.delete('calendar_date');
                    const cleanQuery = params.toString();
                    const nextUrl = `${window.location.pathname}${cleanQuery ? `?${cleanQuery}` : ''}${window.location.hash || ''}`;
                    window.history.replaceState({}, '', nextUrl);
                },

                async init() {
                    this.loadUIPreferences();
                    this.installZoomGuards();
                    this.installViewportGuards();
                    this.handleViewportResize();
                    this.registerServiceWorker();
                    if (!this.isMobileLayout) {
                        this.mobileModulesOpen = true;
                    }
                    if (this.isMobileLayout && this.sidebarCollapsed !== true) {
                        this.sidebarCollapsed = true;
                    }

                    if (!this.calendarCursor) this.calendarCursor = this.getTodayKey();
                    if (!this.selectedDate) this.selectedDate = this.getTodayKey();
                    if (!this.monthlyMonthKey) this.monthlyMonthKey = this.getCurrentMonthKey();
                    if (!this.medicationsDate) this.medicationsDate = this.getTodayKey();
                    this.applyRouteFromUrl();

                    await Promise.all([
                        this.loadModules(),
                        this.loadAllTasks(),
                        this.loadRewardSummary(),
                        this.loadMedications(),
                        this.loadBrainDump(),
                        this.loadNotificationSettings(),
                        this.loadNotificationHistory(),
                        this.loadSharingConnections(),
                        this.loadSecurityProfile(),
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

                closeOverlayMenus() {
                    this.settingsMenuOpen = false;
                    this.fabOpen = false;
                },

                toggleFab() {
                    this.settingsMenuOpen = false;
                    this.fabOpen = !this.fabOpen;
                },

                closeFab() {
                    this.fabOpen = false;
                },

                navigateMainView(target) {
                    this.closeOverlayMenus();
                    if (target === 'dash') {
                        this.view = 'dash';
                        this.closeMobileModules();
                        return;
                    }
                    if (target === 'kanban') {
                        this.openAllTasksView();
                        return;
                    }
                    if (target === 'global') {
                        this.view = 'global';
                        this.closeMobileModules();
                        return;
                    }
                    if (target === 'calendar') {
                        this.openCalendarView();
                        return;
                    }
                    if (target === 'combined' && !this.isMobileLayout) {
                        this.setTaskScope('all');
                        this.view = 'combined';
                        this.closeMobileModules();
                        if (!this.calendarCursor) this.calendarCursor = this.getTodayKey();
                        if (!this.selectedDate) this.selectedDate = this.getTodayKey();
                        this.syncCalendarMonthData();
                    }
                },

                navigateUtilityView(target) {
                    this.closeOverlayMenus();
                    this.closeMobileModules();
                    if (target === 'brain') {
                        this.view = 'brain';
                        return;
                    }
                    const allowedViews = ['canvas', 'docs', 'monthly', 'meds', 'debts', 'notifications', 'sharing', 'security'];
                    if (allowedViews.includes(target)) {
                        this.view = target;
                        if (target === 'sharing') this.loadSharingConnections();
                        if (target === 'security') this.loadSecurityProfile();
                    }
                },

                openFabNewTask() {
                    this.closeFab();
                    this.openNewTaskModal();
                },

                openBrainDumpAction() {
                    this.closeOverlayMenus();
                    this.view = 'brain';
                    this.closeMobileModules();
                    window.setTimeout(() => {
                        document.querySelector('[data-brain-dump-input]')?.focus();
                    }, 0);
                },

                toggleSidebar() {
                    this.sidebarCollapsed = !this.sidebarCollapsed;
                    this.saveUIPreferences();
                },

                toggleMobileModules() {
                    if (!this.isMobileLayout) return;
                    this.mobileModulesOpen = !this.mobileModulesOpen;
                },

                closeMobileModules() {
                    if (!this.isMobileLayout) return;
                    this.mobileModulesOpen = false;
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
                    this.closeMobileModules();
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

                getAssignableModules() {
                    return this.getSidebarModules().filter(module => !module.is_shared);
                },

                getTaskModuleOptions(task = null) {
                    if (task?.shared_role === 'shared') {
                        const currentModuleId = this.normalizeOptionalId(task.module_id);
                        return this.modules.filter(module => Number(module.id) === Number(currentModuleId));
                    }
                    return this.getAssignableModules();
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
                    return ['oczekujace', 'przygotowanie', 'todo', 'obserwacja', 'gotowe'].includes(value) ? value : 'oczekujace';
                },

                normalizePointsWeight(value) {
                    const normalizedRaw = typeof value === 'string'
                        ? value.replace(',', '.').trim()
                        : value;
                    const parsed = Number(normalizedRaw);
                    if (!Number.isFinite(parsed) || parsed <= 0) return 1;
                    return Math.round(parsed * 100) / 100;
                },

                normalizeEstimatedMinutes(value) {
                    const parsed = Math.round(Number(value));
                    if (!Number.isFinite(parsed) || parsed < 0) return 0;
                    return parsed;
                },

                normalizeReminderOffsetMinutes(value) {
                    const parsed = Math.round(Number(value));
                    if (!Number.isFinite(parsed)) return 0;
                    if (parsed < 0) return -1;
                    return Math.min(1440, parsed);
                },

                normalizeOptionalId(value) {
                    const parsed = Number(value);
                    if (!Number.isFinite(parsed) || parsed <= 0) return null;
                    return parsed;
                },

                normalizeSubtaskPointsWeight(value) {
                    const normalizedRaw = typeof value === 'string'
                        ? value.replace(',', '.').trim()
                        : value;
                    const parsed = Number(normalizedRaw);
                    if (!Number.isFinite(parsed) || parsed < 0) return 0;
                    return Math.round(parsed * 100) / 100;
                },

                normalizeSubtaskEstimatedMinutes(value) {
                    const parsed = Math.round(Number(value));
                    if (!Number.isFinite(parsed) || parsed < 0) return 0;
                    return parsed;
                },

                formatDurationMinutes(value) {
                    const minutes = this.normalizeEstimatedMinutes(value);
                    const hours = Math.floor(minutes / 60);
                    const rest = minutes % 60;
                    if (hours > 0 && rest > 0) return `${hours}h ${rest}m`;
                    if (hours > 0) return `${hours}h`;
                    return `${rest}m`;
                },

                normalizeSubtasks(subtasks) {
                    if (!Array.isArray(subtasks)) return [];
                    const normalized = [];
                    for (const item of subtasks) {
                        const title = (item?.title || '').toString().trim();
                        if (!title) continue;
                        const idValue = Number(item?.id);
                        normalized.push({
                            id: Number.isFinite(idValue) ? idValue : null,
                            title,
                            done: !!item?.done,
                            estimated_time: this.normalizeSubtaskEstimatedMinutes(item?.estimated_time),
                            points_weight: this.normalizeSubtaskPointsWeight(item?.points_weight),
                            done_at: item?.done_at || '',
                            source_task_id: this.normalizeOptionalId(item?.source_task_id),
                            source_module_id: this.normalizeOptionalId(item?.source_module_id),
                            source_due_date: this.sanitizeDateKey(item?.source_due_date),
                            source_due_time: this.sanitizeDueTime(item?.source_due_time, ''),
                            position: normalized.length
                        });
                    }
                    return normalized;
                },

                createSubtaskDraft(title = '') {
                    return {
                        id: null,
                        title: title || '',
                        done: false,
                        estimated_time: 15,
                        points_weight: 1,
                        done_at: '',
                        source_task_id: null,
                        source_module_id: null,
                        source_due_date: '',
                        source_due_time: ''
                    };
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
                        this.showToast('Nazwa modulu nie moze byc pusta.');
                        return;
                    }

                    const response = await fetch(`${this.API}/modules/${module.id}`, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ name: cleanName })
                    });

                    if (!response.ok) {
                        this.showToast(await this.getApiErrorMessage(response, 'Nie udalo sie zmienic nazwy modulu.'));
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
                        module_id: this.normalizeOptionalId(task.module_id),
                        status: this.normalizeTaskStatus(task.status),
                        priority: this.normalizePriorityValue(task.priority),
                        estimated_time: this.normalizeEstimatedMinutes(task.estimated_time),
                        points_weight: this.normalizePointsWeight(task.points_weight),
                        due_time: this.sanitizeDueTime(task.due_time, ''),
                        reminder_offset_minutes: this.normalizeReminderOffsetMinutes(task.reminder_offset_minutes),
                        is_shared: !!task.is_shared,
                        shared_role: (task.shared_role || 'owner').toString(),
                        share_count: Number(task.share_count || 0),
                        owner_username: (task.owner_username || '').toString(),
                        shares: Array.isArray(task.shares) ? task.shares : [],
                        shared_user_ids: Array.isArray(task.shared_user_ids)
                            ? task.shared_user_ids.map(Number).filter(Number.isFinite)
                            : [],
                        subtasks: this.normalizeSubtasks(task.subtasks)
                    }));
                },

                async loadSharingConnections() {
                    try {
                        const response = await fetch(`${this.API}/sharing`);
                        if (!response.ok) throw new Error('sharing_load_failed');
                        const payload = await response.json();
                        this.sharingConnections = Array.isArray(payload.connections) ? payload.connections : [];
                        this.incomingSharingInvitations = Array.isArray(payload.incoming) ? payload.incoming : [];
                        this.outgoingSharingInvitations = Array.isArray(payload.outgoing) ? payload.outgoing : [];
                    } catch (error) {
                        this.sharingConnections = [];
                        this.incomingSharingInvitations = [];
                        this.outgoingSharingInvitations = [];
                    }
                },


                applySecurityProfile(payload) {
                    const next = payload && typeof payload === 'object' ? payload : {};
                    this.securityProfile = {
                        username: (next.username || '').toString(),
                        email: (next.email || '').toString(),
                        email_masked: (next.email_masked || '').toString(),
                        email_verified: !!next.email_verified,
                        mailer_configured: !!next.mailer_configured,
                        pending_email: (next.pending_email || '').toString(),
                        pending_email_masked: (next.pending_email_masked || '').toString(),
                        devices: Array.isArray(next.devices) ? next.devices : [],
                        dev_code: (next.dev_code || '').toString()
                    };
                    this.securityProfileLoaded = true;
                    this.securityAwaitingCode = !!this.securityProfile.pending_email;
                    if (this.securityProfile.email && !this.securityEmailDraft) {
                        this.securityEmailDraft = this.securityProfile.email;
                    }
                },

                async loadSecurityProfile() {
                    try {
                        const response = await fetch(`${this.API}/security/profile`);
                        if (!response.ok) throw new Error('security_profile_failed');
                        this.applySecurityProfile(await response.json());
                    } catch (error) {
                        this.securityProfileLoaded = true;
                    }
                },

                formatSecurityTime(value) {
                    const raw = (value || '').toString();
                    if (!raw) return 'brak aktywności';
                    const parsed = new Date(raw);
                    if (Number.isNaN(parsed.getTime())) return raw;
                    return parsed.toLocaleString('pl-PL', { dateStyle: 'short', timeStyle: 'short' });
                },

                async startEmailVerification() {
                    const email = (this.securityEmailDraft || '').trim();
                    if (!email) {
                        this.showToast('Wpisz adres e-mail.');
                        return;
                    }
                    this.securitySaving = true;
                    try {
                        const response = await fetch(`${this.API}/security/email/start`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ email })
                        });
                        if (!response.ok) {
                            this.showToast(await this.getApiErrorMessage(response, 'Nie udalo sie wyslac kodu.'));
                            return;
                        }
                        const payload = await response.json();
                        this.securityAwaitingCode = true;
                        this.securityEmailCode = '';
                        this.securityProfile.pending_email_masked = payload.email_masked || email;
                        this.securityProfile.dev_code = payload.dev_code || '';
                        this.showToast('Kod poszedl na e-mail.', 'success');
                    } finally {
                        this.securitySaving = false;
                    }
                },

                async resendEmailVerification() {
                    this.securitySaving = true;
                    try {
                        const response = await fetch(`${this.API}/security/email/resend`, { method: 'POST' });
                        if (!response.ok) {
                            this.showToast(await this.getApiErrorMessage(response, 'Nie udalo sie wyslac kodu ponownie.'));
                            return;
                        }
                        const payload = await response.json();
                        this.securityProfile.pending_email_masked = payload.email_masked || this.securityProfile.pending_email_masked;
                        this.securityProfile.dev_code = payload.dev_code || '';
                        this.showToast('Wyslalismy nowy kod.', 'success');
                    } finally {
                        this.securitySaving = false;
                    }
                },

                async confirmEmailVerification() {
                    const code = (this.securityEmailCode || '').trim();
                    if (!code) {
                        this.showToast('Wpisz kod z e-maila.');
                        return;
                    }
                    this.securitySaving = true;
                    try {
                        const response = await fetch(`${this.API}/security/email/confirm`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ code })
                        });
                        if (!response.ok) {
                            this.showToast(await this.getApiErrorMessage(response, 'Niepoprawny kod.'));
                            return;
                        }
                        this.applySecurityProfile(await response.json());
                        this.securityEmailCode = '';
                        this.securityAwaitingCode = false;
                        this.showToast('E-mail potwierdzony. Nowe urzadzenia beda prosic o kod.', 'success');
                    } finally {
                        this.securitySaving = false;
                    }
                },

                async revokeTrustedDevice(device) {
                    if (!device?.id) return;
                    if (!await this.askConfirmation('Odwołać to urządzenie? Przy następnym logowaniu poprosi o kod z e-maila.', 'Odwołaj')) return;
                    const response = await fetch(`${this.API}/security/devices/${device.id}`, { method: 'DELETE' });
                    if (!response.ok) {
                        this.showToast(await this.getApiErrorMessage(response, 'Nie udalo sie odwolac urzadzenia.'));
                        return;
                    }
                    await this.loadSecurityProfile();
                    this.showToast('Urządzenie odwołane.', 'success');
                },

                async revokeAllTrustedDevices() {
                    if (!await this.askConfirmation('Wylogować wszystkie zapisane urządzenia? Każde będzie musiało potwierdzić kod z e-maila.', 'Wyloguj wszystkie')) return;
                    const response = await fetch(`${this.API}/security/devices/revoke-all`, { method: 'POST' });
                    if (!response.ok) {
                        this.showToast(await this.getApiErrorMessage(response, 'Nie udalo sie wylogowac urzadzen.'));
                        return;
                    }
                    await this.loadSecurityProfile();
                    this.showToast('Wyczyszczono zaufane urządzenia.', 'success');
                },

                async sendSharingInvitation() {
                    const username = (this.sharingInviteUsername || '').trim();
                    if (!username || this.sharingLoading) return;
                    this.sharingLoading = true;
                    try {
                        const response = await fetch(`${this.API}/sharing/invitations`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ username })
                        });
                        if (!response.ok) {
                            this.showToast(await this.getApiErrorMessage(response, 'Nie udalo sie wyslac zaproszenia.'));
                            return;
                        }
                        this.sharingInviteUsername = '';
                        await this.loadSharingConnections();
                        this.showToast('Zaproszenie wyslane. Udostepnianie ruszy po akceptacji.', 'success');
                    } finally {
                        this.sharingLoading = false;
                    }
                },

                async respondToSharingInvitation(invitationId, accept) {
                    if (this.sharingLoading) return;
                    this.sharingLoading = true;
                    try {
                        const action = accept ? 'accept' : 'decline';
                        const response = await fetch(`${this.API}/sharing/invitations/${invitationId}/${action}`, { method: 'POST' });
                        if (!response.ok) {
                            this.showToast(await this.getApiErrorMessage(response, 'Nie udalo sie odpowiedziec na zaproszenie.'));
                            return;
                        }
                        await this.loadSharingConnections();
                        this.showToast(accept ? 'Zaproszenie zaakceptowane.' : 'Zaproszenie odrzucone.', 'success');
                    } finally {
                        this.sharingLoading = false;
                    }
                },

                async removeSharingConnection(connection) {
                    if (!connection) return;
                    const confirmed = await this.askConfirmation(
                        `Usunac ${connection.username} z listy? Istniejace wspolne zadania przestana byc udostepnione.`,
                        'Usun polaczenie'
                    );
                    if (!confirmed) return;
                    const response = await fetch(`${this.API}/sharing/connections/${connection.user_id}`, { method: 'DELETE' });
                    if (!response.ok) {
                        this.showToast(await this.getApiErrorMessage(response, 'Nie udalo sie usunac polaczenia.'));
                        return;
                    }
                    await Promise.all([this.loadSharingConnections(), this.loadAllTasks(), this.loadModules()]);
                    this.showToast('Polaczenie i dostep do wspolnych zadan zostaly usuniete.', 'success');
                },

                normalizeBrainDumpNote(note) {
                    return {
                        id: Number(note?.id) || 0,
                        title: (note?.title || 'Nowa notatka').toString(),
                        content: (note?.content || '').toString(),
                        created_at: (note?.created_at || '').toString(),
                        updated_at: (note?.updated_at || '').toString()
                    };
                },

                async loadBrainDump() {
                    try {
                        const res = await fetch(`${this.API}/brain-dump-notes`);
                        if (!res.ok) throw new Error('brain_dump_load_failed');
                        const payload = await res.json();
                        this.brainDumpNotes = Array.isArray(payload.items)
                            ? payload.items.map(note => this.normalizeBrainDumpNote(note)).filter(note => note.id > 0)
                            : [];

                        if (this.brainDumpNotes.length === 0) {
                            try {
                                const localDraft = localStorage.getItem(this.brainDumpStorageKey);
                                if (typeof localDraft === 'string' && localDraft.trim()) {
                                    const created = await this.createBrainDumpNote(localDraft, 'Szkic lokalny', false);
                                    if (created) return;
                                }
                            } catch (error) {
                                /* ignore local draft migration errors */
                            }
                        }

                        const preferred = this.brainDumpNotes.find(note => note.id === Number(this.activeBrainDumpNoteId)) || this.brainDumpNotes[0] || null;
                        this.applyActiveBrainDumpNote(preferred);
                        try {
                            localStorage.removeItem(this.brainDumpStorageKey);
                        } catch (error) {
                            /* ignore storage cleanup errors */
                        }
                    } catch (error) {
                        try {
                            const localDraft = localStorage.getItem(this.brainDumpStorageKey);
                            this.brainDump = typeof localDraft === 'string' ? localDraft : '';
                            this.brainDumpNoteTitle = 'Szkic lokalny';
                        } catch (readError) {
                            this.brainDump = '';
                            this.brainDumpNoteTitle = '';
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
                    this.monthlyTasks = Array.isArray(payload.items)
                        ? payload.items.map(task => ({
                            ...task,
                            id: Number(task.id) || 0,
                            instance_id: task.instance_id || `${task.id || 'task'}-${task.state_key || this.monthlyMonthKey}`,
                            due_day: this.normalizeMonthlyDueDay(task.due_day),
                            due_time: this.sanitizeDueTime(task.due_time, '23:59') || '23:59',
                            repeat_type: this.normalizeMonthlyRepeatType(task.repeat_type),
                            repeat_weekday: this.normalizeMonthlyRepeatWeekday(task.repeat_weekday),
                            date_key: this.sanitizeDateKey(task.date_key),
                            display_date_key: this.sanitizeDateKey(task.display_date_key || task.date_key),
                            state_key: (task.state_key || payload.month_key || month).toString(),
                            legacy_state_key: (task.legacy_state_key || '').toString(),
                            overdue: !!task.overdue,
                            done: !!task.done
                        }))
                        : [];
                },

                async loadMedications(dateKey = '') {
                    const cleanDate = this.sanitizeDateKey(dateKey || this.medicationsDate || this.getTodayKey()) || this.getTodayKey();
                    this.medicationsDate = cleanDate;
                    const res = await fetch(`${this.API}/medications?date=${encodeURIComponent(cleanDate)}`);
                    if (!res.ok) {
                        this.medications = [];
                        this.medicationsSummary = { total: 0, active: 0, paused: 0, scheduled: 0, done: 0, open: 0 };
                        return;
                    }
                    const payload = await res.json();
                    this.medicationsDate = this.sanitizeDateKey(payload.date_key) || cleanDate;
                    this.medications = Array.isArray(payload.items)
                        ? payload.items.map(item => ({
                            ...item,
                            id: Number(item.id) || 0,
                            schedule_type: this.normalizeMedicationScheduleType(item.schedule_type),
                            reminder_time: this.sanitizeDueTime(item.reminder_time, '08:00') || '08:00',
                            active: !!item.active,
                            scheduled_today: !!item.scheduled_today,
                            done: !!item.done
                        }))
                        : [];
                    this.medicationsSummary = {
                        total: Number(payload.summary?.total || 0),
                        active: Number(payload.summary?.active || 0),
                        paused: Number(payload.summary?.paused || 0),
                        scheduled: Number(payload.summary?.scheduled || 0),
                        done: Number(payload.summary?.done || 0),
                        open: Number(payload.summary?.open || 0)
                    };
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

                getDefaultNotificationSettings() {
                    return {
                        enabled: true,
                        quiet_hours_enabled: true,
                        quiet_hours_start: '22:00',
                        quiet_hours_end: '07:00',
                        opening_enabled: true,
                        opening_time: '08:00',
                        day_summary_enabled: true,
                        day_summary_time: '20:30',
                        medication_enabled: true,
                        medication_repeat_enabled: false,
                        medication_repeat_minutes: 5,
                        medication_repeat_window_minutes: 120,
                        task_due_enabled: true,
                        task_reminder_enabled: true,
                        task_reminder_repeat_minutes: 120,
                        task_reminder_window_minutes: 480,
                        timezone: 'Europe/Warsaw'
                    };
                },

                resetNotificationSettingsDraft() {
                    this.notificationSettings = this.getDefaultNotificationSettings();
                    this.pushState.message = 'Przywrocono bezpieczne wartosci. Kliknij Zapisz, aby je zastosowac.';
                },

                useBrowserNotificationTimezone() {
                    const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
                    if (timezone) {
                        this.notificationSettings.timezone = timezone;
                        this.pushState.message = `Wykryta strefa: ${timezone}. Kliknij Zapisz.`;
                    }
                },

                async loadNotificationSettings() {
                    this.pushState.permission = typeof Notification === 'undefined' ? 'unsupported' : Notification.permission;
                    try {
                        const response = await fetch(`${this.API}/notifications/settings`);
                        if (!response.ok) throw new Error('notification_settings_failed');
                        const payload = await response.json();
                        this.notificationSettings = {
                            ...this.getDefaultNotificationSettings(),
                            ...(payload.settings || {})
                        };
                        this.pushState.subscriptionCount = Number(payload.subscription_count || 0);
                        this.pushState.vapidConfigured = !!payload.vapid_configured;
                    } catch (error) {
                        this.notificationSettings = this.getDefaultNotificationSettings();
                    }
                    await this.refreshPushState();
                },

                async loadNotificationHistory() {
                    this.notificationHistoryLoading = true;
                    try {
                        const response = await fetch(`${this.API}/notifications/history?limit=30`);
                        if (!response.ok) throw new Error('notification_history_failed');
                        const payload = await response.json();
                        this.notificationHistory = Array.isArray(payload.items) ? payload.items : [];
                    } catch (error) {
                        this.notificationHistory = [];
                    } finally {
                        this.notificationHistoryLoading = false;
                    }
                },

                getNotificationHistoryKindLabel(kind) {
                    return ({
                        opening: 'Start dnia',
                        day_summary: 'Podsumowanie',
                        medication: 'Leki',
                        medication_repeat: 'Leki · ponowienie',
                        task_due: 'Termin zadania',
                        task_overdue: 'Zadania po terminie',
                        test: 'Test'
                    })[kind] || 'Powiadomienie';
                },

                formatNotificationHistoryDate(value) {
                    const parsed = new Date(value || '');
                    if (Number.isNaN(parsed.getTime())) return value || '';
                    return new Intl.DateTimeFormat('pl-PL', {
                        day: '2-digit',
                        month: '2-digit',
                        hour: '2-digit',
                        minute: '2-digit'
                    }).format(parsed);
                },

                isIOSDevice() {
                    return /iPad|iPhone|iPod/.test(navigator.userAgent || '') || (
                        navigator.platform === 'MacIntel' && Number(navigator.maxTouchPoints || 0) > 1
                    );
                },

                isStandalonePWA() {
                    return window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone === true;
                },

                async registerServiceWorker() {
                    this.pushState.supported = 'serviceWorker' in navigator && 'PushManager' in window && typeof Notification !== 'undefined';
                    if (!this.pushState.supported) {
                        this.pushState.message = this.isIOSDevice() && !this.isStandalonePWA()
                            ? 'Na iPhonie powiadomienia wlaczysz po otwarciu aplikacji z ikony na ekranie glownym.'
                            : 'Ta przegladarka nie wspiera Web Push.';
                        return null;
                    }
                    try {
                        const registration = await navigator.serviceWorker.register('/sw.js', { scope: '/' });
                        this.pushState.serviceWorkerReady = true;
                        await this.refreshPushState(registration);
                        return registration;
                    } catch (error) {
                        this.pushState.serviceWorkerReady = false;
                        this.pushState.message = 'Nie udalo sie zarejestrowac Service Workera.';
                        return null;
                    }
                },

                async refreshPushState(registration = null) {
                    this.pushState.supported = 'serviceWorker' in navigator && 'PushManager' in window && typeof Notification !== 'undefined';
                    this.pushState.permission = typeof Notification === 'undefined' ? 'unsupported' : Notification.permission;
                    if (!this.pushState.supported) return;
                    try {
                        const readyRegistration = registration || await navigator.serviceWorker.ready;
                        const subscription = await readyRegistration.pushManager.getSubscription();
                        this.pushState.subscribed = !!subscription;
                        if (this.pushState.permission === 'granted') {
                            if (!subscription && this.pushState.vapidConfigured && this.notificationSettings.enabled) {
                                const recreated = await this.recreatePushSubscription(readyRegistration, { quiet: true });
                                this.pushState.subscribed = !!recreated;
                            } else if (subscription && this.pushState.vapidConfigured && Number(this.pushState.subscriptionCount || 0) <= 0) {
                                const recreated = await this.recreatePushSubscription(readyRegistration, { quiet: true });
                                this.pushState.subscribed = !!recreated;
                            } else if (subscription && (this.pushState.vapidConfigured || Number(this.pushState.subscriptionCount || 0) > 0)) {
                                await this.savePushSubscription(subscription, { quiet: true });
                            }
                        }
                    } catch (error) {
                        this.pushState.subscribed = false;
                    }
                },

                async loadVapidPublicKey() {
                    if (this.pushState.publicKey) return this.pushState.publicKey;
                    const response = await fetch(`${this.API}/notifications/vapid-public-key`);
                    if (!response.ok) throw new Error('vapid_key_failed');
                    const payload = await response.json();
                    this.pushState.publicKey = payload.public_key || '';
                    this.pushState.vapidConfigured = !!payload.configured;
                    return this.pushState.publicKey;
                },

                urlBase64ToUint8Array(base64String) {
                    const padding = '='.repeat((4 - base64String.length % 4) % 4);
                    const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
                    const rawData = window.atob(base64);
                    const outputArray = new Uint8Array(rawData.length);
                    for (let index = 0; index < rawData.length; index++) {
                        outputArray[index] = rawData.charCodeAt(index);
                    }
                    return outputArray;
                },

                async savePushSubscription(subscription, options = {}) {
                    if (!subscription) return false;
                    const response = await fetch(`${this.API}/notifications/subscribe`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            subscription: subscription.toJSON(),
                            user_agent: navigator.userAgent || ''
                        })
                    });
                    if (!response.ok) {
                        if (!options.quiet) {
                            this.showToast(await this.getApiErrorMessage(response, 'Nie udalo sie zapisac subskrypcji powiadomien.'));
                        }
                        return false;
                    }

                    const payload = await response.json();
                    this.pushState.subscribed = true;
                    this.pushState.subscriptionCount = Number(payload.subscription_count || 1);
                    return true;
                },

                async recreatePushSubscription(registration, options = {}) {
                    const publicKey = await this.loadVapidPublicKey();
                    if (!publicKey) return null;

                    const existing = await registration.pushManager.getSubscription();
                    if (existing) {
                        try {
                            await existing.unsubscribe();
                        } catch (error) {}
                    }

                    const subscription = await registration.pushManager.subscribe({
                        userVisibleOnly: true,
                        applicationServerKey: this.urlBase64ToUint8Array(publicKey)
                    });
                    const saved = await this.savePushSubscription(subscription, options);
                    return saved ? subscription : null;
                },

                async enablePushNotifications() {
                    if (!this.pushState.supported) {
                        this.showToast(this.isIOSDevice() && !this.isStandalonePWA()
                            ? 'Na iPhonie dodaj aplikacje do ekranu glownego i otworz ja z ikony.'
                            : 'Ta przegladarka nie wspiera Web Push.');
                        return;
                    }

                    const publicKey = await this.loadVapidPublicKey();
                    if (!publicKey) {
                        this.showToast('Brakuje VAPID_PUBLIC_KEY na backendzie. Wygeneruj klucze i dodaj je do .env.');
                        return;
                    }

                    // If your API lives on a different domain, replace this.API endpoints with that backend URL.
                    const permission = await Notification.requestPermission();
                    this.pushState.permission = permission;
                    if (permission !== 'granted') {
                        this.pushState.message = 'Powiadomienia nie dostaly zgody w przegladarce.';
                        return;
                    }

                    const registration = await navigator.serviceWorker.ready;
                    let subscription = await registration.pushManager.getSubscription();
                    if (!subscription) {
                        subscription = await registration.pushManager.subscribe({
                            userVisibleOnly: true,
                            applicationServerKey: this.urlBase64ToUint8Array(publicKey)
                        });
                    }

                    const saved = await this.savePushSubscription(subscription);
                    if (!saved) {
                        return;
                    }

                    this.pushState.message = 'Powiadomienia sa wlaczone na tym urzadzeniu.';
                },

                async disablePushNotifications() {
                    if (!this.pushState.supported) return;
                    const registration = await navigator.serviceWorker.ready;
                    const subscription = await registration.pushManager.getSubscription();
                    if (!subscription) {
                        this.pushState.subscribed = false;
                        return;
                    }
                    const endpoint = subscription.endpoint;
                    await subscription.unsubscribe();
                    await fetch(`${this.API}/notifications/unsubscribe`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ endpoint })
                    });
                    this.pushState.subscribed = false;
                    this.pushState.subscriptionCount = Math.max(0, Number(this.pushState.subscriptionCount || 0) - 1);
                    this.pushState.message = 'Powiadomienia wylaczone na tym urzadzeniu.';
                },

                async saveNotificationSettings() {
                    if (this.notificationSettingsSaving) return;
                    this.notificationSettingsSaving = true;
                    try {
                        const settings = {
                            ...this.notificationSettings,
                            medication_repeat_minutes: Math.max(1, Number(this.notificationSettings.medication_repeat_minutes || 5)),
                            medication_repeat_window_minutes: Math.max(1, Number(this.notificationSettings.medication_repeat_window_minutes || 120)),
                            task_reminder_repeat_minutes: Math.max(15, Number(this.notificationSettings.task_reminder_repeat_minutes || 120)),
                            task_reminder_window_minutes: Math.max(15, Number(this.notificationSettings.task_reminder_window_minutes || 480)),
                            timezone: (this.notificationSettings.timezone || 'Europe/Warsaw').trim() || 'Europe/Warsaw'
                        };
                        const response = await fetch(`${this.API}/notifications/settings`, {
                            method: 'PUT',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(settings)
                        });
                        if (!response.ok) {
                            this.showToast(await this.getApiErrorMessage(response, 'Nie udalo sie zapisac ustawien powiadomien.'));
                            return;
                        }
                        const payload = await response.json();
                        this.notificationSettings = {
                            ...this.getDefaultNotificationSettings(),
                            ...(payload.settings || {})
                        };
                        this.pushState.subscriptionCount = Number(payload.subscription_count || this.pushState.subscriptionCount || 0);
                        this.pushState.vapidConfigured = !!payload.vapid_configured;
                        this.pushState.message = 'Ustawienia powiadomien zapisane.';
                    } catch (error) {
                        this.showToast('Nie udalo sie zapisac ustawien. Sprawdz polaczenie i sprobuj ponownie.');
                    } finally {
                        this.notificationSettingsSaving = false;
                    }
                },

                async sendTestNotification() {
                    const response = await fetch(`${this.API}/notifications/test`, { method: 'POST' });
                    if (!response.ok) {
                        this.showToast(await this.getApiErrorMessage(response, 'Nie udalo sie wyslac testowego powiadomienia.'));
                        return;
                    }
                    this.pushState.message = 'Wyslano testowe powiadomienie.';
                    this.showToast('Test wysłany. Pojawił się też w historii.', 'success');
                    await this.loadNotificationHistory();
                },

                getPushPermissionLabel() {
                    if (this.pushState.permission === 'granted') return 'zgoda udzielona';
                    if (this.pushState.permission === 'denied') return 'zablokowane';
                    if (this.pushState.permission === 'unsupported') return 'brak wsparcia';
                    return 'czeka na zgode';
                },

                getNotificationStatusLabel() {
                    if (this.isIOSDevice() && !this.isStandalonePWA()) return 'otworz z ekranu glownego';
                    if (!this.pushState.supported) return 'brak wsparcia';
                    if (!this.pushState.vapidConfigured) return 'brak kluczy VAPID';
                    if (this.pushState.subscribed) return 'wlaczone na tym urzadzeniu';
                    return 'wylaczone na tym urzadzeniu';
                },

                async loadRewardSummary() {
                    try {
                        const response = await fetch(`${this.API}/rewards/summary`);
                        if (!response.ok) throw new Error('reward_summary_failed');
                        const payload = await response.json();
                        this.rewardSummary = {
                            earned_points: this.roundScore(payload?.earned_points || 0),
                            spent_points: this.roundScore(payload?.spent_points || 0),
                            available_points: this.roundScore(payload?.available_points || 0),
                            available_budget_pln: this.roundScore(payload?.available_budget_pln || 0),
                            point_value_pln: Number(payload?.point_value_pln) || 1
                        };
                    } catch (error) {
                        this.rewardSummary = {
                            earned_points: 0,
                            spent_points: 0,
                            available_points: 0,
                            available_budget_pln: 0,
                            point_value_pln: 1
                        };
                    }
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

                normalizeMonthlyRepeatType(value) {
                    const type = (value || 'monthly').toString().trim().toLowerCase();
                    return type.startsWith('week') ? 'weekly' : 'monthly';
                },

                normalizeMonthlyRepeatWeekday(value) {
                    const day = Math.round(Number(value || 1));
                    if (!Number.isFinite(day) || day < 1) return 1;
                    return Math.min(7, day);
                },

                normalizeMedicationScheduleType(value) {
                    const type = (value || 'daily').toString().trim().toLowerCase();
                    return ['weekdays', 'weekday', 'workdays', 'workday', 'pon-pt', 'mon-fri'].includes(type)
                        ? 'weekdays'
                        : 'daily';
                },

                getMedicationScheduleLabel(item) {
                    return this.normalizeMedicationScheduleType(item?.schedule_type) === 'weekdays'
                        ? 'pon-pt'
                        : 'codziennie';
                },

                getMedicationStatusLabel(item) {
                    if (!item?.active) return 'wstrzymany';
                    if (!item?.scheduled_today) return 'nie dzis';
                    return item?.done ? 'odhaczone' : 'do odhaczenia';
                },

                getMedicationStatusClass(item) {
                    if (!item?.active) return 'bg-violet-50 text-violet-700';
                    if (!item?.scheduled_today) return 'bg-slate-100 text-slate-500';
                    return item?.done ? 'bg-emerald-50 text-emerald-700' : 'bg-amber-50 text-amber-700';
                },

                resetMedicationDraft() {
                    this.editingMedicationId = null;
                    this.newMedication = {
                        name: '',
                        schedule_type: 'daily',
                        reminder_time: '08:00'
                    };
                },

                editMedication(medication) {
                    if (!medication) return;
                    this.editingMedicationId = Number(medication.id) || null;
                    this.newMedication = {
                        name: medication.name || '',
                        schedule_type: this.normalizeMedicationScheduleType(medication.schedule_type),
                        reminder_time: this.sanitizeDueTime(medication.reminder_time, '08:00') || '08:00'
                    };
                    window.requestAnimationFrame(() => {
                        document.querySelector('.meds-form-card')?.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    });
                },

                shiftMedicationsDate(step) {
                    this.medicationsDate = this.shiftDateKey(this.medicationsDate || this.getTodayKey(), step);
                    this.loadMedications();
                },

                goToMedicationsToday() {
                    this.medicationsDate = this.getTodayKey();
                    this.loadMedications();
                },

                getWeekdayLabel(weekday) {
                    const labels = ['poniedzialek', 'wtorek', 'sroda', 'czwartek', 'piatek', 'sobota', 'niedziela'];
                    return labels[this.normalizeMonthlyRepeatWeekday(weekday) - 1] || labels[0];
                },

                getMonthlyDueTime(task) {
                    return this.sanitizeDueTime(task?.due_time, '23:59') || '23:59';
                },

                getMonthlyDueLabel(task) {
                    const dueTime = this.getMonthlyDueTime(task);
                    if (task?.overdue && task?.date_key) {
                        const source = this.keyToDate(task.date_key);
                        return `zalegle od ${source.getDate()}.${String(source.getMonth() + 1).padStart(2, '0')} • ${dueTime}`;
                    }
                    if (this.normalizeMonthlyRepeatType(task?.repeat_type) === 'weekly') {
                        const dayLabel = this.getWeekdayLabel(task?.repeat_weekday);
                        if (task?.date_key) {
                            const date = this.keyToDate(task.date_key);
                            return `${dayLabel} • ${date.getDate()}.${String(date.getMonth() + 1).padStart(2, '0')} • ${dueTime}`;
                        }
                        return `co tydzien: ${dayLabel} • ${dueTime}`;
                    }
                    const dueDay = this.normalizeMonthlyDueDay(task?.due_day);
                    if (!dueDay) return 'bez dnia';
                    return `do ${dueDay}. dnia miesiaca • ${dueTime}`;
                },

                getMonthlyDueBadgeClass(task) {
                    if (task?.done) return 'bg-slate-100 text-slate-500';
                    if (task?.overdue) return 'bg-red-50 text-red-600';
                    const dateKey = this.sanitizeDateKey(task?.date_key);
                    if (!dateKey) return 'bg-slate-100 text-slate-500';
                    const currentMonth = this.getCurrentMonthKey();
                    if ((this.monthlyMonthKey || currentMonth) !== currentMonth) return 'bg-cyan-50 text-cyan-700';
                    const daysLeft = this.getDaysBetweenDateKeys(this.getTodayKey(), dateKey);
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

                getDebtPaymentNoun(item) {
                    return (item?.kind || 'debt') === 'fixed' ? 'Oplata' : 'Rata';
                },

                getDebtPaymentDoneLabel(item) {
                    const noun = this.getDebtPaymentNoun(item);
                    return item?.month_done
                        ? `${noun} odhaczona na ten miesiac`
                        : `Oznacz: ${noun.toLowerCase()} oplacona`;
                },

                getDebtMonthlyLabel(item) {
                    return (item?.kind || 'debt') === 'fixed' ? 'Kwota oplaty' : 'Rata mies.';
                },

                getDebtPrimaryAmountLabel(item) {
                    return (item?.kind || 'debt') === 'fixed' ? 'Koszt' : 'Calosc';
                },

                getDebtPrimaryAmount(item) {
                    return (item?.kind || 'debt') === 'fixed'
                        ? Number(item?.monthly_amount || 0)
                        : Number(item?.total_amount || 0);
                },

                getDebtsByKind(kind) {
                    return this.debts.filter(item => (item.kind || 'debt') === kind);
                },

                resetMonthlyTaskDraft() {
                    this.newMonthlyTaskName = '';
                    this.newMonthlyTaskDueDay = '';
                    this.newMonthlyTaskDueTime = '23:59';
                    this.newMonthlyTaskRepeatType = 'monthly';
                    this.newMonthlyTaskRepeatWeekday = 1;
                    this.editingMonthlyTaskId = null;
                },

                openMonthlyTaskModal(task = null) {
                    if (task && Number(task.id) > 0) {
                        this.editingMonthlyTaskId = Number(task.id);
                        this.newMonthlyTaskName = (task.name || '').toString();
                        this.newMonthlyTaskDueDay = this.normalizeMonthlyDueDay(task.due_day) || '';
                        this.newMonthlyTaskDueTime = this.getMonthlyDueTime(task);
                        this.newMonthlyTaskRepeatType = this.normalizeMonthlyRepeatType(task.repeat_type);
                        this.newMonthlyTaskRepeatWeekday = this.normalizeMonthlyRepeatWeekday(task.repeat_weekday);
                    } else {
                        this.resetMonthlyTaskDraft();
                    }
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
                    return this.monthlyTasks
                        .filter(task => this.sanitizeDateKey(task?.display_date_key || task?.date_key) === dateKey)
                        .map(task => ({
                            type: 'monthly',
                            id: `monthly-${task.instance_id || task.id}-${dateKey}`,
                            dateKey,
                            item: task,
                            done: !!task.done,
                            isCarriedOver: !!task.overdue,
                            delayDays: task?.overdue ? Math.max(0, this.getDaysBetweenDateKeys(task.date_key, dateKey)) : 0,
                            sourceDateKey: task.date_key
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
                        item: task,
                        isCarriedOver: false,
                        delayDays: 0,
                        sourceDateKey: task.due_date
                    }));
                    const monthlyEntries = this.getMonthlyEntriesForDate(dateKey);
                    const debtEntries = this.getDebtEntriesForDate(dateKey);
                    return this.sortCalendarEntries([...debtEntries, ...monthlyEntries, ...taskEntries]);
                },

                getCalendarAgendaEntriesForDate(dateKey) {
                    const cleanDateKey = this.sanitizeDateKey(dateKey);
                    if (!cleanDateKey) return [];
                    const todayKey = this.getTodayKey();
                    const allowCarryOver = cleanDateKey <= todayKey;

                    const taskEntries = this.getOpenTasks()
                        .filter(task => {
                            const dueDate = this.sanitizeDateKey(task?.due_date);
                            if (!dueDate) return false;
                            if (dueDate === cleanDateKey) return true;
                            return allowCarryOver && dueDate < cleanDateKey;
                        })
                        .map(task => {
                            const delayDays = Math.max(0, this.getDaysBetweenDateKeys(task.due_date, cleanDateKey));
                            return {
                                type: 'task',
                                id: `agenda-task-${task.id}-${cleanDateKey}`,
                                dateKey: cleanDateKey,
                                item: task,
                                isCarriedOver: delayDays > 0,
                                delayDays,
                                sourceDateKey: task.due_date
                            };
                        });

                    const monthlyEntries = this.getMonthlyEntriesForDate(cleanDateKey);
                    const debtEntries = this.getDebtEntriesForDate(cleanDateKey);
                    return this.sortCalendarEntries([...debtEntries, ...monthlyEntries, ...taskEntries]);
                },

                sortCalendarEntries(entries) {
                    return [...entries].sort((a, b) => {
                        const timeDiff = this.getCalendarEntrySortScore(a) - this.getCalendarEntrySortScore(b);
                        if (timeDiff !== 0) return timeDiff;
                        const urgencyDiff = this.getCalendarEntryUrgencyRank(a) - this.getCalendarEntryUrgencyRank(b);
                        if (urgencyDiff !== 0) return urgencyDiff;
                        const priorityDiff = this.getCalendarEntryPriorityRank(a) - this.getCalendarEntryPriorityRank(b);
                        if (priorityDiff !== 0) return priorityDiff;
                        const workflowDiff = this.getCalendarEntryWorkflowRank(a) - this.getCalendarEntryWorkflowRank(b);
                        if (workflowDiff !== 0) return workflowDiff;
                        const aName = (a.item?.name || '').toString();
                        const bName = (b.item?.name || '').toString();
                        return aName.localeCompare(bName, 'pl');
                    });
                },

                isCalendarTimelineEntry(entry) {
                    if (entry?.type === 'task') return !!this.getTaskDueTime(entry.item);
                    return entry?.type === 'monthly';
                },

                getDaysBetweenDateKeys(fromDateKey, toDateKey) {
                    const from = this.sanitizeDateKey(fromDateKey);
                    const to = this.sanitizeDateKey(toDateKey);
                    if (!from || !to) return 0;
                    return Math.round((this.keyToDate(to) - this.keyToDate(from)) / 86400000);
                },

                getCalendarPreviewDays() {
                    const startKey = this.sanitizeDateKey(this.selectedDate || this.calendarCursor || this.getTodayKey()) || this.getTodayKey();
                    const days = [];
                    for (let offset = 0; offset < 3; offset++) {
                        const dateKey = this.shiftDateKey(startKey, offset);
                        const workload = this.getDayWorkloadSummary(dateKey);
                        const entries = this.getCalendarAgendaEntriesForDate(dateKey);
                        const dayDraft = { dateKey, entries };
                        dayDraft.timelineMetrics = this.getCalendarTimelineMetrics(dayDraft, entries);
                        dayDraft.timelineEntries = this.getCalendarTimelineTaskEntries(entries, dayDraft);
                        days.push({
                            dateKey,
                            isToday: dateKey === this.getTodayKey(),
                            isSelected: dateKey === this.selectedDate,
                            entries,
                            timelineMetrics: dayDraft.timelineMetrics,
                            timelineEntries: dayDraft.timelineEntries,
                            nonTaskEntries: entries.filter(entry => (
                                entry?.type === 'debt' ||
                                (entry?.type === 'task' && !this.getTaskDueTime(entry.item))
                            )),
                            plannedMinutes: workload.plannedMinutes,
                            isOverLimit: workload.isOverLimit
                        });
                    }
                    return days;
                },

                getCalendarPreviewEntriesCount() {
                    return this.getCalendarPreviewDays().reduce((sum, day) => sum + (day.entries?.length || 0), 0);
                },

                formatCalendarPreviewWeekday(dateKey) {
                    return new Intl.DateTimeFormat('pl-PL', { weekday: 'long' }).format(this.keyToDate(dateKey));
                },

                formatCalendarPreviewDay(dateKey) {
                    return new Intl.DateTimeFormat('pl-PL', { day: 'numeric', month: 'long' }).format(this.keyToDate(dateKey));
                },

                getCalendarTimelineWindow(day = null, entries = null) {
                    const sourceEntries = Array.isArray(entries) ? entries : (day?.entries || []);
                    const taskRanges = sourceEntries
                        .filter(entry => this.isCalendarTimelineEntry(entry))
                        .map(entry => this.getCalendarTaskTimelineRange(entry));

                    const fallbackStart = 6 * 60;
                    const fallbackEnd = 24 * 60;
                    if (taskRanges.length === 0) {
                        return {
                            dayStart: fallbackStart,
                            dayEnd: fallbackEnd,
                            startHour: 6,
                            endHour: 23
                        };
                    }

                    const minTaskStart = Math.min(...taskRanges.map(range => range.startMinutes));
                    const maxTaskEnd = Math.max(...taskRanges.map(range => range.endMinutes));
                    const bufferBefore = 75;
                    const bufferAfter = 90;
                    const roundStep = 30;

                    let dayStart = Math.floor((Math.max(0, minTaskStart - bufferBefore)) / roundStep) * roundStep;
                    let dayEnd = Math.ceil((Math.min(24 * 60, maxTaskEnd + bufferAfter)) / roundStep) * roundStep;

                    if (day?.dateKey && this.sanitizeDateKey(day.dateKey) === this.getTodayKey()) {
                        const now = new Date();
                        const nowMinutes = (now.getHours() * 60) + now.getMinutes();
                        dayStart = Math.min(dayStart, Math.floor(Math.max(0, nowMinutes - 60) / roundStep) * roundStep);
                        dayEnd = Math.max(dayEnd, Math.ceil(Math.min(24 * 60, nowMinutes + 60) / roundStep) * roundStep);
                    }

                    dayStart = Math.max(0, dayStart);
                    dayEnd = Math.min(24 * 60, dayEnd);

                    const minWindowMinutes = 4 * 60;
                    if ((dayEnd - dayStart) < minWindowMinutes) {
                        const midpoint = (minTaskStart + maxTaskEnd) / 2;
                        dayStart = Math.floor(Math.max(0, midpoint - (minWindowMinutes / 2)) / roundStep) * roundStep;
                        dayEnd = Math.min(24 * 60, dayStart + minWindowMinutes);
                        if ((dayEnd - dayStart) < minWindowMinutes) {
                            dayStart = Math.max(0, dayEnd - minWindowMinutes);
                        }
                    }

                    if (dayEnd <= dayStart) {
                        dayStart = fallbackStart;
                        dayEnd = fallbackEnd;
                    }

                    return {
                        dayStart,
                        dayEnd,
                        startHour: Math.floor(dayStart / 60),
                        endHour: Math.max(Math.floor((dayEnd - 1) / 60), Math.floor(dayStart / 60))
                    };
                },

                getCalendarTimelineGapScale() {
                    return 0.22;
                },

                getCalendarTimelineSegments(taskRanges, dayStart, dayEnd) {
                    const safeStart = Math.max(0, Math.min(24 * 60, Math.round(dayStart)));
                    const safeEnd = Math.max(safeStart + 60, Math.min(24 * 60, Math.round(dayEnd)));
                    const focusPaddingMinutes = 26;
                    const gapScale = this.getCalendarTimelineGapScale();

                    const focusRanges = taskRanges
                        .map(range => ({
                            start: Math.max(safeStart, range.startMinutes - focusPaddingMinutes),
                            end: Math.min(safeEnd, range.endMinutes + focusPaddingMinutes),
                        }))
                        .filter(range => range.end > range.start)
                        .sort((a, b) => a.start - b.start);

                    const mergedFocusRanges = [];
                    for (const range of focusRanges) {
                        const previous = mergedFocusRanges[mergedFocusRanges.length - 1];
                        if (!previous || range.start > previous.end) {
                            mergedFocusRanges.push({ ...range });
                        } else {
                            previous.end = Math.max(previous.end, range.end);
                        }
                    }

                    const segments = [];
                    const appendSegment = (startMinute, endMinute, scale) => {
                        if (endMinute <= startMinute) return;
                        const previous = segments[segments.length - 1];
                        if (previous && previous.scale === scale && Math.abs(previous.endMinute - startMinute) < 0.001) {
                            previous.endMinute = endMinute;
                            return;
                        }
                        segments.push({
                            startMinute,
                            endMinute,
                            scale,
                            renderStartMinute: 0,
                            renderEndMinute: 0,
                        });
                    };

                    let cursor = safeStart;
                    for (const focus of mergedFocusRanges) {
                        if (focus.start > cursor) {
                            appendSegment(cursor, focus.start, gapScale);
                        }
                        appendSegment(Math.max(cursor, focus.start), focus.end, 1);
                        cursor = Math.max(cursor, focus.end);
                    }
                    if (cursor < safeEnd) {
                        appendSegment(cursor, safeEnd, gapScale);
                    }
                    if (segments.length === 0) {
                        appendSegment(safeStart, safeEnd, 1);
                    }

                    let virtualCursor = 0;
                    for (const segment of segments) {
                        const duration = Math.max(0, segment.endMinute - segment.startMinute);
                        const virtualDuration = duration * segment.scale;
                        segment.renderStartMinute = virtualCursor;
                        segment.renderEndMinute = virtualCursor + virtualDuration;
                        virtualCursor = segment.renderEndMinute;
                    }

                    return {
                        segments,
                        virtualSpan: Math.max(60, virtualCursor),
                        compressionApplied: segments.some(segment => segment.scale < 1),
                    };
                },

                mapTimelineRealMinuteToRenderMinute(totalMinutes, metrics) {
                    const safeMinutes = Math.max(metrics.dayStart, Math.min(metrics.dayEnd, Number(totalMinutes) || metrics.dayStart));
                    for (let index = 0; index < metrics.timelineSegments.length; index++) {
                        const segment = metrics.timelineSegments[index];
                        if (safeMinutes <= segment.endMinute || index === metrics.timelineSegments.length - 1) {
                            const offsetMinutes = Math.max(0, safeMinutes - segment.startMinute);
                            return segment.renderStartMinute + (offsetMinutes * segment.scale);
                        }
                    }
                    return metrics.virtualSpan;
                },

                getCalendarTimelineMetrics(day = null, entries = null) {
                    if (day?.timelineMetrics) return day.timelineMetrics;

                    const sourceEntries = Array.isArray(entries) ? entries : (day?.entries || []);
                    const window = this.getCalendarTimelineWindow(day, sourceEntries);
                    const taskRanges = sourceEntries
                        .filter(entry => this.isCalendarTimelineEntry(entry))
                        .map(entry => this.getCalendarTaskTimelineRange(entry));

                    const segmentsData = this.getCalendarTimelineSegments(taskRanges, window.dayStart, window.dayEnd);
                    const daySpan = Math.max(60, window.dayEnd - window.dayStart);
                    const edgePaddingMinutes = Math.max(
                        8,
                        Math.floor(this.getCalendarTimelineMinCardMinutes() / 2)
                    );
                    const metrics = {
                        startHour: window.startHour,
                        endHour: window.endHour,
                        dayStart: window.dayStart,
                        dayEnd: window.dayEnd,
                        daySpan,
                        edgePaddingMinutes,
                        renderSpan: segmentsData.virtualSpan + (edgePaddingMinutes * 2),
                        virtualSpan: segmentsData.virtualSpan,
                        timelineSegments: segmentsData.segments,
                        compressionApplied: segmentsData.compressionApplied,
                    };

                    if (day && typeof day === 'object') {
                        day.timelineMetrics = metrics;
                    }
                    return metrics;
                },

                getCalendarTimelineHourMarkers(day = null) {
                    const metrics = this.getCalendarTimelineMetrics(day);
                    const startHour = Math.floor(metrics.dayStart / 60);
                    const endHour = Math.ceil(metrics.dayEnd / 60);
                    const markers = [];
                    for (let hour = startHour; hour <= endHour; hour++) {
                        const minuteMark = hour * 60;
                        if (minuteMark < metrics.dayStart || minuteMark > metrics.dayEnd) continue;
                        const minuteOffset = metrics.edgePaddingMinutes + this.mapTimelineRealMinuteToRenderMinute(minuteMark, metrics);
                        markers.push({
                            hour,
                            label: `${String(hour).padStart(2, '0')}:00`,
                            offsetPercent: (minuteOffset / metrics.renderSpan) * 100
                        });
                    }
                    return markers;
                },

                timeLabelToMinutes(timeValue, fallbackMinutes = (23 * 60) + 59) {
                    const clean = this.sanitizeDueTime(timeValue, '');
                    if (!clean) return fallbackMinutes;
                    const [hours, minutes] = clean.split(':').map(Number);
                    return ((hours || 0) * 60) + (minutes || 0);
                },

                minutesToTimeLabel(totalMinutes) {
                    const safe = Math.max(0, Math.min(24 * 60, Math.round(Number(totalMinutes) || 0)));
                    const hours = Math.floor(safe / 60);
                    const minutes = safe % 60;
                    return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}`;
                },

                getCalendarTaskTimelineRange(entry) {
                    const dueTime = this.getCalendarEntryTime(entry);
                    const dueMinutes = this.timeLabelToMinutes(dueTime, (23 * 60) + 59);
                    const durationMinutes = entry?.type === 'task'
                        ? Math.max(15, this.getTaskEffectiveEstimatedMinutes(entry?.item))
                        : 30;
                    const startMinutes = Math.max(0, dueMinutes);
                    const endMinutes = Math.min(24 * 60, Math.max(startMinutes + 15, dueMinutes + durationMinutes));
                    return {
                        startMinutes,
                        endMinutes,
                        durationMinutes: Math.max(15, endMinutes - startMinutes)
                    };
                },

                getCalendarTimelineTaskEntries(entries, day = null) {
                    const metrics = this.getCalendarTimelineMetrics(day, entries);
                    const { dayStart, dayEnd, virtualSpan } = metrics;

                    const taskEntries = (entries || [])
                        .filter(entry => this.isCalendarTimelineEntry(entry))
                        .map(entry => {
                            const range = this.getCalendarTaskTimelineRange(entry);
                            const clampedStart = Math.max(dayStart, Math.min(dayEnd, range.startMinutes));
                            const clampedEnd = Math.max(clampedStart + 1, Math.min(dayEnd, range.endMinutes));
                            const mappedStart = this.mapTimelineRealMinuteToRenderMinute(clampedStart, metrics);
                            const mappedEnd = this.mapTimelineRealMinuteToRenderMinute(clampedEnd, metrics);
                            const visualMinutes = Math.max(
                                this.getCalendarTimelineMinCardMinutes(),
                                mappedEnd - mappedStart,
                            );
                            const renderStart = Math.max(0, Math.min(mappedStart, virtualSpan - visualMinutes));
                            return {
                                ...entry,
                                timelineStartMinutes: range.startMinutes,
                                timelineEndMinutes: range.endMinutes,
                                timelineDurationMinutes: range.durationMinutes,
                                timelineVisualMinutes: visualMinutes,
                                timelineRenderStartMinutes: renderStart,
                                timelineRenderEndMinutes: renderStart + visualMinutes,
                                timelineLane: 0,
                                timelineLaneCount: 1
                            };
                        })
                        .sort((a, b) => {
                            const startDiff = a.timelineStartMinutes - b.timelineStartMinutes;
                            if (startDiff !== 0) return startDiff;
                            const endDiff = a.timelineEndMinutes - b.timelineEndMinutes;
                            if (endDiff !== 0) return endDiff;
                            const dueDiff = this.getCalendarEntrySortScore(a) - this.getCalendarEntrySortScore(b);
                            if (dueDiff !== 0) return dueDiff;
                            return (a.item?.name || '').localeCompare((b.item?.name || ''), 'pl');
                        });

                    if (taskEntries.length === 0) return [];

                    const laneEndMinutes = [];
                    for (let index = 0; index < taskEntries.length; index++) {
                        const entry = taskEntries[index];
                        let lane = laneEndMinutes.findIndex(endMinute => endMinute <= entry.timelineRenderStartMinutes);
                        if (lane === -1) lane = laneEndMinutes.length;
                        laneEndMinutes[lane] = entry.timelineRenderEndMinutes;
                        entry.timelineLane = lane;
                        entry.timelineIndex = index;
                    }

                    const overlaps = (first, second) => (
                        first.timelineRenderStartMinutes < second.timelineRenderEndMinutes &&
                        second.timelineRenderStartMinutes < first.timelineRenderEndMinutes
                    );

                    const parent = taskEntries.map((_, index) => index);
                    const find = (index) => {
                        if (parent[index] !== index) parent[index] = find(parent[index]);
                        return parent[index];
                    };
                    const union = (first, second) => {
                        const rootA = find(first);
                        const rootB = find(second);
                        if (rootA !== rootB) parent[rootB] = rootA;
                    };

                    for (let first = 0; first < taskEntries.length; first++) {
                        for (let second = first + 1; second < taskEntries.length; second++) {
                            if (taskEntries[second].timelineRenderStartMinutes >= taskEntries[first].timelineRenderEndMinutes) break;
                            if (overlaps(taskEntries[first], taskEntries[second])) {
                                union(first, second);
                            }
                        }
                    }

                    const groupLaneCount = new Map();
                    for (let index = 0; index < taskEntries.length; index++) {
                        const root = find(index);
                        const lanes = Math.max(
                            groupLaneCount.get(root) || 1,
                            Number(taskEntries[index].timelineLane || 0) + 1
                        );
                        groupLaneCount.set(root, lanes);
                    }

                    return taskEntries.map((entry, index) => ({
                        ...entry,
                        timelineLaneCount: groupLaneCount.get(find(index)) || 1
                    }));
                },

                getCalendarTimelinePixelsPerMinute() {
                    return 1.62;
                },

                getCalendarTimelineMinCardMinutes() {
                    const minCardHeightPx = 54;
                    return Math.ceil(minCardHeightPx / this.getCalendarTimelinePixelsPerMinute());
                },

                getCalendarTimelineVisualMinutes(durationMinutes) {
                    const safeDuration = Math.max(15, Number(durationMinutes) || 15);
                    return Math.max(safeDuration, this.getCalendarTimelineMinCardMinutes());
                },

                getCalendarTimelineTaskDensityClass(entry) {
                    const visualMinutes = Number(entry?.timelineVisualMinutes || 0);
                    return visualMinutes <= (this.getCalendarTimelineMinCardMinutes() + 6)
                        ? 'calendar-timeline-task-compact'
                        : '';
                },

                getCalendarTimelineBoardStyle(day) {
                    const { renderSpan } = this.getCalendarTimelineMetrics(day);
                    const pixelsPerMinute = this.getCalendarTimelinePixelsPerMinute();
                    const boardHeight = Math.round(renderSpan * pixelsPerMinute);
                    return `min-height:${Math.max(520, boardHeight)}px`;
                },

                getCalendarTimelineEntryStyle(entry, day = null) {
                    const { virtualSpan, edgePaddingMinutes, renderSpan } = this.getCalendarTimelineMetrics(day);
                    const visualMinutes = Math.max(1, Number(entry?.timelineVisualMinutes || this.getCalendarTimelineMinCardMinutes()));
                    const safeVisualMinutes = Math.min(virtualSpan, visualMinutes);
                    const renderStart = Math.max(
                        0,
                        Math.min(virtualSpan - safeVisualMinutes, Number(entry?.timelineRenderStartMinutes ?? 0))
                    );
                    const topPercent = ((edgePaddingMinutes + renderStart) / renderSpan) * 100;
                    const heightPercent = (safeVisualMinutes / renderSpan) * 100;
                    const laneCount = Math.max(1, Number(entry?.timelineLaneCount || 1));
                    const lane = Math.max(0, Math.min(laneCount - 1, Number(entry?.timelineLane || 0)));
                    const laneWidth = 100 / laneCount;
                    const laneGapPercent = Math.min(0.8, laneWidth * 0.14);
                    const leftPercent = (lane * laneWidth) + (laneGapPercent / 2);
                    const widthPercent = Math.max(1.2, laneWidth - laneGapPercent);
                    return `top:${topPercent.toFixed(3)}%;height:${heightPercent.toFixed(3)}%;left:${leftPercent.toFixed(3)}%;width:${widthPercent.toFixed(3)}%`;
                },

                getCalendarTimelineTimeRangeLabel(entry) {
                    const startLabel = this.minutesToTimeLabel(entry?.timelineStartMinutes || 0);
                    const endLabel = this.minutesToTimeLabel(entry?.timelineEndMinutes || 0);
                    return `${startLabel} - ${endLabel}`;
                },

                getCalendarTimelineNowStyle(day = null) {
                    if (!day?.dateKey || this.sanitizeDateKey(day.dateKey) !== this.getTodayKey()) return '';
                    const metrics = this.getCalendarTimelineMetrics(day);
                    const now = new Date();
                    const nowMinutes = (now.getHours() * 60) + now.getMinutes();
                    const clamped = Math.max(metrics.dayStart, Math.min(metrics.dayEnd, nowMinutes));
                    const mapped = this.mapTimelineRealMinuteToRenderMinute(clamped, metrics);
                    const topPercent = ((metrics.edgePaddingMinutes + mapped) / metrics.renderSpan) * 100;
                    return `top:${topPercent.toFixed(3)}%`;
                },

                getCalendarEntryTime(entry) {
                    if (entry?.type === 'task') return this.getTaskDueTime(entry.item);
                    if (entry?.type === 'monthly') return this.getMonthlyDueTime(entry.item);
                    return '';
                },

                getCalendarEntrySortScore(entry) {
                    if (entry?.type === 'task' || entry?.type === 'monthly') {
                        const dueTime = this.getCalendarEntryTime(entry);
                        if (/^([01]\d|2[0-3]):[0-5]\d$/.test(dueTime)) {
                            const [hours, minutes] = dueTime.split(':').map(Number);
                            return (hours * 60) + minutes;
                        }
                        return 24 * 60;
                    }
                    if (entry?.type === 'debt') return (24 * 60) + 10;
                    return (24 * 60) + 30;
                },

                getCalendarEntryUrgencyRank(entry) {
                    if (entry?.type === 'monthly') return entry?.isCarriedOver ? 0 : 3;
                    if (entry?.type !== 'task') return 4;
                    if (entry?.isCarriedOver || this.isTaskOverdue(entry?.item)) return 0;
                    if (this.normalizePriorityValue(entry?.item?.priority) === 'P1') return 1;
                    return 2;
                },

                getCalendarEntryPriorityRank(entry) {
                    if (entry?.type !== 'task') return 4;
                    return this.priorityRank(entry?.item?.priority);
                },

                getCalendarEntryWorkflowRank(entry) {
                    if (entry?.type !== 'task') return 6;
                    return this.statusRank(entry?.item?.status);
                },

                getCalendarTaskUrgencyLabel(entry) {
                    if (entry?.type !== 'task') return '';
                    if (entry?.isCarriedOver) {
                        return entry.delayDays <= 1 ? 'opoznione' : `opoznione ${entry.delayDays} dni`;
                    }
                    const task = entry?.item;
                    if (this.isTaskOverdue(task)) {
                        const days = this.daysUntilDue(task);
                        return days < 0 ? `${Math.abs(days)} d. po terminie` : 'po terminie';
                    }
                    const days = this.daysUntilDue(task);
                    if (days === 0) return 'na dzis';
                    if (days === 1) return 'jutro';
                    if (days !== null && days > 1 && days <= 7) return `za ${days} dni`;
                    if (this.normalizePriorityValue(task?.priority) === 'P1') return 'pilne';
                    return 'niepilne';
                },

                getCalendarTaskUrgencyClass(entry) {
                    if (entry?.type !== 'task') return 'calendar-entry-urgency-normal';
                    const task = entry?.item;
                    if (entry?.isCarriedOver || this.isTaskOverdue(task)) return 'calendar-entry-urgency-overdue';
                    const days = this.daysUntilDue(task);
                    if (days === 0) return 'calendar-entry-urgency-today';
                    if (days === 1 || (days !== null && days > 1 && days <= 7)) return 'calendar-entry-urgency-upcoming';
                    if (this.normalizePriorityValue(task?.priority) === 'P1') return 'calendar-entry-urgency-urgent';
                    return 'calendar-entry-urgency-normal';
                },

                getCalendarTaskStateClass(entry) {
                    if (entry?.type !== 'task') return '';
                    return (entry?.isCarriedOver || this.isTaskOverdue(entry?.item)) ? 'calendar-entry-overdue' : '';
                },

                getCalendarTaskStatusLabel(entry) {
                    if (entry?.type !== 'task') return '';
                    const normalized = this.normalizeTaskStatus(entry?.item?.status);
                    return {
                        todo: 'w toku',
                        przygotowanie: 'przygot.',
                        oczekujace: 'oczek.'
                    }[normalized] || normalized;
                },

                getCalendarTaskStatusClass(entry) {
                    if (entry?.type !== 'task') return 'calendar-entry-status-waiting';
                    const normalized = this.normalizeTaskStatus(entry?.item?.status);
                    return {
                        todo: 'calendar-entry-status-todo',
                        przygotowanie: 'calendar-entry-status-prep',
                        oczekujace: 'calendar-entry-status-waiting'
                    }[normalized] || 'calendar-entry-status-waiting';
                },

                getCalendarCarryOverLabel(entry) {
                    if (!entry?.isCarriedOver) return '';
                    if (entry.delayDays <= 1) return 'z wczoraj';
                    return `z ${entry.delayDays} dni temu`;
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

                sanitizeDueTime(value, fallback = '23:59') {
                    const clean = (value || '').toString().trim();
                    if (/^([01]\d|2[0-3]):[0-5]\d$/.test(clean)) return clean;
                    if (/^([01]\d|2[0-3]):[0-5]\d:[0-5]\d$/.test(clean)) return clean.slice(0, 5);
                    if (/^([01]\d|2[0-3]):[0-5]\d$/.test((fallback || '').toString().trim())) {
                        return (fallback || '').toString().trim();
                    }
                    return '';
                },

                getTaskDueDateTime(task) {
                    const dueDate = this.sanitizeDateKey(task?.due_date);
                    if (!dueDate) return null;
                    const dueTime = this.sanitizeDueTime(task?.due_time, '');
                    const [hours, minutes] = (dueTime || '23:59').split(':').map(Number);
                    const due = this.keyToDate(dueDate);
                    due.setHours(hours || 0, minutes || 0, 0, 0);
                    return due;
                },

                getTaskDueTime(task) {
                    if (!this.sanitizeDateKey(task?.due_date)) return '';
                    return this.sanitizeDueTime(task?.due_time, '');
                },

                getTaskDoneDateKey(task) {
                    const description = (task?.description || '').toString();
                    const matches = [...description.matchAll(/\[Done:\s*(\d{4}-\d{2}-\d{2})\]/g)];
                    if (matches.length === 0) return '';
                    return this.sanitizeDateKey(matches[matches.length - 1][1]);
                },

                getTaskWorkloadMinutesForDate(task, dateKey) {
                    const cleanDate = this.sanitizeDateKey(dateKey);
                    if (!cleanDate) return 0;
                    if (this.normalizeTaskStatus(task?.status) === 'gotowe') {
                        const taskDoneMinutes = this.getTaskDoneDateKey(task) === cleanDate
                            ? this.getTaskEffectiveEstimatedMinutes(task)
                            : 0;
                        return taskDoneMinutes || this.getSubtasksWorkloadMinutesForDate(task?.subtasks, cleanDate);
                    }
                    const plannedMinutes = this.sanitizeDateKey(task?.due_date) === cleanDate
                        ? this.getTaskEffectiveEstimatedMinutes(task)
                        : 0;
                    return plannedMinutes || this.getSubtasksWorkloadMinutesForDate(task?.subtasks, cleanDate);
                },

                getSubtasksWorkloadMinutesForDate(subtasks, dateKey) {
                    const cleanDate = this.sanitizeDateKey(dateKey);
                    if (!cleanDate) return 0;
                    return this.normalizeSubtasks(subtasks).reduce((sum, subtask) => (
                        this.getSubtaskDoneDateKey(subtask) === cleanDate
                            ? sum + this.normalizeSubtaskEstimatedMinutes(subtask?.estimated_time)
                            : sum
                    ), 0);
                },

                getPlannedMinutesForDate(dateKey, excludeTaskId = null) {
                    const cleanDate = this.sanitizeDateKey(dateKey);
                    if (!cleanDate) return 0;
                    return this.tasks.reduce((sum, task) => {
                        if (excludeTaskId && Number(task?.id) === Number(excludeTaskId)) return sum;
                        return sum + this.getTaskWorkloadMinutesForDate(task, cleanDate);
                    }, 0);
                },

                isWorkdayOverLimitByMinutes(minutes) {
                    return this.normalizeEstimatedMinutes(minutes) > this.workdayLimitMinutes;
                },

                isDateOverWorkdayLimit(dateKey) {
                    return this.isWorkdayOverLimitByMinutes(this.getPlannedMinutesForDate(dateKey));
                },

                getDayWorkloadSummary(dateKey) {
                    const plannedMinutes = this.getPlannedMinutesForDate(dateKey);
                    const limitMinutes = this.workdayLimitMinutes;
                    return {
                        plannedMinutes,
                        limitMinutes,
                        isOverLimit: plannedMinutes > limitMinutes
                    };
                },

                getSelectedDateWorkloadSummary() {
                    return this.getDayWorkloadSummary(this.selectedDate || this.getTodayKey());
                },

                getCalendarOverloadedDaysCount() {
                    return this.getMonthDays().filter(day => day.isCurrentMonth && day.isOverLimit).length;
                },

                getCalendarVisiblePlannedMinutes() {
                    return this.getMonthDays()
                        .filter(day => day.isCurrentMonth)
                        .reduce((sum, day) => sum + (day.plannedMinutes || 0), 0);
                },

                getEditingTaskProjectedMinutes() {
                    const isDone = this.normalizeTaskStatus(this.editingTask?.status) === 'gotowe';
                    const cleanDueDate = this.sanitizeDateKey(this.editingTask?.due_date);
                    const workloadDate = isDone
                        ? (this.getTaskDoneDateKey(this.editingTask) || this.getTodayKey())
                        : cleanDueDate;
                    if (!workloadDate) {
                        return {
                            date: '',
                            total: 0,
                            limit: this.workdayLimitMinutes,
                            over: false
                        };
                    }

                    const baseMinutes = this.getPlannedMinutesForDate(workloadDate, this.editingTask?.id || null);
                    const taskMinutes = this.getTaskEffectiveEstimatedMinutes(this.editingTask);
                    const totalMinutes = baseMinutes + taskMinutes;
                    return {
                        date: workloadDate,
                        total: totalMinutes,
                        limit: this.workdayLimitMinutes,
                        over: totalMinutes > this.workdayLimitMinutes
                    };
                },

                getEditingTaskWorkloadLabel() {
                    const preview = this.getEditingTaskProjectedMinutes();
                    if (!preview.date) return 'Wybierz termin, aby policzyc obciazenie dnia.';
                    return `${this.formatDurationMinutes(preview.total)} / ${this.formatDurationMinutes(preview.limit)} limitu`;
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
                    return module ? module.name : 'Bez modulu';
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
                    return { todo: 0, przygotowanie: 1, oczekujace: 3, obserwacja: 4, gotowe: 9 }[this.normalizeTaskStatus(status)] ?? 8;
                },

                daysUntilDue(task) {
                    if (!task?.due_date) return null;
                    const due = this.keyToDate(task.due_date);
                    const today = this.keyToDate(this.getTodayKey());
                    return Math.round((due - today) / 86400000);
                },

                isTaskOverdue(task) {
                    if (this.normalizeTaskStatus(task?.status) === 'gotowe') return false;
                    const dueAt = this.getTaskDueDateTime(task);
                    if (!dueAt) return false;
                    return Date.now() > dueAt.getTime();
                },

                isTaskDueToday(task) {
                    if (this.normalizeTaskStatus(task?.status) === 'gotowe') return false;
                    return this.daysUntilDue(task) === 0;
                },

                isTaskUpcoming(task) {
                    if (this.normalizeTaskStatus(task?.status) === 'gotowe') return false;
                    const days = this.daysUntilDue(task);
                    return days !== null && days > 0 && days <= 7;
                },

                dueSortValue(task) {
                    const dueAt = this.getTaskDueDateTime(task);
                    return dueAt ? dueAt.getTime() : Number.MAX_SAFE_INTEGER;
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
                        obserwacja: 'do obserwacji',
                        gotowe: 'gotowe'
                    }[this.normalizeTaskStatus(status)] || status;
                },

                hasConfiguredSubtaskTimes(subtasks) {
                    const normalized = this.normalizeSubtasks(subtasks);
                    return normalized.length > 0 && normalized.every(subtask => this.normalizeSubtaskEstimatedMinutes(subtask?.estimated_time) > 0);
                },

                hasConfiguredSubtaskPoints(subtasks) {
                    const normalized = this.normalizeSubtasks(subtasks);
                    return normalized.length > 0 && normalized.every(subtask => this.normalizeSubtaskPointsWeight(subtask?.points_weight) > 0);
                },

                getSubtasksTimeSum(subtasks) {
                    return this.normalizeSubtasks(subtasks).reduce(
                        (sum, subtask) => sum + this.normalizeSubtaskEstimatedMinutes(subtask?.estimated_time),
                        0
                    );
                },

                getSubtasksPointsSum(subtasks) {
                    return this.roundScore(this.normalizeSubtasks(subtasks).reduce(
                        (sum, subtask) => sum + this.normalizeSubtaskPointsWeight(subtask?.points_weight),
                        0
                    ));
                },

                getTaskEffectiveEstimatedMinutes(task) {
                    const subtasks = this.normalizeSubtasks(task?.subtasks);
                    if (this.hasConfiguredSubtaskTimes(subtasks)) {
                        return this.getSubtasksTimeSum(subtasks);
                    }
                    return this.normalizeEstimatedMinutes(task?.estimated_time);
                },

                getTaskEffectivePointsWeight(task) {
                    const subtasks = this.normalizeSubtasks(task?.subtasks);
                    if (this.hasConfiguredSubtaskPoints(subtasks)) {
                        return this.getSubtasksPointsSum(subtasks);
                    }
                    return this.normalizePointsWeight(task?.points_weight);
                },

                getTaskTimeLabel(task) {
                    const effectiveTime = this.getTaskEffectiveEstimatedMinutes(task);
                    const time = effectiveTime > 0 ? `${effectiveTime} min` : 'bez czasu';
                    const points = `${this.formatScore(this.getTaskEffectivePointsWeight(task))} pkt`;
                    const dueTime = this.getTaskDueTime(task);
                    return dueTime ? `${time} • ${points} • do ${dueTime}` : `${time} • ${points}`;
                },

                getTaskUrgencyLabel(task) {
                    if (this.normalizeTaskStatus(task?.status) === 'gotowe') return '';
                    const days = this.daysUntilDue(task);
                    if (days === null) return this.hasPriority(task) ? 'priorytet' : '';
                    if (this.isTaskOverdue(task)) {
                        if (days < 0) return `${Math.abs(days)} d. po terminie`;
                        return 'po terminie';
                    }
                    const dueTime = this.getTaskDueTime(task);
                    if (days === 0) return dueTime ? `na dzis ${dueTime}` : 'na dzis';
                    if (days === 1) return 'jutro';
                    if (days <= 7) return `za ${days} dni`;
                    return 'zaplanowane';
                },

                getUrgencyClass(task) {
                    const days = this.daysUntilDue(task);
                    if (this.isTaskOverdue(task)) return 'bg-red-50 text-red-600';
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
                    const value = prompt('Dzienny cel (punkty):', String(this.dailyGoal));
                    if (value === null) return;
                    const next = Number(value);
                    if (!Number.isFinite(next) || next <= 0) {
                        this.showToast('Podaj liczbe wieksza od 0.');
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

                getSubtaskDoneDateKey(subtask) {
                    if (!subtask?.done || !subtask?.done_at) return '';
                    const doneAt = new Date(subtask.done_at);
                    if (Number.isNaN(doneAt.getTime())) return '';
                    return this.dateToKey(doneAt);
                },

                getTaskPointsByDate(task, dateKey) {
                    const taskWeight = this.getTaskEffectivePointsWeight(task);
                    const subtasks = this.normalizeSubtasks(task?.subtasks);
                    if (subtasks.length > 0) {
                        const hasConfiguredPoints = this.hasConfiguredSubtaskPoints(subtasks);
                        const piece = hasConfiguredPoints ? 0 : (taskWeight / subtasks.length);
                        return subtasks.reduce((sum, subtask) => {
                            const doneDateKey = this.getSubtaskDoneDateKey(subtask);
                            if (doneDateKey !== dateKey) return sum;
                            if (hasConfiguredPoints) {
                                return sum + this.normalizeSubtaskPointsWeight(subtask?.points_weight);
                            }
                            return sum + piece;
                        }, 0);
                    }

                    const stamp = `[Done: ${dateKey}]`;
                    return task?.status === 'gotowe' && (task?.description || '').includes(stamp) ? taskWeight : 0;
                },

                hasDoneStamp(task) {
                    const description = (task?.description || '').toString();
                    return /\[Done:\s*\d{4}-\d{2}-\d{2}\]/.test(description);
                },

                getHistoricalTaskPointsFraction(task) {
                    const subtasks = this.normalizeSubtasks(task?.subtasks);
                    if (subtasks.length > 0) {
                        if (this.hasConfiguredSubtaskPoints(subtasks)) {
                            const donePoints = subtasks.reduce((sum, subtask) => {
                                const hasHistoryStamp = !!subtask?.done_at;
                                if (!(subtask?.done || hasHistoryStamp)) return sum;
                                return sum + this.normalizeSubtaskPointsWeight(subtask?.points_weight);
                            }, 0);
                            const totalPoints = this.getSubtasksPointsSum(subtasks);
                            if (totalPoints <= 0) return 0;
                            return Math.min(1, donePoints / totalPoints);
                        }
                        const doneCount = subtasks.reduce((count, subtask) => {
                            const hasHistoryStamp = !!subtask?.done_at;
                            return count + (subtask?.done || hasHistoryStamp ? 1 : 0);
                        }, 0);
                        return Math.min(1, doneCount / subtasks.length);
                    }
                    if (this.normalizeTaskStatus(task?.status) === 'gotowe' || this.hasDoneStamp(task)) return 1;
                    return 0;
                },

                getHistoricalEarnedPoints() {
                    const total = this.tasks.reduce((sum, task) => {
                        const weight = this.getTaskEffectivePointsWeight(task);
                        return sum + (weight * this.getHistoricalTaskPointsFraction(task));
                    }, 0);
                    return this.roundScore(total);
                },

                getRewardEarnedPoints() {
                    return this.roundScore(Math.max(
                        Number(this.rewardSummary?.earned_points || 0),
                        this.getHistoricalEarnedPoints()
                    ));
                },

                getRewardSpentPoints() {
                    const earned = this.getRewardEarnedPoints();
                    const spent = this.roundScore(Number(this.rewardSummary?.spent_points || 0));
                    return this.roundScore(Math.min(earned, spent));
                },

                getRewardAvailablePoints() {
                    const earned = this.getRewardEarnedPoints();
                    const spent = this.getRewardSpentPoints();
                    return this.roundScore(Math.max(0, earned - spent));
                },

                getRewardAvailableBudgetPln() {
                    return this.getRewardAvailablePoints();
                },

                roundScore(value) {
                    return Math.round((Number(value) || 0) * 100) / 100;
                },

                formatScore(value) {
                    const rounded = this.roundScore(value);
                    if (Number.isInteger(rounded)) return String(rounded);
                    return rounded.toFixed(2).replace(/\.?0+$/, '');
                },

                getDoneCountByDate(dateKey) {
                    const total = this.tasks.reduce((sum, task) => sum + this.getTaskPointsByDate(task, dateKey), 0);
                    return this.roundScore(total);
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
                    return left === 1 ? 'Jeszcze 1 i cel siada' : `Jeszcze ${this.formatScore(left)} do celu`;
                },

                getWeeklyDoneTotal() {
                    const today = this.shiftDateKey(this.getTodayKey(), this.dopamineWeekOffset * 7);
                    let total = 0;
                    for (let offset = 0; offset < 7; offset++) {
                        total += this.getDoneCountByDate(this.shiftDateKey(today, -offset));
                    }
                    return this.roundScore(total);
                },

                getWeeklyGoalDots() {
                    const realToday = this.getTodayKey();
                    const today = this.shiftDateKey(realToday, this.dopamineWeekOffset * 7);
                    const dots = [];
                    for (let offset = 6; offset >= 0; offset--) {
                        const dateKey = this.shiftDateKey(today, -offset);
                        const done = this.getDoneCountByDate(dateKey);
                        const rawPercent = this.dailyGoal > 0 ? Math.round((done / this.dailyGoal) * 100) : 0;
                        const ratio = this.dailyGoal > 0 ? Math.min(1, done / this.dailyGoal) : 0;
                        const percent = Math.round(ratio * 100);
                        const date = this.keyToDate(dateKey);
                        dots.push({
                            dateKey,
                            done,
                            ratio,
                            percent,
                            rawPercent,
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
                    if (done > this.dailyGoal) return 'dopamine-dot-over';
                    if (done >= this.dailyGoal) return 'dopamine-dot-full';
                    if (done >= Math.max(1, Math.ceil(this.dailyGoal * 0.6))) return 'dopamine-dot-good';
                    if (done > 0) return 'dopamine-dot-low';
                    return 'dopamine-dot-empty';
                },

                getDopamineDotStyle(day) {
                    const percent = Math.max(0, Math.min(100, Number(day?.percent || 0)));
                    return `--dopamine-progress: ${percent};`;
                },

                getDopaminePercentLabel(day) {
                    const rawPercent = Math.max(0, Number(day?.rawPercent || 0));
                    if (rawPercent > 100) return '';
                    return `${rawPercent}%`;
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
                    if (this.brainDumpNotes.length === 0) {
                        return 'Brain dump jest pusty. Dodaj osobna notatke na kazdy zrzut mysli.';
                    }
                    const snippets = this.brainDumpNotes.slice(0, 3).map(note => {
                        const firstLine = (note.content || '').split('\n').map(line => line.trim()).find(Boolean);
                        return firstLine || note.title || 'Nowa notatka';
                    });
                    return `${snippets.join(' • ')}${this.brainDumpNotes.length > 3 ? ' ...' : ''}`;
                },

                countBrainDumpLines() {
                    return this.brainDumpNotes.reduce((sum, note) => (
                        sum + (note.content || '').split('\n').map(line => line.trim()).filter(Boolean).length
                    ), 0);
                },

                countActiveBrainDumpLines() {
                    return (this.brainDump || '').split('\n').map(line => line.trim()).filter(Boolean).length;
                },

                getBrainDumpLastSavedAt() {
                    const timestamps = this.brainDumpNotes
                        .map(note => note.updated_at || '')
                        .filter(Boolean)
                        .sort();
                    return timestamps[timestamps.length - 1] || this.noteSavedAt || '';
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

                    if (status !== 'gotowe') {
                        return [{
                            moduleId: 0,
                            moduleName: '',
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
                        task.status !== 'gotowe' &&
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

                isTaskOwner(task) {
                    if (!task) return false;
                    return !task.shared_role || task.shared_role === 'owner';
                },

                isTaskShared(task) {
                    if (!task) return false;
                    return !!task.is_shared || task.shared_role === 'shared' || Number(task.share_count || 0) > 0;
                },

                canShareTask(task) {
                    return !!(task && Number(task.id) > 0 && this.isTaskOwner(task));
                },

                getTaskSharedLabel(task) {
                    if (!this.isTaskShared(task)) return '';
                    if (task?.shared_role === 'shared' && task?.owner_username) {
                        return `👥 Wspólne · ${task.owner_username}`;
                    }
                    return '👥 Wspólne';
                },

                buildDoneDescription(description = '') {
                    const stamp = `[Done: ${this.getTodayKey()}]`;
                    if ((description || '').includes(stamp)) return description || stamp;
                    const clean = (description || '').trimEnd();
                    return clean ? `${clean}\n${stamp}` : stamp;
                },

                pickTaskPayload(task) {
                    const dueDate = this.sanitizeDateKey(task.due_date);
                    const dueTime = dueDate ? this.sanitizeDueTime(task.due_time, '') : '';
                    return {
                        name: task.name,
                        module_id: this.normalizeOptionalId(task.module_id),
                        priority: this.normalizePriorityValue(task.priority),
                        description: task.description || '',
                        due_date: dueDate,
                        due_time: dueTime,
                        reminder_offset_minutes: this.normalizeReminderOffsetMinutes(task.reminder_offset_minutes),
                        estimated_time: this.normalizeEstimatedMinutes(task.estimated_time) || 15,
                        points_weight: this.normalizePointsWeight(task.points_weight),
                        status: this.normalizeTaskStatus(task.status),
                        subtasks: this.normalizeSubtasks(task.subtasks).map(subtask => ({
                            id: subtask.id,
                            title: subtask.title,
                            done: !!subtask.done,
                            estimated_time: this.normalizeSubtaskEstimatedMinutes(subtask.estimated_time),
                            points_weight: this.normalizeSubtaskPointsWeight(subtask.points_weight),
                            done_at: subtask.done_at || '',
                            source_task_id: this.normalizeOptionalId(subtask.source_task_id),
                            source_module_id: this.normalizeOptionalId(subtask.source_module_id),
                            source_due_date: this.sanitizeDateKey(subtask.source_due_date),
                            source_due_time: this.sanitizeDueTime(subtask.source_due_time, '')
                        }))
                    };
                },

                async patchTask(taskId, payload) {
                    await fetch(`${this.API}/tasks/${taskId}`, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });
                },

                async setTaskDueTime(task, rawTime, targetDate = '') {
                    if (!task) return false;
                    const dueTime = this.sanitizeDueTime(rawTime, '');
                    const dueDate = this.sanitizeDateKey(targetDate) || this.sanitizeDateKey(task.due_date);
                    if (!dueDate || !dueTime) {
                        this.showToast('Wybierz poprawna godzine.');
                        return false;
                    }

                    const send = (allowOverflow = false) => fetch(`${this.API}/tasks/${task.id}`, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            due_date: dueDate,
                            due_time: dueTime,
                            allow_time_overflow: !!allowOverflow
                        })
                    });

                    let response = await send(false);
                    if (response.status === 409) {
                        let message = 'Dodanie zadania o tej godzinie przekroczy limit 8h.';
                        try {
                            const payload = await response.json();
                            message = payload?.detail?.message || message;
                        } catch (error) {
                            /* keep fallback */
                        }
                        if (!await this.askConfirmation(message, 'Zaplanuj mimo to')) return false;
                        response = await send(true);
                    }
                    if (!response.ok) {
                        this.showToast(await this.getApiErrorMessage(response, 'Nie udalo sie ustawic godziny zadania.'));
                        return false;
                    }
                    await this.loadAllTasks();
                    this.showToast(`Zadanie zaplanowane na ${dueTime}.`, 'success');
                    return true;
                },

                async changeTaskStatus(task, nextStatus) {
                    if (!task) return;
                    const payload = { status: nextStatus };
                    if (nextStatus === 'gotowe') {
                        payload.description = this.buildDoneDescription(task.description);
                        const subtasks = this.normalizeSubtasks(task.subtasks);
                        if (subtasks.length > 0) {
                            payload.subtasks = subtasks.map(subtask => ({
                                id: subtask.id,
                                title: subtask.title,
                                done: true,
                                estimated_time: this.normalizeSubtaskEstimatedMinutes(subtask.estimated_time),
                                points_weight: this.normalizeSubtaskPointsWeight(subtask.points_weight),
                                done_at: subtask.done_at || '',
                                source_task_id: this.normalizeOptionalId(subtask.source_task_id),
                                source_module_id: this.normalizeOptionalId(subtask.source_module_id),
                                source_due_date: this.sanitizeDateKey(subtask.source_due_date),
                                source_due_time: this.sanitizeDueTime(subtask.source_due_time, '')
                            }));
                        }
                    }
                    await this.patchTask(task.id, payload);
                    await this.init();
                },

                openModule(module) {
                    this.activeModule = module;
                    this.setTaskScope('module');
                    this.view = 'kanban';
                    this.closeMobileModules();
                },

                goToTask(task) {
                    if (!task) return;
                    const module = this.modules.find(item => item.id === task.module_id);
                    if (module) {
                        this.activeModule = module;
                        this.setTaskScope('module');
                    } else {
                        this.setTaskScope('all');
                    }
                    this.view = 'kanban';
                    this.closeMobileModules();
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
                    return this.queueUndoableAction('Zadanie zostanie usunięte za chwilę.', async () => {
                        const response = await fetch(`${this.API}/tasks/${taskId}`, { method: 'DELETE' });
                        if (!response.ok) throw new Error(await this.getApiErrorMessage(response, 'Nie udało się usunąć zadania.'));
                        await this.init();
                        this.showToast('Zadanie usunięte.', 'success');
                    });
                },

                async shareTaskPrompt(taskId) {
                    const id = Number(taskId);
                    const task = this.getTaskById(id) || (Number(this.editingTask?.id) === id ? this.editingTask : null);
                    if (!id || !this.canShareTask(task)) {
                        this.showToast('Tylko wlasciciel moze udostepnic to zadanie.');
                        return false;
                    }

                    await this.loadSharingConnections();
                    if (this.sharingConnections.length === 0) {
                        this.showToast('Najpierw dodaj osobe w Ustawienia → Udostepnianie. Zaproszenie musi zostac zaakceptowane.');
                        this.taskModal = false;
                        this.navigateUtilityView('sharing');
                        return false;
                    }

                    this.sharingTaskId = id;
                    this.shareTaskDueTime = this.getTaskDueTime(task);
                    this.shareTaskModal = true;
                    return true;
                },

                closeShareTaskModal() {
                    this.shareTaskModal = false;
                    this.sharingTaskId = null;
                    this.shareTaskDueTime = '';
                },

                isTaskSharedWith(task, connection) {
                    const ids = Array.isArray(task?.shared_user_ids) ? task.shared_user_ids.map(Number) : [];
                    return ids.includes(Number(connection?.user_id));
                },

                getSharingTask() {
                    const id = Number(this.sharingTaskId);
                    return this.getTaskById(id) || (Number(this.editingTask?.id) === id ? this.editingTask : null);
                },

                async shareTaskWithConnection(connection) {
                    const task = this.getSharingTask();
                    if (!task || !connection || this.isTaskSharedWith(task, connection)) return false;

                    try {
                        const dueDate = this.sanitizeDateKey(task.due_date);
                        const selectedTime = this.sanitizeDueTime(this.shareTaskDueTime, '');
                        if (dueDate && !selectedTime) {
                            this.showToast('Wybierz godzine. Dzieki temu zadanie trafi na os czasu obu osob.');
                            return false;
                        }
                        if (dueDate && selectedTime !== this.getTaskDueTime(task)) {
                            const timeResponse = await fetch(`${this.API}/tasks/${task.id}`, {
                                method: 'PUT',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ due_date: dueDate, due_time: selectedTime })
                            });
                            if (!timeResponse.ok) {
                                this.showToast(await this.getApiErrorMessage(timeResponse, 'Nie udalo sie zapisac godziny zadania.'));
                                return false;
                            }
                        }

                        const response = await fetch(`${this.API}/tasks/${task.id}/share`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ user_id: Number(connection.user_id) })
                        });

                        if (!response.ok) {
                            this.showToast(await this.getApiErrorMessage(response, 'Nie udalo sie udostepnic zadania.'));
                            return false;
                        }

                        const taskId = Number(task.id);
                        await this.init();
                        const refreshedTask = this.getTaskById(taskId);
                        if (this.taskModal && Number(this.editingTask?.id) === taskId && refreshedTask) {
                            this.openTaskModal(refreshedTask);
                        }
                        this.closeShareTaskModal();
                        this.showToast(`Zadanie udostepnione: ${connection.username}.`, 'success');
                        return true;
                    } catch (error) {
                        this.showToast('Nie udalo sie udostepnic zadania. Sprawdz polaczenie z backendem.');
                        return false;
                    }
                },

                async deleteModule(module) {
                    if (!module) return false;
                    const taskCount = this.tasks.filter(task => task.module_id === module.id).length;
                    const suffix = taskCount === 1 ? 'zadanie' : (taskCount >= 2 && taskCount <= 4 ? 'zadania' : 'zadan');
                    return this.queueUndoableAction(`Moduł „${module.name}” i ${taskCount} ${suffix} zostaną usunięte.`, async () => {
                        const response = await fetch(`${this.API}/modules/${module.id}`, { method: 'DELETE' });
                        if (!response.ok) throw new Error('Nie udało się usunąć modułu.');
                        if (this.activeModule?.id === module.id) {
                            this.activeModule = null;
                            this.setTaskScope('all');
                        }
                        await this.init();
                        if (!this.activeModule && this.modules.length > 0) {
                            this.activeModule = this.getSidebarModules()[0] || this.modules[0];
                        }
                        this.showToast('Moduł usunięty.', 'success');
                    });
                },

                async quickMove(task, direction) {
                    const columns = [...this.columnsMeta.map(column => column.id), 'gotowe'];
                    const nextIndex = columns.indexOf(task.status) + direction;
                    if (nextIndex < 0 || nextIndex >= columns.length) return;
                    await this.changeTaskStatus(task, columns[nextIndex]);
                },

                startTaskDrag(task, event) {
                    if (!task) return;
                    this.draggedTaskId = task.id;
                    this.draggedTaskTargetId = null;
                    if (event?.dataTransfer) {
                        event.dataTransfer.effectAllowed = 'move';
                        event.dataTransfer.setData('text/plain', String(task.id));
                    }
                },

                endTaskDrag() {
                    this.draggedTaskId = null;
                    this.draggedTaskTargetId = null;
                },

                canDropTaskOnTask(task) {
                    return !!(this.draggedTaskId && task && Number(this.draggedTaskId) !== Number(task.id));
                },

                dragTaskOverTask(task, event) {
                    if (!this.canDropTaskOnTask(task)) return;
                    this.draggedTaskTargetId = task.id;
                    if (event?.dataTransfer) {
                        event.dataTransfer.dropEffect = 'move';
                    }
                },

                clearTaskMergeTarget(task) {
                    if (!task || Number(this.draggedTaskTargetId) === Number(task.id)) {
                        this.draggedTaskTargetId = null;
                    }
                },

                getTaskBundleCount(task) {
                    return this.normalizeSubtasks(task?.subtasks).length;
                },

                getTaskBundleLabel(task) {
                    const count = this.getTaskBundleCount(task);
                    if (!count) return '';
                    return `${count} podz.`;
                },

                getSubtaskSourceLabel(subtask) {
                    const pieces = [];
                    const moduleName = subtask?.source_module_id ? this.getModuleName(subtask.source_module_id) : '';
                    if (moduleName) pieces.push(moduleName);
                    const dueDate = this.sanitizeDateKey(subtask?.source_due_date);
                    if (dueDate) {
                        const dueTime = this.sanitizeDueTime(subtask?.source_due_time, '');
                        pieces.push(dueTime ? `${dueDate} ${dueTime}` : dueDate);
                    }
                    return pieces.join(' • ');
                },

                getMergeDefaultName(sourceTask, targetTask) {
                    const targetName = (targetTask?.name || '').trim();
                    const sourceName = (sourceTask?.name || '').trim();
                    const moduleName = this.getModuleName(targetTask?.module_id);
                    const joined = `${targetName} ${sourceName}`.toLowerCase();
                    const looksLikeFixes = ['popraw', 'napraw', 'fix', 'bug', 'blad', 'korekt'].some(keyword => joined.includes(keyword));
                    if (Number(sourceTask?.module_id) === Number(targetTask?.module_id) && moduleName && looksLikeFixes) {
                        return `Poprawki: ${moduleName}`;
                    }
                    if (Number(sourceTask?.module_id) === Number(targetTask?.module_id) && moduleName) {
                        return `${moduleName}: pakiet zadan`;
                    }
                    return `Pakiet: ${targetName || sourceName || 'zadania'}`;
                },

                getTaskMergePrompt(sourceTask, targetTask) {
                    const targetHasSubtasks = this.getTaskBundleCount(targetTask) > 0;
                    if (targetHasSubtasks) {
                        return `Dodac "${sourceTask?.name || 'zadanie'}" jako podzadanie do "${targetTask?.name || 'pakietu'}"?`;
                    }
                    return 'Nazwa nowego zadania zbiorczego:';
                },

                async mergeTasks(sourceTask, targetTask, name = '', allowOverflow = false) {
                    const response = await fetch(`${this.API}/tasks/merge`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            source_task_id: sourceTask.id,
                            target_task_id: targetTask.id,
                            name,
                            allow_time_overflow: !!allowOverflow
                        })
                    });

                    if (response.status === 409) {
                        let detail = null;
                        try {
                            const payloadError = await response.json();
                            detail = payloadError?.detail || null;
                        } catch (error) {
                            detail = null;
                        }
                        const warningMessage = typeof detail === 'object' && detail?.message
                            ? detail.message
                            : 'Polaczone zadanie przekroczy limit 8h w kalendarzu.';
                        const acceptOverflow = await this.askConfirmation(warningMessage, 'Połącz mimo to');
                        if (!acceptOverflow) return false;
                        return this.mergeTasks(sourceTask, targetTask, name, true);
                    }

                    if (!response.ok) {
                        this.showToast(await this.getApiErrorMessage(response, 'Nie udalo sie polaczyc zadan.'));
                        return false;
                    }

                    const payload = await response.json();
                    await this.init();
                    const mergedTask = this.getTaskById(payload?.id);
                    if (mergedTask) {
                        const module = this.modules.find(item => Number(item.id) === Number(mergedTask.module_id));
                        if (module) this.activeModule = module;
                    }
                    return true;
                },

                async dropTaskOnTask(targetTask, event = null) {
                    if (event?.stopPropagation) event.stopPropagation();
                    const sourceTaskId = Number(this.draggedTaskId);
                    this.draggedTaskId = null;
                    this.draggedTaskTargetId = null;
                    if (!sourceTaskId || !targetTask || sourceTaskId === Number(targetTask.id)) return;

                    const sourceTask = this.getTaskById(sourceTaskId);
                    if (!sourceTask) return;

                    const targetHasSubtasks = this.getTaskBundleCount(targetTask) > 0;
                    let mergeName = '';
                    if (targetHasSubtasks) {
                        if (!await this.askConfirmation(this.getTaskMergePrompt(sourceTask, targetTask), 'Połącz zadania')) return;
                        mergeName = targetTask.name || '';
                    } else {
                        const defaultName = this.getMergeDefaultName(sourceTask, targetTask);
                        const pickedName = prompt(this.getTaskMergePrompt(sourceTask, targetTask), defaultName);
                        if (pickedName === null) return;
                        mergeName = pickedName.trim();
                        if (!mergeName) {
                            this.showToast('Nazwa zadania zbiorczego nie moze byc pusta.');
                            return;
                        }
                    }

                    await this.mergeTasks(sourceTask, targetTask, mergeName);
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
                    if (event.key === 'Escape' && this.shareTaskModal) {
                        event.preventDefault();
                        this.closeShareTaskModal();
                        return;
                    }
                    if (event.key === 'Escape' && (this.settingsMenuOpen || this.fabOpen)) {
                        event.preventDefault();
                        this.closeOverlayMenus();
                        return;
                    }

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
                    this.isCreatingTask = true;
                    this.taskFormError = '';
                    const assignableModules = this.getAssignableModules();
                    const preferredId = this.normalizeOptionalId(preferredModuleId);
                    const preferredModule = assignableModules.find(module => Number(module.id) === Number(preferredId));
                    const activeModule = assignableModules.find(module => Number(module.id) === Number(this.activeModule?.id));
                    const defaultModule = preferredModule || activeModule || assignableModules[0] || null;
                    this.editingTask = {
                        id: null,
                        name: '',
                        module_id: defaultModule ? String(defaultModule.id) : '',
                        description: '',
                        due_date: '',
                        due_time: '',
                        reminder_offset_minutes: 0,
                        estimated_time: 15,
                        points_weight: 1,
                        priority: '',
                        status: 'oczekujace',
                        subtasks: []
                    };
                    this.taskModal = true;
                },

                openTaskModal(task) {
                    this.isCreatingTask = false;
                    this.taskFormError = '';
                    const baseSubtasks = this.normalizeSubtasks(task?.subtasks);
                    const needsLegacySubtaskDefaults = baseSubtasks.length > 0 && (
                        !this.hasConfiguredSubtaskTimes(baseSubtasks) || !this.hasConfiguredSubtaskPoints(baseSubtasks)
                    );
                    const fallbackTaskMinutes = this.normalizeEstimatedMinutes(task?.estimated_time) || 15;
                    const fallbackTaskPoints = this.normalizePointsWeight(task?.points_weight);
                    const fallbackSubtaskMinutes = Math.max(1, Math.round(fallbackTaskMinutes / Math.max(1, baseSubtasks.length)));
                    const fallbackSubtaskPoints = this.roundScore(fallbackTaskPoints / Math.max(1, baseSubtasks.length));
                    const normalizedSubtasks = needsLegacySubtaskDefaults
                        ? baseSubtasks.map(subtask => ({
                            ...subtask,
                            estimated_time: this.normalizeSubtaskEstimatedMinutes(subtask?.estimated_time) || fallbackSubtaskMinutes,
                            points_weight: this.normalizeSubtaskPointsWeight(subtask?.points_weight) || fallbackSubtaskPoints
                        }))
                        : baseSubtasks;

                    const effectiveMinutes = this.hasConfiguredSubtaskTimes(normalizedSubtasks)
                        ? this.getSubtasksTimeSum(normalizedSubtasks)
                        : (this.normalizeEstimatedMinutes(task?.estimated_time) || 15);
                    const effectivePoints = this.hasConfiguredSubtaskPoints(normalizedSubtasks)
                        ? this.getSubtasksPointsSum(normalizedSubtasks)
                        : this.normalizePointsWeight(task?.points_weight);

                    this.editingTask = {
                        description: '',
                        due_date: '',
                        due_time: '',
                        reminder_offset_minutes: 0,
                        estimated_time: 15,
                        points_weight: 1,
                        priority: '',
                        status: 'oczekujace',
                        subtasks: [],
                        ...task,
                        status: this.normalizeTaskStatus(task?.status),
                        module_id: this.normalizeOptionalId(task?.module_id) || '',
                        priority: this.normalizePriorityValue(task?.priority),
                        estimated_time: effectiveMinutes,
                        points_weight: effectivePoints,
                        due_time: this.sanitizeDueTime(task?.due_time, ''),
                        reminder_offset_minutes: this.normalizeReminderOffsetMinutes(task?.reminder_offset_minutes),
                        subtasks: normalizedSubtasks
                    };
                    this.taskModal = true;
                },

                handleEditingTaskStatusChange() {
                    if (this.normalizeTaskStatus(this.editingTask?.status) !== 'obserwacja') return;
                    this.editingTask.due_date = '';
                    this.editingTask.due_time = '';
                    this.editingTask.reminder_offset_minutes = -1;
                },

                addEditingSubtask() {
                    const current = Array.isArray(this.editingTask?.subtasks) ? this.editingTask.subtasks : [];
                    this.editingTask.subtasks = [...current, this.createSubtaskDraft('')];
                },

                removeEditingSubtask(index) {
                    const current = Array.isArray(this.editingTask?.subtasks) ? this.editingTask.subtasks : [];
                    this.editingTask.subtasks = current.filter((_, itemIndex) => itemIndex !== index);
                },

                toggleEditingSubtaskDone(subtask, checked) {
                    if (!subtask) return;
                    subtask.done = !!checked;
                    subtask.done_at = subtask.done ? new Date().toISOString() : '';
                },

                async saveTask() {
                    try {
                        this.taskFormError = '';
                        const pickedDueDate = this.$refs?.taskDueDateInput?.value || this.editingTask.due_date;
                        const pickedDueTime = this.$refs?.taskDueTimeInput?.value || this.editingTask.due_time;
                        this.editingTask.due_date = this.sanitizeDateKey(pickedDueDate);
                        this.editingTask.due_time = this.editingTask.due_date
                            ? this.sanitizeDueTime(pickedDueTime, '')
                            : '';
                        this.editingTask.reminder_offset_minutes = this.normalizeReminderOffsetMinutes(this.editingTask.reminder_offset_minutes);
                        this.editingTask.estimated_time = this.normalizeEstimatedMinutes(this.editingTask.estimated_time) || 15;
                        this.editingTask.points_weight = this.normalizePointsWeight(this.editingTask.points_weight);
                        this.editingTask.subtasks = this.normalizeSubtasks(this.editingTask.subtasks);
                        const payload = this.pickTaskPayload(this.editingTask);
                        if (!payload.module_id) {
                            this.taskFormError = this.getAssignableModules().length > 0
                                ? 'Wybierz modul. Dzieki temu zadanie nie zniknie po ukonczeniu.'
                                : 'Najpierw utworz modul, a potem zapisz zadanie.';
                            this.$nextTick(() => this.$refs?.taskModuleInput?.focus());
                            return;
                        }
                        const subtasks = this.normalizeSubtasks(payload.subtasks);
                        if (subtasks.length > 0) {
                            for (let index = 0; index < subtasks.length; index++) {
                                const subtask = subtasks[index];
                                const subtaskMinutes = this.normalizeSubtaskEstimatedMinutes(subtask.estimated_time);
                                const subtaskPoints = this.normalizeSubtaskPointsWeight(subtask.points_weight);
                                if (subtaskMinutes <= 0) {
                                    this.showToast(`Podzadanie #${index + 1} musi miec czas wiekszy od 0 minut.`);
                                    return;
                                }
                                if (subtaskPoints <= 0) {
                                    this.showToast(`Podzadanie #${index + 1} musi miec punkty wieksze od 0.`);
                                    return;
                                }
                            }
                            payload.estimated_time = this.getSubtasksTimeSum(subtasks);
                            payload.points_weight = this.getSubtasksPointsSum(subtasks);
                            payload.subtasks = subtasks;
                        }

                        payload.name = (payload.name || '').trim();
                        if (!payload.name) {
                            this.showToast('Podaj nazwe zadania.');
                            return;
                        }

                        if (payload.estimated_time <= 0) {
                            this.showToast('Podaj szacowany czas zadania (minuty, wiecej niz 0).');
                            return;
                        }

                        payload.points_weight = this.normalizePointsWeight(payload.points_weight);
                        if (payload.points_weight <= 0) {
                            this.showToast('Waga zadania musi byc wieksza od 0.');
                            return;
                        }

                        if (payload.status === 'gotowe') {
                            payload.description = this.buildDoneDescription(payload.description);
                            if (Array.isArray(payload.subtasks) && payload.subtasks.length > 0) {
                                payload.subtasks = payload.subtasks.map(subtask => ({ ...subtask, done: true }));
                            }
                        }

                        const endpoint = this.isCreatingTask || !this.editingTask.id
                            ? `${this.API}/tasks`
                            : `${this.API}/tasks/${this.editingTask.id}`;
                        const method = this.isCreatingTask || !this.editingTask.id ? 'POST' : 'PUT';

                        const sendPayload = async (allowOverflow = false) => fetch(endpoint, {
                            method,
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                ...payload,
                                allow_time_overflow: !!allowOverflow
                            })
                        });

                        let response = await sendPayload(false);
                        if (response.status === 409) {
                            let detail = null;
                            try {
                                const payloadError = await response.json();
                                detail = payloadError?.detail || null;
                            } catch (error) {
                                detail = null;
                            }

                            const projected = this.getEditingTaskProjectedMinutes();
                            const defaultMessage = projected.date
                                ? `Plan na ${projected.date} przekroczy limit 8h (${this.formatDurationMinutes(projected.total)}).`
                                : 'Przekroczysz limit 8h na ten dzien.';
                            const warningMessage = typeof detail === 'object' && detail?.message
                                ? detail.message
                                : defaultMessage;

                            const acceptOverflow = await this.askConfirmation(warningMessage, 'Zapisz mimo to');
                            if (!acceptOverflow) return;
                            response = await sendPayload(true);
                        }

                        if (!response.ok) {
                            this.showToast(await this.getApiErrorMessage(response, 'Nie udalo sie zapisac zadania.'));
                            return;
                        }

                        this.taskModal = false;
                        this.isCreatingTask = false;
                        await this.init();
                    } catch (error) {
                        this.showToast('Nie udalo sie zapisac zadania. Sprawdz polaczenie z backendem i odswiez strone.');
                    }
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

                async addModuleForTask() {
                    const name = prompt('Nazwa nowego modulu:');
                    if (name === null) return;
                    const cleanName = name.trim();
                    if (!cleanName) {
                        this.taskFormError = 'Nazwa modulu nie moze byc pusta.';
                        return;
                    }
                    const response = await fetch(`${this.API}/modules`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ name: cleanName, category: 'praca' })
                    });
                    if (!response.ok) {
                        this.taskFormError = await this.getApiErrorMessage(response, 'Nie udalo sie utworzyc modulu.');
                        return;
                    }
                    const created = await response.json();
                    await this.loadModules();
                    this.editingTask.module_id = String(created.id);
                    this.taskFormError = '';
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

                applyActiveBrainDumpNote(note) {
                    if (!note) {
                        this.activeBrainDumpNoteId = null;
                        this.brainDumpNoteTitle = '';
                        this.brainDump = '';
                        this.noteSavedAt = '';
                        return;
                    }
                    const normalized = this.normalizeBrainDumpNote(note);
                    this.activeBrainDumpNoteId = normalized.id;
                    this.brainDumpNoteTitle = normalized.title;
                    this.brainDump = normalized.content;
                    this.noteSavedAt = normalized.updated_at;
                },

                getActiveBrainDumpNote() {
                    return this.brainDumpNotes.find(note => note.id === Number(this.activeBrainDumpNoteId)) || null;
                },

                updateActiveBrainDumpDraft() {
                    const noteId = Number(this.activeBrainDumpNoteId);
                    if (!noteId) return;
                    this.brainDumpNotes = this.brainDumpNotes.map(note => (
                        note.id === noteId
                            ? { ...note, title: this.brainDumpNoteTitle || 'Nowa notatka', content: this.brainDump || '' }
                            : note
                    ));
                },

                async createBrainDumpNote(content = '', title = 'Nowa notatka', focusEditor = true) {
                    const response = await fetch(`${this.API}/brain-dump-notes`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ title, content })
                    });
                    if (!response.ok) {
                        this.showToast(await this.getApiErrorMessage(response, 'Nie udalo sie utworzyc notatki.'));
                        return null;
                    }
                    const note = this.normalizeBrainDumpNote(await response.json());
                    this.brainDumpNotes = [note, ...this.brainDumpNotes.filter(item => item.id !== note.id)];
                    this.applyActiveBrainDumpNote(note);
                    if (focusEditor) {
                        window.setTimeout(() => document.querySelector('[data-brain-dump-input]')?.focus(), 0);
                    }
                    return note;
                },

                async createEmptyBrainDumpNote() {
                    await this.saveBrainDump(true);
                    await this.createBrainDumpNote('', 'Nowa notatka');
                },

                async selectBrainDumpNote(noteId) {
                    if (Number(noteId) === Number(this.activeBrainDumpNoteId)) return;
                    await this.saveBrainDump(true);
                    const note = this.brainDumpNotes.find(item => item.id === Number(noteId)) || null;
                    this.applyActiveBrainDumpNote(note);
                },

                async deleteBrainDumpNote(noteId = null) {
                    const targetId = Number(noteId || this.activeBrainDumpNoteId);
                    if (!targetId) return;
                    return this.queueUndoableAction('Notatka zostanie usunięta za chwilę.', async () => {
                        const response = await fetch(`${this.API}/brain-dump-notes/${targetId}`, { method: 'DELETE' });
                        if (!response.ok) throw new Error(await this.getApiErrorMessage(response, 'Nie udało się usunąć notatki.'));
                        this.brainDumpNotes = this.brainDumpNotes.filter(note => note.id !== targetId);
                        this.applyActiveBrainDumpNote(this.brainDumpNotes[0] || null);
                        this.showToast('Notatka usunięta.', 'success');
                    });
                },

                async saveBrainDump(quiet = false) {
                    clearTimeout(this.brainDumpSaveTimer);
                    if (!this.activeBrainDumpNoteId) {
                        if (!(this.brainDump || '').trim() && !(this.brainDumpNoteTitle || '').trim()) return true;
                        const created = await this.createBrainDumpNote(this.brainDump || '', this.brainDumpNoteTitle || 'Nowa notatka', false);
                        return !!created;
                    }

                    this.updateActiveBrainDumpDraft();
                    try {
                        const response = await fetch(`${this.API}/brain-dump-notes/${this.activeBrainDumpNoteId}`, {
                            method: 'PUT',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                title: this.brainDumpNoteTitle || 'Nowa notatka',
                                content: this.brainDump || ''
                            })
                        });
                        if (!response.ok) throw new Error('brain_dump_save_failed');
                        const note = this.normalizeBrainDumpNote(await response.json());
                        this.brainDumpNotes = [note, ...this.brainDumpNotes.filter(item => item.id !== note.id)];
                        this.applyActiveBrainDumpNote(note);
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
                            this.showToast('Nie udalo sie zapisac notatki na serwerze. Zostala zabezpieczona lokalnie.');
                        }
                        return false;
                    }
                },

                async saveBrainDumpQuiet() {
                    await this.saveBrainDump(true);
                },

                handleBrainDumpInput() {
                    this.updateActiveBrainDumpDraft();
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

                handleBrainDumpTitleInput() {
                    this.updateActiveBrainDumpDraft();
                    clearTimeout(this.brainDumpSaveTimer);
                    this.brainDumpSaveTimer = setTimeout(() => {
                        this.saveBrainDumpQuiet();
                    }, 500);
                },

                clearActiveBrainDumpNote() {
                    this.brainDump = '';
                    this.handleBrainDumpInput();
                },

                async sendBrainDumpToModule() {
                    if (!this.brainDumpTargetModuleId) {
                        this.showToast('Najpierw wybierz modul.');
                        return;
                    }

                    const lines = (this.brainDump || '').split('\n').map(line => line.trim()).filter(Boolean);
                    if (lines.length === 0) {
                        this.showToast('Aktywna notatka jest pusta.');
                        return;
                    }

                    if (!await this.askConfirmation(`Utworzyć ${lines.length} zadań z aktywnej notatki?`, 'Utwórz zadania')) return;

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

                clampCanvasZoom(value) {
                    const min = Number(this.canvasMinZoom) || 0.35;
                    const max = Number(this.canvasMaxZoom) || 2.5;
                    const numeric = Number(value);
                    const fallback = Number(this.canvasZoom) || 1;
                    const safeValue = Number.isFinite(numeric) ? numeric : fallback;
                    return this.clampCanvasValue(safeValue, min, max);
                },

                getCanvasStageStyle() {
                    const zoom = this.clampCanvasZoom(this.canvasZoom || 1);
                    const width = Math.round(this.canvasBoardWidth * zoom);
                    const height = Math.round(this.canvasBoardHeight * zoom);
                    return `width:${width}px;height:${height}px;min-height:${height}px;`;
                },

                getCanvasBoardStyle() {
                    const zoom = this.clampCanvasZoom(this.canvasZoom || 1);
                    return `width:${this.canvasBoardWidth}px;height:${this.canvasBoardHeight}px;min-height:${this.canvasBoardHeight}px;transform:scale(${zoom});transform-origin:top left;`;
                },

                handleCanvasViewportWheel(event) {
                    if (!event?.ctrlKey) return;
                    const viewport = this.$refs?.canvasViewport;
                    if (!viewport) return;
                    event.preventDefault();

                    const currentZoom = this.clampCanvasZoom(this.canvasZoom || 1);
                    const zoomStep = event.deltaY < 0 ? 1.12 : 0.88;
                    const nextZoom = this.clampCanvasZoom(currentZoom * zoomStep);
                    if (nextZoom === currentZoom) return;

                    const rect = viewport.getBoundingClientRect();
                    const pointerX = event.clientX - rect.left;
                    const pointerY = event.clientY - rect.top;
                    const worldX = (viewport.scrollLeft + pointerX) / currentZoom;
                    const worldY = (viewport.scrollTop + pointerY) / currentZoom;

                    this.canvasZoom = nextZoom;
                    viewport.scrollLeft = Math.max(0, (worldX * nextZoom) - pointerX);
                    viewport.scrollTop = Math.max(0, (worldY * nextZoom) - pointerY);
                },

                resetCanvasZoom() {
                    this.canvasZoom = 1;
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
                        const colorMeta = this.getCanvasColorMeta(link.color);
                        const color = colorMeta.line || colorMeta.swatch;
                        const ux = dx / length;
                        const uy = dy / length;
                        const headLength = 11;
                        const headWidth = 4.8;
                        const lineX2 = x2 - (ux * headLength);
                        const lineY2 = y2 - (uy * headLength);
                        const baseX = x2 - (ux * headLength);
                        const baseY = y2 - (uy * headLength);
                        const leftX = baseX - (uy * headWidth);
                        const leftY = baseY + (ux * headWidth);
                        const rightX = baseX + (uy * headWidth);
                        const rightY = baseY - (ux * headWidth);
                        const headPoints = `${x2},${y2} ${leftX},${leftY} ${rightX},${rightY}`;

                        return { ...link, x1, y1, x2, y2, lineX2, lineY2, headPoints, color };
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
                    const zoom = this.clampCanvasZoom(this.canvasZoom || 1);
                    const baseX = viewport ? ((viewport.scrollLeft + (viewport.clientWidth * 0.28)) / zoom) : 120;
                    const baseY = viewport ? ((viewport.scrollTop + (viewport.clientHeight * 0.24)) / zoom) : 120;
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
                        this.showToast('Najpierw wybierz element, od ktorego chcesz poprowadzic strzalke.');
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

                startCanvasNodePointer(node, event) {
                    if (!node || !event) return;
                    if (event.button === 2) {
                        this.startCanvasPan(event);
                        return;
                    }
                    if (event.button !== 0) return;

                    const tagName = event?.target?.tagName?.toLowerCase();
                    if (tagName === 'textarea' || tagName === 'button' || tagName === 'input' || tagName === 'select' || tagName === 'option') return;

                    this.startCanvasDrag(node, event);
                },

                startCanvasDrag(node, event) {
                    if (!node || !event) return;
                    if (event.button === 2) {
                        this.startCanvasPan(event);
                        return;
                    }
                    if (event.button !== 0) return;
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

                startCanvasPan(event) {
                    if (!event || event.button !== 2) return false;
                    const viewport = this.$refs?.canvasViewport;
                    if (!viewport) return false;
                    this.canvasPointerAction = {
                        mode: 'pan',
                        startX: event.clientX,
                        startY: event.clientY,
                        scrollLeft: viewport.scrollLeft,
                        scrollTop: viewport.scrollTop
                    };
                    event.preventDefault();
                    return true;
                },

                startCanvasResize(node, event) {
                    if (!node || !event) return;
                    if (event.button === 2) {
                        this.startCanvasPan(event);
                        return;
                    }
                    if (event.button !== 0) return;
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
                    if (event?.button === 2) {
                        this.startCanvasPan(event);
                        return;
                    }
                    if (event?.button !== 0) return;
                    const tagName = event?.target?.tagName?.toLowerCase();
                    if (event?.target === event?.currentTarget || tagName === 'svg') {
                        this.clearCanvasSelection();
                    }
                },

                moveCanvasDrag(event) {
                    if (!this.canvasPointerAction || !event) return;
                    const action = this.canvasPointerAction;
                    if (action.mode === 'pan') {
                        const viewport = this.$refs?.canvasViewport;
                        if (!viewport) return;
                        const deltaX = event.clientX - action.startX;
                        const deltaY = event.clientY - action.startY;
                        viewport.scrollLeft = Math.max(0, action.scrollLeft - deltaX);
                        viewport.scrollTop = Math.max(0, action.scrollTop - deltaY);
                        event.preventDefault();
                        return;
                    }

                    const node = this.getCanvasNodeById(action.id);
                    if (!node) return;
                    const zoom = this.clampCanvasZoom(this.canvasZoom || 1);

                    if (action.mode === 'drag') {
                        let nextX = action.nodeX + ((event.clientX - action.startX) / zoom);
                        let nextY = action.nodeY + ((event.clientY - action.startY) / zoom);
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
                        let nextWidth = action.width + ((event.clientX - action.startX) / zoom);
                        let nextHeight = action.height + ((event.clientY - action.startY) / zoom);
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
                    const shouldSave = this.canvasPointerAction.mode === 'drag' || this.canvasPointerAction.mode === 'resize';
                    this.canvasPointerAction = null;
                    if (shouldSave) this.saveCanvasBoard();
                },

                clearCanvasBoard() {
                    const previousNodes = this.canvasNodes.map(node => ({ ...node }));
                    const previousLinks = this.canvasLinks.map(link => ({ ...link }));
                    this.canvasNodes = [];
                    this.canvasLinks = [];
                    this.selectedCanvasNodeId = null;
                    this.selectedCanvasLinkId = null;
                    this.canvasLinkDraftFromId = null;
                    this.saveCanvasBoard();
                    this.showToast('Tablica wyczyszczona.', 'warning', {
                        duration: 7000,
                        actionLabel: 'Cofnij',
                        onAction: () => {
                            this.canvasNodes = previousNodes;
                            this.canvasLinks = previousLinks;
                            this.saveCanvasBoard();
                            this.showToast('Przywrócono tablicę.', 'success');
                        },
                        closable: false
                    });
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
                        if (!quiet) this.showToast('Nie udalo sie zapisac dokumentu na serwerze. Kopia zostala lokalnie.');
                        return false;
                    }
                },

                async getApiErrorMessage(response, fallback) {
                    try {
                        const payload = await response.json();
                        if (payload?.detail && payload.detail !== 'Not Found') {
                            if (typeof payload.detail === 'string') return payload.detail;
                            if (typeof payload.detail === 'object' && payload.detail?.message) return payload.detail.message;
                        }
                    } catch (error) {
                        /* response was not JSON */
                    }
                    if (response.status === 404) {
                        return 'Endpoint nie znaleziony. Otworz aplikacje przez backend (http://127.0.0.1:8000) i odswiez strone, zeby formularze trafialy do API.';
                    }
                    return fallback;
                },

                async resetRewardWallet() {
                    if (!await this.askConfirmation('Wyzerować dostępny budżet punktowy po zakupie nagrody?', 'Wyzeruj')) return;
                    const response = await fetch(`${this.API}/rewards/reset`, { method: 'POST' });
                    if (!response.ok) {
                        this.showToast(await this.getApiErrorMessage(response, 'Nie udalo sie zresetowac portfela punktow.'));
                        return;
                    }
                    const payload = await response.json();
                    this.rewardSummary = {
                        earned_points: this.roundScore(payload?.earned_points || 0),
                        spent_points: this.roundScore(payload?.spent_points || 0),
                        available_points: this.roundScore(payload?.available_points || 0),
                        available_budget_pln: this.roundScore(payload?.available_budget_pln || 0),
                        point_value_pln: Number(payload?.point_value_pln) || 1
                    };
                },

                async addMedication() {
                    const name = (this.newMedication.name || '').trim();
                    if (!name) {
                        this.showToast('Podaj nazwe leku.');
                        return;
                    }

                    const medicationId = Number(this.editingMedicationId || 0);
                    const response = await fetch(
                        medicationId ? `${this.API}/medications/${medicationId}` : `${this.API}/medications`,
                        {
                        method: medicationId ? 'PUT' : 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            name,
                            schedule_type: this.normalizeMedicationScheduleType(this.newMedication.schedule_type),
                            reminder_time: this.sanitizeDueTime(this.newMedication.reminder_time, '08:00') || '08:00'
                        })
                    });

                    if (!response.ok) {
                        this.showToast(await this.getApiErrorMessage(response, medicationId ? 'Nie udalo sie zapisac zmian leku.' : 'Nie udalo sie dodac leku.'));
                        return;
                    }

                    this.resetMedicationDraft();
                    await this.loadMedications();
                    this.showToast(medicationId ? 'Zmiany leku zapisane.' : 'Lek dodany do planu.', 'success');
                },

                async toggleMedicationActive(medication) {
                    if (!medication) return;
                    const nextActive = !medication.active;
                    const response = await fetch(`${this.API}/medications/${medication.id}`, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ active: nextActive })
                    });
                    if (!response.ok) {
                        this.showToast(await this.getApiErrorMessage(response, 'Nie udało się zmienić stanu leku.'));
                        return;
                    }
                    await this.loadMedications();
                    this.showToast(nextActive ? 'Lek wznowiony.' : 'Lek wstrzymany. Nie będzie przypomnień.', 'success');
                },

                async toggleMedicationDone(medication, checked) {
                    if (!medication || !medication.scheduled_today) return;
                    const response = await fetch(`${this.API}/medications/${medication.id}/state`, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            date_key: this.medicationsDate || this.getTodayKey(),
                            done: !!checked
                        })
                    });

                    if (!response.ok) {
                        this.showToast(await this.getApiErrorMessage(response, 'Nie udalo sie odhaczyc leku.'));
                        return;
                    }

                    await this.loadMedications();
                },

                async deleteMedication(medicationId) {
                    return this.queueUndoableAction('Lek zostanie usunięty za chwilę.', async () => {
                        const response = await fetch(`${this.API}/medications/${medicationId}`, { method: 'DELETE' });
                        if (!response.ok) {
                            throw new Error(await this.getApiErrorMessage(response, 'Nie udało się usunąć leku.'));
                        }
                        if (Number(this.editingMedicationId) === Number(medicationId)) this.resetMedicationDraft();
                        await this.loadMedications();
                        this.showToast('Lek usunięty.', 'success');
                    });
                },

                async addMonthlyTask() {
                    const name = (this.newMonthlyTaskName || '').trim();
                    if (!name) {
                        this.showToast('Podaj nazwe zadania cyklicznego.');
                        return;
                    }
                    const repeatType = this.normalizeMonthlyRepeatType(this.newMonthlyTaskRepeatType);
                    const dueDay = repeatType === 'monthly' ? this.normalizeMonthlyDueDay(this.newMonthlyTaskDueDay) : 0;
                    if (repeatType === 'monthly' && !dueDay) {
                        this.showToast('Podaj dzien miesiaca.');
                        return;
                    }
                    const dueTime = this.sanitizeDueTime(this.newMonthlyTaskDueTime, '23:59') || '23:59';
                    const taskId = Number(this.editingMonthlyTaskId || 0);

                    const response = await fetch(taskId ? `${this.API}/monthly-tasks/${taskId}` : `${this.API}/monthly-tasks`, {
                        method: taskId ? 'PUT' : 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            name,
                            due_day: dueDay,
                            due_time: dueTime,
                            repeat_type: repeatType,
                            repeat_weekday: this.normalizeMonthlyRepeatWeekday(this.newMonthlyTaskRepeatWeekday)
                        })
                    });

                    if (!response.ok) {
                        this.showToast(await this.getApiErrorMessage(response, taskId ? 'Nie udalo sie zapisac zadania cyklicznego.' : 'Nie udalo sie dodac zadania cyklicznego.'));
                        return;
                    }

                    this.closeMonthlyTaskModal();
                    await this.loadMonthlyTasks();
                },

                async saveMonthlyTaskDetails(task) {
                    if (!task) return;
                    const name = (task.name || '').trim();
                    if (!name) {
                        this.showToast('Nazwa zadania cyklicznego nie moze byc pusta.');
                        await this.loadMonthlyTasks();
                        return;
                    }
                    const repeatType = this.normalizeMonthlyRepeatType(task.repeat_type);
                    const dueTime = this.sanitizeDueTime(task.due_time, '23:59') || '23:59';

                    const response = await fetch(`${this.API}/monthly-tasks/${task.id}`, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            name,
                            due_day: repeatType === 'monthly' ? this.normalizeMonthlyDueDay(task.due_day) : 0,
                            due_time: dueTime,
                            repeat_type: repeatType,
                            repeat_weekday: this.normalizeMonthlyRepeatWeekday(task.repeat_weekday)
                        })
                    });

                    if (!response.ok) {
                        this.showToast(await this.getApiErrorMessage(response, 'Nie udalo sie zapisac zadania cyklicznego.'));
                    }

                    await this.loadMonthlyTasks();
                },

                async toggleMonthlyTaskDone(task) {
                    if (!task) return;
                    const response = await fetch(`${this.API}/monthly-tasks/${task.id}/state`, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            month_key: task.state_key || this.monthlyMonthKey || this.getCurrentMonthKey(),
                            done: !task.done,
                            note: task.note || ''
                        })
                    });

                    if (!response.ok) {
                        this.showToast('Nie udalo sie zaktualizowac statusu.');
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
                            month_key: task.state_key || this.monthlyMonthKey || this.getCurrentMonthKey(),
                            done: !!task.done,
                            note: task.note || ''
                        })
                    });

                    if (!response.ok) {
                        this.showToast('Nie udalo sie zapisac notatki.');
                        return;
                    }

                    await this.loadMonthlyTasks();
                },

                async deleteMonthlyTask(taskId) {
                    return this.queueUndoableAction('Zadanie cykliczne zostanie usunięte za chwilę.', async () => {
                        const response = await fetch(`${this.API}/monthly-tasks/${taskId}`, { method: 'DELETE' });
                        if (!response.ok) throw new Error('Nie udało się usunąć zadania cyklicznego.');
                        await this.loadMonthlyTasks();
                        this.showToast('Zadanie cykliczne usunięte.', 'success');
                    });
                },

                async addDebt() {
                    const name = (this.newDebt.name || '').trim();
                    if (!name) {
                        this.showToast('Podaj nazwe pozycji splaty.');
                        return;
                    }

                    const payload = {
                        name,
                        place: (this.newDebt.place || '').trim(),
                        kind: this.newDebt.kind === 'fixed' ? 'fixed' : 'debt',
                        total_amount: this.newDebt.kind === 'fixed' ? 0 : Number(this.newDebt.total_amount || 0),
                        monthly_amount: Number(this.newDebt.monthly_amount || this.newDebt.total_amount || 0),
                        due_day: this.normalizeMonthlyDueDay(this.newDebt.due_day),
                        note: (this.newDebt.note || '').trim()
                    };

                    const response = await fetch(`${this.API}/debts`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });

                    if (!response.ok) {
                        this.showToast(await this.getApiErrorMessage(response, 'Nie udalo sie dodac pozycji splaty.'));
                        return;
                    }

                    this.closeDebtModal();
                    await this.loadDebts(this.debtsMonthKey || this.getCurrentMonthKey());
                },

                async deleteDebt(debtId) {
                    return this.queueUndoableAction('Pozycja finansowa zostanie usunięta za chwilę.', async () => {
                        const response = await fetch(`${this.API}/debts/${debtId}`, { method: 'DELETE' });
                        if (!response.ok) throw new Error('Nie udało się usunąć pozycji finansowej.');
                        await this.loadDebts(this.debtsMonthKey || this.getCurrentMonthKey());
                        this.showToast('Pozycja finansowa usunięta.', 'success');
                    });
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
                        this.showToast('Nie udalo sie zapisac statusu splaty.');
                        return;
                    }
                    await this.loadDebts(monthKey);
                },

                async shredTask() {
                    this.isShredding = true;
                    try {
                        const res = await fetch(`${this.API}/tasks/${this.editingTask.id}/shred`, { method: 'POST' });
                        let data = {};
                        try {
                            data = await res.json();
                        } catch (parseError) {
                            data = {};
                        }

                        if (!res.ok || data.error) {
                            const serverMessage = typeof data?.detail === 'string'
                                ? data.detail
                                : (typeof data?.error === 'string' ? data.error : '');
                            this.showToast(serverMessage || 'Nie udalo sie rozbic zadania przez AI.');
                            return;
                        }

                        this.taskModal = false;
                        await this.init();
                    } catch (error) {
                        this.showToast('Blad polaczenia z Ollama.');
                    } finally {
                        this.isShredding = false;
                    }
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
                        this.showToast('Najpierw dodaj zadanie do planera.');
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
                    this.closeMobileModules();
                    if (this.isMobileLayout) {
                        this.calendarMobileSection = 'preview';
                        this.calendarCursor = this.getTodayKey();
                        this.selectedDate = this.getTodayKey();
                    }
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
                    const tasks = this.getOpenTasks().filter(task => task.due_date === dateKey);
                    return [...tasks].sort((a, b) => {
                        const aTime = this.getTaskDueTime(a) || '99:99';
                        const bTime = this.getTaskDueTime(b) || '99:99';
                        const timeDiff = aTime.localeCompare(bTime, 'pl');
                        if (timeDiff !== 0) return timeDiff;

                        const priorityDiff = this.priorityRank(a.priority) - this.priorityRank(b.priority);
                        if (priorityDiff !== 0) return priorityDiff;

                        const statusDiff = this.statusRank(a.status) - this.statusRank(b.status);
                        if (statusDiff !== 0) return statusDiff;

                        return (a.name || '').localeCompare((b.name || ''), 'pl');
                    });
                },

                getSelectedDateTasks() {
                    return this.getTasksForDate(this.selectedDate || this.getTodayKey());
                },

                getSelectedDateEntries() {
                    return this.getCalendarAgendaEntriesForDate(this.selectedDate || this.getTodayKey());
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
                        const workload = this.getDayWorkloadSummary(dateKey);
                        days.push({
                            dateKey,
                            dayNumber: date.getDate(),
                            weekdayShort: new Intl.DateTimeFormat('pl-PL', { weekday: 'short' }).format(date),
                            isCurrentMonth: date.getMonth() === cursor.getMonth(),
                            isToday: dateKey === this.getTodayKey(),
                            isSelected: dateKey === this.selectedDate,
                            entries,
                            plannedMinutes: workload.plannedMinutes,
                            isOverLimit: workload.isOverLimit,
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
