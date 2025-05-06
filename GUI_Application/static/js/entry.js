document.addEventListener("DOMContentLoaded", () => {

    const buttons = document.querySelectorAll('.entry-button');
    
    const projectForm = document.getElementById('project-form');
    const userForm = document.getElementById('user-form');
    const postForm = document.getElementById('post-form');
    const analysisForm = document.getElementById('analysis-form');
    const flashContainer = document.getElementById('flash-container');
    
    // Toggle visibility of text fields and selection
    buttons.forEach(button => {
        button.addEventListener('click', () => {
            const isSelected = button.classList.contains('selected');
    
            buttons.forEach(btn => btn.classList.remove('selected'));
            projectForm.classList.add('hidden');
            userForm.classList.add('hidden');  // Added this line to hide user form
            postForm.classList.add('hidden');
            analysisForm.classList.add('hidden');

            if (flashContainer) {
                flashContainer.style.display = 'none';
            }
    
            if (!isSelected) {
                button.classList.add('selected');
    
                if (button.id === 'project-btn') {
                    projectForm.classList.remove('hidden');
                } else if (button.id === 'posts-btn') {
                    postForm.classList.remove('hidden');
                } else if (button.id === 'analysis-btn') {
                    analysisForm.classList.remove('hidden');
                } else if (button.id === 'user-btn') {
                    userForm.classList.remove('hidden');
                }
            }
        });
    });
    
    // Add project parameters
    document.getElementById("submit-project").addEventListener("click", () => {
        const projectData = {
            project_name: document.getElementById("project-name").value.trim(),
            manager_first_name: document.getElementById("manager-first-name").value.trim(),
            manager_last_name: document.getElementById("manager-last-name").value.trim(),
            institute: document.getElementById("institute-name").value.trim(),
            start_date: document.getElementById("start-date").value.trim(),
            end_date: document.getElementById("end-date").value.trim()
        };
    
        console.log("Project submission:", projectData);
        
        fetch("/projects/add", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(projectData)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error("Network response was not ok");
            }
            return response.text();  // or .json() if your backend returns JSON
        })
        .then(data => {
            console.log("Server response:", data);
            alert("Project added successfully!");
            window.location.href = "/entry";
        })
        
        // .catch(error => {
        //     console.error("Error submitting project:", error);
        //     alert("Error submitting project.");
        // });
    });
    
    // Add user parameters
document.getElementById("submit-user").addEventListener("click", () => {
    const ageValue = document.getElementById("age").value.trim();

    if (isNaN(ageValue) || Number(ageValue) < 0) {
        alert("Age must be a non-negative number.");
        return; // Stop form submission
    }

    const userInfo = {
        username: document.getElementById("user-username").value.trim(),
        social_media: document.getElementById("user-social-media").value.trim(),
        first_name: document.getElementById("user-first-name").value.trim(),
        last_name: document.getElementById("user-last-name").value.trim(),
        country_birth: document.getElementById("user-country-birth").value.trim(),
        country_residence: document.getElementById("user-country-residence").value.trim(),
        age: document.getElementById("user-age").value.trim(),
        gender: document.getElementById("user-gender").value.trim(),
        verified: document.getElementById("user-verified").value.trim()
    };

    console.log("User submission:", projectData);
    
    fetch("/user/add", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(userData)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Network response was not ok");
        }
        return response.text();  // or .json() if your backend returns JSON
    })
    .then(data => {
        console.log("Server response:", data);
        alert("Project added successfully!");
        window.location.href = "/entry";  // redirect if desired
    })
    .catch(error => {
        console.error("Error submitting project:", error);
        alert("Error submitting project.");
    });
});
    
    // Add post parameters
    document.getElementById("submit-post").addEventListener("click", (event) => {
        event.preventDefault(); 
        const ageValue = document.getElementById("age").value.trim();
        const likes = document.getElementById("likes").value.trim();
        const dislikes = document.getElementById("dislikes").value.trim();
        const repostLikes = document.getElementById("repost-likes").value.trim();
        const repostDislikes = document.getElementById("repost-dislikes").value.trim()

        const originalPostTime = document.getElementById("post-time").value.trim();
        const repostTime = document.getElementById("repost-time").value.trim();

        if (repostTime && originalPostTime) {
            const originalDate = new Date(originalPostTime);
            const repostDate = new Date(repostTime);

        if (repostDate < originalDate) {
            alert("Repost time must be later than the original post time.");
        return; // Stop form submission
        }
    }
    
        if (ageValue && (isNaN(ageValue) || Number(ageValue) < 0)) {
            alert("Age must be a non-negative number.");
            return; // Stop form submission
        }
    
        if (likes && (isNaN(likes) || Number(likes) < 0)) {
            alert("Likes must be a non-negative number.");
            return; // Stop form submission
        }
    
        if (dislikes && (isNaN(dislikes) || Number(dislikes) < 0)) {
            alert("Dislikes must be a non-negative number.");
            return; // Stop form submission
        }
    
        if (repostLikes && (isNaN(repostLikes) || Number(repostLikes) < 0)) {
            alert("Repost likes must be a non-negative number.");
            return; // Stop form submission
        }
    
        if (repostDislikes && (isNaN(repostDislikes) || Number(repostDislikes) < 0)) {
            alert("Repost dislikes must be a non-negative number.");
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
            // Always redirect to entry page regardless of response status
            window.location.href = "/entry";
            return null;
        })
        .catch(error => {
            console.error("Error submitting post:", error);
            // Instead of showing alert, just redirect to see the flash message
            window.location.href = "/entry";
        });
    });
    
    // Add analysis parameters
    document.getElementById("submit-analysis").addEventListener("click", () => {
        const analysisData = {
            projectName: document.getElementById("analysis-project-name").value.trim(),
            postUsername: document.getElementById("username").value.trim(),
            socialMedia: document.getElementById("social-media").value.trim(),
            timeOfPost: document.getElementById("post-time").value.trim(),
            fieldName: document.getElementById("field-name").value.trim(),
            result: document.getElementById("analysis").value.trim()  // Fixed typo here (document was misspelled)
        };
    
        console.log("Analysis submission:", analysisData);
    
        fetch("/analysis/add", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(analysisData)
        })
        .then(response => {
            // Always redirect to entry page regardless of response status
            window.location.href = "/entry";
            return null;
        })
        .catch(error => {
            console.error("Error submitting analysis:", error);
            // Instead of showing alert, just redirect to see the flash message
            window.location.href = "/entry";
        });
    });
    
    });