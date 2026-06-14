
interface MarkdownTextProps {
  content: string;
}

export function MarkdownText({ content }: MarkdownTextProps) {
  const lines = content.split("\n");

  return (
    <div className="space-y-2">
      {lines.map((line, idx) => {
        const isBullet = line.trim().startsWith("-");
        const textContent = isBullet ? line.trim().substring(1).trim() : line;

        const parts = textContent.split(/(\*\*.*?\*\*|\*.*?\*)/g);

        return (
          <div
            key={idx}
            className={isBullet ? "ml-4 flex gap-2" : ""}
          >
            {isBullet && <span>•</span>}
            <div>
              {parts.map((part, i) => {
                if (part.startsWith("**") && part.endsWith("**")) {
                  return (
                    <strong key={i}>
                      {part.slice(2, -2)}
                    </strong>
                  );
                }
                if (part.startsWith("*") && part.endsWith("*")) {
                  return (
                    <em key={i}>
                      {part.slice(1, -1)}
                    </em>
                  );
                }
                return <span key={i}>{part}</span>;
              })}
            </div>
          </div>
        );
      })}
    </div>
  );
}
