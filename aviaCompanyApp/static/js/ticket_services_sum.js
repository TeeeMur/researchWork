const services_cards = document.getElementsByClassName('service-card');
const services_added_list = document.getElementsByClassName('service-added-list');
const services_sum = document.getElementById('services_sum');


for (const card of services_cards) {
    const checkbox = card.querySelector('.service-check');
    const int_service_price = parseInt(card.querySelector('.service-price').innerHTML);

    checkbox.addEventListener('change', function() {
        if (this.checked) {
            services_sum.innerHTML = (parseInt(services_sum.innerHTML) + int_service_price).toString();
        } else {
            services_sum.innerHTML = (parseInt(services_sum.innerHTML) - int_service_price).toString();
        }
    });
}