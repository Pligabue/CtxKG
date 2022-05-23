import { buildGraph, fileData } from "./graph"

export const fetchGraph = (endpoint) => {
  fetch(endpoint)
    .then(res => res.json())
    .then(data => {
      fileData = data
      buildGraph(fileData)
    })
}