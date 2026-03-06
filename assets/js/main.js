(function(){
  const body = document.body;
  const base = body.dataset.base || "./";

  async function loadComponent(targetId, path){
    const el = document.getElementById(targetId);
    if(!el) return;
    const res = await fetch(path, {cache:"no-store"});
    if(!res.ok) throw new Error("Failed to load " + path);
    let html = await res.text();
    html = html.replaceAll("{{base}}", base);
    el.innerHTML = html;
  }

  function wireNav(){
    const toggle = document.querySelector("[data-nav-toggle]");
    const menu = document.querySelector("[data-nav-menu]");
    if(toggle && menu){
      toggle.addEventListener("click", ()=>{
        const open = menu.classList.toggle("open");
        toggle.setAttribute("aria-expanded", String(open));
      });
    }

    document.querySelectorAll(".dropdown > button").forEach(btn=>{
      btn.addEventListener("click", ()=>{
        const parent = btn.closest(".dropdown");
        const isOpen = parent.classList.toggle("open");
        btn.setAttribute("aria-expanded", String(isOpen));
      });
    });

    document.addEventListener("click", (e)=>{
      const dd = e.target.closest(".dropdown");
      document.querySelectorAll(".dropdown").forEach(d=>{
        if(d !== dd) d.classList.remove("open");
      });
    });
  }

  function heroVideoFallback(){
    const v = document.querySelector(".hero video");
    if(!v) return;
    v.addEventListener("error", ()=>{ v.style.display="none"; });
    // 僅在「省流量」模式下不自動播放，手機也讓影片動起來
    const saveData = navigator.connection && navigator.connection.saveData;
    if(saveData){
      try{ v.pause(); v.removeAttribute("autoplay"); }catch(_){}
    }
  }

  function initBookCopy(){
    const btn = document.getElementById("book-copy-btn");
    const pre = document.getElementById("booking-template");
    if(!btn || !pre) return;
    btn.addEventListener("click", async ()=>{
      try {
        await navigator.clipboard.writeText(pre.textContent.trim());
        const orig = btn.textContent;
        btn.textContent = "已複製！";
        btn.setAttribute("aria-label", "已複製到剪貼簿");
        setTimeout(()=>{ btn.textContent = orig; btn.setAttribute("aria-label", "一鍵複製預約模板到剪貼簿"); }, 2000);
      } catch (e) {
        btn.textContent = "請手動複製";
      }
    });
  }

  function initCarousels(){
    document.querySelectorAll(".gallery--carousel").forEach(gallery=>{
      const imgs = gallery.querySelectorAll(":scope > img");
      if(imgs.length < 2) return;
      const viewport = document.createElement("div");
      viewport.className = "carousel-viewport";
      const track = document.createElement("div");
      track.className = "carousel-track";
      imgs.forEach(img=>{
        const slide = document.createElement("div");
        slide.className = "carousel-slide";
        slide.appendChild(img);
        track.appendChild(slide);
      });
      viewport.appendChild(track);
      gallery.innerHTML = "";
      gallery.appendChild(viewport);
      const nav = document.createElement("div");
      nav.className = "carousel-nav";
      const prev = document.createElement("button");
      prev.type = "button";
      prev.className = "carousel-btn carousel-btn-prev";
      prev.setAttribute("aria-label", "上一張照片");
      prev.textContent = "‹";
      const next = document.createElement("button");
      next.type = "button";
      next.className = "carousel-btn carousel-btn-next";
      next.setAttribute("aria-label", "下一張照片");
      next.textContent = "›";
      const dotsWrap = document.createElement("div");
      dotsWrap.className = "carousel-dots";
      const slides = track.querySelectorAll(".carousel-slide");
      const total = slides.length;
      let autoTimer = null;
      const AUTO_MS = 4500;
      function getPerView(){
        if(window.innerWidth >= 981) return 4;
        if(window.innerWidth >= 521) return 2;
        return 1;
      }
      function getScrollIndex(){
        const per = getPerView();
        const w = viewport.offsetWidth;
        const scrollLeft = viewport.scrollLeft;
        const slideWidth = w / per;
        return Math.min(total - per, Math.max(0, Math.round(scrollLeft / slideWidth)));
      }
      function updateDots(){
        const per = getPerView();
        const maxIndex = Math.max(0, total - per);
        const index = getScrollIndex();
        dotsWrap.querySelectorAll(".carousel-dot").forEach((d,i)=>{ d.classList.toggle("active", i === index); });
      }
      function scrollToIndex(index){
        const per = getPerView();
        const w = viewport.offsetWidth;
        const slideWidth = w / per;
        viewport.scrollTo({ left: index * slideWidth, behavior: "smooth" });
        updateDots();
        resetAuto();
      }
      function goPrev(){
        const index = getScrollIndex();
        const per = getPerView();
        const maxIndex = Math.max(0, total - per);
        if(index <= 0) scrollToIndex(maxIndex);
        else scrollToIndex(index - 1);
      }
      function goNext(){
        const index = getScrollIndex();
        const per = getPerView();
        const maxIndex = Math.max(0, total - per);
        if(index >= maxIndex) scrollToIndex(0);
        else scrollToIndex(index + 1);
      }
      function resetAuto(){
        if(autoTimer) clearInterval(autoTimer);
        autoTimer = setInterval(goNext, AUTO_MS);
      }
      function buildTrack(){
        const per = getPerView();
        track.style.width = (total * 100 / per) + "%";
        track.querySelectorAll(".carousel-slide").forEach(slide=>{
          slide.style.flex = "0 0 " + (100 * per / total) + "%";
        });
      }
      function buildDots(){
        const per = getPerView();
        const maxIndex = Math.max(0, total - per);
        dotsWrap.innerHTML = "";
        for(let i = 0; i <= maxIndex; i++){
          const dot = document.createElement("button");
          dot.type = "button";
          dot.className = "carousel-dot" + (i === 0 ? " active" : "");
          dot.setAttribute("aria-label", "第 " + (i+1) + " 張");
          dot.addEventListener("click", ()=>{ scrollToIndex(i); });
          dotsWrap.appendChild(dot);
        }
      }
      viewport.addEventListener("scroll", ()=>{ updateDots(); resetAuto(); }, { passive: true });
      prev.addEventListener("click", (e)=>{ e.preventDefault(); goPrev(); });
      next.addEventListener("click", (e)=>{ e.preventDefault(); goNext(); });
      window.addEventListener("resize", ()=>{
        buildTrack();
        buildDots();
        updateDots();
      });
      nav.appendChild(prev);
      nav.appendChild(dotsWrap);
      nav.appendChild(next);
      gallery.appendChild(nav);
      buildTrack();
      buildDots();
      updateDots();
      resetAuto();
    });
  }

  function initServiceSlider(){
    const slider = document.getElementById("serviceSlider");
    if(!slider) return;
    const track = slider.querySelector(".service-track");
    const slides = slider.querySelectorAll(".service-slide");
    const prevBtn = slider.querySelector(".prev");
    const nextBtn = slider.querySelector(".next");
    const currentSlideEl = document.getElementById("currentSlide");
    const totalSlidesEl = document.getElementById("totalSlides");
    let currentIndex = 0;
    let startX = 0;
    let currentTranslate = 0;
    const total = slides.length;
    if(totalSlidesEl) totalSlidesEl.textContent = total;
    function updateSlider(){
      if(track) track.style.transform = "translateX(-" + currentIndex * 100 + "%)";
      if(currentSlideEl) currentSlideEl.textContent = currentIndex + 1;
    }
    function goToSlide(index){
      currentIndex = Math.max(0, Math.min(index, total - 1));
      updateSlider();
    }
    if(prevBtn) prevBtn.addEventListener("click", function(){ goToSlide(currentIndex - 1); });
    if(nextBtn) nextBtn.addEventListener("click", function(){ goToSlide(currentIndex + 1); });
    track.addEventListener("touchstart", function(e){ startX = e.touches[0].clientX; }, { passive: true });
    track.addEventListener("touchmove", function(e){ currentTranslate = e.touches[0].clientX; }, { passive: true });
    track.addEventListener("touchend", function(){
      const movedBy = currentTranslate - startX;
      if(movedBy < -50) goToSlide(currentIndex + 1);
      else if(movedBy > 50) goToSlide(currentIndex - 1);
      startX = 0;
      currentTranslate = 0;
    });
    updateSlider();
  }

  document.addEventListener("DOMContentLoaded", async ()=>{
    try{
      await loadComponent("site-header", base + "components/header.html");
      await loadComponent("site-footer", base + "components/footer.html");
      if (document.getElementById("cta-global")) {
        await loadComponent("cta-global", base + "components/cta-global.html");
      }
      wireNav();
      heroVideoFallback();
      initBookCopy();
      initCarousels();
      initServiceSlider();
    }catch(err){
      console.warn(err);
      // If components fail, allow page to still render
    }
  });
})();
