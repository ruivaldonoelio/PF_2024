document.addEventListener("DOMContentLoaded", function() {
    const uploadArea1 = document.getElementById('up_doc1');
    const uploadArea2 = document.getElementById('up_doc2');
    const fileInput1 = document.getElementById('fileInput1');
    const fileInput2 = document.getElementById('fileInput2');
    const fileName1 = document.getElementById('file_name1');
    const fileName2 = document.getElementById('file_name2');
    const fileDescription1 = document.getElementById('file_description1');
    const fileDescription2 = document.getElementById('file_description2');

    function handleFileChange(input, fileNameElement, fileDescription) {
        return function(event) {
            const file = event.target.files[0];
            if (file) {
                fileNameElement.textContent = file.name;
                fileDescription.style.display = 'none';
            } else {
                fileNameElement.textContent = 'Drag file(s) here to upload.';
            }
        }
    }

    fileInput1.addEventListener('change', handleFileChange(fileInput1, fileName1, fileDescription1));
    fileInput2.addEventListener('change', handleFileChange(fileInput2, fileName2, fileDescription2));

    function handleDragOver(event) {
        event.preventDefault();
    }

    function handleDrop(input) {
        return function(event) {
            event.preventDefault();
            const files = event.dataTransfer.files;
            if (files.length > 0) {
                input.files = files;
                const changeEvent = new Event('change');
                input.dispatchEvent(changeEvent);
            }
        }
    }

    uploadArea1.addEventListener('dragover', function(event) {
        handleDragOver(event, fileDescription1);
    });
    uploadArea2.addEventListener('dragover', function(event) {
        handleDragOver(event, fileDescription2);
    });

    uploadArea1.addEventListener('drop', handleDrop(fileInput1));
    uploadArea2.addEventListener('drop', handleDrop(fileInput2));

    document.addEventListener('click', function(event) {
        const target = event.target;
        if (target.classList.contains('upload-area')) {
            const input = target.querySelector('input[type=file]');
            input.click();
        }
    });

});
