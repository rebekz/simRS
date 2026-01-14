import * as React from "react"
import { cn } from "@/lib/utils"

const ModalBody = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      "flex-1 overflow-y-auto py-4",
      className
    )}
    {...props}
  />
))
ModalBody.displayName = "ModalBody"

export { ModalBody }
