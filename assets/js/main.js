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
      prev.className = "carousel-btn";
      prev.setAttribute("aria-label", "上一張");
      prev.textContent = "‹";
      const next = document.createElement("button");
      next.type = "button";
      next.className = "carousel-btn";
      next.setAttribute("aria-label", "下一張");
      next.textContent = "›";
      const dotsWrap = document.createElement("div");
      dotsWrap.className = "carousel-dots";
      const slides = track.querySelectorAll(".carousel-slide");
      const total = slides.length;
      let index = 0;
      function getPerView(){
        if(window.innerWidth >= 981) return 4;
        if(window.innerWidth >= 521) return 2;
        return 1;
      }
      function buildDots(){
        const per = getPerView();
        const maxIndex = Math.max(0, total - per);
        dotsWrap.innerHTML = "";
        for(let i = 0; i <= maxIndex; i++){
          const dot = document.createElement("button");
          dot.type = "button";
          dot.className = "carousel-dot" + (i === index ? " active" : "");
          dot.setAttribute("aria-label", "第 " + (i+1) + " 張");
          dot.addEventListener("click", ()=>{ index = i; update(); });
          dotsWrap.appendChild(dot);
        }
      }
      function update(){
        const per = getPerView();
        const maxIndex = Math.max(0, total - per);
        index = Math.max(0, Math.min(index, maxIndex));
        track.style.width = (100 * total / per) + '%';
        track.querySelectorAll(".carousel-slide").forEach(slide=>{
          slide.style.flex = `0 0 ${100 * per / total}%`;
        });
        track.style.transform = `translateX(-${index * (100 / per)}%)`;
        dotsWrap.querySelectorAll(".carousel-dot").forEach((d,i)=>{ d.classList.toggle("active", i === index); });
      }
      buildDots();
      prev.addEventListener("click", ()=>{ index--; update(); });
      next.addEventListener("click", ()=>{ index++; update(); });
      window.addEventListener("resize", ()=>{
        buildDots();
        update();
      });
      nav.appendChild(prev);
      nav.appendChild(dotsWrap);
      nav.appendChild(next);
      gallery.appendChild(nav);
      update();
    });
  }

  document.addEventListener("DOMContentLoaded", async ()=>{
    try{
      await loadComponent("site-header", base + "components/header.html");
      await loadComponent("site-footer", base + "components/footer.html");
      wireNav();
      heroVideoFallback();
      initCarousels();
    }catch(err){
      console.warn(err);
      // If components fail, allow page to still render
    }
  });
})();
