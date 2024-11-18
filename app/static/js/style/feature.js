// Функция для загрузки удобств в зависимости от выбранного типарпнннннннннннннн
function updateFeatures(typeInput) {
    const featureGroup = typeInput.closest('.feature-group');
    const featureInput = featureGroup.querySelector('.feature-input');
    const selectedType = typeInput.value.trim();
    const featuresData = JSON.parse(document.getElementById('feature-data-container').dataset.features);

    const datalistId = `feature-values-${Array.from(document.querySelectorAll('.feature-group')).indexOf(featureGroup) + 1}`;
    let featureDatalist = featureGroup.querySelector('datalist');

    // Если datalist не существует, создаем его
    if (!featureDatalist) {
        featureDatalist = document.createElement('datalist');
        featureDatalist.id = datalistId;
        featureGroup.appendChild(featureDatalist);
    }

    // Не очищаем datalist, а только добавляем новые значения
    const existingOptions = new Set();
    featureDatalist.querySelectorAll('option').forEach(option => {
        existingOptions.add(option.value);
    });

    // Заполняем datalist, если тип существует в данных
    if (featuresData[selectedType]) {
        featuresData[selectedType].forEach(feature => {
            // Добавляем только новые значения, которые еще не присутствуют
            if (!existingOptions.has(feature)) {
                const option = document.createElement('option');
                option.value = feature;
                featureDatalist.appendChild(option);
            }
        });
    }

    featureInput.setAttribute('list', datalistId);
}



// Добавляем обработчики событий для полей типа удобства
document.querySelectorAll('.feature-type-input').forEach(input => {
    input.addEventListener('focus', (event) => {
        updateFeatures(event.target); // Обновляем datalist при каждом фокусе
    });
});

// Функция добавления новой группы для типа удобства и удобств
function addFeatureGroup() {
    const featureGroupContainer = document.getElementById('feature-group-container');
    const featureGroup = createFeatureGroup();
    featureGroupContainer.appendChild(featureGroup);
}

// В функции создания группы добавьте токен CSRF
function createFeatureGroup() {
    const featureGroup = document.createElement('div');
    featureGroup.className = 'feature-group mb-3';

    // Динамическое создание datalist
    const featureGroups = document.querySelectorAll('.feature-group');
    const datalistId = `feature-values-${featureGroups.length + 1}`;
    const featureValuesDatalist = document.createElement('datalist');
    featureValuesDatalist.id = datalistId;
    featureGroup.appendChild(featureValuesDatalist);

    // Поля для типа и удобств
    const newFeatureTypeGroup = createFeatureTypeGroup(datalistId);
    featureGroup.appendChild(newFeatureTypeGroup);

    const featureInputGroup = createFeatureInputGroup(featureGroup, datalistId);
    featureGroup.appendChild(featureInputGroup);

    const hr = createSeparator();
    featureGroup.appendChild(hr);

    return featureGroup;
}


// Создание группы для типа удобства
function createFeatureTypeGroup() {
    const newFeatureTypeGroup = document.createElement('div');
    newFeatureTypeGroup.className = 'input-group mb-3';

    const newFeatureTypeInput = createFeatureTypeInput();
    // newFeatureTypeInput.setAttribute('onchange', 'loadFeatures(this.id, "features")');
    newFeatureTypeGroup.appendChild(newFeatureTypeInput);

    const removeGroupButton = createRemoveGroupButton();
    newFeatureTypeGroup.appendChild(removeGroupButton);

    return newFeatureTypeGroup;
}

// Создание поля для типа удобства 
function createFeatureTypeInput(datalistId) {
    const input = document.createElement('input');
    input.type = 'text';
    input.className = 'form-control feature-type-input';
    input.placeholder = 'Введите тип удобств';
    input.setAttribute('list', 'feature-types');
    input.autocomplete = 'off';

    // Добавляем обработчик события для обновления списка значений
    input.addEventListener('input', function() {
        updateFeatures(this); // Передаем текущий input в updateFeatures
    });

    return input;
}
// Кнопка удаления группы удобств
function createRemoveGroupButton() {
    const button = document.createElement('button');
    button.className = 'btn btn-outline-danger';
    button.type = 'button';
    button.innerText = '-';
    button.onclick = (event) => {
        const featureGroup = event.target.closest('.feature-group');
        featureGroup.remove();
    };
    return button;
}

// Создание группы для удобств
function createFeatureInputGroup(featureGroup, datalistId) {
    const featureInputGroup = document.createElement('div');
    featureInputGroup.className = 'input-group mb-3';

    const newFeatureInput = createFeatureInput(datalistId);
    featureInputGroup.appendChild(newFeatureInput);

    const addFeatureButton = createAddFeatureButton(featureGroup);
    featureInputGroup.appendChild(addFeatureButton);

    return featureInputGroup;
}


// Поле для удобства
// Функция для создания input с уникальным datalist
function createFeatureInput(datalistId) {

    const input = document.createElement('input');
    input.type = 'text';
    input.className = 'form-control feature-input';
    input.placeholder = 'Введите удобство';
    input.setAttribute('list', datalistId); // Используем переданный ID
    input.autocomplete = 'off';
    
    input.addEventListener('input', function() {
        updateFeatures(input); // Передаём конкретный input для обновления его datalist
    });

    return input;
}




// Кнопка добавления поля для нового удобства
function createAddFeatureButton(featureGroup) {
    const button = document.createElement('button');
    button.className = 'btn btn-outline-secondary';
    button.type = 'button';
    button.innerText = '+';
    button.onclick = () => addExtraFeatureInput(featureGroup);
    return button;
}

// Добавление нового поля для удобства
function addExtraFeatureInput(featureGroup) {
    const datalist = featureGroup.querySelector('datalist');
    const datalistId = datalist ? datalist.id : null; // Получаем ID существующего datalist

    const extraFeatureInputGroup = document.createElement('div');
    extraFeatureInputGroup.className = 'input-group mb-3';

    const extraFeatureInput = createFeatureInput(datalistId); // Передаём ID datalist
    extraFeatureInputGroup.appendChild(extraFeatureInput);

    const removeFeatureButton = createRemoveFeatureButton(extraFeatureInputGroup);
    extraFeatureInputGroup.appendChild(removeFeatureButton);

    const hr = featureGroup.querySelector('hr');
    featureGroup.insertBefore(extraFeatureInputGroup, hr);
}


// Кнопка для удаления поля удобства
function createRemoveFeatureButton(extraFeatureInputGroup) {
    const button = document.createElement('button');
    button.className = 'btn btn-outline-danger';
    button.type = 'button';
    button.innerText = '-';
    button.onclick = () => {
        extraFeatureInputGroup.remove();
    };
    return button;
}

// Разделитель между группами удобств
function createSeparator() {
    const hr = document.createElement('hr');
    hr.className = 'my-4';
    return hr;
}

// Функция для сбора всех значений с полей типа удобства и удобств
function collectFeatureValues() {
    const featureGroups = document.querySelectorAll('.feature-group');
    const featuresByType = [];

    featureGroups.forEach(group => {
        const typeInput = group.querySelector('.feature-type-input');
        const featureInputs = group.querySelectorAll('.feature-input'); 
        const datalist = group.querySelector('datalist'); // Получаем datalist из группы

        if (typeInput) {
            const type = typeInput.value;
            const features = Array.from(featureInputs).map(input => input.value);

            // Добавляем удобства в datalist
            features.forEach(feature => {
                if (feature) {
                    const option = document.createElement('option');
                    option.value = feature;
                    datalist.appendChild(option); // Добавляем опцию в datalist
                }
            });

            featuresByType.push({ type, features });
        } else {
            console.warn("Отсутствует поле типа удобства в одной из групп");
        }
    });

    return featuresByType;
}


function prepareFeaturesJson() {
    const featuresByType = collectFeatureValues(); // Собираем данные
    const featuresJsonField = document.querySelector('input[name="features_json"]');
    featuresJsonField.value = JSON.stringify(featuresByType);
}

// Функция для вывода значений в консоль
function logFeatureValues() {
    const featuresByType = collectFeatureValues();
    console.log("Удобства по типам:", featuresByType);
}

// Проверка заполненности полей типа и вывод предупреждения
function validateFeatureTypes(event) {
    const featureGroups = document.querySelectorAll('.feature-group');
    let hasEmptyType = false;

    featureGroups.forEach(group => {
        const typeInput = group.querySelector('.feature-type-input');
        if (!typeInput.value.trim()) {
            hasEmptyType = true;
            // alert("Заполните поле типа удобства.");
        }
    });

    if (hasEmptyType) {
        event.preventDefault();
        console.log("Отправка формы отменена из-за пустого поля типа удобства.");
    }
}

// Функция для логирования значений и подготовки JSON
function prepareAndConfirmSubmission(event) {
    logFeatureValues(); // Выводим значения в консоль
    prepareFeaturesJson(); // Подготавливаем JSON
    validateFeatureTypes();
    // Запрос подтверждения у пользователя
    const confirmSubmit = confirm("Вы уверены, что хотите отправить форму с этими данными?");
    
    if (!confirmSubmit) {
        // Если пользователь нажал "Отмена", предотвратить отправку формы
        event.preventDefault();
        console.log("Отправка формы отменена пользователем.");
    } else {
        console.log("Форма отправлена.");
    }
}

// Привязываем обработчик к кнопке отправки
document.querySelector('.btn.btn-primary').addEventListener('click', prepareAndConfirmSubmission);

// Добавляем обработчики событий для полей типа удобства
document.querySelectorAll('.feature-type-input').forEach(input => {
    input.addEventListener('input', prepareFeaturesJson);
});







// Удаление группы удобств
function removeFeatureGroup(button) {
    const featureGroup = button.closest('.feature-group');
    featureGroup.remove();
}

// Функция удаления поля удобства
function removeFeatureInput(button) {
    const featureInputGroup = button.closest('.input-group');
    featureInputGroup.remove();
}

// Функция добавления нового поля удобства
function addFeatureInput(featureGroup) {
    const datalist = featureGroup.querySelector('datalist');
    const datalistId = datalist ? datalist.id : null;

    const extraFeatureInputGroup = document.createElement('div');
    extraFeatureInputGroup.className = 'input-group mb-3';

    const extraFeatureInput = createFeatureInput(datalistId);
    extraFeatureInputGroup.appendChild(extraFeatureInput);

    const removeFeatureButton = createRemoveFeatureButton(extraFeatureInputGroup);
    extraFeatureInputGroup.appendChild(removeFeatureButton);

    const hr = featureGroup.querySelector('hr');
    featureGroup.insertBefore(extraFeatureInputGroup, hr);
}

