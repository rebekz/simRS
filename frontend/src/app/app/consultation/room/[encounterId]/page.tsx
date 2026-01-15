"use client"

import { useParams } from "next/navigation"
import { ConsultationWorkspace } from "@/components/consultation/ConsultationWorkspace"

export default function ConsultationWorkspacePage() {
  const params = useParams()
  const encounterId = params.encounterId ? parseInt(params.encounterId as string) : undefined

  return (
    <div className="h-screen">
      <ConsultationWorkspace patientId={0} encounterId={encounterId} />
    </div>
  )
}
