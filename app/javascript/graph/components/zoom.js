import { select } from "d3"

export function zoom(newScale, oldScale, event) {
  let svg = select("#graph-svg")
  let container = svg.node().parentNode
  let { offsetWidth, offsetHeight } = container
  
  svg.style("width", offsetWidth * newScale)
  svg.style("height", offsetHeight * newScale)
  
  if (event) {
    let ratio = newScale / oldScale
    let { scrollLeft, scrollTop } = container
    let { offsetX, offsetY } = event
    let mouseOffsetX = offsetX - scrollLeft
    let mouseOffsetY = offsetY - scrollTop
  
    container.scrollLeft = (offsetX * ratio) - mouseOffsetX
    container.scrollTop = (offsetY * ratio) - mouseOffsetY
  }
}