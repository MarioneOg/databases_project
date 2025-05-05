document.addEventListener("DOMContentLoaded", () => {

    const buttons = document.querySelectorAll('.entry-button');
    
    const projectForm = document.getElementById('project-form');
    const postForm = document.getElementById('post-form');
    const analysisForm = document.getElementById('analysis-form');
    
    // Add event listeners to toggle visibility of forms when buttons are clicked
    buttons.forEach(button => {
        button.addEventListener('click', () => {
            const isSelected = button.classList.contains('selected');
    
            buttons.forEach(btn => btn.classList.remove('selected'));
            projectForm.classList.add('hidden');
            postForm.classList.add('hidden');
            analysisForm.classList.add('hidden');
    
            if (!isSelected) {
                button.classList.add('selected');
    
                if (button.id === 'project-btn') {
                    projectForm.classList.remove('hidden');
                } else if (button.id === 'posts-btn') {
                    postForm.classList.remove('hidden');
                } else if (button.id === 'analysis-btn') {
                    analysisForm.classList.remove('hidden');
                }
            }
        });
    });
    
    // Handle project form submission
    document.getElementById("submit-project").addEventListener("click", (event) => {
        event.preventDefault(); 
    
        let startDate = document.getElementById("start-date").value.trim();
        let endDate = document.getElementById("end-date").value.trim();
        
        // Date validation check
        if(endDate && startDate && new Date(endDate) < new Date(startDate)){
            alert("End date cannot be earlier than the start date.");
            return;
        }
    
        const form = document.getElementById('project-form');
        const formData = new FormData(form);
        
        // Check required fields
        if (!formData.get('project_name')) {
            alert('Project name is required.');
            return;
        }
        
        // Print data to console (for debugging)
        console.log("Project submission:");
        for (let pair of formData.entries()) {
            console.log(pair[0] + ': ' + pair[1]);
        }
        
        // send data
        fetch(form.action, {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Server response error: ' + response.status);
            }
            return response.text();
        })
        .then(data => {
            console.log("Server response:", data);
            alert("Project added successfully!");
            window.location.reload(); // Refresh the page
        })
        .catch(error => {
            console.error("Error submitting project:", error);
            alert("Error adding project.");
        });
    });
    
    // Handle post form submission and validation
    document.getElementById("submit-post").addEventListener("click", (event) => {
        event.preventDefault(); 
        const ageValue = document.getElementById("age").value.trim();
        const likes = document.getElementById("likes").value.trim();
        const dislikes = document.getElementById("dislikes").value.trim();
    
        if (isNaN(ageValue) || Number(ageValue) < 0) {
            alert("Age must be a non-negative number.");
            return; // Stop form submission
        }
    
        if (isNaN(likes) || Number(likes) < 0) {
            alert("Likes must be a non-negative number.");
            return; // Stop form submission
        }
    
        if (isNaN(dislikes) || Number(dislikes) < 0) {
            alert("Dislikes must be a non-negative number.");
            return; // Stop form submission
        }
    
        const postData = {
            project_name: document.getElementById("post-project-name").value.trim(),
            userInfo: {
                username: document.getElementById("username").value.trim(),
                social_media: document.getElementById("social-media").value.trim(),
                first_name: document.getElementById("first-name").value.trim(),
                last_name: document.getElementById("last-name").value.trim(),
                country_birth: document.getElementById("country-birth").value.trim(),
                country_residence: document.getElementById("country-residence").value.trim(),
                age: document.getElementById("age").value.trim(),
                gender: document.getElementById("gender").value.trim(),
                verified: document.getElementById("verified").value.trim()
            },
            originalPost: {
                post_time: document.getElementById("post-time").value.trim(),
                post_text: document.getElementById("text").value.trim(),
                post_likes: document.getElementById("likes").value.trim(),
                post_dislikes: document.getElementById("dislikes").value.trim(),
                post_city: document.getElementById("city").value.trim(),
                post_state: document.getElementById("state").value.trim(),
                post_country: document.getElementById("country").value.trim(),
                post_multimedia: document.getElementById("multimedia").value.trim()
            },
            repost: {
                repost_username: document.getElementById("repost-username").value.trim(),
                repost_social_media: document.getElementById("repost-social-media").value.trim(),
                repost_time: document.getElementById("repost-time").value.trim(),
                repost_city: document.getElementById("repost-city").value.trim(),
                repost_state: document.getElementById("repost-state").value.trim(),
                repost_country: document.getElementById("repost-country").value.trim(),
                repost_likes: document.getElementById("repost-likes").value.trim(),
                repost_dislikes: document.getElementById("repost-dislikes").value.trim(),
                repost_hasMedia: document.getElementById("repost-multimedia").value.trim()
            }
        };
    
        console.log("Post submission:", postData);
    
        fetch("/posts/add", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(postData)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error("Network response was not ok");
            }
            return response.text();  // or .json() if your backend returns JSON
        })
        .then(data => {
            console.log("Server response:", data);
            alert("Post added successfully!");
            window.location.href = "/entry";  // redirect if desired
        })
        .catch(error => {
            console.error("Error submitting post:", error);
            alert("Error submitting post.");
        });
    });
    
    // Handle analysis form submission
    document.getElementById("submit-analysis").addEventListener("click", (event) => {
        event.preventDefault();
        
        const form = document.getElementById('analysis-form');
        const formData = new FormData(form);
        
        // Check required fields
        if (!formData.get('project_name') || !formData.get('username') || 
            !formData.get('social_media') || !formData.get('post_time') || 
            !formData.get('field_name')) {
            alert('All required fields must be completed.');
            return;
        }
        
        // Print data to console (for debugging)
        console.log("Analysis submission:");
        for (let pair of formData.entries()) {
            console.log(pair[0] + ': ' + pair[1]);
        }
        
        // Send data to server
        fetch(form.action, {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Server response error: ' + response.status);
            }
            return response.text();
        })
        .then(data => {
            console.log("Server response:", data);
            alert("Analysis added successfully!");
            window.location.reload(); // Refresh the page
        })
        .catch(error => {
            console.error("Error submitting analysis:", error);
            alert("Error adding analysis.");
        });
    });
    
    });