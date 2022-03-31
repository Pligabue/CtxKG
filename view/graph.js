
let overallStrength = -parseFloat(document.querySelector("#overall-strength").value)
let synonymStrength = parseFloat(document.querySelector("#synonym-strength").value)
let relationshipStrength = parseFloat(document.querySelector("#relationship-strength").value)
let colorVariation = parseFloat(document.querySelector("#color-variation").value)
let data = null

const handleStrength = () => {
  overallStrength = -parseFloat(document.querySelector("#overall-strength").value)
  synonymStrength = parseFloat(document.querySelector("#synonym-strength").value)
  relationshipStrength = parseFloat(document.querySelector("#relationship-strength").value)
  loadJSON()
}

const handleColorVariation = () => {
  colorVariation = parseFloat(document.querySelector("#color-variation").value)
  let colors = buildColors(data, colorVariation)

  d3.selectAll("circle")
    .style("fill", d => colors[d.id])
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

const getIdToLabel = (fileData) => {
  let idToLabel = {}
  fileData.forEach(node => {
    idToLabel[node.subject_id] = node.subject
    idToLabel[node.object_id] = node.object
  })
  return idToLabel
}

const buildNodes = (idToLabel) => {
  return Object.keys(idToLabel).map(id => ({ id: id, text: idToLabel[id] }))
}

const buildRelationshipLinks = (fileData, idToLabel) => {
  return fileData.map(node => ({
    source: node.subject_id,
    relation: node.relation,
    target: node.object_id,
    sourceText: node.subject,
    targetText: node.object
  }))
}

const buildSynonymLinks = (fileData, idToLabel) => {
  let subjectSynonymLinks = fileData.map(node => {
    return node.subject_links.map(link => ({ source: node.subject_id, target: link, sourceText: node.subject, targetText: idToLabel[link] }))
  }).flat()
  
  let objectSynonymLinks = fileData.map(node => {
    return node.object_links.map(link => ({ source: node.object_id, target: link, sourceText: node.object, targetText: idToLabel[link] }))
  }).flat()

  return [...subjectSynonymLinks, ...objectSynonymLinks]
}

const getIndexOfLink = (links, entityOne, entityTwo) => {
  return links.findIndex(({ source, target }) => (entityOne === source && entityTwo === target) || (entityTwo === source && entityOne === target))
}

const removeDuplicates = (data) => {
  data.relationshipLinks = data.relationshipLinks.filter((link, i, links) => i === getIndexOfLink(links, link.source, link.target))
  data.synonymLinks = data.synonymLinks.filter(link => getIndexOfLink(data.relationshipLinks, link.source, link.target) === -1)
}

const cleanData = (fileData) => {
  let cleanedData = fileData

  if (!Array.isArray(fileData)) {
    if (cleanedData.nodes) {
      cleanedData = cleanedData.nodes
    } else {
      console.error("NODES MISSING")
      return cleanedData
    }
  }

  for (node of cleanedData) {
    if (node.subject_links === undefined) {
      node.subject_links = []
    }
    if (node.object_links === undefined) {
      node.object_links = []
    }
  }

  return cleanedData
}

const buildGraph = (fileData) => {
  let idToLabel = getIdToLabel(fileData)
  let colors = null

  cleanPrevious()
  
  data = {
    nodes: buildNodes(idToLabel),
    relationshipLinks: buildRelationshipLinks(fileData, idToLabel),
    synonymLinks: buildSynonymLinks(fileData, idToLabel)
  }
  removeDuplicates(data)
  colors = buildColors(data, colorVariation)

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
      .attr("data-info", d => `${d.sourceText} ⟷ ${d.targetText}`)
      .on("mouseover", showInfo)

  const relationshipLinks = svg
    .selectAll("line.relationship")
    .data(data.relationshipLinks)
    .enter()
    .append("line")
      .attr("stroke-width", 1)
      .classed("relationship", true)
      .attr("data-info", d => `${d.sourceText} > ${d.relation} > ${d.targetText}`)
      .on("mouseover", showInfo)

  const nodes = svg
    .selectAll("g")
    .data(data.nodes)
    .enter()
    .append("g")
    .attr("data-entity", d => d.text)
    .attr("data-id", d => d.id)

  const radius = 8
  const nodeCircles = nodes
    .append("circle")
      .attr("r", radius)
      .attr("stroke", "black")
      .attr("stroke-width", "2")
      .attr("data-info", d => d.text)
      .style("fill", d => colors[d.id])
      .on("mouseover", showInfo)

  const nodeLabel = nodes
    .append("text")
      .text(d => d.text)
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
      let filenames = file.name.split(".").slice(0, -1).join(".")
      if (fileData.filenames) {
        filenames = fileData.filenames.join(", ")
      }
      d3.select(".filenames").text(filenames)
      let cleanedData = cleanData(fileData)
      buildGraph(cleanedData)
    }
    reader.readAsText(file, "utf-8")
  }
}