onmessage = (event) => {
  importScripts('//cdnjs.cloudflare.com/ajax/libs/highlight.js/9.15.6/highlight.min.js');
  const result = self.hljs.highlightAuto(event.data);
  postMessage(result.value);
};
