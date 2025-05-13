/**
 * @typedef {Object} RequestOptions
 * @property {string} [baseUrl] Override the default endpoint for this call
 * @property {Record<string,string>} [headers] Additional HTTP headers
 * @property {number} [timeout] Timeout in milliseconds before rejecting
 * @property {AbortSignal} [signal] Signal to abort the request
 * @property {Object} [fetchOptions] Extra options passed directly to fetch()
 * @property {boolean} [returnRawResponse] If true, returns raw Response with data
 */

/**
 * @typedef {Object} ExecutionResult
 * @property {number} status HTTP status code
 * @property {Record<string,string>} headers Response headers as a key/value object
 * @property {any|null} data Parsed response data, or null for 204 No Content
 */

/**
 * Error thrown for non-2xx HTTP responses
 */
export class HTTPError extends Error {
  /**
   * @param {number} status HTTP status code
   * @param {string} statusText HTTP status text
   */
  constructor(status, statusText) {
    super(`Execution API returned non-OK status code: ${status} ${statusText}`);
    this.name = 'HTTPError';
    this.status = status;
    this.statusText = statusText;
  }
}

/** Error thrown when network failure occurs */
export class NetworkError extends Error {
  constructor() {
    super('Failed to send execution request due to network issues');
    this.name = 'NetworkError';
  }
}

/** Error thrown when the request times out */
export class TimeoutError extends Error {
  constructor() {
    super('Execution request timed out');
    this.name = 'TimeoutError';
  }
}

/** Error thrown when the request is aborted */
export class AbortError extends Error {
  constructor() {
    super('Execution request was aborted');
    this.name = 'AbortError';
  }
}

/** Error thrown when JSON parsing of the response fails */
export class ResponseParseError extends Error {
  constructor() {
    super('Failed to parse execution API JSON response');
    this.name = 'ResponseParseError';
  }
}
