interface StatRowProps {
  label: string;
  valueA: number;
  valueB: number;
  format?: (value: number, player: "a" | "b") => string;
}

export default function StatRow({ label, valueA, valueB, format }: StatRowProps) {
  return (
    <tr className="border-t border-white/10">
      <td className={`py-4 pr-2 text-left font-semibold tabular-nums sm:pr-6 ${valueA > valueB ? "text-accent" : "text-foreground"}`}>
        {format ? format(valueA, "a") : valueA.toLocaleString("en-US")}
      </td>
      <th scope="row" className="px-2 py-4 text-center text-sm font-normal text-muted">
        {label}
      </th>
      <td className={`py-4 pl-2 text-right font-semibold tabular-nums sm:pl-6 ${valueB > valueA ? "text-accent" : "text-foreground"}`}>
        {format ? format(valueB, "b") : valueB.toLocaleString("en-US")}
      </td>
    </tr>
  );
}
