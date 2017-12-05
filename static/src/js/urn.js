
export default function parseURN(urn) {
  const parsed = {
    urnNamespace: null,
    ctsNamespace: null,
    textGroup: null,
    work: null,
    version: null,
    reference: null,
  };
  [urn] = urn.split('#');
  let bits = urn.split(':').slice(1);
  if (bits.length > 2) {
    let workIdentifier = '';
    [
      parsed.urnNamespace,
      parsed.ctsNamespace,
      workIdentifier,
      parsed.reference,
    ] = bits;
    bits = workIdentifier.split('.');
    if (bits.length >= 1) {
      parsed.textGroup = bits[0]; // eslint-disable-line prefer-destructuring
    }
    if (bits.length >= 2) {
      parsed.work = bits[1]; // eslint-disable-line prefer-destructuring
    }
    if (bits.length >= 3) {
      parsed.version = bits[2]; // eslint-disable-line prefer-destructuring
    }
  }
  return parsed;
}
