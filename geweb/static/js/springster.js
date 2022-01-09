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
        e.target.style.background = 'url("http://127.0.0.1:8000/static/img/springster/dismiss.svg") no-repeat 3px 5px/auto 80%'
    } else {
        elemSearchBar.style.display = 'none'
        elemSearchBar.style.visibility = 'hidden'
        e.target.style.background = 'url("http://127.0.0.1:8000/static/img/springster/nav_search.svg") no-repeat 3px 0/auto 95%'
    }
})


/**
 * Menu active class for sections menu across header & footer at once AND footer menu
 */

const menuLinksFooter = document.querySelectorAll('.footer-nav-list p a')
    menuLinksFooter.forEach(function(elem, i) {
        elem.classList.add('nav-list__anchor')
    })

const menuLinks = document.querySelectorAll('.nav-list__anchor')
    for(let i = 0; i < menuLinks.length; i++) {
        menuLinks[i].addEventListener('click', function(e) {
            //e.preventDefault()
            const $this = e.target         
            menuLinks.forEach(function(item, i) {
                item.classList.remove('selected')    
                if ($this.classList.length > 1) {
                    document.querySelectorAll(`.${$this.classList[1]}`).forEach(function(elems, i) {
                        elems.classList.add('selected')
                    })
                } else {
                    $this.classList.add('selected')
                }
            })
           
        })
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
    
    