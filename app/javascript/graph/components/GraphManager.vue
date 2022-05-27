<script>
import ControlPanel from "./ControlPanel.vue"

export default {
  components: {
    ControlPanel
  },
  data() {
    return {
      baseGraphUrl: window.location.pathname + "json",
      nodes: [],
      relationshipLinks: [],
      synonymlinks: [],
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
  <ControlPanel
    v-model:show-text="showText"
    v-model:overall-strength="overallStrength" 
    v-model:synonym-strength="synonymStrength"
    v-model:relationship-strength="relationshipStrength" 
    v-model:color-variation="colorVariation"
  />
</template>