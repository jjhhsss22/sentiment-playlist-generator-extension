
export const generateRequestId = () =>
  crypto.randomUUID().replaceAll("-", "");  // idempotency key