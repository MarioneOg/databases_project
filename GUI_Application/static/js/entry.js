document.addEventListener("DOMContentLoaded", () => {

const buttons = document.querySelectorAll('.entry-button');

const projectForm = document.getElementById('project-form');
const postForm = document.getElementById('post-form');
const analysisForm = document.getElementById('analysis-form');

// Toggle visibility of text fields and selection
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

// Add project parameters
document.getElementById("submit-project").addEventListener("click", () => {
    const projectData = {
        projectName: document.getElementById("project-name").value.trim(),
        managerFirst: document.getElementById("manager-first-name").value.trim(),
        managerLast: document.getElementById("manager-last-name").value.trim(),
        institute: document.getElementById("institute-name").value.trim(),
        startDate: document.getElementById("start-date").value.trim(),
        endDate: document.getElementById("end-date").value.trim()
    };

    console.log("Project submission:", projectData);
    // Backend connection goes here???
});

// Add post parameters
    document.getElementById("submit-post").addEventListener("click", (event) => {
        event.preventDefault(); 
        const ageValue = document.getElementById("age").value.trim();

        if (isNaN(ageValue) || Number(ageValue) < 0) {
            alert("Age must be a non-negative number.");
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
    // Backend connection goes here???
    });


// Add analysis parameters
document.getElementById("submit-analysis").addEventListener("click", () => {
    const analysisData = {
        projectName: document.getElementById("analysis-project-name").value.trim(),
        postUsername: document.getElementById("username").value.trim(),
        socialMedia: document.getElementById("social-media").value.trim(),
        timeOfPost: document.getElementById("post-time").value.trim(),
        fieldName: document.getElementById("field-name").value.trim(),
        result: document.getElementById("analysis").value.trim()
    };

    console.log("Analysis submission:", analysisData);
    // Backend connection goes here???
});

});
  

