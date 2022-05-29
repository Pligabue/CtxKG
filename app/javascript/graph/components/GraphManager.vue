<script>
import { selectAll } from "d3-selection"

import ControlPanel from "./ControlPanel.vue"
import Graph from "./Graph.vue"
import Highlight from "./Highlight.vue"

export default {
  components: {
    Graph,
    ControlPanel,
    Highlight
},
  data() {
    return {
      reload: false,
      showText: true,
      overallStrength: 50,
      synonymStrength: 1,
      relationshipStrength: 0.2,
      colorVariation: 1,
      radius: 8,
      highlightedNode: null,
      highlightedLink: null
    }
  },
  methods: {
    highlightNode(node) {
      this.highlightedNode = node
    },
    highlightLink(link) {
      this.highlightedLink = link
    }
  }
}
</script>

<template>
  <Graph
    :show-text="showText"
    :overall-strength="overallStrength"
    :synonym-strength="synonymStrength"
    :relationship-strength="relationshipStrength"
    :color-variation="colorVariation"
    :radius="radius"
    :reload="reload"
    @highlight-node="highlightNode"
    @highlight-link="highlightLink"
    @finish-reload="reload = false"
  />
  <ControlPanel
    v-model:show-text="showText"
    v-model:overall-strength="overallStrength" 
    v-model:synonym-strength="synonymStrength"
    v-model:relationship-strength="relationshipStrength"
    v-model:color-variation="colorVariation"
    v-model:radius="radius"
    @reload="reload = true"
  />
  <Highlight
    :node="highlightedNode"
    :link="highlightedLink"
  />
</template>