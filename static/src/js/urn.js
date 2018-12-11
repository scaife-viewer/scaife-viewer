export default class URN {
  constructor(value) {
    this.value = value;
    this.urnNamespace = null;
    this.ctsNamespace = null;
    this.textGroup = null;
    this.work = null;
    this.version = null;
    this.reference = null;
    this.parse();
  }

  parse() {
    const [urn] = this.value.split('#');
    let bits = urn.split(':').slice(1);
    if (bits.length > 2) {
      let workIdentifier = '';
      [this.urnNamespace, this.ctsNamespace, workIdentifier, this.reference] = bits;
      bits = workIdentifier.split('.');
      if (bits.length >= 1) {
        this.textGroup = bits[0]; // eslint-disable-line prefer-destructuring
      }
      if (bits.length >= 2) {
        this.work = bits[1]; // eslint-disable-line prefer-destructuring
      }
      if (bits.length >= 3) {
        this.version = bits[2]; // eslint-disable-line prefer-destructuring
      }
    }
  }

  upTo(segment) {
    const segments = ['urn', this.urnNamespace, this.ctsNamespace];
    const workSegments = [];
    if (['textGroup', 'work', 'version', 'reference'].indexOf(segment) !== -1 && this.textGroup) {
      workSegments.push(this.textGroup);
    }
    if (['work', 'version', 'reference'].indexOf(segment) !== -1 && this.work) {
      workSegments.push(this.work);
    }
    if (['version', 'reference'].indexOf(segment) !== -1 && this.version) {
      workSegments.push(this.version);
    }
    segments.push(workSegments.join('.'));
    if (segment === 'reference' && this.reference) {
      segments.push(this.reference);
    }
    return segments.join(':');
  }

  replace({
    textGroup, work, version, reference,
  }) {
    const clone = Object.assign(Object.create(Object.getPrototypeOf(this)), this);
    if (textGroup) {
      clone.textGroup = textGroup;
    }
    if (work) {
      clone.work = work;
    }
    if (version) {
      clone.version = version;
    }
    if (reference) {
      clone.reference = reference;
    }
    return clone;
  }

  toString() {
    return this.upTo('reference');
  }
}
