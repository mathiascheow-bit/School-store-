import { apiGet, apiPost, apiPostForm } from './api.js';

async function loadSummary() {
	const s = await apiGet('/admin/summary');
	document.getElementById('summary').innerHTML = `
		<div class="card" style="padding:12px;display:grid;grid-template-columns:repeat(4,1fr);gap:12px;">
			<div><div class="muted">Users</div><div class="title">${s.total_users}</div></div>
			<div><div class="muted">Products</div><div class="title">${s.total_products}</div></div>
			<div><div class="muted">Orders</div><div class="title">${s.total_orders}</div></div>
			<div><div class="muted">Items</div><div class="title">${s.total_items}</div></div>
		</div>`;
}

async function loadCharts() {
	const stats = await apiGet('/orders/stats');
	const ctxL = document.getElementById('chartLine');
	const ctxB = document.getElementById('chartBar');
	new Chart(ctxL, {
		type: 'line',
		data: { labels: stats.line.map(d => d.date), datasets: [{ label: 'Orders', data: stats.line.map(d => d.count), borderColor: '#7c3aed' }] },
		options: { scales: { y: { beginAtZero: true } } }
	});
	new Chart(ctxB, {
		type: 'bar',
		data: { labels: stats.bar.map(b => b.product), datasets: [{ label: 'Items', data: stats.bar.map(b => b.count), backgroundColor: '#22c55e' }] },
		options: { scales: { y: { beginAtZero: true } } }
	});
}

async function loadOrders() {
	const list = await apiGet('/orders');
	const box = document.getElementById('orders');
	box.innerHTML = '';
	for (const o of list) {
		const div = document.createElement('div');
		div.className = 'card';
		div.style.padding = '12px';
		div.innerHTML = `<div><strong>#${o.order_code}</strong> • ${o.customer_name} • ${o.location}</div>`;
		const ul = document.createElement('ul');
		for (const it of o.items) {
			const li = document.createElement('li');
			li.textContent = `${it.product_name} x${it.quantity}`;
			ul.append(li);
		}
		div.append(ul);
		box.append(div);
	}
}

function wireAddProduct() {
	const form = document.getElementById('addProductForm');
	const res = document.getElementById('addProductResult');
	form.onsubmit = async (e) => {
		e.preventDefault();
		const fd = new FormData(form);
		try {
			await apiPostForm('/products', fd);
			res.textContent = 'Product created!';
			form.reset();
		} catch (e) {
			res.textContent = 'Failed to create product';
		}
	};
}

function wireGrantAdmin() {
	const form = document.getElementById('grantAdminForm');
	const res = document.getElementById('grantResult');
	form.onsubmit = async (e) => {
		e.preventDefault();
		const fd = new FormData(form);
		try {
			await apiPost('/auth/grant-admin', { email: fd.get('email') });
			res.textContent = 'Granted!';
			form.reset();
		} catch (e) {
			res.textContent = 'Failed to grant';
		}
	};
}

(async function init() {
	await loadSummary();
	await loadCharts();
	await loadOrders();
	wireAddProduct();
	wireGrantAdmin();
})();
