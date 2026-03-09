if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("/sw.js").catch(() => {});
}

document.addEventListener("DOMContentLoaded", () => {
    initScrollReveal();
    initPassGate();
    initMenu();
    initBookGallery();
    initBookViewer();
    initLang();
});

function initScrollReveal() {
    const targets = document.querySelectorAll("[data-animate]");
    if (!targets.length) return;

    if ("IntersectionObserver" in window) {
        const observer = new IntersectionObserver(
            entries => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add("in-view");
                        observer.unobserve(entry.target);
                    }
                });
            },
            { threshold: 0.15 }
        );

        targets.forEach(target => observer.observe(target));
    } else {
        targets.forEach(target => target.classList.add("in-view"));
    }
}

function initPassGate() {
    const toggleBtn = document.querySelector("[data-pass-toggle]");
    const submitBtn = document.querySelector("[data-pass-submit]");
    const panel = document.querySelector(".pass-panel");
    const input = document.querySelector("#gallery-pass");
    const feedback = document.querySelector(".pass-feedback");
    const secret = document.querySelector("[data-secret-gallery]");
    if (!toggleBtn || !submitBtn || !panel || !input || !feedback) return;

    const PASS_CODE = "MASU10";

    toggleBtn.addEventListener("click", () => {
        panel.classList.toggle("visible");
        panel.setAttribute("aria-hidden", panel.classList.contains("visible") ? "false" : "true");
        if (panel.classList.contains("visible")) {
            input.focus();
        } else {
            input.value = "";
            feedback.textContent = "";
        }
    });

    submitBtn.addEventListener("click", () => {
        const value = input.value.trim().toUpperCase();
        if (!value) return;
        if (value === PASS_CODE) {
            feedback.textContent = "Access granted. We will guide you quietly.";
            feedback.style.color = "var(--gold)";
            if (secret) {
                secret.classList.add("open");
            }
        } else {
            feedback.textContent = "Invalid pass. Please check your 10€ pass.";
            feedback.style.color = "#f17373";
        }
        input.value = "";
    });
}

function initBookGallery() {
    const photos = document.querySelectorAll(".book-photo");
    if (!photos.length) return;

    if ("IntersectionObserver" in window) {
        const observer = new IntersectionObserver(
            entries => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add("visible");
                        observer.unobserve(entry.target);
                    }
                });
            },
            { threshold: 0.2 }
        );

        photos.forEach(photo => observer.observe(photo));
    } else {
        photos.forEach(photo => photo.classList.add("visible"));
    }
}

function initBookViewer() {
    document.querySelectorAll(".book-viewer").forEach(section => {
        const pagesRoot = section.querySelector("[data-viewer-pages]");
        const leftImg = section.querySelector(".book-page-left img");
        const rightImg = section.querySelector(".book-page-right img");
        const rightPage = section.querySelector(".book-page-right");
        const prevBtn = section.querySelector(".book-nav.prev");
        const nextBtn = section.querySelector(".book-nav.next");
        if (!pagesRoot || !leftImg || !rightImg || !rightPage || !prevBtn || !nextBtn) return;

        const indicator = section.querySelector("[data-book-current]");
        const thumbsRoot = section.querySelector("[data-viewer-thumbs]");
        let thumbs = [];

        const pages = Array.from(pagesRoot.querySelectorAll("span"))
            .map(span => ({
                src: span.dataset.src,
                alt: span.dataset.alt || ""
            }))
            .filter(page => page.src);

        if (!pages.length) return;

        const initThumbs = () => {
            if (!thumbsRoot) return [];
            let nodes = Array.from(thumbsRoot.querySelectorAll("[data-thumb]"));
            if (!nodes.length) {
                const fragment = document.createDocumentFragment();
                pages.forEach((page, idx) => {
                    const button = document.createElement("button");
                    button.type = "button";
                    button.className = "book-thumb";
                    button.dataset.thumb = "";
                    button.dataset.pageIndex = String(idx);
                    const img = document.createElement("img");
                    img.src = page.src;
                    img.alt = page.alt;
                    img.loading = "lazy";
                    button.appendChild(img);
                    fragment.appendChild(button);
                });
                thumbsRoot.appendChild(fragment);
                nodes = Array.from(thumbsRoot.querySelectorAll("[data-thumb]"));
            } else {
                nodes.forEach((button, idx) => {
                    if (!button.dataset.pageIndex) {
                        button.dataset.pageIndex = String(idx);
                    }
                    const img = button.querySelector("img");
                    if (img && !img.getAttribute("src") && pages[idx]) {
                        img.src = pages[idx].src;
                        img.alt = pages[idx].alt;
                    }
                });
            }
            return nodes;
        };

        thumbs = initThumbs();

        const TURN_UPDATE_DELAY = 260;
        const TURN_RESET_DELAY = 520;
        let index = 0;
        let isAnimating = false;

        const maxIndex = () => {
            if (pages.length <= 1) return 0;
            return pages.length % 2 === 0 ? pages.length - 2 : pages.length - 1;
        };

        const updateIndicator = () => {
            if (!indicator) return;
            const start = index + 1;
            const end = Math.min(index + 2, pages.length);
            indicator.textContent = start === end ? `${start}` : `${start}\u2013${end}`;
        };

        const updateNavState = () => {
            prevBtn.disabled = index <= 0;
            nextBtn.disabled = index >= maxIndex();
        };

        const updateThumbs = () => {
            if (!thumbs.length) return;
            thumbs.forEach(button => {
                const pageIndex = Number(button.dataset.pageIndex);
                const active = pageIndex === index || pageIndex === index + 1;
                button.classList.toggle("is-active", active);
            });
        };

        const render = () => {
            const leftPage = pages[index];
            if (leftPage) {
                leftImg.src = leftPage.src;
                leftImg.alt = leftPage.alt;
            }

            const rightPageData = pages[index + 1];
            if (rightPageData) {
                rightImg.src = rightPageData.src;
                rightImg.alt = rightPageData.alt;
                rightPage.classList.remove("is-empty");
            } else {
                rightImg.removeAttribute("src");
                rightImg.alt = "";
                rightPage.classList.add("is-empty");
            }

            updateIndicator();
            updateNavState();
            updateThumbs();
        };

        const turnForward = () => {
            if (isAnimating || index >= maxIndex()) return;
            isAnimating = true;
            rightPage.classList.remove("turning-back");
            rightPage.classList.add("turning-forward");
            setTimeout(() => {
                index = Math.min(index + 2, pages.length - 1);
                render();
            }, TURN_UPDATE_DELAY);
            setTimeout(() => {
                rightPage.classList.remove("turning-forward");
                isAnimating = false;
            }, TURN_RESET_DELAY);
        };

        const turnBackward = () => {
            if (isAnimating || index <= 0) return;
            isAnimating = true;
            rightPage.classList.remove("turning-forward");
            rightPage.classList.add("turning-back");
            setTimeout(() => {
                index = Math.max(index - 2, 0);
                render();
            }, TURN_UPDATE_DELAY);
            setTimeout(() => {
                rightPage.classList.remove("turning-back");
                isAnimating = false;
            }, TURN_RESET_DELAY);
        };

        prevBtn.addEventListener("click", turnBackward);
        nextBtn.addEventListener("click", turnForward);

        thumbs.forEach(button => {
            button.addEventListener("click", () => {
                if (isAnimating) return;
                const pageIndex = Number(button.dataset.pageIndex);
                if (Number.isNaN(pageIndex)) return;
                const spreadStart = Math.max(0, pageIndex - (pageIndex % 2));
                if (spreadStart === index) return;
                index = spreadStart;
                render();
            });
        });

        render();
    });
}

function initMenu() {
    const toggle = document.querySelector(".menu-toggle");
    const nav = document.querySelector(".site-header nav");
    if (!toggle || !nav) return;

    toggle.addEventListener("click", () => {
        const expanded = toggle.getAttribute("aria-expanded") === "true";
        toggle.setAttribute("aria-expanded", String(!expanded));
        toggle.classList.toggle("active");
        nav.classList.toggle("open");
    });

    nav.querySelectorAll("a").forEach(link => {
        link.addEventListener("click", () => {
            toggle.setAttribute("aria-expanded", "false");
            toggle.classList.remove("active");
            nav.classList.remove("open");
        });
    });
}

function initLang() {
    const translations = {
        en: {
            hero_title: "A wooden vessel traveling the world.",
            hero_lead: "A MASU in hand.<br>A moment you can feel.",
            hero_btn: "VIEW PHOTO BOOKS",
            about_title: "What is MASU PHOTO",
            about_body: "A MASU —<br>a wooden vessel shaped by centuries.<br><br>In a single touch,<br>light, air, and human presence come alive.<br><br>An old form,<br>reborn as contemporary art.",
            books_title: "PHOTO BOOK SERIES",
            books_desc: "A collection of journeys,<br>captured across different lands.<br>All volumes are open to read.",
            partner_headline: "Your story,<br>told through the MASU.",
            partner_text1: "MASU PHOTO documents quiet moments across the world — people, places and light through the presence of a wooden vessel.",
            partner_text2: "As the archive grows, so does the possibility of new expressions with cities, brands, and cultural projects that resonate with its vision.",
            partner_cta: "EXPLORE PARTNERSHIP",
            sponsors_label: "SUPPORTED BY"
        },
        ja: {
            hero_title: "枡が、世界を旅している。",
            hero_lead: "手のひらに、枡がひとつ。<br>それだけで、心が動く瞬間がある。",
            hero_btn: "写真集を見る",
            about_title: "MASU PHOTO とは",
            about_body: "枡 ——<br>何百年もの時を経て受け継がれてきた、日本の器。<br><br>ひとつ手に取るだけで、<br>光や空気、人の気配が静かに立ち上がる。<br><br>古い形が、<br>現代アートとして生まれ変わる。",
            books_title: "写真集シリーズ",
            books_desc: "さまざまな土地を巡りながら<br>記録してきた旅の断片。<br>すべての写真集を、自由にご覧いただけます。",
            partner_headline: "あなたの物語を、<br>枡を通して届ける。",
            partner_text1: "MASU PHOTO は、枡とともに世界各地の静かな瞬間を記録しています。人、場所、光——そこに枡があることで生まれる風景。",
            partner_text2: "アーカイブが広がるほど、都市やブランド、文化プロジェクトとの新しい表現の可能性も広がっていきます。",
            partner_cta: "パートナーシップについて",
            sponsors_label: "サポーター"
        }
    };

    let currentLang = "en";
    const toggleBtn = document.querySelector("[data-lang-toggle]");
    if (!toggleBtn) return;

    const applyLang = (lang) => {
        currentLang = lang;
        document.documentElement.lang = lang;
        document.querySelectorAll("[data-i18n]").forEach(el => {
            const key = el.getAttribute("data-i18n");
            if (translations[lang] && translations[lang][key]) {
                el.innerHTML = translations[lang][key];
            }
        });
        toggleBtn.textContent = lang === "en" ? "EN / JA" : "JA / EN";
    };

    toggleBtn.addEventListener("click", () => {
        applyLang(currentLang === "en" ? "ja" : "en");
    });
}
