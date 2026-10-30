const run = () => {
    const bodyFont = getComputedStyle(document.body).fontFamily;
    console.log("Body Font:",bodyFont);
    const style = document.createElement('style');
    style.textContent = `span.katex span.mord.text { font-family: ${bodyFont} !important; }`;
    document.head.appendChild(style);
};
if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", run, { once: true });
} else {
    run();
}