const services_cards = document.getElementsByClassName('service-card');
const services_sum_list = document.getElementsByClassName('service-added-list');
const add_lug_element = document.getElementById('add_lug')
if (add_lug_element.checked) {
    
}


for (const card of services_cards) {
    const checkbox = card.querySelector('.service-check');
    const service_price = card.querySelector('.service-price').innerHTML;

    checkbox.addEventListener('change', function() {
        if (this.checked) {
            alert("YES" + service_price);
        } else {
            alert("NO");
        }
    });
}