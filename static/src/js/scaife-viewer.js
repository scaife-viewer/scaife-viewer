import parseLinkHeader from 'parse-link-header';
import qs from 'query-string';


class Reference {
  constructor(value) {
    this.value = value;
    this.parse();
  }
  parse() {
    this.value.split('-');
  }
}

class URN {
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
  replace({ textGroup, work, version, reference }) {
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

module.exports = {
  Reference,
  URN,
  async handleError(res) {
    if (!res.ok) {
      if (res.headers.get('content-type') === 'application/json') {
        const err = await res.json();
        throw new Error(`[${res.status}] ${res.statusText}: ${err.reason}`);
      } else {
        throw new Error(`[${res.status}] ${res.statusText}`);
      }
    }
  },
  async fetchCollection(urn) {
    const url = `/library/${urn}/json/`;
    const res = await fetch(url);
    await this.handleError(res);
    return res.json();
  },
  async fetchCollectionVector(urn, ends) {
    const params = qs.stringify({ e: ends });
    const url = `/library/vector/${urn}/?${params}`;
    const res = await fetch(url);
    await this.handleError(res);
    const vector = await res.json();
    return Object.values(vector.collections);
  },
  async fetchPassage(urn) {
    const url = `/library/passage/${urn}/json/`;
    const res = await fetch(url);
    await this.handleError(res);
    const pagination = {};
    if (res.headers.has('link')) {
      const links = parseLinkHeader(res.headers.get('link'));
      if (links.prev) {
        pagination.prev = {
          url: links.prev.url,
          urn: links.prev.urn,
          ref: new URN(links.prev.urn).reference,
        };
      }
      if (links.next) {
        pagination.next = {
          url: links.next.url,
          urn: links.next.urn,
          ref: new URN(links.next.urn).reference,
        };
      }
    }
    const metadata = await res.json();
    return { ...metadata, ...pagination };
  },
  async textSearch({ q, size, offset, ...scope }) {
    const params = { q, size, offset, ...scope };
    const url = `/search/json/?${qs.stringify(params)}`;
    const res = await fetch(url);
    await this.handleError(res);
    return res.json();
  },
};
