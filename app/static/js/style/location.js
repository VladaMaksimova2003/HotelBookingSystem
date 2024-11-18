function updateCities() {
    // Получаем название страны, введенное пользователем
    const countryName = document.getElementById("country").value;
    
    // Находим элемент <option> с соответствующим значением
    const selectedOption = Array.from(document.querySelectorAll("#countries option"))
        .find(option => option.value === countryName);

    if (selectedOption) {
        // Получаем ID страны из data-id атрибута
        const countryId = selectedOption.getAttribute("data-id");

        // Очистка списка городов
        const cityDatalist = document.getElementById("cities");
        cityDatalist.innerHTML = '';

        // Отправка запроса для загрузки городов по countryId
        fetch(`/hotel/get_cities_by_country/${countryId}`)
            .then(response => response.json())
            .then(data => {
                data.cities.forEach(city => {
                    const option = document.createElement("option");
                    option.value = city.name;
                    cityDatalist.appendChild(option);
                });
            })
            .catch(error => console.error('Ошибка загрузки городов:', error));
    } else {
        console.error('Страна не найдена в списке.');
    }
}