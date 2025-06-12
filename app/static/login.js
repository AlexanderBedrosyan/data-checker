let generatedCaptcha = "";

function getRandomInt(min, max) {
    return Math.floor(Math.random() * (max - min) + min);
}

function generateCaptcha() {
    const canvas = document.getElementById("captchaCanvas");
    const ctx = canvas.getContext("2d");

    const chars = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghjkmnpqrstuvwxyz23456789";
    generatedCaptcha = Array.from({length: 4}, () => chars[Math.floor(Math.random() * chars.length)]).join("");

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    for (let i = 0; i < 5; i++) {
        ctx.strokeStyle = `rgba(${getRandomInt(0, 255)}, ${getRandomInt(0, 255)}, ${getRandomInt(0, 255)}, 0.5)`;
        ctx.beginPath();
        ctx.moveTo(getRandomInt(0, canvas.width), getRandomInt(0, canvas.height));
        ctx.lineTo(getRandomInt(0, canvas.width), getRandomInt(0, canvas.height));
        ctx.stroke();
    }

    for (let i = 0; i < 50; i++) {
        ctx.fillStyle = `rgba(${getRandomInt(0, 255)}, ${getRandomInt(0, 255)}, ${getRandomInt(0, 255)}, 0.3)`;
        ctx.beginPath();
        ctx.arc(getRandomInt(0, canvas.width), getRandomInt(0, canvas.height), 1.5, 0, 2 * Math.PI);
        ctx.fill();
    }

    for (let i = 0; i < generatedCaptcha.length; i++) {
        const char = generatedCaptcha[i];
        const x = 10 + i * 20;
        const y = getRandomInt(25, 35);
        const angle = getRandomInt(-25, 25) * Math.PI / 180;

        ctx.save();
        ctx.translate(x, y);
        ctx.rotate(angle);
        ctx.font = `${getRandomInt(20, 28)}px Arial`;
        ctx.fillStyle = `rgb(${getRandomInt(50, 200)}, ${getRandomInt(50, 200)}, ${getRandomInt(50, 200)})`;
        ctx.fillText(char, 0, 0);
        ctx.restore();
    }

    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    fetch("/set-captcha", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken
        },
        body: JSON.stringify({captcha: generatedCaptcha})
    }).then(res => {
        if (!res.ok) {
            console.error("CAPTCHA send failed");
        }
    });
}

window.onload = generateCaptcha;