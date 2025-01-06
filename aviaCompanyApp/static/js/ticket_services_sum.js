const services_cards = document.getElementsByClassName('service-card');
const services_added_list = document.getElementById('service-added-list');
const services_sum = document.getElementById('services_sum');
const add_lug_service = document.getElementById('Дополнительный багаж')

for (const card of services_cards) {
    const checkbox = card.querySelector('.service-check');
    const int_service_price = parseInt(card.querySelector('.service-price').innerHTML);
    const service_name = card.querySelector('.service-name').innerHTML

    if (checkbox.checked) {
        services_sum.innerHTML = (parseInt(services_sum.innerHTML) + int_service_price).toString();
        add_to_list(services_added_list, service_name, int_service_price);
    }

    checkbox.addEventListener('change', function() {
        if (this.checked) {
            services_sum.innerHTML = (parseInt(services_sum.innerHTML) + int_service_price).toString();
            add_to_list(services_added_list, service_name, int_service_price);
        } else {
            services_sum.innerHTML = (parseInt(services_sum.innerHTML) - int_service_price).toString();
            remove_from_list(services_added_list, service_name);
        }
    });
}

function add_to_list(list_to_add, service_name, service_price) {
    var item_to_add = document.createElement("li");
    item_to_add.setAttribute("id", service_name + "-list-item");
    item_to_add.setAttribute("class", "w-100 d-inline-flex justify-content-between");
    var name = document.createElement("div");
    name.appendChild(document.createTextNode(service_name.toString()));
    var price = document.createElement("div");
    price.appendChild(document.createTextNode(service_price.toString()));
    item_to_add.appendChild(name);
    item_to_add.appendChild(price);
    list_to_add.appendChild(item_to_add);
}

function remove_from_list(list_to_remove, service_name) {
    const item_to_remove = document.getElementById(service_name + "-list-item")
    list_to_remove.removeChild(item_to_remove)
}