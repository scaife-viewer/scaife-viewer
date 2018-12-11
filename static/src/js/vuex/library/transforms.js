import URN from '../../urn';

export const transformTextGroupList = (data) => {
  const textGroups = data.text_groups.map((textGroup) => {
    return {
      ...textGroup,
      urn: new URN(textGroup.urn),
      works: textGroup.works.map(work => ({
        ...work,
        urn: new URN(work.urn),
        texts: work.texts.map(text => ({
          ...text,
          urn: new URN(text.urn),
        })),
      })),
    };
  });

  const works = data.works.map((work) => {
    return {
      ...work,
      urn: new URN(work.urn),
      texts: work.texts.map(text => ({
        ...text,
        urn: new URN(text.urn),
      })),
    };
  });

  const texts = data.texts.map((text) => {
    return {
      urn: new URN(text.urn),
      ...text,
    };
  });

  const textGroupUrns = {};
  textGroups.reduce((map, o) => {
    map[o.urn] = o;
    return map;
  }, textGroupUrns);
  works.reduce((map, o) => {
    map[o.urn] = o;
    return map;
  }, textGroupUrns);
  texts.reduce((map, o) => {
    map[o.urn] = o;
    return map;
  }, textGroupUrns);

  return {
    textGroups, works, texts, textGroupUrns,
  };
};

