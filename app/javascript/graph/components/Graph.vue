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
    viewBox() {
      let limits = this.nodes.reduce((lim, node) => ({
        minX: node.x < lim.minX ? node.x : lim.minX,
        minY: node.y < lim.minY ? node.y : lim.minY,
        maxX: node.x > lim.maxX ? node.x : lim.maxX,
        maxY: node.y > lim.maxY ? node.y : lim.maxY
      }), { minX: 0, minY: 0, maxX: 0, maxY: 0 })

      let radiusAddedLimits = {
        minX: limits.minX - 2 * this.radius,
        minY: limits.minY - 2 * this.radius,
        maxX: limits.maxX + 2 * this.radius,
        maxY: limits.maxY + 2 * this.radius
      }

      return `${radiusAddedLimits.minX} ${radiusAddedLimits.minY} ${radiusAddedLimits.maxX - radiusAddedLimits.minX} ${radiusAddedLimits.maxY - radiusAddedLimits.minY}`
    },
    colorSchema() {
      return buildColors(this.nodes, this.colorVariation)
    }
  },
  emits: ["highlightNode", "highlightLink", "finishReload"],
  watch: {
    nodes() { this.runSimulation() },
    overallStrength() { this.runSimulation() },
    synonymStrength() { this.runSimulation() },
    relationshipStrength() { this.runSimulation() },
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
            .flatMap(([entity, links]) => links.map((link) => ({ source: entity, target: link, label: "=" })))
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
  <svg id="graph-svg" class="graph-svg"
    :viewBox="viewBox"
    @wheel="updateScale($event)" @mousedown="navigate($event)"
  >
    <line v-for="link in synonymLinks"
      class="synonym"
      :x1="link.source.x" :y1="link.source.y" :x2="link.target.x" :y2="link.target.y"
      :index="link.index"
      @mouseover="$emit('highlightLink', link)"
    />
    <line v-for="link in relationshipLinks"
      class="relationship"
      :x1="link.source.x" :y1="link.source.y" :x2="link.target.x" :y2="link.target.y"
      :index="link.index"
      @mouseover="$emit('highlightLink', link)"
    />
    <g v-for="node in nodes" :transform="`translate(${node.x}, ${node.y})`">
      <circle class="node-circle"
        :r="radius" :fill="colorSchema[node.id]" :index="node.index"
        @mouseover="$emit('highlightNode', node)"
      />
      <text v-if="showText" class="node-text">{{ node.label }}</text>
    </g>
  </svg>
</template>