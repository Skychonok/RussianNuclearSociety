document.addEventListener("DOMContentLoaded", function() {
    if (typeof tinymce !== 'undefined') {
        tinymce.init({
            selector: 'textarea[name="content"], textarea[name="description"]',
            height: 500,
            plugins: 'advlist autolink lists link image charmap preview anchor searchreplace visualblocks code fullscreen insertdatetime media table help wordcount',
            toolbar: 'undo redo | blocks | bold italic | alignleft aligncenter alignright | bullist numlist outdent indent | link image media | code preview',
            language: 'ru',
            branding: false
        });
    }
});