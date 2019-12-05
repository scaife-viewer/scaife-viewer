import { faArrowLeft } from '@fortawesome/free-solid-svg-icons/faArrowLeft';
import { faArrowRight } from '@fortawesome/free-solid-svg-icons/faArrowRight';
import { faExpandArrowsAlt } from '@fortawesome/free-solid-svg-icons/faExpandArrowsAlt';
import { faCompressArrowsAlt } from '@fortawesome/free-solid-svg-icons/faCompressArrowsAlt';
import { faChevronDown } from '@fortawesome/free-solid-svg-icons/faChevronDown';
import { faChevronLeft } from '@fortawesome/free-solid-svg-icons/faChevronLeft';
import { faChevronRight } from '@fortawesome/free-solid-svg-icons/faChevronRight';
import { faTimes } from '@fortawesome/free-solid-svg-icons/faTimes';
import { faBook } from '@fortawesome/free-solid-svg-icons/faBook';
import { faColumns } from '@fortawesome/free-solid-svg-icons/faColumns';

const iconMap = [
  faArrowLeft,
  faArrowRight,
  faExpandArrowsAlt,
  faCompressArrowsAlt,
  faChevronDown,
  faChevronLeft,
  faChevronRight,
  faTimes,
  faBook,
  faColumns,
].reduce((map, obj) => {
  map[obj.iconName] = obj;
  return map;
}, {});

export default iconMap;
