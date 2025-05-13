// src/integration/storage_service.js

// Default configuration
let baseURL = (typeof process !== 'undefined' && process.env && process.env.STORAGE_SERVICE_BASE_URL) || '/api';
const DEFAULT_TIMEOUT = 30000; // ms

// Log initial baseURL
console.debug(`Using base URL: ${baseURL}`);

// Custom error classes
export class NetworkError extends Error {
  constructor(message) {
    super(message);
    this.name = 'NetworkError';
  }
}

export class HTTPError extends Error {
  constructor(message, status) {
    super(message);
    this.name = 'HTTPError';
    this.status = status;
  }
}

export class TimeoutError extends Error {
  constructor(message) {
    super(message);
    this.name = 'TimeoutError';
  }
}

export class ParseError extends Error {
  constructor(message) {
    super(message);
    this.name = 'ParseError';
  }
}

/**
 * Override the base URL for the storage service API.
 * @param {string} url - Full base URL (e.g. "https://api.example.com/v1").
 */
export function setBaseURL(url) {
  baseURL = url;
  console.debug(`Using base URL: ${baseURL}`);
}

/**
 * Save or update a flow definition by ID.
 * @param {string} id - Unique flow identifier.
 * @param {object} flowJson - Flow definition JSON.
 * @returns {Promise<void>}
 */
export async function saveFlow(id, flowJson) {
  const url = `${baseURL}/flows/${encodeURIComponent(id)}`;
  console.debug(`Initiating saveFlow request for id ${id} to ${url} with payload:`, flowJson);

  const controller = new AbortController();
  const timeoutHandle = setTimeout(() => controller.abort(), DEFAULT_TIMEOUT);

  // Prepare headers
  const headers = { 'Content-Type': 'application/json' };
  const token = (typeof process !== 'undefined' && process.env && process.env.AUTH_TOKEN) || null;
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  try {
    const response = await fetch(url, {
      method: 'PUT',
      headers,
      body: JSON.stringify(flowJson),
      signal: controller.signal,
      mode: 'cors',
      credentials: token ? 'same-origin' : 'include'
    });
    clearTimeout(timeoutHandle);

    console.debug(`Received saveFlow response for id ${id}: status ${response.status}`);
    if (!response.ok) {
      throw new HTTPError(`Failed to save flow ${id}: received status ${response.status}`, response.status);
    }
    console.info(`Flow saved successfully for id ${id}`);
  } catch (err) {
    clearTimeout(timeoutHandle);
    if (err.name === 'AbortError') {
      throw new TimeoutError(`Request timed out after ${DEFAULT_TIMEOUT} ms while saving flow ${id}`);
    }
    if (err instanceof HTTPError) {
      throw err;
    }
    // Network or other
    throw new NetworkError(`Network error occurred while saving flow ${id}: ${err.message}`);
  }
}

/**
 * Load a flow definition by ID.
 * @param {string} id - Unique flow identifier.
 * @returns {Promise<object|null>} - Parsed flow JSON or null if none.
 */
export async function loadFlow(id) {
  const url = `${baseURL}/flows/${encodeURIComponent(id)}`;
  console.debug(`Initiating loadFlow request for id ${id} to ${url}`);

  const controller = new AbortController();
  const timeoutHandle = setTimeout(() => controller.abort(), DEFAULT_TIMEOUT);

  // Prepare headers
  const headers = { 'Content-Type': 'application/json' };
  const token = (typeof process !== 'undefined' && process.env && process.env.AUTH_TOKEN) || null;
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  try {
    const response = await fetch(url, {
      method: 'GET',
      headers,
      signal: controller.signal,
      mode: 'cors',
      credentials: token ? 'same-origin' : 'include'
    });
    clearTimeout(timeoutHandle);

    console.debug(`Received loadFlow response for id ${id}: status ${response.status}`);

    if (response.status === 204) {
      console.info(`Flow loaded successfully for id ${id}`);
      return null;
    }
    if (!response.ok) {
      throw new HTTPError(`Failed to load flow ${id}: received status ${response.status}`, response.status);
    }

    const text = await response.text();
    if (!text) {
      console.info(`Flow loaded successfully for id ${id}`);
      return null;
    }

    let data;
    try {
      data = JSON.parse(text);
    } catch (parseErr) {
      throw new ParseError(`Failed to parse flow JSON for id ${id}: ${parseErr.message}`);
    }

    console.debug(`Parsed loadFlow response for id ${id}:`, data);
    console.info(`Flow loaded successfully for id ${id}`);
    return data;
  } catch (err) {
    clearTimeout(timeoutHandle);
    if (err.name === 'AbortError') {
      throw new TimeoutError(`Request timed out after ${DEFAULT_TIMEOUT} ms while loading flow ${id}`);
    }
    if (err instanceof HTTPError || err instanceof ParseError) {
      throw err;
    }
    // Network or other
    throw new NetworkError(`Network error occurred while loading flow ${id}: ${err.message}`);
  }
}