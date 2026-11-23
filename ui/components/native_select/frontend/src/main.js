const root = document.getElementById("root");
const label = document.createElement("label");
const labelText = document.createElement("span");
const select = document.createElement("select");
const style = document.createElement("style");
const renderEvent = "streamlit:render";

style.textContent = `
  :root { color-scheme: light; font-family: system-ui, -apple-system, "Segoe UI", sans-serif; }
  * { box-sizing: border-box; }
  body { margin: 0; color: #172b4d; }
  label { display: block; margin: 0 0 0.35rem; font-size: 0.875rem; line-height: 1.3; }
  select {
    display: block; width: 100%; min-height: 48px; padding: 0.65rem 2.4rem 0.65rem 0.8rem;
    border: 1px solid #cbd5e1; border-radius: 10px; background: #fff; color: #1e293b;
    font: inherit; font-size: 1rem;
  }
  select:focus { outline: 2px solid #818cf8; outline-offset: 1px; }
  select:disabled { background: #f1f5f9; color: #64748b; }
`;

label.append(labelText, select);
root.append(style, label);

function render(event) {
  const { args, disabled } = event.data;
  labelText.textContent = args.label;
  select.setAttribute("aria-label", args.label);
  select.replaceChildren();

  args.options.forEach((text, index) => {
    const option = document.createElement("option");
    option.value = String(index);
    option.textContent = text;
    select.appendChild(option);
  });

  const initialIndex = args.values.findIndex((value) =>
    Object.is(value, args.selected_value)
  );
  select.value = String(
    Number.isInteger(initialIndex) && initialIndex >= 0 && initialIndex < args.options.length
      ? initialIndex
      : 0
  );
  select.disabled = Boolean(disabled);
  select.onchange = () => send("streamlit:setComponentValue", {
    value: args.values[Number(select.value)],
    dataType: "json"
  });
  send("streamlit:setFrameHeight", { height: 86 });
}

function send(type, data) {
  window.parent.postMessage(
    { isStreamlitMessage: true, type, ...data },
    "*"
  );
}

window.addEventListener("message", (event) => {
  if (event.data?.type === renderEvent) {
    render(event);
  }
});

send("streamlit:componentReady", { apiVersion: 1 });
send("streamlit:setFrameHeight", { height: 86 });
