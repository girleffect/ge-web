import "../styles/springster/springster.scss"; 


/**
 * Header search from toggle 
 */
const elemHeaderSearchToggle = document.getElementById('search'),
    elemSearchBar = document.querySelector('.search--header > .search__bar');
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