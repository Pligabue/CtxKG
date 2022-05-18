fetchGraph = (endpoint) => {
  fetch(endpoint)
    .then(res => res.json())
    .then(data => {
      fileData = data
      buildGraph(fileData)
    })
}