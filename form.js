// 依頼フォーム（Web3Forms）。ページ遷移させずに送り、結果をフォームの下に出す
(function () {
    document.addEventListener("DOMContentLoaded", () => {
        document.querySelectorAll(".inquiry-form").forEach(form => {
            const status = form.querySelector(".form-status");
            const button = form.querySelector('button[type="submit"]');
            form.addEventListener("submit", async e => {
                e.preventDefault();
                button.disabled = true;
                status.hidden = true;
                try {
                    const res = await fetch(form.action, {
                        method: "POST",
                        body: new FormData(form),
                        headers: { Accept: "application/json" }
                    });
                    const data = await res.json();
                    if (!res.ok || !data.success) throw new Error(data.message || "failed");
                    form.reset();
                    status.classList.remove("is-error");
                    status.textContent = form.dataset.ok;
                } catch (err) {
                    status.classList.add("is-error");
                    status.textContent = form.dataset.ng;
                } finally {
                    status.hidden = false;
                    button.disabled = false;
                }
            });
        });
    });
})();

// 依頼ページの本棚：開いた時点で右端（「次の1冊」の空き枠）が見えるようにする
document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".series-shelf").forEach(shelf => {
        shelf.scrollLeft = shelf.scrollWidth;
    });
});

// 依頼ページの作例：1枚の枠で写真を切り替える。触れている間は止め、動きを減らす設定では自動で進めない
document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-slideshow]").forEach(show => {
        const slides = Array.from(show.querySelectorAll(".slide"));
        const dots = Array.from(show.querySelectorAll(".slide-dots button"));
        if (slides.length < 2) return;
        let index = 0;
        let timer = null;
        const go = i => {
            slides[index].classList.remove("is-active");
            dots[index].removeAttribute("aria-current");
            index = (i + slides.length) % slides.length;
            slides[index].classList.add("is-active");
            dots[index].setAttribute("aria-current", "true");
        };
        const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
        const start = () => { if (!reduce && !timer) timer = setInterval(() => go(index + 1), 4000); };
        const stop = () => { clearInterval(timer); timer = null; };
        dots.forEach((d, i) => d.addEventListener("click", () => { go(i); stop(); start(); }));
        show.addEventListener("mouseenter", stop);
        show.addEventListener("mouseleave", start);
        start();
    });
});
