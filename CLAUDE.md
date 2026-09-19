# MASU PHOTO（masuphoto.fomus.jp）

静的HTML。全写真集をこのリポジトリ（masuo444/masuphoto）1つで配信する。**配信は Vercel（プロジェクト masuphoto。GitHub連携で main へ push すると自動公開）**。DNS は Xserver（サーバーパネル → DNSレコード設定 → fomus.jp）で `masuphoto` CNAME `cname.vercel-dns.com`。GitHub Pages の設定と CNAME ファイルは予備として残っているだけ。

旧ドメイン masuphoto.fomusglobal.com は Vercel の別プロジェクト masuphoto-redirect（`~/Desktop/projects/masuphoto-redirect`）で同じパスへ 308 転送している。消さないこと。

## 写真集の仕組み
- 冊の一覧は `books.json`（番号・国名・年・版名）。ページ画像は `photobooks/<slug>/001.jpg …`（元画像そのまま。再圧縮しない）
- `python3 build.py` が `books/<slug>/`・`ja/books/<slug>/`、トップと partnership の本棚／冊数／国数、`sitemap.xml`、スマホ・サムネ用 WebP（`sm/`・`th/`）を生成する
- トップ等の生成範囲は `<!-- BUILD:名前 -->` 〜 `<!-- /BUILD:名前 -->`。この間は手で編集しない（次のビルドで消える）
- 書籍ページ（books/, ja/books/）は丸ごと生成物。文言を変えるときは build.py のテンプレートを直す

## 1冊追加する
1. `books.json` に追記（slug・number・name_en・name_ja・year・year_shelf・date_published）
2. `python3 build.py import <slug> <画像フォルダ>`（ファイル名順に取り込む。PNG は原寸のまま JPEG q92 に）
3. `python3 build.py`（push して公開されたら `python3 build.py indexnow` で Bing 等へ通知）
4. 表紙は `covers-thumb/<slug>.webp`・`covers-lg/<slug>.webp` が無ければ1ページ目から自動生成。差し替えるときは両方消してビルドし直す

## 旧サブドメイン
`masuphoto-<国>.fomusglobal.com`（12個、各リポジトリ）は `/books/<slug>/` への転送ページだけ。印刷物の QR が指しているので消さない。

## 検索・AI まわり
- 写真集ごとの紹介文は `books.json` の `story_en` / `story_ja`。写真から確かに言えることと、MaSU が確認した地名だけを書く
- シェア画像は `og/<slug>.jpg`・`og/site.jpg`（1200x630 JPEG、build.py が生成）。WebP は LINE 等で出ないので og:image に使わない
- Bing Webmaster Tools 登録済み（確認は index.html の msvalidate.01 メタタグ。消さない）。IndexNow の鍵はルートの `<key>.txt` と build.py の INDEXNOW_KEY
- `sitemap.xml` は画像サイトマップ込み。`llms.txt` は AI 向けの要約
