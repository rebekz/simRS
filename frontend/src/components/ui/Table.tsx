import * as React from "react"
import { cn } from "@/lib/utils"
import { ChevronUp, ChevronDown } from "lucide-react"

export interface Column<T> {
  key: string
  title: string
  sortable?: boolean
  render?: (value: any, row: T, index: number) => React.ReactNode
  className?: string
}

interface TableProps<T> {
  data: T[]
  columns: Column<T>[]
  sortable?: boolean
  onSort?: (column: string) => void
  sortColumn?: string
  sortDirection?: "asc" | "desc"
  className?: string
}

export function Table<T extends Record<string, any>>({
  data,
  columns,
  sortable = false,
  onSort,
  sortColumn,
  sortDirection = "asc",
  className,
}: TableProps<T>) {
  const [internalSortColumn, setInternalSortColumn] = React.useState<string>("")
  const [internalSortDirection, setInternalSortDirection] = React.useState<"asc" | "desc">("asc")

  const handleSort = (column: string, columnSortable?: boolean) => {
    if (!sortable || !(columnSortable ?? true)) return

    const currentSortColumn = sortColumn ?? internalSortColumn
    const currentDirection = sortDirection ?? internalSortDirection

    if (onSort) {
      onSort(column)
    } else {
      if (currentSortColumn === column) {
        setInternalSortDirection(currentDirection === "asc" ? "desc" : "asc")
      } else {
        setInternalSortColumn(column)
        setInternalSortDirection("asc")
      }
    }
  }

  const sortedData = React.useMemo(() => {
    if (!sortable) return data

    const activeSortColumn = sortColumn ?? internalSortColumn
    const activeDirection = sortDirection ?? internalSortDirection

    if (!activeSortColumn) return data

    return [...data].sort((a, b) => {
      const aValue = a[activeSortColumn]
      const bValue = b[activeSortColumn]

      if (aValue === bValue) return 0
      if (aValue === null || aValue === undefined) return 1
      if (bValue === null || bValue === undefined) return -1

      const comparison = aValue < bValue ? -1 : 1
      return activeDirection === "asc" ? comparison : -comparison
    })
  }, [data, sortable, sortColumn, internalSortColumn, sortDirection, internalSortDirection])

  const activeSortColumn = sortColumn ?? internalSortColumn
  const activeDirection = sortDirection ?? internalSortDirection

  return (
    <div className={cn("w-full overflow-auto", className)}>
      <table className="w-full caption-bottom text-sm">
        <thead className="[&_tr]:border-b">
          <tr className="border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted">
            {columns.map((column) => {
              const isSortable = sortable && (column.sortable ?? true)
              const isActive = activeSortColumn === column.key

              return (
                <th
                  key={column.key}
                  className={cn(
                    "h-12 px-4 text-left align-middle font-medium text-muted-foreground",
                    isSortable && "cursor-pointer hover:text-foreground select-none",
                    isActive && "text-foreground",
                    column.className
                  )}
                  onClick={() => handleSort(column.key, column.sortable)}
                >
                  <div className="flex items-center gap-2">
                    {column.title}
                    {isSortable && (
                      <span className="flex items-center">
                        {isActive ? (
                          activeDirection === "asc" ? (
                            <ChevronUp className="h-4 w-4" />
                          ) : (
                            <ChevronDown className="h-4 w-4" />
                          )
                        ) : (
                          <div className="flex h-4 w-4 flex-col items-center justify-center opacity-30">
                            <ChevronUp className="h-3 w-3 -mb-1" />
                            <ChevronDown className="h-3 w-3 -mt-1" />
                          </div>
                        )}
                      </span>
                    )}
                  </div>
                </th>
              )
            })}
          </tr>
        </thead>
        <tbody className="[&_tr:last-child]:border-0">
          {sortedData.map((row, rowIndex) => (
            <tr
              key={rowIndex}
              className="border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted"
            >
              {columns.map((column) => (
                <td
                  key={column.key}
                  className={cn("p-4 align-middle", column.className)}
                >
                  {column.render
                    ? column.render(row[column.key], row, rowIndex)
                    : String(row[column.key] ?? "")}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      {sortedData.length === 0 && (
        <div className="flex h-24 items-center justify-center text-muted-foreground">
          No data available
        </div>
      )}
    </div>
  )
}
