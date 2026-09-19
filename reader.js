// 写真集ビューア。ページ一覧は .reader-scroll の <img> から読む（HTML がそのまま唯一の情報源）。
// PC は StPageFlip（vendor/page-flip.browser.js）で紙が曲がる捲りを描く。スマホは縦並びのまま。
(function () {
    // 見開きに読み込む範囲（現在の見開きの前後）。全ページを一度に読むと重い冊（71ページ）があるため
    const PRELOAD_AHEAD = 4;
    const PRELOAD_BEHIND = 2;

    document.addEventListener("DOMContentLoaded", () => {
        document.querySelectorAll("[data-reader]").forEach(root => {
            initReader(root);
            initMobile(root);
        });
    });

    function initReader(root) {
        const pages = Array.from(root.querySelectorAll(".reader-scroll img")).map(img => ({
            src: img.getAttribute("src"),
            srcset: img.getAttribute("srcset"),
            thumb: img.dataset.thumb,
            alt: img.alt,
            w: Number(img.getAttribute("width")),
            h: Number(img.getAttribute("height"))
        }));
        const wrap = root.querySelector(".reader-spread-wrap");
        const bookEl = root.querySelector(".reader-book");
        if (!pages.length || !wrap || !bookEl) return;

        // ライブラリが読めなかった時は縦並びで読んでもらう
        if (!window.St || !window.St.PageFlip) {
            root.classList.add("is-fallback");
            return;
        }

        const spread = wrap.querySelector(".reader-spread");
        const prev = wrap.querySelector(".reader-nav.prev");
        const next = wrap.querySelector(".reader-nav.next");
        const indicator = wrap.querySelector(".reader-indicator");
        const thumbsRoot = wrap.querySelector(".reader-thumbs");
        const edgeL = wrap.querySelector(".reader-edge-left");
        const edgeR = wrap.querySelector(".reader-edge-right");

        // 1ページ＝1枚の紙。偶数番目が見開きの左、奇数番目が右（元サイトの見開きの組み方と同じ）
        const leaves = pages.map((p, i) => {
            const leaf = document.createElement("div");
            leaf.className = "reader-leaf " + (i % 2 === 0 ? "is-left" : "is-right");
            const img = document.createElement("img");
            img.alt = p.alt;
            // 捲った瞬間に白い紙が見えないよう、表示と同時に描く（先読みで decode 済み）
            img.decoding = "sync";
            img.draggable = false;
            leaf.appendChild(img);
            bookEl.appendChild(leaf);
            return leaf;
        });

        const pageWidth = () => Math.round(bookEl.getBoundingClientRect().width / 2) || 600;

        const load = i => {
            const p = pages[i];
            const img = leaves[i] && leaves[i].firstChild;
            if (!p || !img || img.dataset.loaded) return;
            img.sizes = pageWidth() + "px";
            if (p.srcset) img.srcset = p.srcset;
            img.src = p.src;
            img.dataset.loaded = "1";
            if (img.decode) img.decode().catch(() => {});
        };

        const loadAround = i => {
            for (let k = i - PRELOAD_BEHIND; k <= i + 1 + PRELOAD_AHEAD; k++) load(k);
        };

        loadAround(0);

        const flip = new St.PageFlip(bookEl, {
            width: pages[0].w,
            height: pages[0].h,
            size: "stretch",
            minWidth: 200,
            maxWidth: pages[0].w,
            minHeight: 200,
            maxHeight: pages[0].h,
            showCover: false,
            usePortrait: false,
            drawShadow: true,
            maxShadowOpacity: 0.55,
            flippingTime: 900,
            showPageCorners: true,
            mobileScrollSupport: false,
            autoSize: true
        });
        flip.loadFromHTML(leaves);

        let thumbs = [];
        if (thumbsRoot) {
            pages.forEach((p, i) => {
                const b = document.createElement("button");
                b.type = "button";
                b.className = "reader-thumb";
                b.setAttribute("aria-label", String(i + 1));
                const im = document.createElement("img");
                im.src = p.thumb || p.src;
                im.alt = "";
                im.loading = "lazy";
                b.appendChild(im);
                b.addEventListener("click", () => {
                    const target = i - (i % 2);
                    loadAround(target);
                    flip.flip(target);
                });
                thumbsRoot.appendChild(b);
            });
            thumbs = Array.from(thumbsRoot.children);
        }

        // 本の厚み（小口）。読んだ分が左に、残りが右に積もる
        const EDGE_MAX = 10;
        const updateEdges = index => {
            const done = pages.length > 2 ? index / (pages.length - 2) : 0;
            const r = flip.getBoundsRect && flip.getBoundsRect();
            const left = Math.round(EDGE_MAX * Math.min(1, done) + 1);
            const right = Math.round(EDGE_MAX * Math.max(0, 1 - done) + 1);
            spread.style.setProperty("--edge-l", left + "px");
            spread.style.setProperty("--edge-r", right + "px");
            if (r && r.width) {
                const offset = r.left;
                edgeL.style.left = offset - left + "px";
                edgeR.style.left = offset + r.width + "px";
                edgeL.style.top = edgeR.style.top = r.top + 2 + "px";
                edgeL.style.height = edgeR.style.height = r.height - 4 + "px";
            }
        };

        const update = index => {
            const last = pages.length - 1;
            const end = Math.min(index + 2, pages.length);
            indicator.textContent = (index + 1 === end ? String(end) : (index + 1) + "–" + end) + " / " + pages.length;
            prev.disabled = index <= 0;
            next.disabled = index + 2 > last;
            thumbs.forEach((t, i) => t.classList.toggle("is-active", i === index || i === index + 1));
            const active = thumbs[index];
            if (active) {
                thumbsRoot.scrollLeft = active.offsetLeft - thumbsRoot.clientWidth / 2 + active.clientWidth / 2;
            }
            loadAround(index);
            updateEdges(index);
        };

        flip.on("flip", e => update(e.data));
        // 捲り始めた瞬間に、その先のページも読み込んでおく
        flip.on("changeState", e => {
            if (e.data === "user_fold" || e.data === "flipping") loadAround(flip.getCurrentPageIndex());
        });
        flip.on("update", () => updateEdges(flip.getCurrentPageIndex()));

        prev.addEventListener("click", () => flip.flipPrev("bottom"));
        next.addEventListener("click", () => {
            loadAround(flip.getCurrentPageIndex() + 2);
            flip.flipNext("bottom");
        });
        document.addEventListener("keydown", e => {
            if (wrap.offsetParent === null) return;
            if (e.target.closest && e.target.closest("input, textarea")) return;
            if (e.key === "ArrowRight") next.click();
            if (e.key === "ArrowLeft") prev.click();
        });
        window.addEventListener("resize", () => {
            leaves.forEach(l => { l.firstChild.sizes = pageWidth() + "px"; });
            updateEdges(flip.getCurrentPageIndex());
        });

        update(0);
    }

    // ---------------------------------------------------------------- スマホ
    // 縦スクロールはそのまま。今のページ表示・続きから読む・タップで全画面（左右スワイプ／拡大／下スワイプで閉じる）を足す

    const MOBILE = window.matchMedia("(max-width: 900px)");
    const JA = (document.documentElement.lang || "").startsWith("ja");
    const T = JA
        ? { resume: n => `続きから読む（${n}ページ）`, close: "閉じる" }
        : { resume: n => `Continue from page ${n}`, close: "Close" };

    const store = {
        get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
        set(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* 保存できなくても読める */ } }
    };

    function initMobile(root) {
        const imgs = Array.from(root.querySelectorAll(".reader-scroll img")).filter(i => !i.classList.contains("is-blank"));
        if (!imgs.length) return;
        const total = imgs.length;
        const key = "masuphoto:last:" + location.pathname;

        // 今のページ表示（写真集の範囲にいるときだけ出す）
        const counter = document.createElement("div");
        counter.className = "reader-counter";
        counter.setAttribute("aria-hidden", "true");
        document.body.appendChild(counter);
        let current = 0;
        const visible = new Map();
        const io = new IntersectionObserver(entries => {
            entries.forEach(e => visible.set(e.target, e.intersectionRatio));
            let best = -1, ratio = 0;
            visible.forEach((r, el) => { if (r > ratio) { ratio = r; best = imgs.indexOf(el); } });
            if (best >= 0) {
                current = best;
                counter.textContent = (best + 1) + " / " + total;
                if (best > 0) store.set(key, String(best));
            }
            counter.classList.toggle("is-shown", MOBILE.matches && ratio > 0);
        }, { threshold: [0, 0.25, 0.5, 0.75, 1] });
        imgs.forEach(i => io.observe(i));

        // 続きから読む
        const last = parseInt(store.get(key) || "0", 10);
        if (MOBILE.matches && last > 1 && last < total) {
            const b = document.createElement("button");
            b.type = "button";
            b.className = "reader-resume";
            b.textContent = T.resume(last + 1);
            b.addEventListener("click", () => {
                imgs[last].scrollIntoView({ behavior: "smooth", block: "start" });
                b.remove();
            });
            root.querySelector(".reader-scroll").before(b);
        }

        // タップで全画面
        imgs.forEach((img, i) => img.addEventListener("click", () => { if (MOBILE.matches) openViewer(imgs, i); }));
    }

    function openViewer(imgs, start) {
        const box = document.createElement("div");
        box.className = "viewer";
        box.setAttribute("role", "dialog");
        box.setAttribute("aria-modal", "true");
        box.innerHTML = `<div class="viewer-track"></div><div class="viewer-count"></div><button type="button" class="viewer-close" aria-label="${T.close}">×</button>`;
        const track = box.querySelector(".viewer-track");
        const count = box.querySelector(".viewer-count");
        imgs.forEach(src => {
            const slide = document.createElement("div");
            slide.className = "viewer-slide";
            const im = document.createElement("img");
            im.alt = src.alt;
            im.decoding = "async";
            im.loading = "lazy";
            im.sizes = "100vw";
            if (src.getAttribute("srcset")) im.srcset = src.getAttribute("srcset");
            im.src = src.getAttribute("src");
            slide.appendChild(im);
            track.appendChild(slide);
        });
        document.body.appendChild(box);
        document.documentElement.classList.add("viewer-open");
        track.scrollLeft = start * track.clientWidth;
        let index = start;
        const setCount = () => { count.textContent = (index + 1) + " / " + imgs.length; };
        setCount();
        requestAnimationFrame(() => box.classList.add("is-open"));

        // Android の戻るボタン・ブラウザの戻るで閉じる
        history.pushState({ viewer: true }, "");
        let closed = false;
        const close = (fromPop) => {
            if (closed) return;
            closed = true;
            imgs[index].scrollIntoView({ block: "center" });
            box.classList.remove("is-open");
            document.documentElement.classList.remove("viewer-open");
            setTimeout(() => box.remove(), 250);
            window.removeEventListener("popstate", onPop);
            if (!fromPop) history.back();
        };
        const onPop = () => close(true);
        window.addEventListener("popstate", onPop);
        box.querySelector(".viewer-close").addEventListener("click", () => close(false));

        track.addEventListener("scroll", () => {
            const i = Math.round(track.scrollLeft / track.clientWidth);
            if (i !== index) { resetZoom(); index = i; setCount(); }
        }, { passive: true });

        // 拡大（2本指／ダブルタップ）と、拡大中の移動。拡大していないときの下スワイプで閉じる
        let scale = 1, tx = 0, ty = 0, startDist = 0, startScale = 1, lastTap = 0;
        let panX = 0, panY = 0, startX = 0, startY = 0, dragY = 0, mode = null;
        const img = () => track.children[index].querySelector("img");
        const apply = () => {
            img().style.transform = `translate(${tx}px, ${ty}px) scale(${scale})`;
            track.style.overflowX = scale > 1 ? "hidden" : "";
        };
        function resetZoom() {
            scale = 1; tx = 0; ty = 0;
            const el = track.children[index] && img();
            if (el) el.style.transform = "";
            track.style.overflowX = "";
        }
        const dist = t => Math.hypot(t[0].clientX - t[1].clientX, t[0].clientY - t[1].clientY);

        box.addEventListener("touchstart", e => {
            if (e.touches.length === 2) {
                mode = "pinch"; startDist = dist(e.touches); startScale = scale;
            } else if (e.touches.length === 1) {
                startX = e.touches[0].clientX; startY = e.touches[0].clientY;
                panX = tx; panY = ty; dragY = 0;
                mode = scale > 1 ? "pan" : "maybe-close";
                const now = Date.now();
                if (now - lastTap < 280) {  // ダブルタップ
                    if (scale > 1) resetZoom(); else { scale = 2.5; apply(); }
                    mode = null;
                }
                lastTap = now;
            }
        }, { passive: true });

        box.addEventListener("touchmove", e => {
            if (mode === "pinch" && e.touches.length === 2) {
                e.preventDefault();
                scale = Math.min(4, Math.max(1, startScale * dist(e.touches) / startDist));
                if (scale === 1) { tx = 0; ty = 0; }
                apply();
            } else if (mode === "pan" && e.touches.length === 1) {
                e.preventDefault();
                tx = panX + (e.touches[0].clientX - startX);
                ty = panY + (e.touches[0].clientY - startY);
                apply();
            } else if (mode === "maybe-close" && e.touches.length === 1) {
                const dx = e.touches[0].clientX - startX, dy = e.touches[0].clientY - startY;
                if (dy > 12 && Math.abs(dy) > Math.abs(dx) * 1.5) {
                    mode = "close"; 
                }
                if (mode === "close") {
                    e.preventDefault();
                    dragY = Math.max(0, dy);
                    box.style.setProperty("--drag", dragY + "px");
                } else if (Math.abs(dx) > 12) {
                    mode = null;  // 横スワイプはスクロールに任せる
                }
            }
        }, { passive: false });

        box.addEventListener("touchend", () => {
            if (mode === "close") {
                if (dragY > 110) close(false);
                else box.style.setProperty("--drag", "0px");
            }
            if (mode === "pinch" && scale < 1.05) resetZoom();
            mode = null;
        });

        document.addEventListener("keydown", function onKey(e) {
            if (closed) { document.removeEventListener("keydown", onKey); return; }
            if (e.key === "Escape") close(false);
        });
    }
})();
