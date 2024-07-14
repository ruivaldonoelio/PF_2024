function toggleCollapse() {
    const collapsible = document.getElementById('participantes');
    collapsible.classList.toggle('collapsed');
}

document.addEventListener("DOMContentLoaded", function() {
        var scrollableDiv = document.getElementById("myScrollableDiv");
        scrollableDiv.scrollTop = scrollableDiv.scrollHeight;
    });