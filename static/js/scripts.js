allHeroes = JSON.parse(document.getElementById("all-heroes").getAttribute('data'));
document.getElementById("all-heroes").parentNode.removeChild(document.getElementById("all-heroes"));
selectedHeroes = []
allArtifacts = JSON.parse(document.getElementById("all-artifacts").getAttribute('data'));
document.getElementById("all-artifacts").parentNode.removeChild(document.getElementById("all-artifacts"))
selectedArtifacts = []

outputDiv = document.getElementById('output')
selectedDiv = document.getElementById('selected')
searchDiv = document.getElementById("search")


dataType = null;
sortedData = {
    'starts-selectors': [],
    'elements-selectors': [],
    'classes-selectors': []
}
allSelectors = {
    '5-star': function () {
        sortedData['starts-selectors'].push(sortByStars(5))
    },
    '4-star': function () {
        sortedData['starts-selectors'].push(sortByStars(4))
    },
    'fire-element': function () {
        sortedData['elements-selectors'].push(sortByElement('fire'))
    },
    'ice-element': function () {
        sortedData['elements-selectors'].push(sortByElement('ice'))
    },
    'earth-element': function () {
        sortedData['elements-selectors'].push(sortByElement('earth'))
    },
    'light-element': function () {
        sortedData['elements-selectors'].push(sortByElement('light'))
    },
    'dark-element': function () {
        sortedData['elements-selectors'].push(sortByElement('dark'))
    },
    'knight-class': function () {
        sortedData['classes-selectors'].push(sortByClass('knight'))
    },
    'warrior-class': function () {
        sortedData['classes-selectors'].push(sortByClass('warrior'))
    },
    'thief-class': function () {
        sortedData['classes-selectors'].push(sortByClass('thief'))
    },
    'mage-class': function () {
        sortedData['classes-selectors'].push(sortByClass('mage'))
    },
    'ranger-class': function () {
        sortedData['classes-selectors'].push(sortByClass('ranger'))
    },
    'soul_weaver-class': function () {
        sortedData['classes-selectors'].push(sortByClass('soul_weaver'))
    }
}

starsSelectors = ['5-star', '4-star']
elementsSelectors = ['fire-element', 'ice-element', 'earth-element', 'light-element', 'dark-element'];
classesSelectors = ['knight-class', 'warrior-class', 'thief-class', 'mage-class', 'ranger-class', 'soul_weaver-class']
data = []
appliedSelectors = []
selectedData = []
for (let _ in allSelectors) {
    selectorHandler(_)
}

document.getElementById('heroes').addEventListener("click", function () {
    data = allHeroes;
    dataType = 'heroes'
    selectedData = selectedHeroes
    for (let _ of elementsSelectors) {
        document.getElementById(_).parentNode.style.display = ""
    }
    document.getElementById('all-elements').click()
    document.getElementById("all-elements").parentNode.style.display = ""
    document.getElementById("no-elements").parentNode.style.display = ""
    updateOutputDiv()
})

document.getElementById('artifacts').addEventListener("click", function () {
    data = allArtifacts
    dataType = 'artifacts'
    selectedData = selectedArtifacts
    document.getElementById('no-elements').click()
    for (let _ of elementsSelectors) {
        document.getElementById(_).parentNode.style.display = "none"
    }
    document.getElementById("all-elements").parentNode.style.display = "none"
    document.getElementById("no-elements").parentNode.style.display = "none"
    updateOutputDiv()
})

document.getElementById('all-stars').addEventListener("click", function () {
    for (_ of starsSelectors) {
        let el = document.getElementById(_)
        if (!(el.checked)) {
            el.click()
        }
    }
    updateOutputDiv()
})

document.getElementById('no-stars').addEventListener("click", function () {
    for (_ of starsSelectors) {
        let el = document.getElementById(_)
        if (el.checked) {
            el.click()
        }
    }
    updateOutputDiv()
})

document.getElementById('all-elements').addEventListener("click", function () {
    for (_ of elementsSelectors) {
        let el = document.getElementById(_)
        if (!(el.checked)) {
            el.click()
        }
    }
    updateOutputDiv()
})

document.getElementById('no-elements').addEventListener("click", function () {
    for (_ of elementsSelectors) {
        let el = document.getElementById(_)
        if (el.checked) {
            el.click()
        }
    }
    updateOutputDiv()
})

document.getElementById('all-classes').addEventListener("click", function () {
    for (_ of classesSelectors) {
        let el = document.getElementById(_)
        if (!(el.checked)) {
            el.click()
        }
    }
    updateOutputDiv()
})

document.getElementById('no-classes').addEventListener("click", function () {
    for (_ of classesSelectors) {
        let el = document.getElementById(_)
        if (el.checked) {
            el.click()
        }
    }
    updateOutputDiv()
})

function sortByElement(element) {
    let sorted = []
    for (let _ of data) {
        if (_.element == element) {
            sorted.push(_)
        }
    }
    return sorted

}

function sortByStars(stars) {
    let sorted = []
    for (let _ of data) {
        if (_.star == stars) {
            sorted.push(_)
        }
    }
    return sorted
}

function sortByClass(objclass) {
    outputDiv.innerText = ''
    let sorted = []
    for (let _ of data) {
        if (_.classes == objclass) {
            sorted.push(_)
        }
    }
    return sorted
}

function selectorHandler(id) {
    let checkbox = document.getElementById(id)
    if (checkbox.checked) {
        appliedSelectors.push(id)
    }
    document.getElementById(id).addEventListener("click", function () {
        if (this.checked) {
            appliedSelectors.push(id)
        } else {
            let index = appliedSelectors.indexOf(id);
            if (index !== -1) {
                appliedSelectors.splice(index, 1);
            }
        }
        updateOutputDiv()
    })
}

searchDiv.addEventListener("input", function () {
    let convertedInput = searchDiv.value.toLowerCase().replace(/ /g, "_");
    outputDiv.innerText = ''
    for (let _ of output) {
        if (_.name.startsWith(convertedInput)) {
            let img = getImage(_.name)
            img.addEventListener('click', function () {
                if (!(_.name in selectedData)) {
                    selectedDiv.appendChild(getImage(_.name))
                    selectedDiv.appendChild(getHiddenInput(_.name))
                    selectedData.push(_.name)
                }
            })
            outputDiv.appendChild(img)
        }
    }
})

function updateOutputDiv() {
    sortedData = {
        'starts-selectors': [],
        'elements-selectors': [],
        'classes-selectors': []
    }
    output = []
    for (let _ of appliedSelectors) {
        allSelectors[_]()
    }
    for (let group in sortedData) {
        let groupSorted = []
        for (let _ in sortedData[group]) {
            groupSorted.push(...sortedData[group][_])
        }
        if (groupSorted.length) {
            output.push(groupSorted)
        } else {
            output.push(data)
        }
    }
    output = output.reduce((a, b) => a.filter(c => b.includes(c)));
    outputDiv.innerText = ''
    for (let _ of output) {
        let img = getImage(_.name)
        img.addEventListener('click', function () {
            if (!(_.name in selectedData)) {
                img = getImage(_.name)
                img.addEventListener('click', function () {
                    var index = selectedData.indexOf(_.name);
                    if (index !== -1) {
                        selectedData.splice(index, 1);
                    }
                    selectedDiv.removeChild(this)
                    var allInputs = selectedDiv.getElementsByTagName('input')
                    for (let i of allInputs) {
                        if (i.value == _.name) {
                            selectedDiv.removeChild(i)
                            break
                        }
                    }

                })
                selectedDiv.appendChild(img)
                selectedDiv.appendChild(getHiddenInput(_.name))
                selectedData.push(_.name)
            }
        })
        outputDiv.appendChild(img)

    }
}

function getHiddenInput(name) {
    let input = document.createElement('input');
    input.type = 'hidden'
    input.name = dataType
    input.value = name
    return input

}

function getImage(name) {
    let img = document.createElement('img');
    img.src = 'static/img/faces/' + name + '.jpg'
    img.onerror = function () {
        img.src = "static/img/faces/missing.jpg"
    }
    img.width = 190
    img.height = 70
    img.style.display = 'inline'
    img.style.padding = '5px';
    return img

}