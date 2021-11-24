
let overallStrength = -parseFloat(document.querySelector("#overall-strength").value)
let synonymStrength = parseFloat(document.querySelector("#synonym-strength").value)
let relationshipStrength = parseFloat(document.querySelector("#relationship-strength").value)

const handleStrength = () => {
  overallStrength = -parseFloat(document.querySelector("#overall-strength").value)
  synonymStrength = parseFloat(document.querySelector("#synonym-strength").value)
  relationshipStrength = parseFloat(document.querySelector("#relationship-strength").value)
  loadJSON()
}

const cleanPrevious = () => {
  scale = 1.0
  d3.select("svg.display-svg").remove()
}

const toggleText = () => {
  let texts = d3.selectAll("text")
  if (texts.classed("hidden")) {
    texts.classed("hidden", false)
  } else {
    texts.classed("hidden", true)
  }
}

const showInfo = (e) => {
  d3.selectAll(".red-stroke").classed("red-stroke", false)
  e.target.classList.add("red-stroke")
  d3.select("#info").text(e.target.dataset.info)
}

const buildNodes = (fileData) => {
  let subjects = fileData.map(node => node.subject)
  let objects = fileData.map(node => node.object)
  return [...subjects, ...objects].filter((node, i, arr) => arr.indexOf(node) === i).map(node => ({id: node}))
}

const buildRelationshipLinks = (fileData) => {
  return fileData.map(node => ({source: node.subject, target: node.object, relation: node.relation}))
}

const buildSynonymLinks = (fileData) => {
  let subjectSynonymLinks = fileData.map(node => {
    return node.subject_links.map(link => ({source: node.subject, target: link}))
  }).flat()
  
  let objectSynonymLinks = fileData.map(node => {
    return node.object_links.map(link => ({source: node.object, target: link}))
  }).flat()
  
  let synonymLinks = [...subjectSynonymLinks, ...objectSynonymLinks].filter((link, i, arr) => {
    let firstLinkIndex = arr.findIndex(e => e.source === link.source && e.target === link.target)
    return i === firstLinkIndex && link.source !== link.target
  })

  return synonymLinks
}

const removeDuplicates = (data) => {
  let {synonymLinks, relationshipLinks} = data
  data.synonymLinks = synonymLinks.filter(synonymLink => {
    const index = relationshipLinks.findIndex(relationshipLink => {
      return (relationshipLink.source === synonymLink.source && relationshipLink.target === synonymLink.target) ||
             (relationshipLink.target === synonymLink.source && relationshipLink.source === synonymLink.target)
    })
    return index === -1
  })
}

const buildGraph = (fileData) => {
  cleanPrevious()

  const data = {
    nodes: buildNodes(fileData),
    relationshipLinks: buildRelationshipLinks(fileData),
    synonymLinks: buildSynonymLinks(fileData)
  }
  removeDuplicates(data)
  buildColors(data)
  
  console.log(data)

  const svg = d3.select("#display")
    .append("svg")
    .classed("display-svg", true)
    
  const height = parseFloat(svg.style("height"))
  const width = parseFloat(svg.style("width"))
  svg.style("height", height)
  svg.style("width", width)

  const synonymLinks = svg
    .selectAll("line.synonym")
    .data(data.synonymLinks)
    .enter()
    .append("line")
      .attr("stroke-width", 2)
      .classed("synonym", true)
      .attr("data-info", d => `${d.source} ⟷ ${d.target}`)
      .on("mouseover", showInfo)

  const relationshipLinks = svg
    .selectAll("line.relationship")
    .data(data.relationshipLinks)
    .enter()
    .append("line")
      .attr("stroke-width", 1)
      .classed("relationship", true)
      .attr("data-info", d => `${d.source} > ${d.relation} > ${d.target}`)
      .on("mouseover", showInfo)

  const nodes = svg
    .selectAll("g")
    .data(data.nodes)
    .enter()
    .append("g")

  const radius = 8
  const nodeCircles = nodes
    .append("circle")
      .attr("r", radius)
      .attr("stroke", "black")
      .attr("stroke-width", "2")
      .attr("data-info", d => d.id)
      .style("fill", d => data.colors[d.id])
      .on("mouseover", showInfo)

  const nodeLabel = nodes
    .append("text")
      .text(d => d.id)
      .classed("node-text", true)

  const simulation = d3.forceSimulation(data.nodes)
    .force("charge", d3.forceManyBody().strength(overallStrength))
    .force("collision", d3.forceCollide().radius(radius))
    .force("synonymLink", d3.forceLink(data.synonymLinks).id(node => node.id).strength(synonymStrength))
    .force("relationshipLinks", d3.forceLink(data.relationshipLinks).id(node => node.id).strength(relationshipStrength))
    .force("center", d3.forceCenter(width/2, height/2))
    .on("tick", () => {
      let nodeData = nodes.data()
      let extremes = nodeData.reduce((acc, node) => ({
        minX: node.x - radius < acc.minX ? node.x - radius : acc.minX,
        minY: node.y - radius < acc.minY ? node.y - radius : acc.minY,
        maxX: node.x + radius > acc.maxX ? node.x + radius : acc.maxX,
        maxY: node.y + radius > acc.maxY ? node.y + radius : acc.maxY
      }), {
        minX: 0,
        minY: 0,
        maxX: width,
        maxY: height
      })

      synonymLinks.attr("x1", d => d.source.x).attr("y1", d => d.source.y)
                  .attr("x2", d => d.target.x).attr("y2", d => d.target.y)

      relationshipLinks.attr("x1", d => d.source.x).attr("y1", d => d.source.y)
                       .attr("x2", d => d.target.x).attr("y2", d => d.target.y)

      nodes.attr("transform", d => `translate(${d.x}, ${d.y})`)

      svg.attr("viewBox", `${extremes.minX} ${extremes.minY} ${extremes.maxX - extremes.minX} ${extremes.maxY - extremes.minY}`)
    })
}

const loadJSON = function() {
  const file = document.getElementById('file-input').files[0]
  if (file) {
    document.title = file.name
    const reader = new FileReader()
    reader.onload = function(e) {
      let jsonString = e.target.result
      let fileData = JSON.parse(jsonString)
      buildGraph(fileData)
    }
    reader.readAsText(file, "utf-8")
  }
}