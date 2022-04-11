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








/**
* FORMS
* 
* RADIO BUTTONS IN WAGTAIL MESSY MARKUP
*/

// 1. Assign class e.g 'typeRadio' to all radio button labels
// 2. Push the radio button question to array e.g. 'allRadioInputsArray'
function assignListInputs(list, name, arr) {
    for (let m = 0; m < list.length; m++) {
        if (list[m].parentElement.nodeName === 'LABEL') {
            const eachInputLabel = list[m].parentElement,
            eachInputLabelParent = eachInputLabel.parentElement, //MAKE SURE THE MARKUP DOES INDEED HAVE UNNAMED DIV WRAPPER PARENT
            eachInputLabelAncestor = eachInputLabelParent.parentElement;
            arr.push(eachInputLabelAncestor.getAttribute('id'))
            eachInputLabel.classList.add(name)
        }
    }
}

// Remove array duplicates
function removeDuplucateKeys(arr) {
    return arr.filter((val, index) => {
       return arr.indexOf(val) === index
    })
}

function inputChange(arg, action, name, className) {
    for (const attr of arg) {
        const selectEachInputQuestion = document.getElementById(attr);

       const eachInputDivCollection = selectEachInputQuestion.children;
       
        const eachInputDivArray =  [...eachInputDivCollection];
    
        for (let i = 0; i < eachInputDivArray.length; i++) {
            const eachDiv = eachInputDivArray[i],
                label = eachDiv.children[0];

            if (label.classList.contains(name)) {
                label.addEventListener(action, function(e) { 
                    let allLabels, allInputs, $targetInput;
                    if (e.target.nodeName === 'INPUT')  $targetInput = e.target // TARGET RETURNS LABEL + INPUT SO FILTER BY INPUT ONLY
                    //  e.target label will be undefined | filter it out
                    if ($targetInput !== undefined) {
                        // For loop again to get entire radion inputs list on the question
                        for (let j = 0; j < eachInputDivArray.length; j++) {
                            allLabels = eachInputDivArray[j].children[0] 
                            allInputs = allLabels.children[0]

                            // CHECK MULTIPLE CHECKBOXES & ONLY SELECT 1 RADIO BUTTON
                            if (allInputs.getAttribute('type') !== 'checkbox') {
                                allInputs.removeAttribute('checked')
                            }
                            allLabels.classList.remove(className)
                        }
                        if ($targetInput.checked) {
                            $targetInput.setAttribute('checked','checked')
                            label.classList.add(className)
                        } else  {
                            // CHECK OR UNCHECK MULTIPLE CHECKBOXES
                            $targetInput.removeAttribute('checked')
                            label.classList.remove(className)
                        }
                    }
                })
            }
        }
    }
}

//!! DO NOT CHANGE ORDER OF INVOKATION 
// RADIO
const allRadioInputs = document.querySelectorAll('input[type="radio"]'),
    allRadioInputsArray = [];

assignListInputs(allRadioInputs, 'typeRadio', allRadioInputsArray)

const eachRadioInputQuestionId = removeDuplucateKeys(allRadioInputsArray);
inputChange(eachRadioInputQuestionId, 'click', 'typeRadio', 'selected')


// CHECKBOX
const allCheckoutInputs = document.querySelectorAll('input[type="checkbox"]'),
    allCheckoutInputsArray = [];

assignListInputs(allCheckoutInputs, 'typeCheckbox', allCheckoutInputsArray)

const eachCheckboxInputQuestionId = removeDuplucateKeys(allCheckoutInputsArray),
    eachCheckboxQuestionIdArray = eachCheckboxInputQuestionId.filter(item => {
        if (item !== 'header' && item !== 'footer') 
            return [...item]
    });
inputChange(eachCheckboxQuestionIdArray, 'change', 'typeCheckbox', 'is-on')



