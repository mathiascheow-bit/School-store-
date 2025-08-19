import { apiGet, apiPost, setToken } from './api.js';

const productsEl = document.getElementById('products');
const signinBtn = document.getElementById('signinBtn');
const cartCountEl = document.getElementById('cartCount');

function getCart() {
	try { return JSON.parse(localStorage.getItem('cart') || '[]'); } catch { return []; }
}
function setCart(items) {
	localStorage.setItem('cart', JSON.stringify(items));
	cartCountEl.textContent = items.reduce((s, it) => s + it.quantity, 0);
}
setCart(getCart());

async function loadProducts() {
	const list = await apiGet('/products');
	productsEl.innerHTML = '';
	for (const p of list) {
		const card = document.createElement('div');
		card.className = 'card';
		const img = document.createElement('img');
		img.src = p.image_url || 'https://picsum.photos/seed/snack' + p.id + '/400/300';
		img.alt = p.name;
		img.style.cursor = 'pointer';
		img.onclick = () => location.href = `/web/product.html?id=${p.id}`;
		const content = document.createElement('div');
		content.className = 'content';
		const title = document.createElement('div');
		title.className = 'title';
		title.textContent = p.name;
		title.style.cursor = 'pointer';
		title.onclick = () => location.href = `/web/product.html?id=${p.id}`;
		const price = document.createElement('div');
		price.className = 'price';
		price.textContent = `$${(p.price_cents / 100).toFixed(2)}`;
		const btn = document.createElement('button');
		btn.className = 'btn primary';
		btn.textContent = 'Add to Cart';
		btn.onclick = () => {
			const cart = getCart();
			const found = cart.find(it => it.product_id === p.id);
			if (found) found.quantity += 1; else cart.push({ product_id: p.id, product_name: p.name, unit_price_cents: p.price_cents, quantity: 1 });
			setCart(cart);
		};
		content.append(title, price, btn);
		card.append(img, content);
		productsEl.append(card);
	}
}

signinBtn.onclick = async () => {
	const email = prompt('Enter your email to sign in:', 'mathias_cheow@students.edu.sg');
	if (!email) return;
	const name = prompt('Enter your name:') || '';
	try {
		const res = await apiPost('/auth/signin', { email, name });
		setToken(res.token);
		alert('Signed in! ' + (res.user.is_admin ? 'Admin' : 'User'));
	} catch (e) {
		alert('Sign-in failed');
	}
};

loadProducts().catch(console.error);
