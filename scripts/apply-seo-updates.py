#!/usr/bin/env python3
from pathlib import Path
import re

PAGES = Path(__file__).resolve().parents[1] / "pages"
STAY = (
    "拍攝完成後，免費贈送 2 小時空間停留使用，可休息、聚餐、聊天、"
    "陪孩子在草地玩耍，或讓毛孩繼續活動。若希望停留更久，"
    "可另外洽詢加購夜間體驗方案或延長空間使用時間。"
)

def rel(links):
    lines = "\n".join(f'      <a class="card-link" href="../pages/{s}">{l}</a>' for s, l in links)
    return (
        '    <section class="section tight">\n      <motion class="container">\n'
        '        <h2>相關服務</h2>\n        <div class="card-links" style="margin-top:10px">\n'
        f"{lines}\n        </div>\n      </div>\n    </section>"
    ).replace("<motion class", "<div class")

def kw(text):
    return (
        '    <section class="section tight">\n      <div class="container">\n'
        f'        <h2>相關關鍵字</h2>\n        <motion class="card"><p class="small">{text}</p></div>\n'
        "      </div>\n    </section>"
    ).replace('<motion class="card">', '<div class="card">')

def inject(main, block):
    return main if block[:24] in main else main.replace("  </main>", block + "\n  </main>", 1)

def fix_stay(text):
    for a, b in [
        ("拍攝後還可免費延長 2 小時園區體驗時間", STAY),
        ("拍攝結束後還可免費延長 2 小時園區體驗時間", STAY),
        ("拍攝結束後，還可免費延長 2 小時園區體驗時間", STAY),
        ("拍攝結束後，可免費延長 2 小時園區體驗時間", STAY),
        ("拍後可免費延長 2 小時園區體驗", "拍後免費贈送 2 小時空間停留使用"),
        ("園區體驗時間", "空間停留使用"), ("園區時光", "相聚時光"),
        ("園區內", "場地內"), ("完整的園區拍攝體驗", "完整的拍攝與空間體驗"),
    ]:
        text = text.replace(a, b)
    return text

def set_hero(text, desc):
    if "hero-service-desc" in text:
        return re.sub(r'<p class="hero-service-desc">.*?</p>', f'<p class="hero-service-desc">{desc}</p>', text, 1, re.S)
    return re.sub(r'(<h1 class="title">.*?</h1>\s*)<p class="subtitle">.*?</p>',
        rf'\1<p class="subtitle hero-service-desc" style="max-width:42em;line-height:1.65">{desc}</p>', text, 1, re.S)

def add_sec(text, title, body, before):
    if title in text: return text
    b = f'    <section class="section"><motion class="container"><h2>{title}</h2><div class="card"><p class="small">{body}</p></div></div></section>\n'
    b = b.replace("<motion class", "<motion class").replace("<motion class", "<div class")
    return text.replace(f"<h2>{before}</h2>", b + f"        <h2>{before}</h2>", 1)

# portrait
p = PAGES / "portrait-photography.html"
t = fix_stay(p.read_text(encoding="utf-8"))
t = set_hero(t, "這裡不是一般小型攝影棚，而是約 200 坪的森林系拍攝基地。拍攝空間包含雲朵帳篷正式棚拍區、熱氣球帳篷休息化妝與選片空間，以及戶外草地森林自然互動場景。適合家庭照、親子寫真、閨蜜照、個人形象照與生活感人像拍攝。拍攝完成後，免費贈送 2 小時空間停留使用，可以休息、聚餐、聊天，讓拍照變成一段完整的家庭相聚時光。")
t = add_sec(t, "三個空間，完成一場完整寫真拍攝", "雲朵帳篷作為正式棚拍空間，可拍白背景、自然光、簡約人像與家庭合照；熱氣球帳篷作為休息、化妝、換裝與現場選片空間，家人不用擠在攝影區等待；戶外草地與森林則適合拍孩子奔跑、親子互動、自然光生活感照片。這樣的配置讓拍攝不只是拍照，而是從棚拍、外景、休息到選片都能在同一個空間完成。", "寫真攝影服務說明")
t = re.sub(r'    <section class="section tight">\s*<div class="container">\s*<h2>相關拍攝關鍵字</h2>.*?</section>\s*', "", t, flags=re.S)
t = inject(t, rel([("pet-photography","寵物攝影"),("baby-party","抓周派對"),("family-party","家庭聚餐")]) + kw("#家庭照 #家庭親子寫真 #親子寫真 #家庭攝影 #人像寫真 #閨蜜照 #閨蜜寫真 #個人形象照 #個人寫真 #桃園攝影棚 #桃園家庭寫真 #自然光攝影 #白背景棚拍 #森林系寫真 #生活感寫真"))
p.write_text(t, encoding="utf-8"); print("portrait")

p = PAGES / "pet-photography.html"
t = fix_stay(p.read_text(encoding="utf-8"))
t = set_hero(t, "這裡是適合毛孩真正放鬆活動的森林系寵物攝影空間。約 200 坪室內外場地包含正式棚拍區、主人休息與選片空間，以及戶外草地森林互動場景。毛孩可以拍白背景棚拍，也可以在草地奔跑、與主人互動，拍出比一般攝影棚更自然的表情。拍攝完成後，免費贈送 2 小時空間停留使用，可聚餐、聊天、慶生或讓毛孩繼續在草地活動。")
t = add_sec(t, "棚拍、草地、休息空間一次完成", "雲朵帳篷可作為正式寵物攝影棚，適合毛孩生日照、白背景棚拍、主人與毛孩合照；熱氣球帳篷可作為主人休息、毛孩整理、等待與選片空間；戶外草地森林則適合拍狗狗奔跑、毛孩互動、主人陪伴與自然生活感畫面。對容易緊張的毛孩來說，這樣的空間會比一般小型攝影棚更容易放鬆。", "寵物攝影服務說明")
t = inject(t, rel([("pet-party","寵物聚會"),("portrait-photography","親子寫真"),("birthday-party","生日派對")]) + kw("#寵物攝影 #寵物寫真 #毛孩攝影 #狗狗攝影 #貓咪攝影 #人寵合照 #寵物家庭照 #桃園寵物攝影 #寵物友善攝影棚 #毛孩生日 #寵物棚拍 #自然風寵物攝影 #草地寵物攝影 #狗狗生日 #毛孩寫真"))
p.write_text(t, encoding="utf-8"); print("pet-photo")

cfgs = [
("birthday-party", "如果你不想只是在餐廳吃飯，Joyforest 提供約 200 坪森林系包場空間，適合生日派對、朋友聚會、家庭小慶祝與小型活動。室內可吹冷氣、唱歌、玩電動、休息與用餐；戶外可烤肉、野餐、看戶外電影、拍照與草地活動。適合 20 人內希望有隱私、不被打擾、又能自由安排流程的小型聚會。", "室內冷氣＋戶外草地，聚會不只有一張餐桌", "一般餐廳比較適合吃飯，但不一定適合聊天、活動、拍照或讓孩子與毛孩放鬆。Joyforest 的特色是室內與戶外可以一起使用，白天可以在草地拍照、野餐、烤肉，晚上可以搭配燈光、投影或夜間氣氛活動。室內帳篷則適合吹冷氣、唱歌、玩遊戲、放東西與休息。", "適合哪些聚會？", [("family-party","家庭聚餐"),("pet-party","寵物聚會"),("forest-night-experience","夜間體驗")], "#生日派對 #生日包場 #朋友聚會 #聚會場地 #桃園聚會場地 #中壢聚會 #楊梅聚會 #小型派對場地 #森林派對 #草地派對 #夜間聚會 #包場聚餐 #戶外聚會 #生日聚餐 #活動包場"),
("proposal", "Joyforest 適合想要有隱私、有場景、有儀式感的森林系求婚。戶外草地可安排紅毯、花束、燈光、投影與求婚儀式；雲朵帳篷可作為主角休息、換裝、放置物品與準備空間；熱氣球帳篷可作為求婚後的冷氣聚餐與朋友慶祝空間。適合約 20 人內的驚喜求婚、紀念日與小型慶祝活動。", "求婚不是只有佈置，而是完整流程", "一場求婚通常會需要等待、準備、儀式、拍照、慶祝與收尾。Joyforest 的空間可以分區使用：戶外草地負責求婚主場景，室內帳篷負責休息、用餐與朋友等待。求婚成功後，不需要立刻離開，可以在室內冷氣空間聚餐、聊天、播放影片或繼續拍照。", "適合的求婚形式", [("forest-wedding","森林戶外婚禮"),("birthday-party","生日派對"),("forest-night-experience","夜間體驗")], "#求婚場地 #求婚包場 #桃園求婚場地 #中壢求婚 #楊梅求婚 #戶外求婚 #森林求婚 #草地求婚 #求婚佈置 #求婚攝影 #驚喜求婚 #浪漫求婚 #求婚派對 #紀念日求婚 #小型求婚"),
("forest-wedding", "Joyforest 適合約 20 位賓客內的小型森林系婚禮與戶外證婚。戶外草地可作為證婚儀式、紅毯、拍照與親友見證區；雲朵帳篷可作為新人休息室、化妝換裝與物品放置區；熱氣球帳篷可作為儀式後的室內冷氣宴客與用餐空間。適合想要簡單、溫暖、不制式的小型婚禮或證婚儀式。", "戶外儀式＋室內冷氣宴客", "很多戶外婚禮最大的問題，是賓客沒有舒適的休息與用餐空間。Joyforest 的特色是儀式可以在戶外草地完成，儀式後可以回到室內冷氣帳篷用餐、聊天與休息。對約 20 位以內的家人好友來說，空間不會太大太空，也不會像餐廳包廂一樣缺少儀式感。", "適合的婚禮型態", [("proposal","求婚場地"),("family-party","家庭聚餐"),("portrait-photography","攝影服務")], "#戶外婚禮 #森林系婚禮 #戶外證婚 #證婚場地 #草地婚禮 #桃園婚禮場地 #中壢婚禮場地 #楊梅婚禮場地 #小型婚禮 #小型婚宴 #婚禮包場 #森林婚禮 #證婚儀式 #戶外證婚場地 #精緻婚禮"),
]
for slug, hero, st, body, before, links, tags in cfgs:
    p = PAGES / f"{slug}.html"; t = p.read_text(encoding="utf-8")
    t = set_hero(t, hero); t = add_sec(t, st, body, before)
    t = inject(t, rel(links) + kw(tags)); p.write_text(t, encoding="utf-8"); print(slug)

p = PAGES / "pet-party.html"; t = p.read_text(encoding="utf-8")
for a,b in [("或住宿","或夜間體驗"),("加購住宿","加購夜間體驗"),("加購攝影或住宿","加購攝影或夜間體驗"),("攝影／住宿／烤肉","攝影／夜間體驗／烤肉"),("<h3>住宿</h3>","<h3>夜間體驗</h3>"),("若想放慢腳步，可依日期與空房狀況加購住宿（請於預約時詢問）。","若想延長聚會氛圍，可加購夜間體驗或延長空間使用（請於預約時詢問）。"),("是否需要加購攝影或住宿","是否需要加購攝影或夜間體驗"),("唱歌或加購住宿","唱歌或加購夜間體驗"),("也可加購小巴老師寵物攝影或住宿體驗","也可加購小巴老師寵物攝影或夜間體驗")]:
    t = t.replace(a,b)
t = set_hero(t, "毛孩聚會最需要的不是漂亮裝潢，而是安全、放鬆、能活動的空間。Joyforest 提供約 200 坪森林系寵物友善包場空間，適合毛孩生日、狗狗聚會、寵物家庭聚餐與主人朋友聚會。戶外草地可讓毛孩活動與拍照，室內帳篷可吹冷氣、休息、用餐與聊天，也可加購寵物攝影或活動紀錄。")
t = add_sec(t, "毛孩能活動，主人也能聚餐", "一般餐廳或咖啡廳常常空間有限，毛孩只能坐在旁邊等待。Joyforest 的優勢是草地與室內空間可以一起使用，毛孩能在草地活動，主人能在室內或戶外用餐聊天。適合狗狗生日、毛孩聚會、人寵合照、寵物活動與小型寵物派對。", "適合這樣的毛孩聚會")
if "相關關鍵字" not in t: t = inject(t, kw("#寵物聚會 #毛孩聚會 #狗狗聚會 #寵物生日 #毛孩生日 #寵物友善場地 #桃園寵物聚會 #中壢寵物聚會 #楊梅寵物聚會 #寵物派對 #狗狗生日 #寵物包場 #寵物活動 #人寵聚會 #毛孩派對"))
p.write_text(t, encoding="utf-8"); print("pet-party")
