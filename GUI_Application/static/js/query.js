console.log("query.js is running");


const buttons = document.querySelectorAll('.entry-button');

const postForm = document.getElementById('post-form');
const experimentForm = document.getElementById('experiment-form');
const flashContainer = document.getElementById('flash-container');

// Toggle visibility of text fields and selection
buttons.forEach(button => {
    button.addEventListener('click', () => {
        const isSelected = button.classList.contains('selected');
  
        buttons.forEach(btn => btn.classList.remove('selected'));
  
        postForm.classList.add('hidden');
        experimentForm.classList.add('hidden');

        if (flashContainer) {
            flashContainer.style.display = 'none';
        }
  
        if (!isSelected) {
            button.classList.add('selected');
  
            if (button.id === 'project-btn') {
                postForm.classList.remove('hidden');
            } else if (button.id === 'posts-btn') {
                experimentForm.classList.remove('hidden');
            } 
        }
    });
});
  

// Query an experiment
document.getElementById("submit-exp-btn").addEventListener("click", async (event) => {
    event.preventDefault();  

    const experimentName = document.getElementById("experiment-name").value.trim();

    const params = new URLSearchParams({
        experiment_name: experimentName
    });
  
    try {
        
        const response = await fetch(`/search-experiment?${params.toString()}`);
        const data = await response.json();
  
        localStorage.setItem("lastQuery", JSON.stringify({
            queryType: "experiment",
            experimentName,
            // Assuming these things are called "fields" and "posts" in the json, these should be lists
            fields: data.fields,   
            posts: data.posts
        }));
  
        window.location.href = "/results";
    } catch (err) {
        console.error("Failed to fetch experiment data:", err);
        alert("Error querying experiment.");
    }
});

  
  