/** Copy a command across secure-context and permission-restricted browsers. */
export async function copyText(text, browser = globalThis) {
    try {
        if (typeof browser.navigator?.clipboard?.writeText === 'function') {
            await browser.navigator.clipboard.writeText(text);
            return true;
        }
    } catch {
        // Embedded browsers can reject the API even on HTTPS; try native Copy.
    }

    const document = browser.document;
    if (typeof document?.execCommand !== 'function') return false;
    const previousFocus = document.activeElement;
    let field;
    try {
        field = document.createElement('textarea');
        field.value = text;
        field.className = 'clipboard-buffer';
        field.setAttribute('readonly', '');
        field.setAttribute('tabindex', '-1');
        field.setAttribute('aria-label', 'Copy command');
        (document.querySelector('dialog[open]') || document.body).appendChild(field);
        field.focus();
        field.select();
        field.setSelectionRange(0, text.length);
        return document.execCommand('copy') === true;
    } catch {
        return false;
    } finally {
        field?.remove();
        previousFocus?.focus({ preventScroll: true });
    }
}
