const buildColors = (data, colorVariation) => {
  let colors = {}
  const re = /(NE|[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-z]{4}-[0-9a-f]{12})-.*/

  let sections = data.nodes.reduce((set, node) => {
    let { id } = node
    let match = re.exec(id)

    if (match) {
      let section = match[1]
      return set.add(section)
    }
    return set
  }, new Set())
  
  sections = Array.from(sections).sort((a, b) => a === "NE" ? -1 : b === "NE" ? 1 : 0)
  colorScheme = d3.scaleSequential([0, sections.length], d3.interpolateTurbo)
  sections.forEach((section, baseIndex) => {
    let sectionNodes = data.nodes.filter(node => node.id.startsWith(section)).sort()
    sectionNodes.forEach((node, offsetIndex) => {
      let colorIndex = baseIndex + offsetIndex * colorVariation / sectionNodes.length
      colors[node.id] = colorScheme(colorIndex)
    })
  })

  return colors
}
