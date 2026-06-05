document.addEventListener("DOMContentLoaded", function () {
    const links = Array.from(document.querySelectorAll("[data-category-link]"));
    const sections = Array.from(document.querySelectorAll("[data-category-section]"));
    const productPane = document.querySelector(".mobile-product-pane");
    const categoryPane = document.querySelector(".mobile-category-pane");
    const revealElements = Array.from(document.querySelectorAll("[data-reveal]"));

    if (!links.length || !sections.length || !productPane) return;

    let lockedTargetId = null;
    let unlockFallbackTimer = null;

    function setActiveLink(id) {
        links.forEach(link => {
            const isActive = link.getAttribute("href") === "#" + id;
            link.classList.toggle("active", isActive);

            if (isActive && categoryPane) {
                const linkTop = link.offsetTop;
                const linkHeight = link.offsetHeight;
                const paneHeight = categoryPane.clientHeight;
                const targetScroll = linkTop - (paneHeight / 2) + (linkHeight / 2);

                categoryPane.scrollTo({
                    top: Math.max(0, targetScroll),
                    behavior: "smooth"
                });
            }
        });
    }

    function getScrollTopForSection(target) {
        const paneRect = productPane.getBoundingClientRect();
        const targetRect = target.getBoundingClientRect();
        const relativeTop = targetRect.top - paneRect.top;
        return productPane.scrollTop + relativeTop;
    }

    function getLastSectionPriority() {
        const lastSection = sections[sections.length - 1];
        if (!lastSection) return null;

        const lastTop = getScrollTopForSection(lastSection);
        const currentTop = productPane.scrollTop;
        const triggerLine = currentTop + productPane.clientHeight * 0.45;

        if (lastTop <= triggerLine) {
            return lastSection;
        }

        return null;
    }

    function getCurrentSection() {
        const priorityLast = getLastSectionPriority();
        if (priorityLast) {
            return priorityLast;
        }

        const paneTop = productPane.scrollTop;
        let current = sections[0];

        for (const section of sections) {
            const sectionTop = getScrollTopForSection(section);
            if (sectionTop - 24 <= paneTop) {
                current = section;
            } else {
                break;
            }
        }

        return current;
    }

    function isNearTarget(targetId) {
        const target = document.getElementById(targetId);
        if (!target) return true;

        const targetTop = getScrollTopForSection(target);
        return Math.abs(productPane.scrollTop - targetTop) < 12;
    }

    function lockToTarget(targetId) {
        lockedTargetId = targetId;
        clearTimeout(unlockFallbackTimer);

        unlockFallbackTimer = setTimeout(() => {
            lockedTargetId = null;
            const currentSection = getCurrentSection();
            if (currentSection) {
                setActiveLink(currentSection.id);
            }
        }, 900);
    }

    function unlockTargetIfReached() {
        if (!lockedTargetId) return false;

        if (isNearTarget(lockedTargetId)) {
            const doneId = lockedTargetId;
            lockedTargetId = null;
            clearTimeout(unlockFallbackTimer);
            setActiveLink(doneId);
            return true;
        }

        return false;
    }

    function revealInsideProductPane() {
        revealElements.forEach(element => {
            if (element.classList.contains("revealed")) return;

            const rect = element.getBoundingClientRect();
            if (rect.top < window.innerHeight / 1.15) {
                element.classList.add("revealed");
            }
        });
    }

    links.forEach(link => {
        link.addEventListener("click", function (e) {
            e.preventDefault();

            const targetId = this.getAttribute("href").replace("#", "");
            const target = document.getElementById(targetId);
            if (!target) return;

            lockToTarget(targetId);
            setActiveLink(targetId);

            const targetTop = getScrollTopForSection(target);

            productPane.scrollTo({
                top: targetTop,
                behavior: "smooth"
            });

            setTimeout(revealInsideProductPane, 120);
        });
    });

    productPane.addEventListener("scroll", function () {
        if (lockedTargetId) {
            setActiveLink(lockedTargetId);
            unlockTargetIfReached();
            revealInsideProductPane();
            return;
        }

        const currentSection = getCurrentSection();
        if (currentSection) {
            setActiveLink(currentSection.id);
        }

        revealInsideProductPane();
    }, { passive: true });

    window.addEventListener("load", function () {
        const currentSection = getCurrentSection();
        if (currentSection) {
            setActiveLink(currentSection.id);
        }

        revealInsideProductPane();
    });

    const initialSection = getCurrentSection();
    if (initialSection) {
        setActiveLink(initialSection.id);
    }

    revealInsideProductPane();



    /**
     * CART UI
     */

    const cartActions = document.querySelectorAll("[data-cart-action]");

    function renderSelectButton(container) {
        container.innerHTML = `
    <button class="mobile-product-btn mobile-cart-animated" type="button">选择</button>
  `;
    }

    function renderQtyControl(container, count) {
        container.innerHTML = `
    <div class="mobile-qty-control mobile-cart-animated">
      <button class="mobile-qty-btn" type="button" data-action="decrease">-</button>
      <span class="mobile-qty-value">${count}</span>
      <button class="mobile-qty-btn" type="button" data-action="increase">+</button>
    </div>
  `;
    }

    cartActions.forEach(container => {
        container.addEventListener("click", function (e) {
            const target = e.target.closest("button");
            if (!target) return;

            const qtyValue = container.querySelector(".mobile-qty-value");

            if (target.classList.contains("mobile-product-btn")) {
                renderQtyControl(container, 1);
                return;
            }

            if (!qtyValue) return;

            let count = parseInt(qtyValue.textContent, 10) || 0;
            const action = target.dataset.action;

            if (action === "increase") {
                count += 1;
                renderQtyControl(container, count);
                return;
            }

            if (action === "decrease") {
                count -= 1;

                if (count < 1) {
                    renderSelectButton(container);
                } else {
                    renderQtyControl(container, count);
                }
            }
        });
    });
});