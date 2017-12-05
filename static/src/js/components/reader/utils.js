import parseURN from '../../urn';
import store from '../../store';

module.exports = {
  toPassage(urn) {
    const { state } = store;
    const p = parseURN(urn);
    if (!p.reference && this.passage) {
      const { reference: existingReference } = parseURN(state.reader.passage.urn);
      urn += `:${existingReference}`;
    }
    return { name: 'reader', params: { urn }, query: state.route.query };
  },
  toRightPassage(urn) {
    const { state } = store;
    const p = parseURN(urn);
    return { name: 'reader', params: state.route.params, query: { right: p.version } };
  },
  toRef(reference) {
    const { state } = store;
    const p = parseURN(state.reader.passage.urn);
    const urn = `urn:${p.urnNamespace}:${p.ctsNamespace}:${p.textGroup}.${p.work}.${p.version}:${reference}`;
    return { name: 'reader', params: { urn }, query: state.route.query };
  },
  toRemoveLeft() {
    const { state } = store;
    const p = parseURN(state.route.params.urn);
    let urn = `urn:${p.urnNamespace}:${p.ctsNamespace}:${p.textGroup}.${p.work}.${state.route.query.right}`;
    if (p.reference) {
      urn += `:${p.reference}`;
    }
    return { name: 'reader', params: { urn } };
  },
  toRemoveRight() {
    const { state } = store;
    return { name: 'reader', params: { urn: state.route.params.urn } };
  },
};
