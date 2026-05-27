type Tone = "neutral" | "good" | "warn" | "bad";

export default function KPI({
  label,
  value,
  sub,
  tone = "neutral",
}: {
  label: string;
  value: string;
  sub?: string;
  tone?: Tone;
}) {
  const accentColor: Record<Tone, string> = {
    neutral: "var(--accent)",
    good: "var(--good)",
    warn: "var(--warn)",
    bad: "var(--bad)",
  };

  return (
    <div
      style={{
        background: "var(--surface)",
        border: "1px solid var(--border)",
        borderRadius: "var(--radius-lg)",
        borderLeft: `3px solid ${accentColor[tone]}`,
        padding: 14,
        boxShadow: "var(--shadow-sm)",
      }}
    >
      <div
        style={{
          fontSize: 11,
          color: "var(--fg-muted)",
          fontWeight: 600,
          textTransform: "uppercase",
          letterSpacing: "0.05em",
        }}
      >
        {label}
      </div>
      <div style={{ fontSize: 24, fontWeight: 700, marginTop: 6, color: "var(--fg)" }}>
        {value}
      </div>
      {sub && (
        <div style={{ fontSize: 12, color: "var(--fg-muted)", marginTop: 4 }}>
          {sub}
        </div>
      )}
    </div>
  );
}
