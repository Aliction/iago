def patternize_headers(headers):
  patterns=[]
  for header in headers:
      pattern = '.*{' + header + '}.*'
      patterns.append(pattern)
  return patterns
