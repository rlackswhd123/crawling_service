<script setup lang="ts">
import { Primitive } from "reka-ui"
import { cn } from "@/lib/utils"
import { radioGroupVariants } from "."

interface Option {
  label: string
  value: string
}

interface Props {
  modelValue: string
  options: Option[]
  name?: string
  class?: string
}

const props = defineProps<Props>()
const emit = defineEmits(["update:modelValue"])
</script>

<template>
  <div :class="cn(radioGroupVariants(), props.class)">
    <div
      v-for="opt in props.options"
      :key="opt.value"
      class="flex items-center space-x-2"
    >
      <input
        type="radio"
        :id="opt.value"
        :name="props.name"
        :value="opt.value"
        :checked="opt.value === props.modelValue"
        @change="emit('update:modelValue', opt.value)"
        class="h-4 w-4 text-primary border-gray-300 focus:ring-primary"
      />
      <label
        :for="opt.value"
        class="text-sm font-medium text-gray-700 cursor-pointer"
      >
        {{ opt.label }}
      </label>
    </div>
  </div>
</template>
