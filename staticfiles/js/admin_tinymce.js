document.addEventListener("DOMContentLoaded", function() {
    if (typeof tinymce !== 'undefined') {
        tinymce.init({
            selector: 'textarea[name="content"], textarea[name="description"]',
            height: 500,
            plugins: 'advlist autolink lists link image charmap preview anchor searchreplace visualblocks code fullscreen insertdatetime media table help wordcount template noneditable',
            toolbar: 'undo redo | blocks | bold italic | alignleft aligncenter alignright | bullist numlist outdent indent | link image media | template | code preview',
            language: 'ru',
            language_url: 'https://cdn.jsdelivr.net/npm/tinymce-i18n@23.10.9/langs6/ru.js',
            branding: false,
            content_css: [
                'https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css',
                'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css',
                '/static/css/base_style.css',
                '/static/css/theme-light.css'
            ],
            body_class: 'content-richtext',
            templates: [
                {
                    title: 'Блок "Событие"',
                    description: 'Карточка с фоном как на странице мероприятий',
                    content: '<div class="card-event shadow-sm mb-4 p-4 rounded-4" style="background-color: var(--event-bg, #312c49);"><h3 class="fw-bold">Заголовок события</h3><div class="mt-3 opacity-90 content-richtext"><p>Описание события...</p></div></div>'
                },
                {
                    title: 'Блок "Образование"',
                    description: 'Карточка с иконкой и кнопкой',
                    content: '<div class="card-event shadow-sm h-100 p-4 p-md-5 rounded-4 text-center transition-hover d-flex flex-column" style="background-color: var(--event-bg, #312c49);"><i class="fas fa-university fa-3x mb-4 opacity-50"></i><h3 class="fw-bold mb-3">Заголовок</h3><p class="opacity-75 mb-4">Описание...</p><a href="#" class="btn btn-outline-custom-light mt-auto mx-auto px-4" style="border-radius: 8px; width: fit-content;">Подробнее</a></div>'
                },
                {
                    title: 'Сетка из 2 колонок',
                    description: 'Две колонки для контента',
                    content: '<div class="row g-4 mb-5 mceNonEditable"><div class="col-md-6"><div class="mceEditable"><p>Контент левой колонки</p></div></div><div class="col-md-6"><div class="mceEditable"><p>Контент правой колонки</p></div></div></div>'
                },
                {
                    title: 'Блок "История/Тенденции"',
                    description: 'Широкий блок с текстом',
                    content: '<div class="card-event shadow-sm mb-4 p-4 p-md-5 rounded-4" style="background-color: var(--event-bg, #312c49);"><h3 class="fw-bold mb-3">Заголовок</h3><p class="mb-0 opacity-90 lh-lg">Текст...</p></div>'
                }
            ]
        });
    }
});