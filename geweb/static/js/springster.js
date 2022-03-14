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
        e.target.style.background = '#7300ff url("https://standard-wagtail.prd-hub.ie.gehosting.org/static/img/springster/dismiss.svg") no-repeat 3px 3px/auto 80%'
        e.target.style.height = '25px'
    } else {
        elemSearchBar.style.display = 'none'
        elemSearchBar.style.visibility = 'hidden'
        e.target.style.background = 'url("https://standard-wagtail.prd-hub.ie.gehosting.org/static/img/springster/nav_search.svg") no-repeat 3px 0/auto 95%'
    }
})


/**
 * Menu active class for sections menu across header & footer at once AND footer menu
 */
const menuLinks = document.querySelectorAll('.nav-list__anchor'),
    linkPathName = window.location.pathname.split('/'),
    pathArrayCheck = linkPathName.filter(item => item != '' )


if (pathArrayCheck.length <= 1) {
    sessionStorage.setItem('curLink', 'nav-list__springster')
}

for(let i = 0; i < menuLinks.length; i++) {
    menuLinks[i].addEventListener('click', function(e) {
        const $this = e.target
        sessionStorage.setItem('curLink', $this.classList[1])
    })
}

if (sessionStorage.getItem('curLink')) {
    if (sessionStorage.getItem('curLink') !== 'nav-list__springster') {
        document.querySelectorAll('.nav-list__springster').forEach(item => item.classList.remove('selected'))
    }
    document.querySelectorAll(`.${sessionStorage.getItem('curLink')}`).forEach(item => item.classList.add('selected'))
} else {
    sessionStorage.setItem('curLink', linkPathName[2] ? 'nav-list__' + linkPathName[2] : 'nav-list__springster')
    document.querySelectorAll(linkPathName[2] ? '.nav-list__' + linkPathName[2] : '.nav-list__springster').forEach(item => item.classList.add('selected'))
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
