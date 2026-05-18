/* ================= SETTINGS PAGE SCRIPT ================= */

document.addEventListener("DOMContentLoaded", function () {

    /* ================= DELETE CONFIRMATION ================= */

    const input = document.getElementById("confirmInput");
    const deleteBtn = document.getElementById("deleteBtn");

    if (input && deleteBtn) {

        // Auto uppercase + enable button only if DELETE
        input.addEventListener("input", function () {
            input.value = input.value.toUpperCase();

            if (input.value.trim() === "DELETE") {
                deleteBtn.disabled = false;
                deleteBtn.classList.add("active");
            } else {
                deleteBtn.disabled = true;
                deleteBtn.classList.remove("active");
            }
        });

        // Final confirmation popup
        deleteBtn.addEventListener("click", function (e) {
            const confirmDelete = confirm(
                "Are you sure you want to delete your account? This cannot be undone."
            );

            if (!confirmDelete) {
                e.preventDefault();
            }
        });
    }


    /* ================= AUTO HIDE DJANGO MESSAGES ================= */

    const msg = document.querySelector(".message");

    if (msg) {
        setTimeout(() => {
            msg.style.transition = "0.5s";
            msg.style.opacity = "0";

            setTimeout(() => {
                msg.remove();
            }, 500);
        }, 3000);
    }


    /* ================= SMART SAVE BUTTON ================= */

    const form = document.querySelector(".settings-form");

    if (form) {
        const saveBtn = form.querySelector("button[type='submit']");

        // Store initial form data
        const initialData = new FormData(form);

        // Disable button initially
        saveBtn.disabled = true;

        form.addEventListener("input", () => {
            const currentData = new FormData(form);

            let changed = false;

            for (let [key, value] of currentData.entries()) {
                if (value !== initialData.get(key)) {
                    changed = true;
                    break;
                }
            }

            saveBtn.disabled = !changed;
        });


        /* ================= FORM VALIDATION ================= */

        form.addEventListener("submit", function (e) {

            const email = form.querySelector("input[name='email']").value;

            if (!email.includes("@")) {
                alert("Please enter a valid email address");
                e.preventDefault();
                return;
            }

            // Prevent double submit
            saveBtn.disabled = true;
            saveBtn.textContent = "Saving...";
        });
    }


    /* ================= INPUT FOCUS EFFECT ================= */

    document.querySelectorAll("input, select").forEach(el => {

        el.addEventListener("focus", () => {
            el.style.transform = "scale(1.01)";
        });

        el.addEventListener("blur", () => {
            el.style.transform = "scale(1)";
        });

    });

});