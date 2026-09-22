/* ══════════════════════════════════════════════════════════
   MAISON LUXÉ — app.js
   Handles: catalog load, category filters, chat, modal
   ══════════════════════════════════════════════════════════ */

const API_BASE = "http://localhost:8000";

// ── DOM refs ─────────────────────────────────────────────────
const productGrid    = document.getElementById("product-grid");
const productCount   = document.getElementById("product-count");
const chatPanel      = document.getElementById("chat-panel");
const chatMessages   = document.getElementById("chat-messages");
const chatProducts   = document.getElementById("chat-products");
const chatForm       = document.getElementById("chat-form");
const chatInput      = document.getElementById("chat-input");
const sendBtn        = document.getElementById("send-btn");
const toggleChatBtn  = document.getElementById("toggle-chat-btn");
const heroCta        = document.getElementById("hero-cta-btn");
const closeChatBtn   = document.getElementById("close-chat-btn");
const modalOverlay   = document.getElementById("modal-overlay");
const modalClose     = document.getElementById("modal-close");
const toast          = document.getElementById("toast");

// Quick prompts
const quickPills = document.querySelectorAll(".quick-pill");
const quickPrompts = [
  "Show me dresses under $200",
  "What's in the Spring 2025 catalog?",
  "Which products have the highest discount?",
  "Show me all jewelry items",
];

// Nav pills
const navPills = document.querySelectorAll(".nav-pill");

// ── State ─────────────────────────────────────────────────────
let allProducts  = [];
let wishlist     = new Set();
let currentFilter = "";

// ── Helpers ───────────────────────────────────────────────────

/**
 * Compute effective (discounted) price display string.
 */
function formatPrice(price, discount) {
  if (!discount) return `$${Number(price).toFixed(2)}`;
  const discounted = (price * (1 - discount / 100)).toFixed(2);
  return `$${discounted}`;
}

/**
 * Map a color name to a rough CSS color for the dot indicator.
 */
function colorNameToCss(name) {
  if (!name) return "#888";
  const map = {
    "champagne": "#c8a96e", "ivory": "#fffff0", "noir black": "#111",
    "black": "#111", "camel": "#c19a6b", "oat white": "#f5f0e8",
    "indigo blue": "#3949ab", "dusty rose": "#dcae9a", "sage green": "#87a878",
    "tan brown": "#a0785a", "pearl white": "#f5f0e8", "nude beige": "#e0c8b0",
    "jet black": "#111", "pearl": "#f5f0e8", "gold": "#c8a96e",
    "blush pink": "#f4c2c2", "sky blue": "#87ceeb",
  };
  return map[name.toLowerCase()] || "#888";
}

/**
 * Format a timestamp to "hh:mm am/pm".
 */
function timeNow() {
  return new Date().toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" });
}

// ── Catalog Functions ─────────────────────────────────────────

function buildProductCard(p) {
  const discountedPrice = p.discount_pct
    ? `$${(p.price * (1 - p.discount_pct / 100)).toFixed(2)}`
    : `$${Number(p.price).toFixed(2)}`;
  const originalPrice = p.discount_pct
    ? `<span class="card-original-price">$${Number(p.price).toFixed(2)}</span>`
    : "";
  const discountBadge = p.discount_pct
    ? `<div class="card-discount-badge">−${p.discount_pct}%</div>`
    : "";
  const colorDot = colorNameToCss(p.color);

  const card = document.createElement("article");
  card.className = "product-card";
  card.setAttribute("role", "listitem");
  card.setAttribute("tabindex", "0");
  card.setAttribute("aria-label", `${p.name} by ${p.brand}, ${discountedPrice}`);
  card.dataset.id = p.id;

  card.innerHTML = `
    <div class="card-img-wrap">
      <img
        class="card-img"
        src="${p.image_url || 'https://picsum.photos/seed/${p.id}fashion/600/800'}"
        alt="${p.name}"
        loading="lazy"
        onerror="this.onerror=null;this.src='https://picsum.photos/seed/${p.id}${p.id}/600/800';"
      />
      ${discountBadge}
    </div>
    <div class="card-body">
      <p class="card-brand">${p.brand}</p>
      <h3 class="card-name" title="${p.name}">${p.name}</h3>
      <p class="card-category">${p.category}${p.subcategory ? " · " + p.subcategory : ""}</p>
      <div class="card-footer">
        <div>
          <span class="card-price">${discountedPrice}</span>${originalPrice}
        </div>
        <div class="card-color-dot" style="--dot-color:${colorDot}" title="${p.color || 'Color'}"></div>
      </div>
    </div>
  `;

  card.addEventListener("click",  () => openModal(p));
  card.addEventListener("keydown", e => { if (e.key === "Enter" || e.key === " ") openModal(p); });
  return card;
}

function renderProducts(products) {
  productGrid.innerHTML = "";
  if (!products.length) {
    productGrid.innerHTML = `
      <div class="empty-state">
        <h3>No products found</h3>
        <p>Try a different category or ask STELLA for help.</p>
      </div>`;
    productCount.textContent = "0 items";
    return;
  }
  products.forEach((p, i) => {
    const card = buildProductCard(p);
    card.style.animationDelay = `${i * 0.04}s`;
    productGrid.appendChild(card);
  });
  productCount.textContent = `${products.length} item${products.length !== 1 ? "s" : ""}`;
}

async function loadProducts(category = "") {
  // Show skeletons
  productGrid.innerHTML = Array(6).fill('<div class="skeleton-card" aria-hidden="true"></div>').join("");
  productCount.textContent = "Loading…";

  try {
    const url = category
      ? `${API_BASE}/products?category=${encodeURIComponent(category)}`
      : `${API_BASE}/products`;
    const res  = await fetch(url);
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Failed to load products");
    allProducts = data.products || [];
    renderProducts(allProducts);
  } catch (err) {
    productGrid.innerHTML = `
      <div class="empty-state">
        <h3>Couldn't load catalog</h3>
        <p>${err.message}</p>
      </div>`;
    productCount.textContent = "Error";
    showToast("⚠ Backend unreachable. Make sure the server is running.");
  }
}

// ── Category Filter ──────────────────────────────────────────

navPills.forEach(pill => {
  pill.addEventListener("click", () => {
    navPills.forEach(p => p.classList.remove("active"));
    pill.classList.add("active");
    const cat = pill.dataset.category || "";
    currentFilter = cat;
    loadProducts(cat);
  });
});

// ── Modal ─────────────────────────────────────────────────────

function openModal(p) {
  const discountedPrice = p.discount_pct
    ? `$${(p.price * (1 - p.discount_pct / 100)).toFixed(2)}`
    : `$${Number(p.price).toFixed(2)}`;

  document.getElementById("modal-img").src = p.image_url || "";
  document.getElementById("modal-img").alt = p.name;
  document.getElementById("modal-brand").textContent    = p.brand;
  document.getElementById("modal-product-name").textContent = p.name;
  document.getElementById("modal-price").textContent    = discountedPrice;

  const discEl = document.getElementById("modal-discount");
  if (p.discount_pct) {
    discEl.textContent = `−${p.discount_pct}% OFF`;
    discEl.style.display = "";
  } else {
    discEl.style.display = "none";
  }

  const metaCat   = document.getElementById("modal-category");
  const metaColor = document.getElementById("modal-color");
  const metaSizes = document.getElementById("modal-sizes");
  metaCat.textContent   = `${p.category}${p.subcategory ? " · " + p.subcategory : ""}`;
  metaColor.textContent = p.color || "";
  metaColor.style.display = p.color ? "" : "none";
  metaSizes.textContent = p.size_range ? `Sizes: ${p.size_range}` : "";
  metaSizes.style.display = p.size_range ? "" : "none";

  document.getElementById("modal-desc").textContent = p.description || "";

  const cta = document.getElementById("modal-cta");
  const inWishlist = wishlist.has(p.id);
  cta.textContent = inWishlist ? "Added to Wishlist ♥" : "Add to Wishlist ♡";
  cta.className = `modal-cta${inWishlist ? " wishlisted" : ""}`;
  cta.onclick = () => toggleWishlist(p, cta);

  modalOverlay.hidden = false;
  document.body.style.overflow = "hidden";
}

function closeModal() {
  modalOverlay.hidden = true;
  document.body.style.overflow = "";
}

modalClose.addEventListener("click", closeModal);
modalOverlay.addEventListener("click", e => { if (e.target === modalOverlay) closeModal(); });
document.addEventListener("keydown", e => { if (e.key === "Escape") closeModal(); });

function toggleWishlist(p, btn) {
  if (wishlist.has(p.id)) {
    wishlist.delete(p.id);
    btn.textContent = "Add to Wishlist ♡";
    btn.classList.remove("wishlisted");
    showToast(`Removed "${p.name}" from wishlist`);
  } else {
    wishlist.add(p.id);
    btn.textContent = "Added to Wishlist ♥";
    btn.classList.add("wishlisted");
    showToast(`Added "${p.name}" to wishlist ✦`);
  }
}

// ── Chat Panel ────────────────────────────────────────────────

function openChat() {
  chatPanel.classList.add("open");
  chatInput.focus();
}
function closeChat() {
  chatPanel.classList.remove("open");
}

toggleChatBtn.addEventListener("click", openChat);
heroCta.addEventListener("click", openChat);
closeChatBtn.addEventListener("click", closeChat);

quickPills.forEach((pill, i) => {
  pill.addEventListener("click", () => {
    chatInput.value = quickPrompts[i] || pill.textContent;
    openChat();
    sendMessage();
  });
});

function scrollChatsBottom() {
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function appendUserMessage(text) {
  const div = document.createElement("div");
  div.className = "message message-user";
  div.innerHTML = `
    <div class="message-bubble">${escapeHtml(text)}</div>
    <span class="message-time">${timeNow()}</span>
  `;
  chatMessages.appendChild(div);
  scrollChatsBottom();
}

function appendAIMessage(html) {
  const div = document.createElement("div");
  div.className = "message message-ai";
  div.innerHTML = `
    <div class="message-bubble">${html}</div>
    <span class="message-time">${timeNow()}</span>
  `;
  chatMessages.appendChild(div);
  scrollChatsBottom();
  return div;
}

function showTypingIndicator() {
  const div = document.createElement("div");
  div.className = "message message-ai typing-indicator";
  div.id = "typing-indicator";
  div.setAttribute("aria-label", "STELLA is typing");
  div.innerHTML = `
    <div class="message-bubble">
      <div class="typing-dot"></div>
      <div class="typing-dot"></div>
      <div class="typing-dot"></div>
    </div>
  `;
  chatMessages.appendChild(div);
  scrollChatsBottom();
}

function removeTypingIndicator() {
  const el = document.getElementById("typing-indicator");
  if (el) el.remove();
}

function renderChatProducts(products) {
  chatProducts.innerHTML = "";
  if (!products || !products.length) return;

  const label = document.createElement("p");
  label.style.cssText = "font-size:.72rem;color:var(--clr-text-muted);padding:0 0 0.5rem;text-transform:uppercase;letter-spacing:.08em;";
  label.textContent = `${products.length} matching item${products.length !== 1 ? "s" : ""}`;
  chatProducts.appendChild(label);

  const strip = document.createElement("div");
  strip.className = "chat-products-inner";

  products.forEach(p => {
    const price = p.discount_pct
      ? `$${(p.price * (1 - p.discount_pct / 100)).toFixed(2)}`
      : `$${Number(p.price).toFixed(2)}`;
    const card = document.createElement("div");
    card.className = "chat-product-card";
    card.setAttribute("tabindex", "0");
    card.setAttribute("aria-label", `${p.name}, ${price}`);
    card.innerHTML = `
      <img src="${p.image_url || ''}" alt="${p.name}" loading="lazy" />
      <div class="chat-product-info">
        <div class="chat-product-name" title="${p.name}">${p.name}</div>
        <div class="chat-product-price">${price}</div>
      </div>
    `;
    card.addEventListener("click",  () => { openModal(p); });
    card.addEventListener("keydown", e => { if (e.key === "Enter" || e.key === " ") openModal(p); });
    strip.appendChild(card);
  });

  chatProducts.appendChild(strip);
}

async function sendMessage() {
  const text = chatInput.value.trim();
  if (!text) return;

  chatInput.value = "";
  sendBtn.disabled = true;
  openChat();

  appendUserMessage(text);
  chatProducts.innerHTML = "";
  showTypingIndicator();

  try {
    const res = await fetch(`${API_BASE}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }),
    });
    const data = await res.json();
    removeTypingIndicator();

    if (!res.ok) {
      appendAIMessage(`<p style="color:var(--clr-error)">Sorry, something went wrong: ${escapeHtml(data.detail || "Unknown error")}</p>`);
      return;
    }

    const msg = data.message || "";
    appendAIMessage(`<p>${escapeHtml(msg)}</p>`);

    if (data.type === "products" && data.products?.length) {
      renderChatProducts(data.products);
    }
  } catch (err) {
    removeTypingIndicator();
    appendAIMessage(`<p style="color:var(--clr-error)">⚠ Couldn't reach STELLA. Is the backend running?</p>`);
  } finally {
    sendBtn.disabled = false;
    chatInput.focus();
  }
}

chatForm.addEventListener("submit", e => {
  e.preventDefault();
  sendMessage();
});

// ── Toast ─────────────────────────────────────────────────────

let toastTimer;
function showToast(msg) {
  clearTimeout(toastTimer);
  toast.textContent = msg;
  toast.classList.add("show");
  toastTimer = setTimeout(() => toast.classList.remove("show"), 3200);
}

// ── Utility ───────────────────────────────────────────────────

function escapeHtml(str) {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

// ── Init ──────────────────────────────────────────────────────

loadProducts();
