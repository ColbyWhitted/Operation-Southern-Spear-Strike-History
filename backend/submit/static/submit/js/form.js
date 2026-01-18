document.getElementById('existing-strike-wrap').addEventListener('change', function() {
    const strikeListDiv = document.getElementById('strike-list-wrap');
    const dateWrapDiv = document.getElementById('date-wrap');

    if (this.value === 'existing') {
        strikeListDiv.style.display = 'block';
        dateWrapDiv.style.display = 'none';
        console.log("Existing strike selected");
    } else {
        strikeListDiv.style.display = 'none';
        dateWrapDiv.style.display = 'block';
        console.log("New strike selected");
    }
});

console.log("form.js loaded");