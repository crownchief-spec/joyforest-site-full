# 網站上線後優化設定 100 項檢查表（執行版）

狀態說明：`[x] 完成`、`[~] 部分完成/有 TODO`、`[ ] 未完成`

## 一、品牌與網站識別設定
1. [x] favicon.ico
2. [x] SVG favicon
3. [x] favicon link tags
4. [x] apple-touch-icon
5. [x] manifest 檔
6. [x] manifest 引用
7. [x] theme-color
8. [x] logo alt
9. [x] 品牌名稱一致（Joyforest 揪好森）
10. [x] 品牌名稱集中管理（`seo-map.json`）

## 二、每頁基礎 SEO
11. [x] 每頁獨立 title
12. [x] 每頁獨立 meta description
13. [x] 每頁獨立 canonical
14. [x] 每頁 og:url
15. [x] 每頁 og:type（一般頁 website、SEO頁 article）
16. [x] HTML lang
17. [x] 每頁 H1
18. [x] H2/H3 基本層級
19. [x] title 重複檢查
20. [x] description 重複檢查

## 三、社群分享 Open Graph
21. [x] 每頁 og:title
22. [x] 每頁 og:description
23. [x] 每頁 og:image
24. [x] 每頁 og:url
25. [x] twitter:card summary_large_image
26. [x] 每頁 twitter:title
27. [x] 每頁 twitter:description
28. [x] 每頁 twitter:image
29. [x] 移除壞掉的共用 og:image（`logo.png` 不存在已修）
30. [~] 各頁分享圖不再共用「同一預設圖」（仍有部分頁共用同一 hero 圖）

## 四、OG 圖與 hero 圖策略
31. [x] hero 圖優先做 og:image（一般內容頁）
32. [x] 支援專用 og:image（可在 head 個別指定）
33. [x] 選圖邏輯（優先主視覺）
34. [x] og:image 使用絕對網址
35. [x] og:image 路徑可讀取
36. [x] 檢查圖片 404（站內引用路徑掃描）
37. [x] 避免抓到小圖/縮圖做 og:image
38. [~] 多主圖頁面規則（已建立慣例，尚未文件化成程式規則）
39. [x] 首頁專用 og:image
40. [x] 建立 ogImage 欄位（`seo-map.json`）

## 五、靜態網站可維護 SEO 結構
41. [~] 共用 SEO head partial（目前仍為純 HTML 各頁 head）
42. [~] 共用 SEO 區塊完整欄位（透過維護表，非模板注入）
43. [x] per-page SEO 資料來源（`seo-map.json`）
44. [x] 每頁獨立 title
45. [x] 每頁獨立 description
46. [x] 每頁可獨立 hero/og image
47. [x] 每頁可獨立 canonical
48. [x] 每頁可獨立 noindex（404、搬移頁）
49. [x] 每頁可獨立 schemaType（維護表）
50. [x] 純 HTML 維護清單（`SEO_MAINTENANCE.md`）

## 六、Canonical 與網址正規化
51. [x] 每頁 canonical
52. [x] canonical 使用正式網域
53. [x] 統一 non-www
54. [x] 統一 https
55. [x] 尾斜線規則一致（首頁 `/`，其餘無尾斜線）
56. [x] 類似頁 canonical 策略（舊頁 noindex + 導向）
57. [x] 內部連結格式整體一致
58. [~] 舊頁 redirect 規劃（目前為 HTML refresh + JS replace，後續建議 301）
59. [x] sitemap 與 canonical 一致
60. [x] canonical 不含 query

## 七、索引控制與搜尋引擎檔案
61. [x] robots.txt
62. [x] robots.txt 含 sitemap
63. [x] sitemap.xml
64. [x] sitemap 僅收錄正式頁
65. [x] 排除重複頁（舊 family-photography 未進 sitemap）
66. [x] noindex 支援
67. [x] 404.html
68. [~] 薄內容頁（已標註，待持續補強）
69. [x] staging/demo 頁避索引（目前無）
70. [x] 站內死連結/壞資源掃描（本次掃描無壞連結）

## 八、Schema 結構化資料
71. [x] 首頁 Organization
72. [x] LocalBusiness（首頁補上，location 頁已配置）
73. [x] 首頁 WebSite
74. [x] 一般頁 WebPage
75. [x] 服務頁 Service
76. [~] BreadcrumbList（尚未全頁導入）
77. [~] FAQPage（faq 已有；`mainEntity` 後續補強）
78. [x] 文章頁 Article/BlogPosting（seo/*.html 已用 Article）
79. [x] 圖片導向頁 ImageObject（pet-photography）
80. [x] Schema 與頁面內容一致

## 九、圖片 SEO 與媒體最佳化
81. [x] 主要圖片 alt
82. [x] hero 圖 alt
83. [~] 無意義檔名盤點（已盤點，待重命名計畫）
84. [~] 重要圖片 SEO 命名（待批次改名）
85. [~] 圖片尺寸最佳化（需再做壓縮策略）
86. [~] hero 首圖優先載入（部分頁尚有 lazy 需二次盤點）
87. [~] width/height（非全站完成）
88. [x] 壞圖修正（logo 壞圖已修）
89. [~] WebP/AVIF 優先（目前以 jpg/png 為主）
90. [x] 圖片來源可管理（透過 `seo-map.json` 維護）

## 十、AI / LLM / 可讀性 / 技術補強
91. [x] 建立 /llms.txt
92. [x] llms.txt 結構清楚
93. [x] 首頁與重要頁有文字摘要
94. [x] 關鍵資訊為 HTML 文字
95. [x] 首頁清楚描述品牌/服務/地區/預約方式
96. [x] 內部連結結構（header/footer/sitemap）
97. [x] 手機版與桌機版 head 一致（靜態同源）
98. [x] Core Web Vitals 風險盤點（見維護總表）
99. [x] analytics/tracking 預留（`index.html` + `assets/js/main.js` TODO 註記）
100. [x] 維護總表（`SEO_MAINTENANCE.md` + `seo-map.json`）

## 仍需補強（優先）
- BreadcrumbList schema 全站化。
- FAQPage 的 `mainEntity` 完整問答結構。
- hero 圖 `width/height` 與首圖 lazy-loading 二次盤點。
- 圖片格式升級（WebP/AVIF）與檔名優化。
- 伺服器層 301 redirect（取代 HTML refresh）。
