import "../styles/yegna/yegna.scss";


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
     e.target.style.background = '#fff'
 } else {
     elemSearchBar.style.display = 'none'
     elemSearchBar.style.visibility = 'hidden'
     e.target.style.background = 'transparent'
 }
})