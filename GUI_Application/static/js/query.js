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
document.getElementById("submit-post-btn").addEventListener("click", async (event) => {
    const socialMedia = document.getElementById("social-media").value.trim();
    const postTime = document.getElementById("post-time").value.trim();
    const username = document.getElementById("username").value.trim();
    const firstName = document.getElementById("first-name").value.trim();
    const lastName = document.getElementById("last-name").value.trim();
  
    if (!socialMedia && !postTime && !username && !firstName && !lastName) {
        event.preventDefault();  // Prevent form submission
        alert("Please fill out at least one field.");
        return;
    }

    const params = new URLSearchParams({
        socialMedia,
        postTime,
        username,
        firstName,
        lastName
    });
  
    try {
        const response = await fetch(`/search-posts?${params.toString()}`);
        const data = await response.json();
  
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
  

// Query an experiment
document.getElementById("submit-exp-btn").addEventListener("click", async (event) => {
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

  
  