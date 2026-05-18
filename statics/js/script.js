/* ================= MATRIX CANVAS SETUP ================= */

const canvas = document.getElementById("matrixCanvas");

/* Safety check (prevents crash if canvas not found) */
if (!canvas) {
    console.warn("Matrix canvas not found");
} else {

    const ctx = canvas.getContext("2d");

    /* Set initial canvas size */
    canvas.height = window.innerHeight;
    canvas.width = window.innerWidth;


    /* ================= MATRIX CONFIG ================= */

    const letters = "CODE SAGE AI 101010 PYTHON ML DATA".split("");
    const fontSize = 14;

    /* Number of columns based on screen width */
    let columns = Math.floor(canvas.width / fontSize);

    /* Track drop positions */
    let drops = new Array(columns).fill(1);


    /* ================= DRAW FUNCTION ================= */

    function drawMatrix() {

        /* Fade effect (creates trailing effect) */
        ctx.fillStyle = "rgba(0, 0, 0, 0.05)";
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        /* Text styling */
        ctx.fillStyle = "#00ffc8";
        ctx.font = fontSize + "px monospace";

        /* Draw falling characters */
        for (let i = 0; i < drops.length; i++) {

            const text = letters[Math.floor(Math.random() * letters.length)];

            ctx.fillText(text, i * fontSize, drops[i] * fontSize);

            /* Reset drop randomly after reaching bottom */
            if (
                drops[i] * fontSize > canvas.height &&
                Math.random() > 0.975
            ) {
                drops[i] = 0;
            }

            /* Move drop downward */
            drops[i]++;
        }
    }


    /* ================= ANIMATION LOOP ================= */

    setInterval(drawMatrix, 33); // ~30 FPS


    /* ================= RESIZE HANDLER ================= */

    /* Adjust canvas on window resize */
    window.addEventListener("resize", () => {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;

        columns = Math.floor(canvas.width / fontSize);
        drops = new Array(columns).fill(1);
    });

}