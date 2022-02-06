import "../styles/tujibebe/tujibebe.scss";



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
        //elemHeaderSearchToggle.style.backgroundPosition = '-165px -240px'
        console.log(e.target)
    } else {
        elemSearchBar.style.display = 'none'
        elemSearchBar.style.visibility = 'hidden'
        //elemHeaderSearchToggle.style.backgroundPosition = '0 -177px'
    }
})