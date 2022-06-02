<script>
export default {
  props: {
    showText: Boolean,
    overallStrength: Number,
    synonymStrength: Number,
    relationshipStrength: Number,
    colorVariation: Number,
    textSize: Number,
    radius: Number
  },
  emits: [
    "reload",
    "update:showText",
    "update:overallStrength",
    "update:synonymStrength",
    "update:relationshipStrength",
    "update:colorVariation",
    "update:textSize",
    "update:radius"
  ]
}
</script>

<template>
  <div class="absolute bottom-4 left-4">
    <div class="flex mb-1">
      <div class="mx-2" @click="$emit('reload')"><i class="fas fa-sync-alt"></i></div>
      <div class="mx-2" @click="$emit('update:showText', !showText)"><i class="fas fa-eye" :class="{ 'text-gray-500': !showText }"></i></div>
    </div>
    <label class="flex justify-between mb-1">
    Força - Geral:
    <input id="overall-strength" type="range" min="5" max="200" step="1" :value="overallStrength" @change="$emit('update:overallStrength', parseFloat($event.target.value))" />
    </label>
    <label class="flex justify-between mb-1">
    Força - Sinônimos:
    <input id="synonym-strength" type="range" min="0" max="3" step="0.1" :value="synonymStrength" @change="$emit('update:synonymStrength', parseFloat($event.target.value))" />
    </label>
    <label class="flex justify-between mb-1">
    Força - Relações:
    <input id="relationship-strength" type="range" min="0" max="2" step="0.1" :value="relationshipStrength" @change="$emit('update:relationshipStrength', parseFloat($event.target.value))" />
    </label>
    <label class="flex justify-between mb-1">
    Variação de Cores:
    <input id="color-variation" type="range" min="0" max="1" step="0.05" :value="colorVariation" @change="$emit('update:colorVariation', parseFloat($event.target.value))" />
    </label>
    <label class="flex justify-between mb-1">
    Tamanho do Texto:
    <input id="radius" type="range" min="0.2" max="2" step="0.05" :value="textSize" @change="$emit('update:textSize', parseFloat($event.target.value))" />
    </label>
    <label class="flex justify-between">
    Raio:
    <input id="radius" type="range" min="1" max="16" step="1" :value="radius" @change="$emit('update:radius', parseFloat($event.target.value))" />
    </label>
  </div>
</template>