// Run with: node --test tests/test_task_ui.cjs
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const root = path.resolve(__dirname, '..');

function setup({ mobile = false } = {}) {
    let now = Date.parse('2026-09-15T10:00:00Z');
    let timerId = 0;
    const timers = new Map();
    const writes = [];
    class Clock extends Date {
        constructor(...args) { super(...(args.length ? args : [now])); }
        static now() { return now; }
    }
    const sandbox = {
        Date: Clock,
        setTimeout(fn, delay) { timers.set(++timerId, { fn, at: now + delay }); return timerId; },
        clearTimeout(id) { timers.delete(id); },
        matchMedia: () => ({ matches: mobile }),
    };
    sandbox.window = sandbox;
    vm.createContext(sandbox);
    // Load the same local entry points as the page, including any wrappers.
    const html = fs.readFileSync(path.join(root, 'index.html'), 'utf8');
    for (const match of html.matchAll(/<script[^>]*src="\/(static\/[^"?]+\.js)(?:\?[^\"]*)?"/g)) {
        vm.runInContext(fs.readFileSync(path.join(root, match[1]), 'utf8'), sandbox);
    }
    const state = new Proxy(sandbox.app(), {
        set(target, key, value) { writes.push(key); target[key] = value; return true; },
    });
    state.$nextTick = fn => fn();
    state.$refs = {};
    writes.length = 0;
    return { state, writes, advance(ms) {
        now += ms;
        for (const [id, timer] of [...timers]) {
            if (timer.at <= now) { timers.delete(id); timer.fn(); }
        }
    } };
}

function subtask(id, title, extra = {}) {
    return { id, title, done: false, done_at: '', estimated_time: 15, points_weight: 1, ...extra };
}

test('opening and closing a task update reactive state', () => {
    const { state, writes } = setup();
    state.openNewTaskModal();
    assert.equal(state.taskModal, true);
    for (const key of ['editingTask', 'taskModal', 'isCreatingTask']) {
        assert.ok(writes.includes(key), `${key} must be written through the reactive context`);
    }
    state.closeTaskModal();
    assert.equal(state.taskModal, false);
    assert.equal(state.isCreatingTask, false);
});

test('quick capture hands its draft to details without delayed reopening', () => {
    const { state, advance, writes } = setup({ mobile: true });
    state.quickCaptureOpen = true;
    state.quickCaptureText = '  Przygotować plan  ';
    state.openDetailsFromQuickCapture();
    assert.equal(state.quickCaptureOpen, false);
    assert.equal(state.editingTask.name, 'Przygotować plan');
    assert.equal(state.taskDetailsOpen, true);
    assert.equal(state.taskModal, true);
    assert.ok(writes.includes('taskModal'));
    state.closeTaskModal();
    advance(1000);
    assert.equal(state.taskModal, false);
});

test('completing a subtask keeps it visible for three seconds and allows undo', () => {
    const { state, advance } = setup();
    state.openNewTaskModal();
    const item = state.createSubtaskDraft('Krok');
    state.editingTask.subtasks = [item];
    state.toggleEditingSubtaskDone(item, true);
    assert.equal(state.getEditingSubtaskEntries(false).length, 1);
    advance(2999);
    assert.equal(state.getEditingSubtaskEntries(true).length, 0);
    advance(2);
    assert.equal(state.getEditingSubtaskEntries(false).length, 0);
    assert.equal(state.getEditingSubtaskEntries(true).length, 1);
    assert.ok(state.subtaskUiTick > 0, 'expiry must trigger a reactive refresh');
    state.toggleEditingSubtaskDone(item, false);
    assert.equal(state.getEditingSubtaskEntries(false).length, 1);
    assert.equal(item.done_at, '');
});

test('reordering skips folded entries and keeps draft identity and metadata', () => {
    const { state } = setup();
    state.openNewTaskModal();
    const first = state.createSubtaskDraft('Ta sama nazwa');
    const second = state.createSubtaskDraft('Ta sama nazwa');
    const done = subtask(8, 'Gotowe', { done: true, done_at: '2026-01-01T00:00:00Z' });
    first.estimated_time = 135;
    second.estimated_time = 37;
    state.editingTask.subtasks = [first, done, second];
    state.moveEditingSubtask(2, -1);
    assert.equal(state.editingTask.subtasks[0], second);
    assert.equal(state.editingTask.subtasks[2], first);
    assert.notEqual(first._uiKey, second._uiKey);
    const payload = state.pickTaskPayload(state.editingTask);
    assert.deepEqual(Array.from(payload.subtasks, item => item.estimated_time), [37, 15, 135]);
    assert.equal(payload.subtasks[1].done_at, done.done_at);
    assert.equal(payload.subtasks[0]._uiKey, undefined);
});

test('card completion targets the ID and the delay survives new IDs returned by the API', async () => {
    const { state, advance } = setup();
    const task = { id: 1, name: 'Zadanie', subtasks: [subtask(2, 'Krok'), subtask(3, 'Krok')] };
    state.tasks = [task];
    state.patchTask = async () => ({ ok: true });
    state.loadAllTasks = async () => {
        state.tasks = [{ ...task, subtasks: task.subtasks.map(item => ({ ...item, id: item.id + 100 })) }];
        state.scheduleSubtaskHideRefresh();
    };
    await state.toggleCardSubtask(task, task.subtasks[0], true);
    assert.equal(state.tasks[0].subtasks[0].done, true);
    assert.equal(state.tasks[0].subtasks[1].done, false);
    assert.equal(state.getVisibleCardSubtasks(state.tasks[0]).length, 2);
    advance(3001);
    assert.equal(state.getVisibleCardSubtasks(state.tasks[0]).length, 1);
    assert.equal(state.getHiddenCardSubtasks(state.tasks[0]).length, 1);
});

test('failed card save rolls back the checkbox and releases the saving guard', async () => {
    const { state } = setup();
    const task = { id: 4, subtasks: [subtask(1, 'Krok')] };
    state.tasks = [task];
    state.patchTask = async () => ({ ok: false });
    state.showToast = () => {};
    await state.toggleCardSubtask(task, task.subtasks[0], true);
    assert.equal(task.subtasks[0].done, false);
    assert.equal(state.cardSubtaskSaving[task.id], undefined);
});
