const tg = window.Telegram.WebApp;
tg.ready();
tg.expand();
tg.setHeaderColor("#0b0d12");
tg.setBackgroundColor("#0b0d12");

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

function tierFromPSL(psl) {
  if (psl <= 3.0) return "Sub3";
  if (psl <= 4.5) return "Sub5";
  if (psl <= 5.5) return "LTN";
  if (psl <= 6.4) return "MTN";
  if (psl <= 7.2) return "HTN";
  if (psl <= 7.9) return "Chadlite";
  if (psl <= 8.9) return "Chad";
  return "Gigachad";
}

photoInput.addEventListener("change", () => {
  const file = photoInput.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = e => {
    photoData = e.target.result;
    preview.src = photoData;
    preview.style.display = "block";
  };
  reader.readAsDataURL(file);
});

analyzeBtn.addEventListener("click", () => {
  if (!photoInput.files[0]) {
    tg.showAlert("Сначала выбери фото");
    return;
  }

  // Заглушка результата (потом подключим сервер)
  // Имитируем ответ в стиле бота
  const mock = {
    psl: 6.4,
    features: [
      { name: "Глаза", score: 6.9 },
      { name: "Нос", score: 6.3 },
      { name: "Губы", score: 6.4 },
      { name: "Скулы", score: 6.1 },
      { name: "Челюсть", score: 5.8 },
      { name: "Кожа", score: 6.7 },
      { name: "Гармония", score: 6.3 }
    ]
  };
  showResult(mock);
});

premiumBtn.addEventListener("click", () => {
  tg.showAlert("Полный анализ покупается через Stars в боте");
});

backBtn.addEventListener("click", () => {
  resultScreen.classList.add("hidden");
  uploadScreen.classList.remove("hidden");
});

function showResult(data) {
  uploadScreen.classList.add("hidden");
  resultScreen.classList.remove("hidden");

  resultAvatar.src = photoData;
  pslNum.textContent = data.psl.toFixed(1);
  pslFill.style.width = (data.psl * 10) + "%";

  const tier = tierFromPSL(data.psl);
  document.querySelectorAll(".tiers span").forEach(el => {
    el.classList.toggle("active", el.dataset.t === tier);
  });

  featuresEl.innerHTML = "";
  data.features.forEach((f, i) => {
    const row = document.createElement("div");
    row.className = "feature";
    row.innerHTML = `
      <div class="f-name">${f.name}</div>
      <div class="f-bar"><div class="f-fill" id="b${i}"></div></div>
      <div class="f-score">${f.score.toFixed(1)}</div>
    `;
    featuresEl.appendChild(row);
    setTimeout(() => {
      document.getElementById("b" + i).style.width = (f.score * 10) + "%";
    }, 80 + i * 70);
  });
}
