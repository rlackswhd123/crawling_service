import type { VariantProps } from "class-variance-authority"
import { cva } from "class-variance-authority"

export { default as RadioGroup } from "./RadioGroup.vue"

export const radioGroupVariants = cva("space-y-2")

export type RadioGroupVariants = VariantProps<typeof radioGroupVariants>
