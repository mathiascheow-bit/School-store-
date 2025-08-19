import { apiPost } from './api.js';

const cartItemsEl = document.getElementById('cartItems');
const checkoutForm = document.getElementById('checkoutForm');
const resultEl = document.getElementById('orderResult');

function getCart() {
	try { return JSON.parse(localStorage.getItem('cart') || '[]'); } catch { return []; }
}
function setCart(items) {
	localStorage.setItem('cart', JSON.stringify(items));
	renderCart();
}

function renderCart() {
	const items = getCart();
	cartItemsEl.innerHTML = '';
	for (const it of items) {
		const row = document.createElement('div');
		row.className = 'cart-item';
		row.innerHTML = `<div>${it.product_name}</div><div>Qty: ${it.quantity}</div><div>$${((it.unit_price_cents * it.quantity)/100).toFixed(2)}</div>`;
		cartItemsEl.append(row);
	}
	if (!items.length) {
		cartItemsEl.textContent = 'Your cart is empty.';
	}
}

checkoutForm.onsubmit = async (e) => {
	e.preventDefault();
	const form = new FormData(checkoutForm);
	const payload = {
		customer_name: form.get('customer_name'),
		location: form.get('location'),
		items: getCart().map(it => ({ product_id: it.product_id, quantity: it.quantity }))
	};
	try {
		const res = await apiPost('/orders', payload);
		resultEl.textContent = `Order placed! Your order number is ${res.order_code}`;
		setCart([]);
	} catch (e) {
		resultEl.textContent = 'Failed to place order.';
	}
};

renderCart();
