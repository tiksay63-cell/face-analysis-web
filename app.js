const tg = window.Telegram.WebApp;
tg.ready();
tg.expand();
tg.setHeaderColor("#0b0d12");
tg.setBackgroundColor("#0b0d12");

// ========== ВСТАВЬ СВОЮ ССЫЛКУ API ==========
// Пример: если домен https://face-analysis-web-production-abcd.up.railway.app
// то пиши так:
const API_URL = "https://face-analysis-web-production.up.railway.app/analyze";
// ============================================

const photoInput = document.getElementById("photoInput");
const preview = document.getElementById("preview");
const analyzeBtn = document.getElementById("analyzeBtn");
const premiumBtn = document.getElementById("premiumBtn");
const uploadScreen = document.getElementById("uploadScreen");
const resultScreen = document.getElementById("resultScreen");
const resultAvatar = document.getElementById("resultAvatar");
const pslNum = document.getElementById("pslNum");
const pslFill = document.getElementById("pslFill");
const featuresEl = document.getElementById("features");
const backBtn = document.getElementById("backBtn");

let photoData = null;
let photoFile = null;

photoInput.addEventListener("change", () => {
  const file = photoInput.files[0];
  if (!file) return;
  photoFile = file;
  const reader = new FileReader();
  reader.onload = e => {
    photoData = e.target.result;
    preview.src = photoData;
    preview.style.display = "block";
  };
  reader.readAsDataURL(file);
});

analyzeBtn.addEventListener("click", async () => {
  if (!photoFile) {
    tg.showAlert("Сначала выбери фото");
    return;
  }

  analyzeBtn.disabled = true;
  analyzeBtn.textContent = "Анализ...";

  try {
    const form = new FormData();
    form.append("file", photoFile);

    const res = await fetch(API_URL, { method: "POST", body: form });
    if (!res.ok) {
      const err = await res.text();
      throw new Error(err || "Ошибка сервера");
    }
    const data = await res.json();
    showResult(data);
  } catch (e) {
    console.error(e);
    tg.showAlert("Ошибка: " + String(e.message || e));
  } finally {
    analyzeBtn.disabled = false;
    analyzeBtn.textContent = "Анализировать";
  }
});

premiumBtn.addEventListener("click", () => {
  tg.showAlert("Полный анализ — в боте за 100 Stars");
});

backBtn.addEventListener("click", () => {
  resultScreen.classList.add("hidden");
  uploadScreen.classList.remove("hidden");
});

function showResult(data) {
  uploadScreen.classList.add("hidden");
  resultScreen.classList.remove("hidden");

  resultAvatar.src = photoData;
  const psl = Number(data.psl) || 5;
  pslNum.textContent = psl.toFixed(1);
  pslFill.style.width = Math.min(100, psl * 10) + "%";

  const tier = data.tier || "MTN";
  document.querySelectorAll(".tiers span").forEach(el => {
    el.classList.toggle("active", el.dataset.t === tier);
  });

  featuresEl.innerHTML = "";
  (data.features || []).forEach((f, i) => {
    const score = Number(f.score) || 5;
    const row = document.createElement("div");
    row.className = "feature";
    row.innerHTML = `
      <div class="f-name">${f.name}</div>
      <div class="f-bar"><div class="f-fill" id="b${i}"></div></div>
      <div class="f-score">${score.toFixed(1)}</div>
    `;
    featuresEl.appendChild(row);
    setTimeout(() => {
      const el = document.getElementById("b" + i);
      if (el) el.style.width = Math.min(100, score * 10) + "%";
    }, 80 + i * 70);
  });
}
