# SEO / OG 維護總表（靜態 HTML 專案）

## 單一資料來源
- 每頁 SEO 欄位以 `seo-map.json` 為主資料來源（page file / route / title / description / canonical / hero image / og image / schema type / noindex）。
- 新增頁面時，先更新 `seo-map.json`，再同步寫入該頁 `<head>`。

## 每頁必填欄位
1. `title`
2. `meta description`
3. `canonical`
4. `og:title`, `og:description`, `og:url`, `og:image`
5. `twitter:card`, `twitter:title`, `twitter:description`, `twitter:image`
6. `schema`（至少 WebPage；服務頁補 Service；資訊頁補 Article）
7. `robots`（正式頁 `index,follow`；測試/搬移頁 `noindex,follow`）

## 維護流程（新增或修改頁面）
1. 在 `seo-map.json` 新增或更新頁面資料。
2. 將欄位寫入目標 HTML `<head>`（不可依賴 JS 動態補 meta）。
3. 確認 `og:image` 為絕對網址、可公開存取。
4. 若為正式頁，檢查是否需加入 `sitemap.xml`。
5. 重新跑檢查（重複 title/description/canonical、缺欄位、壞連結）。

## Core Web Vitals 風險盤點（目前）
- 首圖與大型圖片檔案偏多（LCP 風險）。
- 部分頁面尚未完整補 `width/height`（CLS 風險）。
- 圖片格式仍以 jpg/png 為主，可逐步導入 WebP/AVIF。
- 影片首屏頁（首頁）需持續監控 LCP 與 INP。

## Redirect 與索引策略
- 統一由 `_redirects`（Cloudflare Pages）做 301 轉址，不再使用 meta refresh 假搬移頁。
- `pages/family-photography.*` → `/pages/portrait-photography`（301）。
- `pages/photo-location.*` → `/pages/photography-studio`（301）。
- 全站一律使用 **不帶 `.html` 的 clean URL**（如 `/pages/about`），`.html` 舊版一律 301 到 clean URL。
- 正式網域統一為 `https://joyforest.tw`（非 www、https）。如 Cloudflare 仍有 www 轉址錯誤，請在 Cloudflare Dashboard → Rules → Redirect Rules 將 www → apex 修正。
- `404.html`：`noindex, nofollow`，不收錄於 sitemap；Cloudflare Pages 會自動把不存在網址回傳 404 + 此頁內容。

## 目前待補強 TODO
- FAQPage `mainEntity` 結構化資料完整化。
- BreadcrumbList schema 全站導入。
- 重要頁專屬 1200x630 og 圖逐步補齊。
- 圖片命名與壓縮策略（檔名語義化、WebP/AVIF）。
