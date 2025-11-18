<script setup lang="ts">
import { ref } from "vue"
import { cn } from "@/lib/utils"
import { avatarVariants } from "."

interface Props {
  src?: string
  alt?: string
  fallback?: string
  size?: "sm" | "md" | "lg"
  class?: string
}

const props = withDefaults(defineProps<Props>(), {
  alt: "avatar",
  fallback: "U",
  size: "md",
})

const imageError = ref(false)
</script>

<template>
  <div :class="cn(avatarVariants({ size: props.size }), props.class)">
    <img
      v-if="props.src && !imageError"
      :src="props.src"
      :alt="props.alt"
      class="object-cover w-full h-full rounded-full"
      @error="imageError = true"
    />
    <span v-else class="text-gray-500 font-medium">{{ props.fallback }}</span>
  </div>
</template>
