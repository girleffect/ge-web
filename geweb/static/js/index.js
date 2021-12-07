//Express server & others 

const brandNames = [
    'springster',
    'ninyampinga',
    'zathu'
]

const brandIterator = (names) => {
    let query = null
    const currentQuery = window.location.search
    let searchParams = new URLSearchParams(currentQuery)

    names.forEach(name => {
        if (name === searchParams.get('brand')) {
            query = name
        } 
    })
    return query
}


brandIterator(brandNames)

console.log(brandIterator(brandNames))