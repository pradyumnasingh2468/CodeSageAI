/* ================= MATRIX CANVAS SETUP ================= */

const canvas = document.getElementById("matrixCanvas");

/* Prevent crash if canvas not present */
if (!canvas) {
    console.warn("Matrix canvas not found");
} else {

    const ctx = canvas.getContext("2d");

    /* Set canvas size */
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;


    /* ================= CONFIG ================= */

    const letters = "CODE SAGE AI PYTHON ML DATA".split("");
    const fontSize = 14;

    /* Ensure integer column count */
    let columns = Math.floor(canvas.width / fontSize);

    /* Initialize drops */
    let drops = new Array(columns).fill(1);


    /* ================= DRAW FUNCTION ================= */

    function draw() {

        /* Trail effect */
        ctx.fillStyle = "rgba(0,0,0,0.05)";
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        /* Text styling */
        ctx.fillStyle = "#00ffc8";
        ctx.font = fontSize + "px monospace";

        for (let i = 0; i < drops.length; i++) {

            const text = letters[Math.floor(Math.random() * letters.length)];

            ctx.fillText(text, i * fontSize, drops[i] * fontSize);

            /* Reset randomly after bottom */
            if (
                drops[i] * fontSize > canvas.height &&
                Math.random() > 0.975
            ) {
                drops[i] = 0;
            }

            drops[i]++;
        }
    }


    /* ================= ANIMATION ================= */

    setInterval(draw, 33); // ~30 FPS


    /* ================= RESIZE FIX ================= */

    window.addEventListener("resize", () => {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;

        columns = Math.floor(canvas.width / fontSize);
        drops = new Array(columns).fill(1);
    });

}