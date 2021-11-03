const buildColors = (data) => {
  let groups = {}
  let numOfGroups = 0
  let colors = {}
  let colorScheme = null

  let i = -1

  data.synonymLinks.forEach(link => {
    let {source, target} = link

    if (source in groups || target in groups) {
      if (source in groups) {
        groups[target] = groups[source]
      } else {
        groups[source] = groups[target]
      }
    } else {
      i++
      groups[source] = i
      groups[target] = i
    }
  })

  data.nodes.forEach(({id}) => {
    if (!(id in groups)) {
      i++
      groups[id] = i
    }
  })

  numOfGroups = Object.entries(groups).reduce((acc, [node, groupIndex]) => {
    return groupIndex > acc ? groupIndex : acc
  }, 0)

  colorScheme = d3.scaleSequential([0, numOfGroups + 2], d3.interpolateTurbo)
  
  Object.entries(groups).forEach(([node, groupIndex]) => {
    colors[node] = colorScheme(groupIndex + 1)
  })

  data.colors = colors
}
