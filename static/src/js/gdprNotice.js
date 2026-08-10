/* global $ */
const STORAGE_KEY = 'sv-gdpr-notice-dismissed';

export default function initGdprNotice() {
  const $notice = $('#gdprNotice');
  if ($notice.length === 0) {
    return;
  }
  $notice.on('closed.bs.alert', () => {
    try {
      window.localStorage.setItem(STORAGE_KEY, '1');
    } catch (e) {
      // localStorage unavailable (e.g. private browsing); nothing to persist
    }
  });
}
