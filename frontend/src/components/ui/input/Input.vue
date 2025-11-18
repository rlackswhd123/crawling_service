<script setup lang="ts">
import type { PrimitiveProps } from "reka-ui"
import type { HTMLAttributes } from "vue"
import { Primitive } from "reka-ui"
import { cn } from "@/lib/utils"
import { inputVariants } from "."

interface Props extends PrimitiveProps {
  modelValue?: string
  class?: HTMLAttributes["class"]
}

const props = withDefaults(defineProps<Props>(), {
  as: "input",
})

const emit = defineEmits(["update:modelValue"])
</script>

<template>
  <Primitive
    data-slot="input"
    :as="as"
    :as-child="asChild"
    :value="props.modelValue"
    @input="emit('update:modelValue', $event.target.value)"
    :class="cn(inputVariants(), props.class)"
  >
    <slot />
  </Primitive>
</template>
