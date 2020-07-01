// custom javascript

let handleForm = async (event) => {
    event.preventDefault();
    let form = document.getElementById('form');
    let formData = new FormData(form);
    let object = {};
    formData.forEach((value, key) => {
        object[key] = value
    });
    console.log(object);

    let response = await fetch('/api/urls', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(object),
    });
    let data = await response.json();
    console.log(data);
    let modal = $('.modal');

    if (!response.ok) {
        modal.find('.modal-title').text('Error!');
        modal.find('.modal-body span').text(data.error);
        modal.find('.modal-body a').attr('href', '');
        modal.find('.modal-body a').text('');
        modal.find('.modal-body a').hide();
        modal.modal();
    } else {
        modal.find('.modal-title').text('Success!');
        modal.find('.modal-body span').text('Short link created @');
        modal.find('.modal-body a').attr('href', data.slug);
        modal.find('.modal-body a').text(window.location.protocol + '//' + window.location.host + '/' + data.slug);
        modal.find('.modal-body a').show();
        modal.modal();
    }
}
