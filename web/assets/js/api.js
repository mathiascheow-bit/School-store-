const DEFAULT_API_BASE = '/api';
const STORED_API_BASE = (typeof localStorage !== 'undefined' && localStorage.getItem('API_BASE')) || '';
const GLOBAL_API_BASE = (typeof window !== 'undefined' && window.API_BASE) || '';
const API_BASE = (GLOBAL_API_BASE || STORED_API_BASE || DEFAULT_API_BASE).replace(/\/$/, '');

export function getToken() {
	return localStorage.getItem('token') || '';
}

export function setToken(token) {
	if (token) localStorage.setItem('token', token);
}

export async function apiGet(path) {
	const res = await fetch(`${API_BASE}${path}`, {
		headers: { 'Authorization': `Bearer ${getToken()}` }
	});
	if (!res.ok) throw new Error(`GET ${path} failed`);
	return res.json();
}

export async function apiPost(path, body) {
	const res = await fetch(`${API_BASE}${path}`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${getToken()}` },
		body: JSON.stringify(body)
	});
	if (!res.ok) throw new Error(await res.text());
	return res.json();
}

export async function apiPostForm(path, formData) {
	const res = await fetch(`${API_BASE}${path}`, {
		method: 'POST',
		headers: { 'Authorization': `Bearer ${getToken()}` },
		body: formData
	});
	if (!res.ok) throw new Error(await res.text());
	return res.json();
}