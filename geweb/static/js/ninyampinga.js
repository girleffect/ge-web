import "../styles/ninyampinga/ninyampinga.scss";


const toggle = document.querySelectorAll('.toggle'),
    toggleNodes = toggle.length > 1 ? toggle : document.querySelector('.toggle')

document.querySelectorAll('.dropdown').forEach((item, i) => {
    item.style.display = 'none'
})

if(toggle.length > 1) {
    toggleNodes.forEach((item, i) => {
        toggleCheck(item)
    })
} else {
    toggleCheck(toggleNodes)
}

function toggleCheck(elem) {
    elem.addEventListener('click', function(e) {
        const $this = e.target,
            menu = $this.parentElement,
            dropdown = menu.querySelector('.dropdown');
    
        if(dropdown.style.display === 'none') {
            dropdown.style.display = 'block';
            $this.classList.add('is-active');
        } else {
            dropdown.style.display = 'none';
            $this.classList.remove('is-active');
        }
    })
}

