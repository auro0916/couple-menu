const content = document.getElementById("content");
const categories = document.querySelectorAll(".category");
const sections = document.querySelectorAll(".section");

let cart = {};
const CART_STORAGE_KEY = "couple_menu_cart";

function saveCartToStorage() {
    localStorage.setItem(CART_STORAGE_KEY, JSON.stringify(cart));
}

function loadCartFromStorage() {
    const savedCart = localStorage.getItem(CART_STORAGE_KEY);

    if (!savedCart) {
        return;
    }

    try {
        cart = JSON.parse(savedCart);

        if (!cart || typeof cart !== "object") {
            cart = {};
        }
    } catch (error) {
        console.error("读取购物车失败：", error);
        cart = {};
    }
}

function clearCartStorage() {
    localStorage.removeItem(CART_STORAGE_KEY);
}

function setActiveCategory(categoryId) {
    categories.forEach(category => {
        if (category.dataset.target === categoryId) {
            category.classList.add("active");
        } else {
            category.classList.remove("active");
        }
    });
}

function scrollToSection(categoryId) {
    const target = document.getElementById(categoryId);
    target.scrollIntoView({ behavior: "smooth", block: "start" });
    setActiveCategory(categoryId);
}

function updateActiveCategoryOnScroll() {
    let currentSectionId = "";

    sections.forEach(section => {
        const rect = section.getBoundingClientRect();
        const contentRect = content.getBoundingClientRect();

        if (rect.top <= contentRect.top + 80) {
            currentSectionId = section.id;
        }
    });

    if (currentSectionId) {
        setActiveCategory(currentSectionId);
    }
}

function parsePrice(priceText) {
    return parseFloat(priceText.replace("元", ""));
}

function addToCart(name, price) {
    if (cart[name]) {
        cart[name].quantity += 1;
    } else {
        cart[name] = {
            price: price,
            quantity: 1
        };
    }

    saveCartToStorage();
    renderCart();
}

function increaseItem(name) {
    if (cart[name]) {
        cart[name].quantity += 1;
        saveCartToStorage();
        renderCart();
    }
}

function decreaseItem(name) {
    if (cart[name]) {
        cart[name].quantity -= 1;

        if (cart[name].quantity <= 0) {
            delete cart[name];
        }

        saveCartToStorage();
        renderCart();
    }
}

function removeItem(name) {
    if (cart[name]) {
        delete cart[name];
        saveCartToStorage();
        renderCart();
    }
}

function clearCart() {
    cart = {};
    clearCartStorage();
    renderCart();
}

function getCartCount() {
    let count = 0;
    Object.keys(cart).forEach(name => {
        count += cart[name].quantity;
    });
    return count;
}

function renderCart() {
    const cartItems = document.getElementById("cart-items");
    const cartTotal = document.getElementById("cart-total");
    const cartBadge = document.getElementById("cart-badge");
    const cartCountText = document.getElementById("cart-count-text");

    const names = Object.keys(cart);

    if (names.length === 0) {
        cartItems.innerHTML = '<div class="empty-cart">还没有选择商品</div>';
        cartTotal.innerHTML = '合计：0元';
        cartCountText.innerHTML = '共 0 件';
        cartBadge.style.display = 'none';
        return;
    }

    let html = '';
    let total = 0;

    names.forEach(name => {
        const item = cart[name];
        const singlePrice = parsePrice(item.price);
        const itemTotal = singlePrice * item.quantity;
        total += itemTotal;

        html += `
                <div class="cart-item">
                    <div class="cart-item-top">
                        <div>
                            <div class="cart-item-name">${name}</div>
                            <div class="cart-item-price">${item.price}</div>
                        </div>
                        <div>${itemTotal}元</div>
                    </div>
                    <div class="cart-item-controls">
                        <div class="qty-controls">
                            <button class="qty-btn minus" onclick="decreaseItem('${name}')">-</button>
                            <span>${item.quantity}</span>
                            <button class="qty-btn" onclick="increaseItem('${name}')">+</button>
                        </div>
                        <button class="delete-btn" onclick="removeItem('${name}')">删除</button>
                    </div>
                </div>
            `;
    });

    cartItems.innerHTML = html;
    cartTotal.innerHTML = `合计：${total}元`;

    const count = getCartCount();
    cartCountText.innerHTML = `共 ${count} 件`;

    if (count > 0) {
        cartBadge.style.display = 'flex';
        cartBadge.innerHTML = count;
    } else {
        cartBadge.style.display = 'none';
    }
}

function openCart() {
    document.getElementById("cart-panel").classList.add("show");
}

function closeCart() {
    document.getElementById("cart-panel").classList.remove("show");
}

function toggleCart() {
    document.getElementById("cart-panel").classList.toggle("show");
}

async function checkout() {
    const names = Object.keys(cart);

    if (names.length === 0) {
        alert("请先选择商品");
        return;
    }

    const checkoutBtn = document.getElementById("checkout-btn");
    const loadingText = document.getElementById("loading-text");

    checkoutBtn.disabled = true;
    checkoutBtn.innerText = "准备支付...";
    loadingText.style.display = "block";
    loadingText.innerText = "正在拉起安全支付中心...";

    try {
        await new Promise((resolve) => {
            setTimeout(() => {
                console.log("[Mock API] 第三方支付扣款成功");
                resolve();
            }, 1500);
        });

        checkoutBtn.innerText = "生成订单...";
        loadingText.innerText = "支付成功，正在创建订单...";

        const response = await fetch("/checkout", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                cart: cart
            })
        });

        const result = await response.json();

        if (!response.ok || !result.success) {
            alert(result.message || "下单失败");
            return;
        }

        showOrderModal(result.order);
        clearCart();
        document.getElementById("cart-panel").classList.remove("show");

    } catch (error) {
        alert("网络异常，请稍后再试");
        console.error(error);
    } finally {
        checkoutBtn.disabled = false;
        checkoutBtn.innerText = "结算";
        loadingText.style.display = "none";
    }
}

function showOrderModal(order) {
    const orderInfo = document.getElementById("order-info");

    let itemsHtml = "";
    order.items.forEach(item => {
        itemsHtml += `
                <div class="order-item">
                    <span>${item.name} x ${item.quantity}</span>
                    <span>${item.item_total}</span>
                </div>
            `;
    });

    orderInfo.innerHTML = `
            <p><strong>订单号：</strong>${order.order_id}</p>
            <p><strong>状态：</strong>${order.status}</p>
            <div class="order-items">
                <p><strong>商品明细：</strong></p>
                ${itemsHtml}
            </div>
            <p><strong>合计：</strong>${order.total}</p>
        `;

    document.getElementById("order-modal").classList.add("show");
}

function closeOrderModal() {
    document.getElementById("order-modal").classList.remove("show");
}

content.addEventListener("scroll", updateActiveCategoryOnScroll);

loadCartFromStorage();
renderCart();

// 已修正：完美适配满宽底部栏的外部点击关闭逻辑
document.addEventListener("click", function (event) {
    const cartPanel = document.getElementById("cart-panel");
    const cartButton = document.querySelector('[onclick="toggleCart()"]');

    // 确保页面上存在这两个元素，并且购物车当前是打开状态
    if (cartPanel && cartButton && cartPanel.classList.contains("show")) {
        const clickedInsidePanel = cartPanel.contains(event.target);
        const clickedCartButton = cartButton.contains(event.target);

        // 如果点击的地方既不在购物车面板内部，也不是底部的购物车按钮，就关闭它
        if (!clickedInsidePanel && !clickedCartButton) {
            cartPanel.classList.remove("show");
        }
    }
});
