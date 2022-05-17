fetchGraph = (el) => {
  let { endpoint } = el.dataset
  fetch(endpoint)
    .then(res => res.json())
    .then(buildGraph)
}