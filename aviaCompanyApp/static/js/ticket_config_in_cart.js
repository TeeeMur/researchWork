const services_buttons = document.getElementsByClassName('service-btn')
const ticket_slug = document.getElementById('ticket-slug')
const services_added_list = document.getElementById('service-added-list');
const services_sum = document.getElementById('services_sum');

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');

for (const each_btn of services_buttons) {
    const service_id = each_btn.getAttribute('id');
    each_btn.addEventListener('click', function() {
        
        const clickRequest = new Request(`async_edit_service_cart/${service_id}/`, 
            {
                method: "POST",
                headers: {'X-CSRFToken': csrftoken},
                mode: 'same-origin',
            }
        );
        
        fetch(clickRequest).then(function(response) {
            response.json().then(function(data) {
                const responseString = data.response
                services_sum.innerHTML = data.ticket_price
                if (responseString == 'REMOVED') {
                    remove_from_list(services_added_list, data.service_name)
                    each_btn.innerHTML = "Добавить";
                    each_btn.classList.replace("btn-outline-primary", "btn-primary");
                } else {
                    add_to_list(services_added_list, data.service_name, data.service_price)
                    each_btn.innerHTML = "Сбросить";
                    each_btn.classList.replace("btn-primary", "btn-outline-primary");
                }
            })
        })
    })
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