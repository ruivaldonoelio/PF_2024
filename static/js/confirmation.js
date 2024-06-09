document.addEventListener('DOMContentLoaded', (event) => {
    const inputs = document.querySelectorAll('.inputs input');

    inputs.forEach((input, index) => {
        input.addEventListener('input', (e) => {
            if (input.value.length === input.maxLength) {
                const nextInput = inputs[index + 1];
                if (nextInput) {
                    nextInput.focus();
                }
            }
        });

        input.addEventListener('keydown', (e) => {
            if (e.key === "Backspace" && input.value.length === 0) {
                const prevInput = inputs[index - 1];
                if (prevInput) {
                    prevInput.focus();
                }
            }
        });
    });
});
