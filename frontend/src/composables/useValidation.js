export function useValidation() {
  const validatePwd = (pwd) => {
    const isValidLength = pwd.length >= 8;
    const hasNumber = /\d/.test(pwd);
    const hasEnglishOrKorean = /[a-zA-Z]|[가-힣]/.test(pwd);

    return isValidLength && hasNumber && hasEnglishOrKorean
      ? ""
      : "8자 이상, 숫자/한영을 포함해야 합니다.";
  };

  return {
    validatePwd,
  };
}