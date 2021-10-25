let scale = 1;
const handleWheel = (e) => {
  let displaySVG = document.querySelector(".display-svg")

  if (displaySVG) {
    e.preventDefault();

    let displayElement = document.querySelector("#display")
    let {scrollTop, scrollLeft} = displayElement
    let {width, height} = displaySVG.viewBox.baseVal
    let {clientX, clientY} = e
    let previousScale = scale

    scale += e.deltaY * -0.005
    scale = Math.min(Math.max(1.0, scale), 10.0)
    let ratio = scale/previousScale
  
    // Apply scale transform
    displaySVG.style.width = width * scale
    displaySVG.style.height = height * scale

    let nextMouseX = (scrollLeft + clientX) * ratio
    let nextMouseY = (scrollTop + clientY) * ratio
    let nextScrollTop = Math.max(nextMouseY - clientY, 0)
    let nextScrollLeft = Math.max(nextMouseX - clientX, 0)
    displayElement.scrollTop = nextScrollTop
    displayElement.scrollLeft = nextScrollLeft
  }
}

document.querySelector("#display").addEventListener("wheel", handleWheel)