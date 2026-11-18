import assert from 'node:assert/strict';
import test from 'node:test';
import { copyText } from '../public/assets/clipboard.mjs';

function browserFixture({ clipboard, modal = false, copied = true, throws = false } = {}) {
    const events = [];
    const field = {
        value: '',
        setAttribute(name, value) { events.push(['attribute', name, value]); },
        focus() { events.push('focus field'); },
        select() { events.push('select'); },
        setSelectionRange(start, end) { events.push(['range', start, end]); },
        remove() { events.push('remove'); },
    };
    const parent = (name) => ({ appendChild(element) { assert.equal(element, field); events.push(name); } });
    const document = {
        activeElement: { focus() { events.push('restore focus'); } },
        body: parent('body'),
        querySelector(selector) { assert.equal(selector, 'dialog[open]'); return modal ? parent('dialog') : null; },
        createElement(tag) { assert.equal(tag, 'textarea'); return field; },
        execCommand(command) {
            assert.equal(command, 'copy');
            assert.ok(events.includes('select'));
            events.push('copy');
            if (throws) throw new Error('Copy blocked');
            return copied;
        },
    };
    return { browser: { navigator: { clipboard }, document }, events, field };
}

test('uses the modern clipboard API when it succeeds', async () => {
    const values = [];
    const fixture = browserFixture({ clipboard: { async writeText(value) { values.push(value); } } });
    assert.equal(await copyText('make audit-mac', fixture.browser), true);
    assert.deepEqual(values, ['make audit-mac']);
    assert.deepEqual(fixture.events, []);
});

test('copies through the DOM when clipboard permission is denied', async () => {
    const fixture = browserFixture({ clipboard: { async writeText() { throw new Error('NotAllowedError'); } } });
    assert.equal(await copyText('make audit-mac', fixture.browser), true);
    assert.equal(fixture.field.value, 'make audit-mac');
    assert.ok(fixture.events.includes('body'));
    assert.deepEqual(fixture.events.slice(-2), ['remove', 'restore focus']);
});

test('supports browsers without the clipboard API', async () => {
    const fixture = browserFixture();
    assert.equal(await copyText('make preview-cache', fixture.browser), true);
    assert.ok(fixture.events.includes('copy'));
});

test('keeps the fallback inside an open modal so it can receive focus', async () => {
    const fixture = browserFixture({ modal: true });
    assert.equal(await copyText('make audit-mac', fixture.browser), true);
    assert.ok(fixture.events.includes('dialog'));
    assert.ok(!fixture.events.includes('body'));
});

test('reports a blocked DOM copy honestly and still removes temporary controls', async () => {
    const fixture = browserFixture({ copied: false });
    assert.equal(await copyText('make audit-mac', fixture.browser), false);
    assert.deepEqual(fixture.events.slice(-2), ['remove', 'restore focus']);
});

test('cleans up and restores focus if the fallback throws', async () => {
    const fixture = browserFixture({ throws: true });
    assert.equal(await copyText('make audit-mac', fixture.browser), false);
    assert.deepEqual(fixture.events.slice(-2), ['remove', 'restore focus']);
});

test('returns false if neither copy mechanism exists', async () => {
    assert.equal(await copyText('make audit-mac', {}), false);
});
