import type { ChipTone } from "../lib/vocab";

const TONE_CLASSES: Record<ChipTone, string> = {
  success: "bg-success-bg text-success border-success-border",
  warning: "bg-warning-bg text-warning border-warning-border",
  danger: "bg-danger-bg text-danger border-danger-border",
  neutral: "bg-neutral-bg text-neutral border-neutral-border",
};

export function StatusChip({ label, tone }: { label: string; tone: ChipTone }) {
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-md border px-2 py-0.5 text-xs font-medium ${TONE_CLASSES[tone]}`}
    >
      {label}
    </span>
  );
}
