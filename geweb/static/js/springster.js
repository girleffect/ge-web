import "../styles/springster.scss";

// SECTION CLASS NAMES
const sectionAnchor = document.querySelectorAll('.nav-list__anchor')

sectionAnchor.forEach(element => {
    element.classList.add('nav-list__' + element.innerText.toLowerCase().replace(' ', '-'));
    console.log(element)
});