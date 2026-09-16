const tg = window.Telegram.WebApp;

tg.ready();

tg.expand();


const photoInput =
    document.getElementById("photoInput");


const preview =
    document.getElementById("preview");


const analyzeButton =
    document.getElementById("analyzeButton");


const premiumButton =
    document.getElementById("premiumButton");


const resultCard =
    document.getElementById("resultCard");


const result =
    document.getElementById("result");


photoInput.addEventListener(
    "change",
    function () {

        const file =
            photoInput.files[0];

        if (!file) {
            return;
        }

        const reader =
            new FileReader();

        reader.onload =
            function (event) {

                preview.src =
                    event.target.result;

                preview.style.display =
                    "block";

            };

        reader.readAsDataURL(file);

    }
);


analyzeButton.addEventListener(
    "click",
    function () {

        if (!photoInput.files[0]) {

            tg.showAlert(
                "Сначала выберите фотографию."
            );

            return;

        }

        tg.showAlert(
            "Загрузка фотографии будет подключена к серверу."
        );

    }
);


premiumButton.addEventListener(
    "click",
    function () {

        tg.showAlert(
            "Полный анализ приобретается через Telegram Stars."
        );

    }
);
