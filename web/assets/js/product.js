import { apiGet, apiPost } from './api.js';

function qs(name) { return new URLSearchParams(location.search).get(name); }

const productId = parseInt(qs('id') || '0', 10);
const box = document.getElementById('productBox');
const cartCountEl = document.getElementById('cartCount');

function getCart() { try { return JSON.parse(localStorage.getItem('cart')||'[]'); } catch { return []; } }
function setCart(items) { localStorage.setItem('cart', JSON.stringify(items)); cartCountEl.textContent = items.reduce((s, it) => s+it.quantity, 0); }
function getBuyer() { try { return JSON.parse(localStorage.getItem('buyer')||'{}'); } catch { return {}; } }
function setBuyer(b) { localStorage.setItem('buyer', JSON.stringify(b)); }

setCart(getCart());

async function loadProduct() {
	const p = await apiGet(`/products/${productId}`);
	const div = document.createElement('div');
	div.style.display = 'grid';
	div.style.gridTemplateColumns = '1fr 1fr';
	div.style.gap = '16px';
	div.innerHTML = `
		<img src="${p.image_url || 'https://picsum.photos/seed/snack'+p.id+'/800/600'}" alt="${p.name}" style="width:100%;height:100%;object-fit:cover;">
		<div class="content">
			<div class="title" style="font-size:22px;">${p.name}</div>
			<div class="price">$${(p.price_cents/100).toFixed(2)}</div>
			<p>${p.description || ''}</p>
			<label>Quantity <input type="number" id="qty" min="1" value="1"></label>
			<label>Name <input type="text" id="buyerName"></label>
			<label>Location <input type="text" id="buyerLoc"></label>
			<div style="display:flex; gap:8px;">
				<button class="btn primary" id="addBtn">Add to Cart</button>
				<button class="btn" id="likeBtn">❤ Like</button>
			</div>
		</div>`;
	box.append(div);

	const buyer = getBuyer();
	document.getElementById('buyerName').value = buyer.customer_name || '';
	document.getElementById('buyerLoc').value = buyer.location || '';

	document.getElementById('addBtn').onclick = () => {
		const quantity = Math.max(1, parseInt(document.getElementById('qty').value || '1', 10));
		const cart = getCart();
		const found = cart.find(it => it.product_id === p.id);
		if (found) found.quantity += quantity; else cart.push({ product_id: p.id, product_name: p.name, unit_price_cents: p.price_cents, quantity });
		setCart(cart);
		setBuyer({ customer_name: document.getElementById('buyerName').value, location: document.getElementById('buyerLoc').value });
		alert('Added to cart!');
	};

	document.getElementById('likeBtn').onclick = async () => {
		try { await apiPost('/preferences/like', { product_id: p.id, liked: true }); alert('Saved to your likes'); } catch (e) { alert('Please sign in first'); }
	};
}

if (productId) loadProduct();
