import { scaleSequential, interpolateTurbo } from "d3"

export const buildColors = (nodes, colorVariation) => {
  let colors = {}
  let colorScheme = null
  const re = /(NE|[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-z]{4}-[0-9a-f]{12})-.*/

  let sections = new Set()
  nodes.forEach(node => {
    let match = re.exec(node.id)

    if (match) {
      let section = match[1]
      sections.add(section)
    }
  })
  
  sections = Array.from(sections).sort((a, b) => a === "NE" ? -1 : b === "NE" ? 1 : 0)
  colorScheme = scaleSequential([0, sections.length], interpolateTurbo)
  console.log(nodes)
  sections.forEach((section, baseIndex) => {
    let sectionNodes = nodes.filter(node => node.id.startsWith(section)).sort()
    sectionNodes.forEach((node, offsetIndex) => {
      if (section === "NE") {
        colors[node.id] = "#ffffff"
      } else {
        let colorIndex = baseIndex + offsetIndex * colorVariation / sectionNodes.length
        colors[node.id] = colorScheme(colorIndex)
      }
    })
  })

  return colors
}
