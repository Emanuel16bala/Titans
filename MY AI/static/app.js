document.addEventListener('DOMContentLoaded', () => {
    initCart();
    initFilters();
    initToast();
});

/* --- TOAST SYSTEM --- */
const showToast = (message, type = 'info') => {
    const container = document.getElementById('toast-container');
    if (!container) return;
    const toast = document.createElement('div');
    toast.className = 'glass toast';
    toast.innerHTML = `
        <i class="fas fa-circle-info" style="color: var(--accent-pink);"></i>
        <span>${message}</span>
    `;
    container.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100px)';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
};

/* --- FILTER SYSTEM --- */
const initFilters = () => {
    const tabs = document.querySelectorAll('.tab');
    const products = document.querySelectorAll('.product-card');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            const cat = tab.getAttribute('data-category');
            products.forEach(p => {
                const pCat = p.getAttribute('data-category');
                p.style.display = (cat === 'all' || pCat === cat) ? 'block' : 'none';
            });
        });
    });
};

/* --- CART SYSTEM --- */
let cart = JSON.parse(localStorage.getItem('titan_cart')) || [];

const initCart = () => updateCartBadge();

const addToCart = (prod) => {
    if (cart.find(i => i.id === prod.id)) return showToast("Deja în coș!");
    cart.push(prod);
    saveCart();
    updateCartBadge();
    showToast(`${prod.name} adăugat!`, "success");
};

const removeFromCart = (id) => {
    cart = cart.filter(i => i.id !== id);
    saveCart();
    updateCartBadge();
    if (document.getElementById('cart-items-container')) {
        renderCartContents();
    } else {
        location.reload();
    }
};

const renderCartContents = () => {
    const container = document.getElementById('cart-items-container');
    const totalEl = document.getElementById('cart-total-price');
    if (!container) return;

    if (cart.length === 0) {
        container.innerHTML = `<div class="glass order-item" style="justify-content: center; padding: 40px;"><p>Coșul tău este gol.</p></div>`;
        if (totalEl) totalEl.innerText = '0€';
        return;
    }

    let total = 0;
    container.innerHTML = '';
    cart.forEach(item => {
        const itemTotal = item.price;
        total += itemTotal;
        container.innerHTML += `
            <div class="glass order-item fade-in" style="display: flex; justify-content: space-between; padding: 20px; margin-bottom: 15px; border-radius: 12px; align-items: center;">
                <div style="display: flex; gap: 15px; align-items: center;">
                    <img src="${item.image || 'https://via.placeholder.com/60/111/fff?text=No+Img'}" style="width: 60px; height: 60px; object-fit: cover; border-radius: 8px;">
                    <div>
                        <h3 style="margin: 0 0 5px 0;">${item.name}</h3>
                        <div style="font-size: 11px; color: var(--text-gray); margin-bottom: 5px;">${item.description || 'Resursă digitală'}</div>
                        <p style="margin: 0; font-size: 11px; color: var(--accent-pink); font-weight: 700;">1x ${item.price}€</p>
                    </div>
                </div>
                <div style="display: flex; flex-direction: column; align-items: flex-end; gap: 10px;">
                    <span style="font-weight: 800; font-size: 18px; color: white;">${itemTotal}€</span>
                    <button onclick="app.removeFromCart(${item.id})" style="background: none; border: none; color: #ff2d95; cursor: pointer; font-size: 11px;"><i class="fas fa-trash"></i> Șterge</button>
                </div>
            </div>
        `;
    });

    if (totalEl) totalEl.innerText = `${total}€`;
};

window.renderCartContents = renderCartContents;

const saveCart = () => localStorage.setItem('titan_cart', JSON.stringify(cart));
const updateCartBadge = () => {
    const badge = document.getElementById('cart-count');
    if (badge) badge.innerText = cart.length;
};

const checkout = () => {
    if (cart.length === 0) return showToast("Coșul este gol!", "info");
    const total = cart.reduce((t, i) => t + i.price, 0);
    const modal = document.getElementById('payment-modal');
    if (modal) {
        modal.style.display = 'flex';
        const modalTotal = document.getElementById('modal-total');
        if (modalTotal) modalTotal.innerText = `${total}€`;
        const payAmount = document.getElementById('pay-amount');
        if (payAmount) payAmount.innerText = `${total}€`;
        const pList = document.getElementById('checkout-product-list');
        if (pList) pList.innerText = cart.map(i => i.name).join(", ");
        
        if (total === 0) {
            const ppContainer = document.getElementById('paypal-button-container');
            if (ppContainer) ppContainer.style.display = 'none';
            let fb = document.getElementById('free-checkout-btn');
            if (!fb) {
                fb = document.createElement('button');
                fb.id = 'free-checkout-btn';
                fb.className = 'btn-neon';
                fb.style.width = '100%';
                fb.style.padding = '18px';
                fb.innerText = 'OBȚINE GRATUIT';
                fb.onclick = () => processPayment('Free');
                const ui = document.getElementById('payment-methods-ui');
                if (ui) ui.appendChild(fb);
            }
            fb.style.display = 'block';
        } else {
            const fb = document.getElementById('free-checkout-btn');
            if (fb) fb.style.display = 'none';
            if (window.paypal) {
                const ppContainer = document.getElementById('paypal-button-container');
                if (ppContainer) {
                    ppContainer.style.display = 'block';
                    ppContainer.innerHTML = '';
                    paypal.Buttons({
                        createOrder: (data, actions) => {
                            return actions.order.create({
                                purchase_units: [{ amount: { value: total.toFixed(2), currency_code: 'EUR' } }]
                            });
                        },
                        onApprove: (data, actions) => {
                            return actions.order.capture().then(details => {
                                processPayment('PayPal');
                            });
                        }
                    }).render('#paypal-button-container');
                }
            }
        }
    }
};
window.checkout = checkout;

/* --- CHECKOUT & REVIEWS --- */
const processPayment = (method) => {
    const total = cart.reduce((t, i) => t + i.price, 0);
    if (total < 0) return;

    fetch('/checkout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ items: cart, total: total })
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            const methodsUI = document.getElementById('payment-methods-ui');
            const reviewUI = document.getElementById('review-request-ui');
            const container = document.getElementById('review-items-container');
            
            if (methodsUI) methodsUI.style.display = 'none';
            if (reviewUI) {
                reviewUI.style.display = 'block';
                container.innerHTML = cart.map(item => `
                    <div class="glass" style="padding: 15px; margin-bottom: 10px; border-radius: 10px; text-align: left;">
                        <div style="font-weight: 700; margin-bottom: 10px;">Review pentru ${item.name}</div>
                        <div style="display: flex; gap: 10px;">
                            <select id="rating-${item.id}" style="background: #111; color: #fbbf24; border: 1px solid #fbbf24; border-radius: 8px; padding: 8px; outline: none; font-size: 10px;">
                                <option value="5">⭐⭐⭐⭐⭐ 5</option>
                                <option value="4">⭐⭐⭐⭐ 4</option>
                                <option value="3">⭐⭐⭐ 3</option>
                                <option value="2">⭐⭐ 2</option>
                                <option value="1">⭐ 1</option>
                            </select>
                            <input type="text" id="comment-${item.id}" placeholder="Cum ți se pare?" style="flex: 1; font-size: 11px; padding: 8px; color: white; background: rgba(0,0,0,0.5); border: 1px solid var(--glass-border); border-radius: 8px; outline: none;">
                            <button onclick="submitReview(${item.id}, this)" class="btn-neon" style="font-size: 10px; padding: 5px 15px;">TRIMITE</button>
                        </div>
                    </div>
                `).join('');
            }

            cart = [];
            saveCart();
            updateCartBadge();
            showToast("Tranzacție Reușită!", "success");
        }
    });
};

const submitReview = (pid, btnElement) => {
    const rating = document.getElementById(`rating-${pid}`).value;
    const comment = document.getElementById(`comment-${pid}`).value;
    const fd = new FormData();
    fd.append('product_id', pid);
    fd.append('rating', rating);
    fd.append('comment', comment);

    fetch('/submit_review', { method: 'POST', body: fd })
    .then(() => {
        showToast("Review trimis! Îți mulțumim!", "success");
        if(btnElement) {
            btnElement.innerHTML = "<i class='fas fa-check'></i> OK";
            btnElement.disabled = true;
            btnElement.style.opacity = '0.5';
            btnElement.style.pointerEvents = 'none';
        }
    });
};

const closePayment = () => {
    document.getElementById('payment-modal').style.display = 'none';
    if(cart.length === 0) location.href = '/orders';
};

/* Global app object */
window.app = {
    addToCart,
    removeFromCart,
    processPayment,
    submitReview,
    closePayment
};
const initToast = () => {};
