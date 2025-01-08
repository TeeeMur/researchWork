const services_buttons = document.getElementsByClassName('service-btn')
const services_added_list = document.getElementById('ticket-service-list')
const available_services_node = document.getElementById('available-service-list')
const main_node = document.getElementById('main-container')

const available_services_list = []

if (available_services_list.length == 0) {
    available_services_node.parentNode.removeChild(available_services_node)
    main_node.classList.remove('col-7')
    main_node.classList.add('col-12')
}

for (const each_btn of services_buttons) {
    const service_id = each_btn.getAttribute('id');
    const card_to_remove = document.getElementById(service_id + '-card');
    available_services_list.push(card_to_remove)

    each_btn.addEventListener('click', function() {
        
        const clickRequest = new Request(`async_edit_service_bought/${service_id}/`, 
            {
                method: "POST",
                headers: {'X-CSRFToken': csrftoken},
                mode: 'same-origin',
            }
        );

        fetch(clickRequest).then(function(response) {
            response.json().then(function(data) {
                add_to_list(services_added_list, data.service_name)
                const index = available_services_list.indexOf(card_to_remove);
                if (index > -1) { 
                    available_services_list.splice(index, 1);
                }
                card_to_remove.parentNode.removeChild(card_to_remove)
                if (available_services_list.length == 0) {
                    available_services_node.parentNode.removeChild(available_services_node)
                    main_node.classList.remove('col-7')
                    main_node.classList.add('col-12')
                }
            })
        })
    })
}

function add_to_list(list_to_add, service_name) {
    var item_to_add = document.createElement("li");
    item_to_add.setAttribute("id", service_name + "-list-item");
    item_to_add.setAttribute("class", "fs-5");
    item_to_add.appendChild(document.createTextNode(service_name.toString()));
    list_to_add.appendChild(item_to_add);
}

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