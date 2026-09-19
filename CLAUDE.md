# MASU PHOTO（masuphoto.fomusglobal.com）

GitHub Pages（masuo444/masuphoto）。静的HTML。全写真集をこのリポジトリ1つで配信する。

## 写真集の仕組み
- 冊の一覧は `books.json`（番号・国名・年・版名）。ページ画像は `photobooks/<slug>/001.jpg …`（元画像そのまま。再圧縮しない）
- `python3 build.py` が `books/<slug>/`・`ja/books/<slug>/`、トップと partnership の本棚／冊数／国数、`sitemap.xml`、スマホ・サムネ用 WebP（`sm/`・`th/`）を生成する
- トップ等の生成範囲は `<!-- BUILD:名前 -->` 〜 `<!-- /BUILD:名前 -->`。この間は手で編集しない（次のビルドで消える）
- 書籍ページ（books/, ja/books/）は丸ごと生成物。文言を変えるときは build.py のテンプレートを直す

## 1冊追加する
1. `books.json` に追記（slug・number・name_en・name_ja・year・year_shelf・date_published）
2. `python3 build.py import <slug> <画像フォルダ>`（ファイル名順に取り込む。PNG は原寸のまま JPEG q92 に）
3. `python3 build.py`
4. 表紙は `covers-thumb/<slug>.webp`・`covers-lg/<slug>.webp` が無ければ1ページ目から自動生成。差し替えるときは両方消してビルドし直す

## 旧サブドメイン
`masuphoto-<国>.fomusglobal.com`（12個、各リポジトリ）は `/books/<slug>/` への転送ページだけ。印刷物の QR が指しているので消さない。
