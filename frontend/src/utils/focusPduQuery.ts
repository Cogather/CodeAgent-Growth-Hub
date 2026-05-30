export function appendFocusPduOnly(search: URLSearchParams, enabled: boolean) {
  if (enabled) {
    search.set('focus_pdu_only', 'true')
  }
}
