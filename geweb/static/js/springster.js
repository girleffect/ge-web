import "../styles/springster/springster.scss"; 


/**
 * Header search from toggle 
 */
const elemHeaderSearchToggle = document.getElementById('search'),
    elemSearchBar = document.querySelector('.search--header > .search__bar')
elemSearchBar.style.display = 'none'
elemSearchBar.style.visibility = 'hidden'
elemHeaderSearchToggle.addEventListener('click', (e) => { 

    if (elemSearchBar.style.display === 'none') {
        elemSearchBar.style.display = 'block'
        elemSearchBar.style.visibility = 'visible'
        e.target.style.background = '#7300ff url("http://127.0.0.1:8000/static/img/springster/dismiss.svg") no-repeat 3px 3px/auto 80%'
        e.target.style.height = '25px'
    } else {
        elemSearchBar.style.display = 'none'
        elemSearchBar.style.visibility = 'hidden'
        e.target.style.background = 'url("http://127.0.0.1:8000/static/img/springster/nav_search.svg") no-repeat 3px 0/auto 95%'
    }
})


/**
 * Menu active class for sections menu across header & footer at once AND footer menu
 */
const menuLinks = document.querySelectorAll('.nav-list__anchor')
let selectedLink = sessionStorage.getItem('curLink')

for(let i = 0; i < menuLinks.length; i++) {
    menuLinks[i].addEventListener('click', function(e) {
        const $this = e.target  
        sessionStorage.setItem('curLink', $this.classList[1])
    })
}

if (selectedLink) {
    if (selectedLink !== 'nav-list__springster') {
        document.querySelectorAll('.nav-list__springster').forEach(item => item.classList.remove('selected'))
    }
    document.querySelectorAll(`.${selectedLink}`).forEach(item => item.classList.add('selected'))
} else {
    let pathName = window.location.pathname.split('/')    
    let pathNameFilter = pathName.filter(item => item !== '')
    sessionStorage.setItem('curLink', pathNameFilter[2] ? 'nav-list__' + pathNameFilter[2] : 'nav-list__springster')
    document.querySelectorAll(pathNameFilter[2] ? '.nav-list__' + pathNameFilter[2] : '.nav-list__springster').forEach(item => item.classList.add('selected'))
}



/**
 * Forms
 */

const terms_input = document.getElementById('id_terms_and_conditions')
if (terms_input) {
    terms_input.addEventListener('change', function(e) {
        if (e.target.checked) {
            e.target.classList.add('is-on')
        } else {
            e.target.classList.remove('is-on')
        }
    })
}
    
  
    
