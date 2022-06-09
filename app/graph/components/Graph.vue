<script>
import { select, selectAll } from "d3"
import { forceSimulation, forceCenter, forceCollide, forceLink, forceManyBody } from "d3-force"

import BridgeManager from "./BridgeManager.vue"
import ControlPanel from "./ControlPanel.vue"
import Highlight from "./Highlight.vue"

import { buildColors } from "./colors"
import { zoom } from "./zoom"

export default {
  components: {
    ControlPanel,
    BridgeManager,
    Highlight
  },
  data() {
    return {
      baseUrl: window.location.pathname.match(/.*(?:base|clean)\//)[0],
      baseGraphName: window.location.pathname.match(/\/([^\/]*)\/$/)[1],
      title: "",
      showText: true,
      overallStrength: 50,
      synonymStrength: 1,
      relationshipStrength: 0.2,
      colorVariation: 1,
      textSize: 1.0,
      radius: 8,
      nodes: [],
      relationshipLinks: [],
      synonymLinks: [],
      simulation: null,
      scale: { value: 1.0, event: null },
      highlighted: { el: null, type: null },
      bridgeNode: null
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
  emits: ["highlightNode", "highlightLink", "openBridges", "finishReload"],
  watch: {
    nodes() { this.runSimulation() },
    overallStrength() { this.runSimulation() },
    synonymStrength() { this.runSimulation() },
    relationshipStrength() { this.runSimulation() },
    radius() { this.runSimulation() },
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
      fetch(this.baseUrl + `${this.baseGraphName}/json/`)
        .then(res => res.json())
        .then(data => {
          let { document, entities, graph, links } = data
          this.title = document.split("/").slice(-1)[0].split(".")[0]
          this.nodes = Object.entries(entities).map(([id, label]) => ({ id: id, label: label, graph: this.baseGraphName }))
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
        value: Math.min(Math.max(1.0, this.scale.value + e.deltaY * -0.005), 50.0),
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
    },
    expandNode(startingNode, data) {
      let { nodes, relationshipLinks, synonymLinks } = data
      nodes.forEach(n => {
        n.x = startingNode.x
        n.y = startingNode.y
      })

      let newNodes = nodes.filter(node => !this.nodes.some(n => n.id === node.id))
      let newRelationshipLinks = relationshipLinks.filter(link => !this.relationshipLinks.some(l => l.source.id === link.source && l.target.id === link.target))
      let newSynonymLinks = synonymLinks.filter(link => !this.synonymLinks.some(l => l.source.id === link.source && l.target.id === link.target))
      this.nodes = [...this.nodes, ...newNodes]
      this.relationshipLinks = [...this.relationshipLinks, ...newRelationshipLinks]
      this.synonymLinks = [...this.synonymLinks, ...newSynonymLinks]
      this.colorVariation = 0.0
    }
  }
}
</script>

<template>
  <div class="overflow-auto h-full w-full">
    <svg id="graph-svg" class="graph-svg"
      :viewBox="viewBox"
      @wheel="updateScale($event)" @mousedown="navigate($event)" @dblclick="bridgeNode = null"
    >
      <line v-for="link in synonymLinks"
        class="synonym"
        :x1="link.source.x" :y1="link.source.y" :x2="link.target.x" :y2="link.target.y"
        :index="link.index"
        @mouseover="highlighted = { el: link, type: 'synonymLink'}"
      />
      <line v-for="link in relationshipLinks"
        class="relationship"
        :x1="link.source.x" :y1="link.source.y" :x2="link.target.x" :y2="link.target.y"
        :index="link.index"
        @mouseover="highlighted = { el: link, type: 'relationshipLink'}"
      />
      <g v-for="node in nodes" :transform="`translate(${node.x}, ${node.y})`">
        <circle class="node-circle"
          :r="radius" :fill="colorSchema[node.id]" :index="node.index"
          @mouseover="highlighted = { el: node, type: 'node'}" @click="bridgeNode = node"
        />
        <text v-if="showText" class="node-text" :style="{ fontSize: textSize + 'em' }">{{ node.label }}</text>
      </g>
    </svg>
  </div>
  <ControlPanel
    v-model:show-text="showText"
    v-model:overall-strength="overallStrength" 
    v-model:synonym-strength="synonymStrength"
    v-model:relationship-strength="relationshipStrength"
    v-model:color-variation="colorVariation"
    v-model:text-size="textSize"
    v-model:radius="radius"
    @reload="fetchGraph"
  />
  <BridgeManager
    :baseUrl="baseUrl"
    :node="bridgeNode"
    @expand-node="expandNode"
  />
  <Highlight
    :el="highlighted.el"
    :type="highlighted.type"
  />
</template>