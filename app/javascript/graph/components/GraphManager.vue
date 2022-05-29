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
      highlight: null
    }
  },
  methods: {
    updateHighlight(e) {
      this.highlight = e.target
    },
    startReload() {
      this.reload = true
    },
    finishReload() {
      this.reload = false
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
    :reload="reload"
    @update-highlight="updateHighlight"
    @finish-reload="finishReload"
  />
  <ControlPanel
    v-model:show-text="showText"
    v-model:overall-strength="overallStrength" 
    v-model:synonym-strength="synonymStrength"
    v-model:relationship-strength="relationshipStrength" 
    v-model:color-variation="colorVariation"
    @reload="startReload"
  />
  <Highlight :highlight="highlight" />
</template>