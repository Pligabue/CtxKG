<script>
import { select, selectAll } from "d3"
import { forceSimulation, forceCenter, forceCollide, forceLink, forceManyBody } from "d3-force"

import { buildColors } from "./colors"
import { zoom } from "./zoom"

export default {
  props: {
    showText: Boolean,
    overallStrength: Number,
    synonymStrength: Number,
    relationshipStrength: Number,
    colorVariation: Number,
    reload: Boolean
  },
  data() {
    return {
      baseGraphUrl: window.location.pathname + "json",
      title: "",
      nodes: [],
      relationshipLinks: [],
      synonymLinks: [],
      radius: 8,
      simulation: null,
      scale: { value: 1.0, event: null }
    }
  },
  computed: {
    viewBoxDimensions() {
      let limits = this.nodes.reduce((lim, node) => ({
        minX: node.x < lim.minX ? node.x : lim.minX,
        minY: node.y < lim.minY ? node.y : lim.minY,
        maxX: node.x > lim.maxX ? node.x : lim.maxX,
        maxY: node.y > lim.maxY ? node.y : lim.maxY
      }), { minX: 0, minY: 0, maxX: 0, maxY: 0 })

      return {
        minX: limits.minX - 2 * this.radius,
        minY: limits.minY - 2 * this.radius,
        maxX: limits.maxX + 2 * this.radius,
        maxY: limits.maxY + 2 * this.radius
      }
    }
  },
  emits: ["updateHighlight", "finishReload"],
  watch: {
    nodes() { this.runSimulation() },
    overallStrength() { this.runSimulation() },
    synonymStrength() { this.runSimulation() },
    relationshipStrength() { this.runSimulation() },
    showText() { this.updateText() },
    colorVariation() { this.updateColors() },
    scale(newScale, oldScale) {
      zoom(newScale.value, oldScale.value, newScale.event)
    },
    reload(newReload, oldReload) {
      if (newReload && !oldReload) {
        this.scale = { value: 1.0, event: null }
        this.fetchGraph()
        this.$emit("finishReload")
      }
    }
  },
  mounted() {
    this.fetchGraph()
    window.select = select
    window.selectAll = selectAll
  },
  methods: {
    fetchGraph() {
      fetch(this.baseGraphUrl)
        .then(res => res.json())
        .then(data => {
          let { documents, entities, graph, links } = data
          this.title = documents.join(", ")
          this.nodes = Object.entries(entities).map(([id, label]) => ({ id: id, label: label }))
          this.relationshipLinks = graph.map(({ subject_id, relation, object_id }) => ({ source: subject_id, target: object_id, label: relation }))
          this.synonymLinks = Object.entries(links)
            .flatMap(([entity, links]) => links.map((link) => ({ source: entity, target: link, label: ">" })))
            .filter((link, index, arr) => index === arr.findIndex((el) => (el.source === link.source && el.target === link.target) || (el.source === link.target && el.target === link.source)))
        })
    },
    runSimulation() {      
      this.simulation?.stop()
      this.simulation = forceSimulation(this.nodes)
        .force("charge", forceManyBody().strength(-this.overallStrength))
        .force("collision", forceCollide().radius(this.radius))
        .force("synonymLink", forceLink(this.synonymLinks).id(node => node.id).strength(this.synonymStrength))
        .force("relationshipLinks", forceLink(this.relationshipLinks).id(node => node.id).strength(this.relationshipStrength))
        .on("tick", this.updateGraph)
    },
    updateGraph() {
      const svg = select("#graph-svg")
      
      const relationshipLinks = svg.selectAll("line.relationship").data(this.relationshipLinks)
      relationshipLinks.attr("x1", d => d.source.x).attr("y1", d => d.source.y).attr("x2", d => d.target.x).attr("y2", d => d.target.y)
      relationshipLinks.attr("data-label", d => `${d.source.label} [${d.label}] ${d.target.label}`)
      relationshipLinks.enter().append("line").attr("stroke-width", 1).classed("relationship", true)
      relationshipLinks.exit().remove()
      relationshipLinks.on("mouseover", e => this.$emit("updateHighlight", e))

      const synonymLinks = svg.selectAll("line.synonym").data(this.synonymLinks)
      synonymLinks.attr("x1", d => d.source.x).attr("y1", d => d.source.y).attr("x2", d => d.target.x).attr("y2", d => d.target.y)
      synonymLinks.attr("data-label", d => `${d.source.label} = ${d.target.label}`)
      synonymLinks.enter().append("line").attr("stroke-width", 2).classed("synonym", true)
      synonymLinks.exit().remove()
      synonymLinks.on("mouseover", e => this.$emit("updateHighlight", e))

      const nodes = svg.selectAll("g").data(this.nodes)
      nodes.attr("transform", d => `translate(${d.x}, ${d.y})`)
      nodes.exit().remove()
      const nodeEnter = nodes.enter().append("g")
      nodeEnter.attr("data-entity", d => d.label).attr("data-id", d => d.id)
      nodeEnter.append("circle").classed("node-circle", true).attr("r", this.radius).attr("data-label", d => d.label).on("mouseover", e => this.$emit("updateHighlight", e))
      nodeEnter.append("text").text(d => d.label).classed("node-text", true)

      this.updateViewBox()
      this.updateColors()
    },
    updateViewBox() {
      let dim = this.viewBoxDimensions
      select("#graph-svg").attr("viewBox", `${dim.minX} ${dim.minY} ${dim.maxX - dim.minX} ${dim.maxY - dim.minY}`)
    },
    updateColors() {
      let colors = buildColors(this.nodes, this.colorVariation)
      selectAll("g").data(this.nodes).selectAll("circle").datum(d => d).style("fill", d => colors[d.id])
    },
    updateText() {
      selectAll("text").classed("hidden", !this.showText)
    },
    updateScale(e) {
      e.preventDefault()
      this.scale = {
        value: Math.min(Math.max(1.0, this.scale.value + e.deltaY * -0.005), 10.0),
        event: e
      }
    },
    navigate(initialEvent) {
      let container = select("#graph-svg").node().parentNode
      let pos = { top: container.scrollTop, left: container.scrollLeft, x: initialEvent.clientX, y: initialEvent.clientY }
      
      container.style.cursor = "grabbing"
      container.style.userSelect = "none"

      function mouseMoveHandler(e) {
        container.scrollLeft = pos.left - (e.clientX - pos.x)
        container.scrollTop = pos.top - (e.clientY - pos.y)
      }

      function mouseUpHandler(e) {
        document.removeEventListener("mousemove", mouseMoveHandler)
        document.removeEventListener("mouseup", mouseUpHandler)
        container.style.cursor = "default"
        container.style.removeProperty("user-select")
      }

      document.addEventListener("mousemove", mouseMoveHandler)
      document.addEventListener("mouseup", mouseUpHandler)
    }
  }
}
</script>

<template>
  <svg id="graph-svg" class="graph-svg" @wheel="updateScale($event)" @mousedown="navigate($event)"></svg>
</template>