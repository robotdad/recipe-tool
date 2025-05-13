import {
  HTTPError,
  NetworkError,
  TimeoutError,
  AbortError,
  ResponseParseError
} from './types.js';

let defaultBaseUrl = '/api/execute';
let logger = console;

/**
 * Override the default endpoint for all subsequent calls
 * @param {string} url
 */
export function setBaseUrl(url) {
  defaultBaseUrl = url;
}

/**
 * Provide a custom logger with debug() and info() methods
 * @param {{ debug: (...args: any[]) => void, info: (...args: any[]) => void }} customLogger
 */
export function setLogger(customLogger) {
  if (customLogger && typeof customLogger.debug === 'function' && typeof customLogger.info === 'function') {
    logger = customLogger;
  }
}

/**
 * Submit a recipe flow JSON to the execution API
 * @param {Object} flowJson
 * @param {import('./types.js').RequestOptions} [options]
 * @returns {Promise<import('./types.js').ExecutionResult|{response: Response, data: any|null}>}
 */
export async function runRecipe(flowJson, options = {}) {
  const {
    baseUrl,
    headers = {},
    timeout,
    signal: externalSignal,
    fetchOptions = {},
    returnRawResponse = false
  } = options;

  const url = baseUrl || defaultBaseUrl;
  const payload = JSON.stringify(flowJson);
  const finalHeaders = Object.assign({ 'Content-Type': 'application/json' }, headers);

  logger.info(`Starting execution request to ${url}`);
  logger.debug('Request headers:', finalHeaders);
  logger.debug('Request payload:', payload);

  // Create an AbortController to handle timeout and external abort
  const controller = new AbortController();
  const signals = [controller.signal];
  if (externalSignal) {
    // propagate external abort
    externalSignal.addEventListener('abort', () => controller.abort());
  }

  // Timeout promise
  let timeoutId;
  const timeoutPromise = timeout > 0
    ? new Promise((_, reject) => {
        timeoutId = setTimeout(() => {
          controller.abort();
          reject(new TimeoutError());
        }, timeout);
      })
    : null;

  // Fetch promise
  const fetchPromise = (async () => {
    try {
      const response = await fetch(url, Object.assign({}, fetchOptions, {
        method: 'POST',
        headers: finalHeaders,
        body: payload,
        signal: controller.signal
      }));
      return response;
    } catch (err) {
      // Network failures and aborts
      if (err instanceof TimeoutError) throw err;
      if (err.name === 'AbortError') {
        throw new AbortError();
      }
      // fetch throws TypeError on network errors
      if (err instanceof TypeError) {
        throw new NetworkError();
      }
      throw err;
    }
  })();

  let response;
  try {
    response = timeoutPromise
      ? await Promise.race([fetchPromise, timeoutPromise])
      : await fetchPromise;
  } catch (err) {
    // clear timer if set
    if (timeoutId) clearTimeout(timeoutId);
    throw err;
  }

  // clear timeout if fetch succeeded
  if (timeoutId) clearTimeout(timeoutId);

  // Log status and headers
  logger.info(`Execution request completed with status ${response.status}`);
  const headersObj = {};
  response.headers.forEach((value, key) => {
    headersObj[key] = value;
  });
  logger.debug('Response headers:', headersObj);

  // Handle non-2xx
  if (response.status < 200 || response.status >= 300) {
    throw new HTTPError(response.status, response.statusText);
  }

  // Handle 204 No Content
  let data = null;
  if (response.status !== 204) {
    try {
      data = await response.json();
    } catch (err) {
      logger.debug('Raw response text for debugging');
      throw new ResponseParseError();
    }
  }

  logger.info(`Execution succeeded with status ${response.status}`);

  if (returnRawResponse) {
    return { response, data };
  }

  return {
    status: response.status,
    headers: headersObj,
    data
  };
}
