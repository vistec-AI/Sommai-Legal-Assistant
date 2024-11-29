import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

const ParseHTML = ({ markdown }: { markdown: string }) => {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      className="prose backdrop:whitespace-pre-line text-gray-600 break-words markdown marker:text-gray-600"
      components={{
        ul: ({ node, ...props }) => (
          <ul
            style={{
              display: "block",
              listStyleType: "disc",
            }}
            {...props}
          />
        ),
        ol: ({ node, ...props }) => (
          <ul
            style={{
              display: "block",
              listStyleType: "decimal",
            }}
            {...props}
          />
        ),
      }}
    >
      {markdown}
    </ReactMarkdown>
  );
};

export default ParseHTML;
