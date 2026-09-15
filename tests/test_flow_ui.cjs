// Run with: node --test tests/test_flow_ui.cjs
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const root = path.resolve(__dirname, '..');
const minute = 60000;

function setup() {
    let now = Date.parse('2026-09-15T10:00:00Z');
    let timerId = 0;
    const intervals = new Map();
    const storage = new Map();
    const messages = [];
    class Clock extends Date {
        constructor(...args) { super(...(args.length ? args : [now])); }
        static now() { return now; }
    }
    const sandbox = {
        Date: Clock,
        setInterval(fn) { intervals.set(++timerId, fn); return timerId; },
        clearInterval(id) { intervals.delete(id); },
        localStorage: {
            getItem: key => storage.get(key) ?? null,
            setItem: (key, value) => storage.set(key, value),
        },
    };
    sandbox.window = sandbox;
    vm.createContext(sandbox);
    const html = fs.readFileSync(path.join(root, 'index.html'), 'utf8');
    for (const match of html.matchAll(/<script[^>]*src="\/(static\/[^"?]+\.js)(?:\?[^\"]*)?"/g)) {
        vm.runInContext(fs.readFileSync(path.join(root, match[1]), 'utf8'), sandbox);
    }
    const state = sandbox.app();
    state.tasks = [{ id: 1, name: 'Spokojna praca', status: 'todo', estimated_time: 120, subtasks: [] }];
    state.getFocusTask = () => state.tasks[0];
    state.showToast = message => messages.push(message);
    state.init = async () => state.loadUIPreferences();
    state.patchTask = async () => ({ ok: true });
    return { state, storage, messages, intervals, now: () => now, elapse(ms, tick = true) {
        now += ms;
        // A suspended tab may run only one callback after a long gap.
        if (tick) for (const callback of [...intervals.values()]) callback();
    } };
}

test('a delayed tick catches up elapsed time and shows the overdue break', async () => {
    const { state, elapse, intervals } = setup();
    await state.startFlow();
    elapse(65 * minute);
    assert.equal(state.flowTimer, 55 * 60);
    assert.equal(state.flowBreakPending, true);
    elapse(2 * minute);
    assert.equal(state.flowTimer, 53 * 60);
    assert.equal(state.flowBreakPending, true);
    assert.equal(intervals.size, 1);
});

test('snooze waits fifteen minutes from the click without changing the preference', async () => {
    const { state, elapse } = setup();
    await state.startFlow();
    elapse(65 * minute);
    state.snoozeFlowBreak();
    assert.equal(state.flowBreakPending, false);
    assert.equal(state.flowBreakMinutes, 60);
    elapse(15 * minute - 1);
    assert.equal(state.flowBreakPending, false);
    elapse(1);
    assert.equal(state.flowBreakPending, true);
    assert.equal(state.flowTimer, 40 * 60);
});

test('a break freezes task time and resume starts a fresh break interval', async () => {
    const { state, elapse, now } = setup();
    await state.startFlow();
    elapse(30 * minute, false);
    state.pauseFlow();
    assert.equal(state.flowTimer, 90 * 60, 'pause catches up before freezing');
    assert.equal(state.flowPaused, true);
    elapse(2 * 60 * minute);
    assert.equal(state.flowTimer, 90 * 60);
    assert.equal(state.flowBreakPending, false);
    state.resumeFlow();
    assert.equal(state.flowBreakDueAt, now() + 60 * minute);
    elapse(20 * minute);
    assert.equal(state.flowTimer, 70 * 60);
    assert.equal(state.flowPaused, false);
    assert.equal(state.flowBreakPending, false);
});

test('returning to focus preserves the running or paused task and its timer', async () => {
    const { state, elapse, intervals } = setup();
    await state.startFlow();
    const original = state.flowTask;
    const dueAt = state.flowBreakDueAt;
    state.view = 'dash';
    state.tasks = [{ id: 2, name: 'Inne zadanie', status: 'todo', estimated_time: 10 }];
    elapse(10 * minute, false);
    await state.startFlow();
    assert.equal(state.flowTask, original);
    assert.equal(state.flowTimer, 110 * 60);
    assert.equal(state.flowBreakDueAt, dueAt);
    assert.equal(intervals.size, 1);
    state.pauseFlow();
    state.view = 'dash';
    elapse(20 * minute);
    await state.startFlow();
    assert.equal(state.flowPaused, true);
    assert.equal(state.flowTimer, 110 * 60);
});

test('interval preferences survive reload, can be disabled and ignore corrupt values', async () => {
    const { state, storage, elapse, now } = setup();
    state.setFlowBreakMinutes('90');
    assert.equal(JSON.parse(storage.get(state.uiPrefsKey)).flowBreakMinutes, 90);
    state.flowBreakMinutes = 60;
    state.loadUIPreferences();
    assert.equal(state.flowBreakMinutes, 90);
    await state.startFlow();
    elapse(60 * minute);
    assert.equal(state.flowBreakPending, false);
    state.setFlowBreakMinutes('50');
    assert.equal(state.flowBreakDueAt, now() + 50 * minute);
    elapse(50 * minute);
    assert.equal(state.flowBreakPending, true);
    state.setFlowBreakMinutes('0');
    elapse(8 * 60 * minute);
    assert.equal(state.flowBreakPending, false);
    state.loadUIPreferences();
    assert.equal(state.flowBreakMinutes, 0, 'disabled is a valid saved preference');
    state.pauseFlow();
    state.setFlowBreakMinutes('60');
    assert.equal(state.flowBreakDueAt, 0, 'changing settings during a break keeps it paused');
    state.resumeFlow();
    assert.equal(state.flowBreakDueAt, now() + 60 * minute);
    storage.set(state.uiPrefsKey, JSON.stringify({ flowBreakMinutes: 'broken', theme: 'dark' }));
    state.loadUIPreferences();
    assert.equal(state.flowBreakMinutes, 60);
    assert.equal(state.theme, 'dark');
});

test('reminders continue past estimated task time and stop when the session ends', async () => {
    const { state, elapse, intervals } = setup();
    state.tasks[0].estimated_time = 15;
    await state.startFlow();
    elapse(60 * minute);
    assert.equal(state.flowTimer, 0);
    assert.equal(state.flowBreakPending, true);
    state.skipFlowTask();
    assert.equal(state.flowTask, null);
    assert.equal(state.flowBreakPending, false);
    assert.equal(intervals.size, 0);
    assert.equal(state.tasks[0].status, 'todo', 'ending focus does not complete the task');
    await state.startFlow();
    assert.equal(state.flowBreakPending, false);
    await state.completeFlowTask();
    elapse(2 * 60 * minute);
    assert.equal(state.flowTask, null);
    assert.equal(state.flowBreakPending, false);
    assert.equal(intervals.size, 0);
});

test('failed start or completion keeps task and timer state recoverable', async () => {
    const { state, intervals, messages } = setup();
    state.patchTask = async () => ({ ok: false, json: async () => ({ detail: 'Brak dostępu' }) });
    state.tasks[0].status = 'oczekujace';
    await state.startFlow();
    assert.equal(state.flowTask, null);
    assert.equal(state.flowStarting, false);
    assert.equal(intervals.size, 0);
    state.tasks[0].status = 'todo';
    await state.startFlow();
    state.pauseFlow();
    await state.completeFlowTask();
    assert.equal(state.flowTask.id, 1);
    assert.equal(state.flowPaused, true);
    assert.equal(state.flowCompleting, false);
    assert.equal(intervals.size, 1);
    state.patchTask = async () => { throw new Error('offline'); };
    await state.completeFlowTask();
    assert.equal(state.flowTask.id, 1);
    assert.equal(state.flowCompleting, false);
    assert.ok(messages.length >= 3);
    state.patchTask = async () => ({ ok: true });
    await state.completeFlowTask();
    assert.equal(state.flowTask, null);
    assert.equal(intervals.size, 0);
});

test('repeated completion clicks do not send duplicate writes or abandon an active save', async () => {
    const { state } = setup();
    await state.startFlow();
    let release;
    let writes = 0;
    state.patchTask = () => { writes++; return new Promise(resolve => { release = resolve; }); };
    const saving = state.completeFlowTask();
    await state.completeFlowTask();
    state.skipFlowTask();
    assert.equal(writes, 1);
    assert.equal(state.flowTask.id, 1);
    release({ ok: true });
    await saving;
    assert.equal(state.flowTask, null);
    assert.equal(state.flowCompleting, false);
});
