(function wrapAdhdFocusApp() {
    const originalApp = window.app;
    if (typeof originalApp !== "function" || originalApp.__compactWrapped) return;

    function wrappedApp() {
        const ctx = originalApp();

        ctx.subtaskUiTick = ctx.subtaskUiTick || 0;
        ctx.doneSubtasksExpanded = false;
        ctx.cardDoneExpanded = ctx.cardDoneExpanded || {};
        ctx.pendingHideKeys = ctx.pendingHideKeys || {};

        ctx.getSubtaskUiKey = function(taskId, subtask, index) {
            const idPart = subtask?.id ? `id-${subtask.id}` : `ix-${index}-${subtask?.title || ""}`;
            return `${taskId || "edit"}:${idPart}`;
        };

        ctx.isSubtaskPendingHide = function(subtask, index, taskId = "edit") {
            const until = this.pendingHideKeys[this.getSubtaskUiKey(taskId, subtask, index)];
            return !!until && Date.now() < until;
        };

        ctx.scheduleSubtaskHide = function(subtask, index, taskId = "edit") {
            const key = this.getSubtaskUiKey(taskId, subtask, index);
            this.pendingHideKeys = { ...this.pendingHideKeys, [key]: Date.now() + 3000 };
            this.subtaskUiTick++;
            window.setTimeout(() => { this.subtaskUiTick++; }, 3050);
        };

        ctx.clearSubtaskHide = function(subtask, index, taskId = "edit") {
            const key = this.getSubtaskUiKey(taskId, subtask, index);
            if (!this.pendingHideKeys[key]) return;
            const next = { ...this.pendingHideKeys };
            delete next[key];
            this.pendingHideKeys = next;
            this.subtaskUiTick++;
        };

        ctx.getVisibleEditingSubtasks = function() {
            const list = Array.isArray(this.editingTask?.subtasks) ? this.editingTask.subtasks : [];
            this.subtaskUiTick;
            return list
                .map((subtask, index) => ({ subtask, index }))
                .filter(({ subtask, index }) => !subtask.done || this.isSubtaskPendingHide(subtask, index));
        };

        ctx.getHiddenEditingSubtasks = function() {
            const list = Array.isArray(this.editingTask?.subtasks) ? this.editingTask.subtasks : [];
            this.subtaskUiTick;
            return list.filter((subtask, index) => subtask.done && !this.isSubtaskPendingHide(subtask, index));
        };

        ctx.moveEditingSubtask = function(index, direction) {
            const current = Array.isArray(this.editingTask?.subtasks) ? [...this.editingTask.subtasks] : [];
            const nextIndex = index + direction;
            if (nextIndex < 0 || nextIndex >= current.length) return;
            const [item] = current.splice(index, 1);
            current.splice(nextIndex, 0, item);
            this.editingTask.subtasks = current;
        };

        ctx.toggleCardDoneSubtasks = function(taskId) {
            const key = String(taskId);
            this.cardDoneExpanded = {
                ...this.cardDoneExpanded,
                [key]: !this.cardDoneExpanded[key]
            };
        };

        ctx.getHiddenCardSubtaskCount = function(task) {
            this.subtaskUiTick;
            const all = this.normalizeSubtasks(task?.subtasks);
            if (this.cardDoneExpanded[String(task?.id)]) return all.filter(item => item.done).length;
            return all.filter((subtask, index) => subtask.done && !this.isSubtaskPendingHide(subtask, index, task?.id)).length;
        };

        ctx.getVisibleCardSubtasks = function(task, limit = 4) {
            this.subtaskUiTick;
            const all = this.normalizeSubtasks(task?.subtasks);
            if (this.cardDoneExpanded[String(task?.id)]) return all;
            const visible = all.filter((subtask, index) => !subtask.done || this.isSubtaskPendingHide(subtask, index, task?.id));
            return visible.slice(0, limit);
        };

        const originalToggleEdit = ctx.toggleEditingSubtaskDone?.bind(ctx);
        ctx.toggleEditingSubtaskDone = function(subtask, checked) {
            if (originalToggleEdit) originalToggleEdit(subtask, checked);
            else {
                if (!subtask) return;
                subtask.done = !!checked;
                subtask.done_at = subtask.done ? new Date().toISOString() : "";
            }
            const list = Array.isArray(this.editingTask?.subtasks) ? this.editingTask.subtasks : [];
            const index = list.indexOf(subtask);
            if (subtask?.done) this.scheduleSubtaskHide(subtask, index);
            else this.clearSubtaskHide(subtask, index);
        };

        const originalToggleCard = ctx.toggleCardSubtask?.bind(ctx);
        ctx.toggleCardSubtask = async function(task, subtask, checked) {
            if (task && subtask) {
                const list = this.normalizeSubtasks(task.subtasks);
                const index = list.findIndex(item => (
                    (item.id && subtask.id && Number(item.id) === Number(subtask.id))
                    || item.title === subtask.title
                ));
                if (checked) this.scheduleSubtaskHide(subtask, index, task.id);
                else this.clearSubtaskHide(subtask, index, task.id);
            }
            if (originalToggleCard) return originalToggleCard(task, subtask, checked);
        };

        const originalOpen = ctx.openTaskModal?.bind(ctx);
        ctx.openTaskModal = function(task) {
            if (originalOpen) originalOpen(task);
            if (this.detectMobileLayout()) this.taskDetailsOpen = false;
            this.doneSubtasksExpanded = false;
        };

        const originalNew = ctx.openNewTaskModal?.bind(ctx);
        ctx.openNewTaskModal = function(preferredModuleId = null) {
            if (originalNew) originalNew(preferredModuleId);
            this.doneSubtasksExpanded = false;
        };

        return ctx;
    }

    wrappedApp.__compactWrapped = true;
    window.app = wrappedApp;
})();
