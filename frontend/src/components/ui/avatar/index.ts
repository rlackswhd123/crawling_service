import type { VariantProps } from "class-variance-authority"
import { cva } from "class-variance-authority"

export { default as Avatar } from "./Avatar.vue"

export const avatarVariants = cva(
  "rounded-full bg-muted overflow-hidden flex items-center justify-center",
  {
    variants: {
      size: {
        sm: "w-8 h-8 text-xs",
        md: "w-10 h-10 text-sm",
        lg: "w-16 h-16 text-base",
      },
    },
    defaultVariants: {
      size: "md",
    },
  }
)

export type AvatarVariants = VariantProps<typeof avatarVariants>
