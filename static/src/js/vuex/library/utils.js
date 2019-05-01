import dayjs from 'dayjs';

function isQuotaExceeded(error) {
  let quotaExceeded = false;
  if (error) {
    if (error.code) {
      const code = parseInt(error.code, 10);
      // chrome and safari
      if (code === 22) {
        quotaExceeded = true;
      }
      // firefox
      if (code === 1014 && error.name === 'NS_ERROR_DOM_QUOTA_REACHED') {
        quotaExceeded = true;
      }
    } else if (error.number === -2147024882) {
      // internet explorer 8
      quotaExceeded = true;
    }
  }
  return quotaExceeded;
}

function isCacheValid(apiVersion, currentVersion) {
  if (!apiVersion || !currentVersion || !currentVersion.version || !currentVersion.date) {
    return false;
  }
  if (parseInt(apiVersion, 10) > parseInt(currentVersion.version, 10)) {
    return false;
  }
  if (dayjs().isAfter(dayjs(currentVersion.date).add(1, 'day'))) {
    return false;
  }
  return true;
}

export default {
  isQuotaExceeded,
  isCacheValid,
};
