function navigateTo(pageId) {
    const pages = document.querySelectorAll('.page');
    pages.forEach(page => {
        page.classList.remove('active');
    });

    document.getElementById(pageId).classList.add('active');
}

document.getElementById("run-sql-btn").addEventListener("click", () => {
    fetch("/connect-db", { method: "POST" })
        .then(res => res.json())
        .then(data => {
            alert(data.status === "success" ? "Database initialized!" : "Error: " + data.message);
        });
});


