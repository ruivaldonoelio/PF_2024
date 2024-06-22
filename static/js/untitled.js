document.getElementById("toggleButton").addEventListener("click", function() {
    var icon = document.getElementById("toggleIcon");
    if (icon.classList.contains("fa-angle-down")) {
        icon.classList.remove("fa-angle-down");
        icon.classList.add("fa-angle-up");
    } else {
        icon.classList.remove("fa-angle-up");
        icon.classList.add("fa-angle-down");
    }
});

document.getElementById("toggleButton-1").addEventListener("click", function() {
    var icon = document.getElementById("ttoggleIcon-1");
    if (icon.classList.contains("fa-angle-down")) {
        icon.classList.remove("fa-angle-down");
        icon.classList.add("fa-angle-up");
    } else {
        icon.classList.remove("fa-angle-up");
        icon.classList.add("fa-angle-down");
    }
});

document.getElementById("toggleButton-2").addEventListener("click", function() {
    var icon = document.getElementById("toggleIcon-2");
    if (icon.classList.contains("fa-angle-down")) {
        icon.classList.remove("fa-angle-down");
        icon.classList.add("fa-angle-up");
    } else {
        icon.classList.remove("fa-angle-up");
        icon.classList.add("fa-angle-down");
    }
});
