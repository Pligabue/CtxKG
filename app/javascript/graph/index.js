import { createApp } from "vue"

import { fetchGraph } from "./fetch_graph"
import { mouseDownHandler } from "./navigation"
import { handleWheel } from "./scale"
import { handleStrength, handleColorVariation, rebuildGraph, toggleText } from "./graph"

document.querySelector("#graph-container").addEventListener("mousedown", mouseDownHandler)
document.querySelector("#graph-container").addEventListener("wheel", handleWheel)

window.fetchGraph = fetchGraph
window.handleStrength = handleStrength
window.handleColorVariation = handleColorVariation
window.rebuildGraph = rebuildGraph
window.toggleText = toggleText