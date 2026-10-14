#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
const dataPath = path.join(root, "assets/data/activity-stories.json");
const data = JSON.parse(fs.readFileSync(dataPath, "utf8"));
const stories = data.stories;

function esc(value = "") {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function abs(url) {
  return url.startsWith("http") ? url : `https://joyforest.tw${url}`;
}

function local(url) {
  return path.join(root, url.replace(/^\//, ""));
}

function tagUrl(tag) {
  return `/pages/stories?tag=${encodeURIComponent(tag)}#story-list`;
}

const seenIds = new Set();
const seenSlugs = new Set();
for (const story of stories) {
  for (const key of ["caseId", "slug", "publishedDate", "title", "description", "intro", "fit"]) {
    if (!story[key]) throw new Error(`${story.slug || "unknown"}: missing ${key}`);
  }
  if (seenIds.has(story.caseId)) throw new Error(`duplicate caseId: ${story.caseId}`);
  if (seenSlugs.has(story.slug)) throw new Error(`duplicate slug: ${story.slug}`);
  seenIds.add(story.caseId);
  seenSlugs.add(story.slug);
  if (!fs.existsSync(local(story.cover.src))) throw new Error(`missing cover: ${story.cover.src}`);
  for (const media of story.media) {
    for (const key of media.type === "video" ? ["poster", "webm", "mp4"] : ["src"]) {
      if (!fs.existsSync(local(media[key]))) throw new Error(`missing media: ${media[key]}`);
    }
  }
}

function head({ title, description, canonical, image, schema, depth = "../" }) {
  return `<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>${esc(title)}</title>
  <meta name="description" content="${esc(description)}" />
  <link rel="canonical" href="${esc(canonical)}" />
  <meta property="og:type" content="article" />
  <meta property="og:locale" content="zh_TW" />
  <meta property="og:url" content="${esc(canonical)}" />
  <meta property="og:title" content="${esc(title)}" />
  <meta property="og:description" content="${esc(description)}" />
  <meta property="og:image" content="${esc(abs(image))}" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="${esc(title)}" />
  <meta name="twitter:description" content="${esc(description)}" />
  <meta name="twitter:image" content="${esc(abs(image))}" />
  <meta name="robots" content="index, follow" />
  <meta name="theme-color" content="#2e4b3f" />
  <link rel="stylesheet" href="${depth}assets/css/style.css?v=20261014-stories" />
  <link rel="icon" href="${depth}favicon.ico" sizes="any" />
  <link rel="icon" type="image/svg+xml" href="${depth}assets/images/favicon.svg" />
  <link rel="apple-touch-icon" href="${depth}apple-touch-icon.png" />
  <link rel="manifest" href="${depth}manifest.webmanifest" />
  <script type="application/ld+json">${JSON.stringify(schema)}</script>
</head>`;
}

function collaborators(story) {
  if (!story.collaborators.length) return "";
  const links = story.collaborators.map(item => `<a href="${esc(item.url)}" target="_blank" rel="noopener">${esc(item.handle)}</a>`).join("、");
  return `<aside class="activity-story-credit" aria-label="合作分享帳號"><strong>合作／真實分享帳號</strong><p>${links}</p></aside>`;
}

function mediaHtml(media) {
  if (media.type === "image") {
    return `<figure class="activity-story-media activity-story-media--image">
      <img src="${esc(media.src)}" alt="${esc(media.alt)}" title="${esc(media.caption)}" width="${media.width}" height="${media.height}" loading="lazy" decoding="async" />
      <figcaption>${esc(media.caption)}</figcaption>
    </figure>`;
  }
  return `<figure class="activity-story-media activity-story-media--video">
    <video controls playsinline preload="metadata" poster="${esc(media.poster)}" title="${esc(media.title)}" aria-label="${esc(media.title)}" width="${media.width}" height="${media.height}">
      <source src="${esc(media.webm)}" type="video/webm" />
      <source src="${esc(media.mp4)}" type="video/mp4" />
      您的瀏覽器無法播放這段森林故事影片。
    </video>
    <figcaption><strong>${esc(media.title)}</strong><span>${esc(media.visualSummary)}</span></figcaption>
    <div class="activity-story-transcript"><p><strong>畫面文字與情境整理：</strong>${esc(media.visualSummary)}</p><p><strong>音訊／語音整理：</strong>${esc(media.audioSummary)}</p></div>
  </figure>`;
}

function sharedTags(a, b) {
  return a.tags.filter(tag => b.tags.includes(tag)).length;
}

function relatedCards(story) {
  return stories
    .filter(item => item.slug !== story.slug)
    .sort((a, b) => sharedTags(story, b) - sharedTags(story, a) || b.publishedDate.localeCompare(a.publishedDate))
    .slice(0, 3)
    .map(cardHtml)
    .join("\n");
}

function tagsHtml(tags) {
  return tags.map(tag => `<a class="activity-story-tag" href="${tagUrl(tag)}">${esc(tag)}</a>`).join("");
}

function cardHtml(story) {
  return `<article class="activity-story-card" data-tags="${esc(story.tags.join("|"))}">
    <a class="activity-story-card__image" href="/stories/${esc(story.slug)}/">
      <img src="${esc(story.cover.src)}" alt="${esc(story.cover.alt)}" width="${story.cover.width}" height="${story.cover.height}" loading="lazy" decoding="async" />
    </a>
    <div class="activity-story-card__body">
      <div class="activity-story-card__meta"><time datetime="${esc(story.publishedDate)}">${esc(story.publishedDate)}</time><span>森林故事</span></div>
      <h2><a href="/stories/${esc(story.slug)}/">${esc(story.title)}</a></h2>
      <p>${esc(story.description)}</p>
      <div class="activity-story-tags">${tagsHtml(story.tags.slice(0, 4))}</div>
    </div>
  </article>`;
}

function articleSchema(story) {
  const videos = story.media.filter(item => item.type === "video").map(item => ({
    "@type": "VideoObject",
    name: item.title,
    description: `${item.visualSummary} ${item.audioSummary}`,
    thumbnailUrl: abs(item.poster),
    uploadDate: story.publishedDate,
    contentUrl: abs(item.mp4)
  }));
  return {
    "@context": "https://schema.org",
    "@type": "Article",
    headline: story.title,
    description: story.description,
    datePublished: story.publishedDate,
    dateModified: data.updatedDate,
    image: abs(story.cover.src),
    mainEntityOfPage: `https://joyforest.tw/stories/${story.slug}/`,
    author: {"@type": "Organization", name: "Joyforest 揪好森", url: "https://joyforest.tw/"},
    publisher: {"@type": "Organization", name: "Joyforest 揪好森", logo: {"@type": "ImageObject", url: "https://joyforest.tw/assets/images/favicon.svg"}},
    keywords: story.tags.join(", "),
    ...(videos.length ? {hasPart: videos} : {})
  };
}

function buildArticle(story) {
  const pageTitle = `${story.title}｜森林故事｜Joyforest 揪好森`;
  const media = story.media.length ? `<section class="activity-story-section" aria-labelledby="media-title"><h2 id="media-title">照片與影片裡的活動故事</h2><div class="activity-story-media-list">${story.media.map(mediaHtml).join("\n")}</div></section>` : "";
  return `${head({title: pageTitle, description: story.description, canonical: `https://joyforest.tw/stories/${story.slug}/`, image: story.cover.src, schema: articleSchema(story), depth: "../../"})}
<body data-base="../../">
  <div id="site-header"></div>
  <main>
    <article>
      <header class="activity-story-hero">
        <div class="container activity-story-hero__grid">
          <div class="activity-story-hero__copy">
            <nav class="activity-story-breadcrumb" aria-label="麵包屑"><a href="/">首頁</a><span>/</span><a href="/pages/stories">森林故事</a></nav>
            <p class="kicker">FOREST STORY · ${esc(story.publishedDate)}</p>
            <h1>${esc(story.title)}</h1>
            <p class="activity-story-deck">${esc(story.description)}</p>
            <div class="activity-story-tags">${tagsHtml(story.tags)}</div>
          </div>
          <figure class="activity-story-cover"><img src="${esc(story.cover.src)}" alt="${esc(story.cover.alt)}" title="${esc(story.title)}" width="${story.cover.width}" height="${story.cover.height}" fetchpriority="high" decoding="async" /></figure>
        </div>
      </header>
      <div class="container activity-story-content">
${collaborators(story)}
        <section class="activity-story-section"><h2>這次在森林裡做了什麼？</h2><p>${esc(story.intro)}</p></section>
${media}
        <section class="activity-story-section activity-story-fit"><h2>適合怎樣的活動？</h2><p>${esc(story.fit)}</p><div class="activity-story-tags">${tagsHtml(story.tags)}</div></section>
        <section class="activity-story-cta"><div><p class="kicker">PLAN YOUR EVENT</p><h2>把這個故事變成你的活動靈感</h2><p>告訴我們日期、人數與想安排的內容，我們會依活動需求協助確認場地使用方式。</p></div><div class="actions"><a class="btn primary" href="${esc(story.servicePath)}">${esc(story.serviceLabel)}</a><a class="btn ghost" href="/pages/book">加入 Line 詢問</a></div></section>
      </div>
    </article>
    <section class="section activity-related" aria-labelledby="related-title"><div class="container"><p class="kicker">MORE STORIES</p><h2 id="related-title">繼續看森林故事</h2><div class="activity-story-grid">${relatedCards(story)}</div></div></section>
  </main>
  <div id="site-footer"></div>
  <div id="cta-global"></div>
  <script src="../../assets/js/main.js" defer></script>
</body>
</html>`;
}

const storyTagSet = new Set(stories.flatMap(story => story.tags));
const preferredFilterTags = [
  "寵物友善",
  "親子活動",
  "好友聚會",
  "戶外電影",
  "烤肉 BBQ",
  "營火體驗",
  "家庭攝影",
  "親子寫真",
  "戶外攝影",
  "自然光攝影棚",
  "企業包場",
  "團隊活動",
  "情侶約會",
  "夜間燈光",
  "場地導覽"
];
const allTags = preferredFilterTags.filter(tag => storyTagSet.has(tag));
const hubSchema = {
  "@context": "https://schema.org",
  "@type": "CollectionPage",
  name: "森林故事｜Joyforest 揪好森",
  description: "真實活動、攝影、聚會與場地使用故事。",
  url: "https://joyforest.tw/pages/stories",
  mainEntity: {"@type": "ItemList", numberOfItems: stories.length, itemListElement: stories.map((story, index) => ({"@type": "ListItem", position: index + 1, url: `https://joyforest.tw/stories/${story.slug}/`, name: story.title}))}
};

const hub = `${head({title: "森林故事｜真實活動、攝影與聚會分享｜Joyforest 揪好森", description: "從真實客戶與合作創作者的照片、影片，看桃園楊梅森林場地如何安排戶外電影、烤肉、營火、親子、寵物、攝影與團體活動。", canonical: "https://joyforest.tw/pages/stories", image: stories[0].cover.src, schema: hubSchema, depth: "../"})}
<body data-base="../">
  <div id="site-header"></div>
  <main>
    <section class="activity-stories-hero"><div class="container"><p class="kicker">JOYFOREST STORIES</p><h1>森林故事</h1><p>從真實客戶與合作創作者的照片、影片，看森林場地如何安排攝影、戶外電影、烤肉、營火、親子、寵物與團體活動。</p><div class="activity-stories-summary"><span><strong>${stories.length}</strong> 則活動故事</span><span>照片與影片皆有文字描述</span><span>合作 IG 帳號保留可點擊連結</span></div></div></section>
    <section class="section tight activity-story-filter" aria-labelledby="filter-title"><div class="container"><h2 id="filter-title">依活動關鍵字找故事</h2><div class="activity-story-tags activity-story-tags--filter"><a class="activity-story-tag is-active" href="/pages/stories#story-list" data-filter="">全部故事</a>${allTags.map(tag => `<a class="activity-story-tag" href="${tagUrl(tag)}" data-filter="${esc(tag)}">${esc(tag)}</a>`).join("")}</div></div></section>
    <section class="section activity-stories-list" id="story-list" aria-labelledby="story-list-title"><div class="container"><div class="activity-story-list-heading"><div><p class="kicker">REAL EXPERIENCES</p><h2 id="story-list-title">真實活動分享</h2></div><p id="activity-story-count" aria-live="polite">共 ${stories.length} 則</p></div><div class="activity-story-grid">${stories.map(cardHtml).join("\n")}</div><p class="activity-story-empty" hidden>目前沒有符合此標籤的故事，請改選其他關鍵字。</p></div></section>
  </main>
  <div id="site-footer"></div>
  <div id="cta-global"></div>
  <script src="../assets/js/main.js" defer></script>
  <script>
    (()=>{
      const cards=[...document.querySelectorAll('.activity-story-card')];
      const links=[...document.querySelectorAll('[data-filter]')];
      const count=document.getElementById('activity-story-count');
      const empty=document.querySelector('.activity-story-empty');
      const params=new URLSearchParams(location.search);
      const initial=params.get('tag')||'';
      const apply=(tag)=>{
        let visible=0;
        cards.forEach(card=>{const show=!tag||card.dataset.tags.split('|').includes(tag);card.hidden=!show;if(show)visible++;});
        links.forEach(link=>link.classList.toggle('is-active',(link.dataset.filter||'')===tag));
        count.textContent=tag ? tag+'：'+visible+' 則' : '共 '+visible+' 則';
        empty.hidden=visible!==0;
      };
      links.forEach(link=>link.addEventListener('click',event=>{event.preventDefault();const tag=link.dataset.filter||'';history.replaceState(null,'',tag?'?tag='+encodeURIComponent(tag)+'#story-list':'#story-list');apply(tag);document.getElementById('story-list').scrollIntoView({behavior:'smooth'});}));
      apply(initial);
    })();
  </script>
</body>
</html>`;

fs.writeFileSync(path.join(root, "pages/stories.html"), hub);
for (const story of stories) {
  const dir = path.join(root, "stories", story.slug);
  fs.mkdirSync(dir, {recursive: true});
  fs.writeFileSync(path.join(dir, "index.html"), buildArticle(story));
}

console.log(JSON.stringify({stories: stories.length, tags: allTags.length, output: "pages/stories.html + stories/*/index.html"}, null, 2));
