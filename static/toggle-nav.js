icon = document.querySelector('.map-icon');
navbar = document.querySelector('.navbar');

icon.addEventListener('click', () => {
    if (navbar.style.display === 'none' || navbar.style.display === '') {
        navbar.style.display = 'flex';
    } else {
        navbar.style.display = 'none';
    }
});