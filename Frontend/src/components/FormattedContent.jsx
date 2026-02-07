import React from 'react';

/**
 * Component to render formatted educational content with proper markdown and emoji support
 * Handles bullets, numbers, bold text, headers, and various formatting
 */
export default function FormattedContent({ content }) {
  if (!content) return null;

  const parseContent = (text) => {
    // Split by double newlines to get paragraphs
    const paragraphs = text.split('\n\n').filter(p => p.trim());
    
    return paragraphs.map((para, paraIdx) => {
      // Check if it's a markdown header
      if (/^#{1,6}\s+/.test(para.trim())) {
        const match = para.trim().match(/^(#{1,6})\s+(.+)$/);
        if (match) {
          const level = match[1].length;
          const content = match[2];
          const HeaderTag = `h${level + 1}`;
          return (
            <div key={paraIdx} className={`formatted-header h${level}`}>
              {parseInlineElements(content)}
            </div>
          );
        }
      }

      // Check if it's a list (contains bullets or numbers)
      const lines = para.split('\n');
      
      // Check for bulleted list
      if (lines.some(line => /^\s*[-•*]\s/.test(line.trim()))) {
        return (
          <ul key={paraIdx} className="formatted-list">
            {lines.map((line, lineIdx) => {
              const trimmed = line.trim();
              if (/^\s*[-•*]\s/.test(trimmed)) {
                const content = trimmed.replace(/^[-•*]\s+/, '');
                return (
                  <li key={lineIdx} className="formatted-list-item">
                    {parseInlineElements(content)}
                  </li>
                );
              }
              return null;
            })}
          </ul>
        );
      }
      
      // Check for numbered list
      if (lines.some(line => /^\s*\d+[.)]\s/.test(line.trim()))) {
        return (
          <ol key={paraIdx} className="formatted-numbered-list">
            {lines.map((line, lineIdx) => {
              const trimmed = line.trim();
              const match = trimmed.match(/^\d+[.)]\s+(.+)/);
              if (match) {
                return (
                  <li key={lineIdx} className="formatted-list-item">
                    {parseInlineElements(match[1])}
                  </li>
                );
              }
              return null;
            })}
          </ol>
        );
      }
      
      // Regular paragraph
      return (
        <p key={paraIdx} className="formatted-paragraph">
          {parseInlineElements(para)}
        </p>
      );
    });
  };

  const parseInlineElements = (text) => {
    if (!text) return null;
    
    const parts = [];
    let lastIndex = 0;
    
    // Pattern to match **bold**, _italic_, `code`, and URLs
    const patterns = [
      { regex: /\*\*(.+?)\*\*/g, type: 'bold', tag: 'strong' },
      { regex: /_(.+?)_/g, type: 'italic', tag: 'em' },
      { regex: /`(.+?)`/g, type: 'code', tag: 'code' },
    ];
    
    // Collect all matches with their positions
    const matches = [];
    patterns.forEach(({ regex, type, tag }) => {
      let match;
      while ((match = regex.exec(text)) !== null) {
        matches.push({
          start: match.index,
          end: match.index + match[0].length,
          content: match[1],
          tag: tag,
        });
      }
    });
    
    // Sort matches by start position
    matches.sort((a, b) => a.start - b.start);
    
    // Remove overlapping matches
    const filtered = [];
    matches.forEach(match => {
      const overlaps = filtered.some(
        m => (match.start < m.end && match.end > m.start)
      );
      if (!overlaps) {
        filtered.push(match);
      }
    });
    
    // Build the result
    lastIndex = 0;
    filtered.forEach((match, idx) => {
      if (lastIndex < match.start) {
        parts.push(text.substring(lastIndex, match.start));
      }
      
      const Tag = match.tag;
      parts.push(
        <Tag key={`match-${idx}`} className={`formatted-${match.tag}`}>
          {match.content}
        </Tag>
      );
      
      lastIndex = match.end;
    });
    
    if (lastIndex < text.length) {
      parts.push(text.substring(lastIndex));
    }
    
    return parts.length > 0 ? parts : text;
  };

  return (
    <div className="formatted-content">
      {parseContent(content)}
    </div>
  );
}
