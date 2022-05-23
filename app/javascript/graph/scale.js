export let scale = 1.0

export const handleWheel = (e) => {
  let graphSvg = document.querySelector(".graph-svg")

  if (graphSvg) {
    e.preventDefault();

    let graphContainer = document.querySelector("#graph-container")
    let { scrollTop, scrollLeft } = graphContainer
    let { clientWidth, clientHeight } = graphContainer
    let { clientX, clientY } = e
    let previousScale = scale

    scale += e.deltaY * -0.005
    scale = Math.min(Math.max(1.0, scale), 10.0)

    if (scale == previousScale) {
      return
    }

    let ratio = scale/previousScale
  
    // Apply scale transform
    graphSvg.style.width = clientWidth * scale
    graphSvg.style.height = clientHeight * scale

    let nextMouseX = (scrollLeft + clientX) * ratio
    let nextMouseY = (scrollTop + clientY) * ratio
    let nextScrollTop = Math.max(nextMouseY - clientY, 0)
    let nextScrollLeft = Math.max(nextMouseX - clientX, 0)
    graphContainer.scrollTop = nextScrollTop
    graphContainer.scrollLeft = nextScrollLeft
  }
}
