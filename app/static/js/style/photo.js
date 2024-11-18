// Функция для сбора данных об удаляемой фотографии
function collectPhotoData(photoUrl) {
    const data = {
        id: Id,
        photo_url: photoUrl
    };
    return data;
}


// Функция для получения маршрута в зависимости от типа фотографии
function getDeletePhotoUrl() {
    if (photoType === 'room') {
        return '/hotel/room/delete/photo';
    } else if (photoType === 'hotel') {
        return '/hotel/delete/photo';
    } else {
        console.error('Unknown photo type');
        return null;
    }
}

// Функция для отправки данных о фото на сервер и удаления из интерфейса
function sendPhotoData(photoUrl, photoElement) {
    const data = collectPhotoData(photoUrl);
    const url = getDeletePhotoUrl();
    console.log(url)
    console.log(data)
    if (!url) return;
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
        .then(response => {
            if (!response.ok) {
                return response.json().then(error => {
                    throw new Error(error.error || 'Unknown error');
                });
            }
            return response.json();
        })
        .then(jsonResponse => {
            console.log("Response data:", jsonResponse);
            // Удаляем фото из интерфейса после успешного ответа
            photoElement.remove();
        })
        .catch(error => {
            console.error("Error:", error);
            alert("Ошибка при удалении фотографии. Пожалуйста, попробуйте снова.");
        });
}