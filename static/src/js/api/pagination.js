import parseLinkHeader from 'parse-link-header';
import URN from '../urn';

export default (response) => {
  const p = {};
  if (response.headers.link) {
    const links = parseLinkHeader(response.headers.link);
    if (links.prev) {
      p.prev = {
        url: links.prev.url,
        urn: links.prev.urn,
        ref: new URN(links.prev.urn).reference,
      };
    }
    if (links.next) {
      p.next = {
        url: links.next.url,
        urn: links.next.urn,
        ref: new URN(links.next.urn).reference,
      };
    }
  }
  return p;
};
