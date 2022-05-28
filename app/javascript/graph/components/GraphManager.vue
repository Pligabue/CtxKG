<script>
import ControlPanel from "./ControlPanel.vue"
import Graph from "./Graph.vue"

export default {
  components: {
    Graph,
    ControlPanel
  },
  data() {
    return {
      showText: true,
      overallStrength: 10,
      synonymStrength: 1,
      relationshipStrength: 0.2,
      colorVariation: 1
    }
  },
  created() {
    
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
  />
  <ControlPanel
    v-model:show-text="showText"
    v-model:overall-strength="overallStrength" 
    v-model:synonym-strength="synonymStrength"
    v-model:relationship-strength="relationshipStrength" 
    v-model:color-variation="colorVariation"
  />
</template>