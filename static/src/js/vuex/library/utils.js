function isQuotaExceeded(error) {
  console.log(error)
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

export default {
  isQuotaExceeded,
};
