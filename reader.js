// 写真集ビューア。ページ一覧は .reader-scroll の <img> から読む（HTML がそのまま唯一の情報源）。
// PC は StPageFlip（vendor/page-flip.browser.js）で紙が曲がる捲りを描く。スマホは縦並びのまま。
(function () {
    // 見開きに読み込む範囲（現在の見開きの前後）。全ページを一度に読むと重い冊（71ページ）があるため
    const PRELOAD_AHEAD = 4;
    const PRELOAD_BEHIND = 2;

    document.addEventListener("DOMContentLoaded", () => {
        document.querySelectorAll("[data-reader]").forEach(initReader);
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
})();
