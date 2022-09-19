function copyText(text, tooltip) {
    navigator.clipboard.writeText(text);
    //var tooltip = document.getElementById(tooltip);
    //tooltip.setAttribute('data-bs-original-title', "Copied: " + text);
}

function tooltipOutFunc(tooltip) {
    //var tooltip = document.getElementById(tooltip);
    //tooltip.setAttribute('data-bs-original-title', "Copy to clipboard");
}