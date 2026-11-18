'use strict';

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];
let toastTimer;
function announce(message) {
    const toast = $('#copy-status');
    toast.textContent = message;
    toast.hidden = false;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => { toast.hidden = true; }, 4500);
}
$$('[data-copy]').forEach((button) => button.addEventListener('click', async () => {
    try {
        await navigator.clipboard.writeText(button.dataset.copy);
        announce('Command copied. Run it in your project’s Terminal.');
    } catch {
        announce('Clipboard unavailable. Copy this command: ' + button.dataset.copy);
    }
}));

let selectedCategory = 'all';
function filterTools() {
    const query = $('#tool-search').value.trim().toLocaleLowerCase();
    let count = 0;
    $$('[data-tool]').forEach((tool) => {
        tool.hidden = !(tool.dataset.tool.includes(query) && (selectedCategory === 'all' || tool.dataset.toolCategory === selectedCategory));
        if (!tool.hidden) count++;
    });
    $('#no-tools').hidden = count > 0;
}
$$('[data-category]').forEach((button) => button.addEventListener('click', () => {
    selectedCategory = button.dataset.category;
    $$('[data-category]').forEach((tab) => {
        const selected = tab === button;
        tab.classList.toggle('selected', selected);
        tab.setAttribute('aria-pressed', String(selected));
    });
    filterTools();
}));
$('#tool-search').addEventListener('input', filterTools);
document.addEventListener('keydown', (event) => {
    if (event.key === '/' && !event.ctrlKey && !event.metaKey && !/INPUT|TEXTAREA|SELECT/.test(document.activeElement.tagName) && !$('#refresh-dialog').open) {
        event.preventDefault();
        $('#tool-search').focus();
    }
});

let showAll = false;
function filterProjects() {
    const rows = $$('[data-project]');
    if (!rows.length) return;
    const query = $('#project-search').value.trim().toLocaleLowerCase();
    const byName = $('#project-sort').value === 'name';
    rows.sort((a, b) => byName ? a.dataset.project.localeCompare(b.dataset.project) : Number(b.dataset.size) - Number(a.dataset.size));
    let matches = 0;
    let visible = 0;
    rows.forEach((row) => {
        $('#project-rows').append(row);
        const match = row.dataset.project.includes(query);
        row.hidden = !match || (!showAll && !query && matches >= 8);
        if (match) matches++;
        if (!row.hidden) visible++;
    });
    $('#project-count').textContent = `Showing ${visible} of ${matches} projects`;
    $('#no-projects').hidden = matches !== 0;
    if ($('#show-projects')) {
        $('#show-projects').hidden = matches <= 8 || !!query;
        $('#show-projects').textContent = showAll ? 'Show fewer projects' : 'Show all projects';
    }
}
$('#project-search').addEventListener('input', filterProjects);
$('#project-sort').addEventListener('change', filterProjects);
$('#show-projects')?.addEventListener('click', () => { showAll = !showAll; filterProjects(); });

$('#refresh-open').addEventListener('click', () => $('#refresh-dialog').showModal());
$('#refresh-close').addEventListener('click', () => $('#refresh-dialog').close());
$('#reload-page').addEventListener('click', () => location.reload());
$('#refresh-dialog').addEventListener('click', (event) => {
    if (event.target === $('#refresh-dialog')) {
        const box = event.target.getBoundingClientRect();
        if (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom) event.target.close();
    }
});
$('#menu-toggle').addEventListener('click', () => {
    const open = $('#sidebar').classList.toggle('is-open');
    $('#menu-toggle').setAttribute('aria-expanded', String(open));
});
$$('.nav-link').forEach((link) => link.addEventListener('click', () => {
    $$('.nav-link').forEach((item) => item.classList.toggle('active', item === link));
    $('#sidebar').classList.remove('is-open');
    $('#menu-toggle').setAttribute('aria-expanded', 'false');
}));
