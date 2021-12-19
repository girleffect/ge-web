import "../styles/springster/springster.scss";

// SECTION CLASS NAMES THEME
const sectionAnchor = document.querySelectorAll('.nav-list__anchor')
sectionAnchor.forEach(element => {
    element.classList.add('nav-list__' + element.innerText.toLowerCase().replace(' ', '-'));
});