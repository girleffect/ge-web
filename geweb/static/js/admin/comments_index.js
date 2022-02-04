window.onload = function() {
    document.getElementsByClassName('actionbutton')[0].remove()

    const rows = document.querySelectorAll('tr')
    for (let i = 0; i < rows.length; i++) {
      var has_parent_comment = rows[i].getElementsByClassName("field-parent_comment")[0]
      if (has_parent_comment){
         if(has_parent_comment.getElementsByTagName("a")[0].innerHTML.includes("True")){
           rows[i].style.backgroundColor='#F0F0F0';
         }

      }
    }

    const filter = document.getElementsByClassName('changelist-filter')[0]
    filter.style.width="15.5%";
};
