const navToggle = document.getElementById('nav-toggle');
const mainNav = document.getElementById('main-nav');

navToggle.addEventListener('click', () => {
  mainNav.classList.toggle('open');
});

document.querySelector('.newsletter-form').addEventListener('submit', (e) => {
  e.preventDefault();
  alert('Thanks for subscribing!');
  e.target.reset();
});
