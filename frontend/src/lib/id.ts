export function createId(): string {
  if (typeof globalThis !== 'undefined') {
    const cryptoObject = globalThis.crypto as Crypto | undefined;
    if (cryptoObject && typeof cryptoObject.randomUUID === 'function') {
      return cryptoObject.randomUUID();
    }
  }

  return `id-${Date.now()}-${Math.random().toString(36).slice(2, 11)}`;
}
