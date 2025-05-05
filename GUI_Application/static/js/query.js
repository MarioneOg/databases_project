console.log("query.js is running");


const buttons = document.querySelectorAll('.entry-button');

const postForm = document.getElementById('post-form');
const experimentForm = document.getElementById('experiment-form');

// Toggle visibility of text fields and selection
buttons.forEach(button => {
    button.addEventListener('click', () => {
        const isSelected = button.classList.contains('selected');
  
        buttons.forEach(btn => btn.classList.remove('selected'));
  
        postForm.classList.add('hidden');
        experimentForm.classList.add('hidden');
  
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
  

// Query a post
document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("submit-post-btn").addEventListener("click", async (event) => {
        event.preventDefault();  

        const username = document.getElementById("username").value.trim();
        const social_media = document.getElementById("social-media").value.trim();
        const post_time = document.getElementById("post-time").value.trim();
        const first_name = document.getElementById("first-name").value.trim();
        const last_name = document.getElementById("last-name").value.trim();

        if (!social_media || !post_time || !username) {
            alert("Please fill out the required fields.");
            return;
        }

        const params = new URLSearchParams({
            username,
            social_media,
            post_time,
            first_name,
            last_name
        });

        try {
            const response = await fetch(`/search-posts?${params.toString()}`);
        
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
        
            const data = await response.json();
            console.log("Parsed JSON:", data);
        
            localStorage.setItem("lastQuery", JSON.stringify({
                queryType: "post",
                results: data
            }));
        
            window.location.href = `/post-results?${params.toString()}`;
        } catch (err) {
            console.error("Failed to fetch results:", err);
            alert("An error occurred while querying the backend.");
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

  
  