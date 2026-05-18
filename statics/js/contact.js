document.addEventListener("DOMContentLoaded", function () {

    const form = document.querySelector("form");

    if (form) {
        const btn = form.querySelector("button");

        form.addEventListener("submit", () => {
            btn.textContent = "Sending...";
            btn.disabled = true;
        });
    }

});