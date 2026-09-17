const tg = window.Telegram.WebApp;
tg.ready();
tg.expand();
tg.setHeaderColor("#0b0d12");
tg.setBackgroundColor("#0b0d12");

const photoInput = document.getElementById("photoInput");
const preview = document.getElementById("preview");
const analyzeButton = document.getElementById("analyzeButton");
const premiumButton = document.getElementById("premiumButton");
const uploadScreen = document.getElementById("uploadScreen");
const resultScreen = document.getElementById("resultScreen");
const resultAvatar = document.getElementById("resultAvatar");
const pslScoreEl = document.getElementById("pslScore");
const pslBar = document.getElementById("pslBar");
const featuresList = document.getElementById("featuresList");
const tierBadge = document.getElementById("tierBadge");
const backButton = document.getElementById("backButton");

let currentPhotoData = null;

photoInput.addEventListener("change", function () {
    const file = photoInput.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = function (e) {
        currentPhotoData = e.target.result;
        preview.src = currentPhotoData;
        preview.style.display = "block";
    };
    reader.readAsDataURL(file);
});

analyzeButton.addEventListener("click", function () {
    if (!photoInput.files[0]) {
        tg.showAlert("Сначала выберите фотографию.");
        return;
    }

    // Пока заглушка — потом подключим сервер
    // Здесь имитируем ответ бота
    showResult({
        psl: 6.4,
        tier: "HTN",
        features: [
            { name: "Глаза", score: 6.9 },
            { name: "Нос", score: 6.3 },
            { name: "Губы", score: 6.4 },
            { name: "Скулы", score: 6.1 },
            { name: "Челюсть", score: 5.8 },
            { name: "Кожа", score: 6.7 },
            { name: "Гармония", score: 6.3 }
        ]
    });
});

premiumButton.addEventListener("click", function () {
    tg.showAlert("Полный анализ покупается через Telegram Stars в боте.");
});

backButton.addEventListener("click", function () {
    resultScreen.classList.add("hidden");
    uploadScreen.classList.remove("hidden");
});

function showResult(data) {
    uploadScreen.classList.add("hidden");
    resultScreen.classList.remove("hidden");

    resultAvatar.src = currentPhotoData;
    pslScoreEl.textContent = data.psl.toFixed(1);
    pslBar.style.width = (data.psl * 10) + "%";
    tierBadge.textContent = data.tier;

    featuresList.innerHTML = "";

    data.features.forEach((f, i) => {
        const row = document.createElement("div");
        row.className = "feature";
        row.innerHTML = `
            <div class="feature-name">${f.name}</div>
            <div class="feature-bar">
                <div class="feature-bar-fill" id="bar-${i}"></div>
            </div>
            <div class="feature-score">${f.score.toFixed(1)}</div>
        `;
        featuresList.appendChild(row);

        // Анимация полосок
        setTimeout(() => {
            document.getElementById(`bar-${i}`).style.width = (f.score * 10) + "%";
        }, 100 + i * 80);
    });
}
