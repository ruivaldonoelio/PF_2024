// upload.js
function handleDragOver(event) {
    event.preventDefault();
    event.stopPropagation();
}

function handleFileDrop(event, fileNumber) {
    event.preventDefault();
    event.stopPropagation();

    const file = event.dataTransfer.files[0];
    const fileName = file.name;
    document.getElementById('file_name' + fileNumber).textContent = fileName;
    document.getElementById('fileInput' + fileNumber).files = event.dataTransfer.files;
    document.querySelector('upload-area-description' + fileNumber).style('display', 'none');
}

function updateFileName(fileNumber) {
    const input = document.getElementById('fileInput' + fileNumber);
    const fileName = input.files[0].name;
    document.getElementById('file_name' + fileNumber).textContent = fileName;
    document.querySelector('upload-area-description' + fileNumber).style('display', 'none');
}
