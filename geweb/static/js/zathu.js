import "../styles/zathu/zathu.scss";

const pathName = window.location.pathname.split('/'),   
    pathNameFilter = pathName.filter(item => item !== ''),
    urlPathLang = pathNameFilter[0],
    htmlTag = document.getElementsByTagName('html')[0]

 htmlTag.setAttribute('lang', urlPathLang) 



/**
 * Forms
 */

const terms_input = document.getElementById('id_terms_and_conditions'),
    terms_label = document.querySelector('label[for="id_terms_and_conditions"]')
if (terms_input) {
    terms_input.addEventListener('change', function(e) {
        if (e.target.checked) {
            e.target.classList.add('is-on')
            terms_label.classList.add('is-on')
        } else {
            e.target.classList.remove('is-on')
            terms_label.classList.remove('is-on')
        }
    })
}