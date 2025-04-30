
function renderResults(data) {
    const container = document.getElementById("results-container");
    // Clear between queries
    container.innerHTML = ""; 
  
    if (data.queryType === "post") {
        data.results.forEach(post => {
            const card = document.createElement("div");
            card.className = "result-card";
            card.innerHTML = `
                <p><strong>Text:</strong> ${post.text}</p>
                <p><strong>Poster:</strong> ${post.socialMedia}, ${post.username}</p>
                <p><strong>Time:</strong> ${post.time}</p>
                <p><strong>Experiment(s):</strong> ${post.experiments.join(", ")}</p>
            `;
            container.appendChild(card);
        });
    }
  
    else if (data.queryType === "experiment") {
        const title = document.createElement("h2");
        title.textContent = `Experiment: ${data.experimentName}`;
        title.id = "experiment-title";
        container.appendChild(title);
  
        const summary = document.createElement("div");
        summary.id = "field-summary";
  
        data.fields.forEach(field => {
            const row = document.createElement("div");
            row.className = "field-row";
            row.innerHTML = `
                <span class="field-name">${field.name}</span>
                <span class="field-percent">${field.percent}%</span>
            `;
            summary.appendChild(row);
        });
  
        container.appendChild(summary);
  
        data.posts.forEach(post => {
            const card = document.createElement("div");
            card.className = "result-card";
            card.innerHTML = `
                <p><strong>Post:</strong> ${post.text}</p>
                <p><strong>Result(s):</strong> ${post.results.join(", ")}</p>
            `;
            container.appendChild(card);
        });
    }
}
  
// replace this with a fetch() call or data passed from query.html
window.addEventListener("DOMContentLoaded", () => {
    const storedData = JSON.parse(localStorage.getItem("lastQuery"));
    if (storedData) renderResults(storedData);
});
  