import "../styles/yegna/yegna.scss";


/**
 * Header search from toggle 
 */
const searchToggle = document.getElementById('search'),
    searchBarDropdown = document.getElementById('searchBar')

    searchBarDropdown.style.display = 'none'
    toggleCheck(searchToggle, searchBarDropdown)

const menuToggle = document.getElementById('menu'),
    navDropdown = document.querySelector('.nav__dropdown')
    
    navDropdown.style.display = 'none'
    toggleCheck(menuToggle, navDropdown)

function toggleCheck(elem, target ) {
    elem.addEventListener('click', function(e) {
        e.preventDefault();
        const $this = e.target
    
        if(target.style.display === 'none') {
            target.style.display = 'flex';
            $this.classList.add('is-active');
        } else {
            target.style.display = 'none';
            $this.classList.remove('is-active');
        }
    })
}
