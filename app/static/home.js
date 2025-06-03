document.addEventListener("DOMContentLoaded", function () {
    $('#fileSelect').select2({
        placeholder: 'Изберете файл...',
        ajax: {
            url: '/get-file-options',
            dataType: 'json',
            delay: 250,
            data: function (params) {
                return {
                    q: params.term
                };
            },
            processResults: function (data) {
                return {
                    results: data.map(item => ({
                        id: item.id,
                        text: item.text
                    }))
                };
            },
            cache: true
        },
        minimumInputLength: 1
    });
});

