<script setup lang="ts">
import { cn } from "@/lib/utils"
import { labelVariants } from "."

interface Props {
  for?: string
  required?: boolean
  class?: string
}

const props = defineProps<Props>()
</script>

<template>
  <label
    :for="props.for"
    :class="cn(labelVariants(), props.class)"
  >
    <slot />
    <span v-if="props.required" class="text-destructive ml-1">*</span>
  </label>
</template>
