export default {
  textMode: 'browser',
  sidebarLeftOpened: true,
  sidebarRightOpened: true,
  versions: null,
  leftText: null,
  rightText: null,
  lowerText: null,
  leftPassage: null,
  rightPassage: null,
  lowerPassage: null,
  leftPassageText: null,
  rightPassageText: null,
  lowerPassageText: null,
  highlight: null,
  annotations: new Map(),
  annotationsHash: {},
  annotationChange: 0,
  // FIXME: Remove placeholder
  commentaryTokensHash: {
    '1.1.t2': ['foo'],
  },
  selectedLemmas: null,
  error: '',
  selectedTokenRange: { start: null, end: null },
};
