"use client";

import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import rehypeRaw from 'rehype-raw';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import 'katex/dist/katex.min.css';

interface MarkdownRendererProps {
  content: string;
}

export default function MarkdownRenderer({ content }: MarkdownRendererProps) {
  return (
    <div className="prose prose-invert max-w-none markdown-content overflow-x-auto">
      <style jsx global>{`
        .markdown-content {
          font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
          font-size: 15px;
          line-height: 1.8;
          color: #e5e5e5;
        }
        .markdown-content strong {
          font-weight: 600;
          color: #f0f0f0;
        }
        .markdown-content h1, .markdown-content h2, .markdown-content h3 {
          font-weight: 600;
          letter-spacing: -0.01em;
        }
        .markdown-content ul, .markdown-content ol {
          padding-left: 1.5rem;
        }
        .markdown-content li {
          margin-top: 0.6rem;
          margin-bottom: 0.6rem;
          line-height: 1.75;
        }
        .markdown-content p {
          margin-top: 1.25rem;
          margin-bottom: 1.25rem;
          line-height: 1.8;
        }
      `}</style>
      <ReactMarkdown
        remarkPlugins={[remarkGfm, remarkMath]}
        rehypePlugins={[rehypeKatex, rehypeRaw]}
        components={{
          // Custom rendering for images
          img: ({ node, ...props }) => (
            <img
              {...props}
              className="max-w-full h-auto rounded-lg my-4 shadow-lg"
              alt={props.alt || 'Image'}
              loading="lazy"
            />
          ),
          // Custom rendering for videos
          video: ({ node, ...props }) => (
            <video
              {...props}
              className="max-w-full h-auto rounded-lg my-4 shadow-lg"
              controls
            />
          ),
          // Custom rendering for tables
          table: ({ node, ...props }) => (
            <div className="overflow-x-auto my-4 rounded-lg border border-gray-700">
              <table className="min-w-full border-collapse" {...props} />
            </div>
          ),
          thead: ({ node, ...props }) => (
            <thead className="bg-gray-800" {...props} />
          ),
          th: ({ node, ...props }) => (
            <th className="border border-gray-700 px-4 py-3 text-left font-semibold" {...props} />
          ),
          td: ({ node, ...props }) => (
            <td className="border border-gray-700 px-4 py-2" {...props} />
          ),
          tr: ({ node, ...props }) => (
            <tr className="hover:bg-gray-800/50 transition-colors" {...props} />
          ),
          // Custom rendering for code blocks with syntax highlighting
          code: ({ node, inline, className, children, ...props }: any) => {
            const match = /language-(\w+)/.exec(className || '');
            const language = match ? match[1] : '';
            
            if (inline) {
              return (
                <code className="bg-gray-800/70 px-1.5 py-0.5 rounded text-sm font-mono text-blue-300" {...props}>
                  {children}
                </code>
              );
            }
            
            return (
              <div className="my-4 rounded-lg overflow-x-auto overflow-hidden">
                <div className="bg-gray-900 px-4 py-2 text-xs text-gray-400 border-b border-gray-700 font-mono">
                  {language || 'code'}
                </div>
                <SyntaxHighlighter
                  style={vscDarkPlus}
                  language={language || 'text'}
                  PreTag="div"
                  className="!m-0 !rounded-none"
                  wrapLongLines={true}
                  {...props}
                >
                  {String(children).replace(/\n$/, '')}
                </SyntaxHighlighter>
              </div>
            );
          },
          // Custom rendering for links
          a: ({ node, ...props }) => (
            <a
              {...props}
              className="text-blue-400 hover:text-blue-300 underline transition-colors"
              target="_blank"
              rel="noopener noreferrer"
            />
          ),
          // Custom rendering for blockquotes
          blockquote: ({ node, ...props }) => (
            <blockquote className="border-l-4 border-blue-500/50 pl-4 py-1 italic my-3 text-gray-300" {...props} />
          ),
          // Custom rendering for lists - better spacing like ChatGPT
          ul: ({ node, ...props }) => (
            <ul className="space-y-2 my-3" {...props} />
          ),
          ol: ({ node, ...props }) => (
            <ol className="space-y-2 my-3" {...props} />
          ),
          li: ({ node, ...props }) => (
            <li className="leading-relaxed" {...props} />
          ),
          // Headings - cleaner, more ChatGPT-like
          h1: ({ node, ...props }) => (
            <h1 className="text-2xl font-semibold mt-6 mb-3 text-white" {...props} />
          ),
          h2: ({ node, ...props }) => (
            <h2 className="text-xl font-semibold mt-5 mb-2.5 text-white" {...props} />
          ),
          h3: ({ node, ...props }) => (
            <h3 className="text-lg font-semibold mt-4 mb-2 text-white" {...props} />
          ),
          h4: ({ node, ...props }) => (
            <h4 className="text-base font-semibold mt-3 mb-1.5 text-white" {...props} />
          ),
          // Paragraphs - better spacing
          p: ({ node, ...props }) => (
            <p className="mb-4 leading-relaxed text-gray-200" {...props} />
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}
